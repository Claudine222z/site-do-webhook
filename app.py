from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
import secrets
import string
from datetime import datetime
import json
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Criar pasta instance
def ensure_instance_folder():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    instance_path = os.path.join(current_dir, 'instance')
    
    if not os.path.exists(instance_path):
        os.makedirs(instance_path, exist_ok=True)
        print(f"✅ Pasta instance criada: {instance_path}")
    
    return instance_path

# Garantir pasta instance
instance_path = ensure_instance_folder()

# Configurar Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')

# Configurar banco
db_path = os.path.join(instance_path, 'webhooks.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

print(f"🗄️ Banco configurado em: {db_path}")

# Inicializar SQLAlchemy
db = SQLAlchemy(app)

# MODELOS
class Webhook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    token = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relacionamento com logs
    logs = db.relationship('WebhookLog', backref='webhook', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Webhook {self.name}>'

class WebhookLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    webhook_id = db.Column(db.Integer, db.ForeignKey('webhook.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    method = db.Column(db.String(10), nullable=False)
    headers = db.Column(db.Text)
    body = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(200))
    
    def __repr__(self):
        return f'<WebhookLog {self.id}>'

# FUNÇÕES AUXILIARES
def create_tables():
    """Criar tabelas do banco de dados"""
    try:
        with app.app_context():
            db.create_all()
            print("✅ Tabelas criadas com sucesso!")
            
            # Verificar
            webhook_count = Webhook.query.count()
            print(f"📊 Webhooks existentes: {webhook_count}")
            
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        raise

def generate_token(length=32):
    """Gerar token aleatório"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

# ROTAS
@app.route('/')
def index():
    webhooks = Webhook.query.all()  # ← CORREÇÃO: Mostra todos os webhooks (ativos e inativos)
    return render_template('index.html', webhooks=webhooks)

@app.route('/create', methods=['GET', 'POST'])
def create_webhook():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        
        if not name:
            flash('Nome do webhook é obrigatório!', 'error')
            return redirect(url_for('create_webhook'))
        
        # Verificar se já existe
        existing = Webhook.query.filter_by(name=name).first()
        if existing:
            flash('Já existe um webhook com este nome!', 'error')
            return redirect(url_for('create_webhook'))
        
        # Criar novo webhook
        token = generate_token()
        webhook = Webhook(name=name, token=token)
        
        try:
            db.session.add(webhook)
            db.session.commit()
            flash(f'Webhook "{name}" criado com sucesso!', 'success')
            return redirect(url_for('webhook_details', webhook_id=webhook.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar webhook: {str(e)}', 'error')
            return redirect(url_for('create_webhook'))
    
    return render_template('create_webhook.html')

@app.route('/webhook/<int:webhook_id>')
def webhook_details(webhook_id):
    webhook = Webhook.query.get_or_404(webhook_id)
    logs = WebhookLog.query.filter_by(webhook_id=webhook_id).order_by(WebhookLog.timestamp.desc()).limit(50).all()
    return render_template('webhook_details.html', webhook=webhook, logs=logs)

@app.route('/webhook/<webhook_name>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def receive_webhook(webhook_name):
    # Buscar webhook pelo nome
    webhook = Webhook.query.filter_by(name=webhook_name, is_active=True).first()
    
    if not webhook:
        return jsonify({'error': 'Webhook não encontrado'}), 404
    
    # Verificar token se fornecido
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        provided_token = auth_header[7:]  # Remove "Bearer "
        if provided_token != webhook.token:
            return jsonify({'error': 'Token inválido'}), 401
    
    # Capturar dados da requisição
    try:
        body_data = request.get_data(as_text=True)
        headers_data = dict(request.headers)
        
        # Criar log
        log = WebhookLog(
            webhook_id=webhook.id,
            method=request.method,
            headers=json.dumps(headers_data),
            body=body_data,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )
        
        db.session.add(log)
        db.session.commit()
        
        # Resposta de sucesso
        response_data = {
            'status': 'success',
            'webhook': webhook_name,
            'timestamp': datetime.utcnow().isoformat(),
            'method': request.method,
            'log_id': log.id
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/webhook/<int:webhook_id>/toggle', methods=['POST'])
def toggle_webhook(webhook_id):
    webhook = Webhook.query.get_or_404(webhook_id)
    webhook.is_active = not webhook.is_active
    
    try:
        db.session.commit()
        status = 'ativado' if webhook.is_active else 'desativado'
        flash(f'Webhook "{webhook.name}" {status} com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao alterar status: {str(e)}', 'error')
    
    return redirect(url_for('webhook_details', webhook_id=webhook_id))

@app.route('/webhook/<int:webhook_id>/delete', methods=['POST'])
def delete_webhook(webhook_id):
    webhook = Webhook.query.get_or_404(webhook_id)
    webhook_name = webhook.name
    
    try:
        db.session.delete(webhook)
        db.session.commit()
        flash(f'Webhook "{webhook_name}" excluído com sucesso!', 'success')
        return redirect(url_for('index'))
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir webhook: {str(e)}', 'error')
        return redirect(url_for('webhook_details', webhook_id=webhook_id))

@app.route('/api/webhooks')
def api_webhooks():
    webhooks = Webhook.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': w.id,
        'name': w.name,
        'created_at': w.created_at.isoformat(),
        'url': url_for('receive_webhook', webhook_name=w.name, _external=True)
    } for w in webhooks])

# INICIALIZAÇÃO
if __name__ == '__main__':
    print("🚀 Iniciando aplicação...")
    
    # Criar tabelas
    create_tables()
    
    # Executar servidor
    print("🌐 Servidor rodando em: http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
