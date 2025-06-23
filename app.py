from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
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
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production-VERY-IMPORTANT')

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

print(f"🗄️ Banco configurado via variável .env")


# Inicializar SQLAlchemy e Login Manager
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Você precisa fazer login para acessar esta página.'
login_manager.login_message_category = 'info'

# MODELOS
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Webhook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    token = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relacionamentos
    logs = db.relationship('WebhookLog', backref='webhook', lazy=True, cascade='all, delete-orphan')
    user = db.relationship('User', backref='webhooks')
    
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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# FUNÇÕES AUXILIARES
def create_tables():
    """Criar tabelas do banco de dados"""
    try:
        with app.app_context():
            db.create_all()
            print("✅ Tabelas criadas com sucesso!")
            
            # Criar usuário admin padrão se não existir
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(
                    username='admin',
                    email='admin@webhook.local'
                )
                admin.set_password('admin123')  # MUDE ESTA SENHA!
                db.session.add(admin)
                db.session.commit()
                print("🔑 Usuário admin criado - Login: admin | Senha: admin123")
                print("⚠️  IMPORTANTE: Mude a senha padrão!")
            
            # Verificar
            user_count = User.query.count()
            webhook_count = Webhook.query.count()
            print(f"👥 Usuários: {user_count} | 📊 Webhooks: {webhook_count}")
            
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        raise

def generate_token(length=32):
    """Gerar token aleatório"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

# ROTAS DE AUTENTICAÇÃO
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Usuário e senha são obrigatórios!', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_active:
            login_user(user, remember=True)
            flash(f'Bem-vindo, {user.username}!', 'success')
            
            # Redirecionar para página solicitada ou dashboard
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Usuário ou senha incorretos!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validações
        if not all([username, email, password, confirm_password]):
            flash('Todos os campos são obrigatórios!', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('As senhas não coincidem!', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('A senha deve ter pelo menos 6 caracteres!', 'error')
            return render_template('register.html')
        
        # Verificar se usuário já existe
        if User.query.filter_by(username=username).first():
            flash('Nome de usuário já existe!', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email já cadastrado!', 'error')
            return render_template('register.html')
        
        # Criar usuário
        user = User(username=username, email=email)
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Conta criada com sucesso! Faça login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar conta: {str(e)}', 'error')
    
    return render_template('register.html')

# ROTAS PROTEGIDAS
@app.route('/')
@login_required
def index():
    # Mostrar apenas webhooks do usuário logado
    webhooks = Webhook.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', webhooks=webhooks)

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_webhook():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        
        if not name:
            flash('Nome do webhook é obrigatório!', 'error')
            return redirect(url_for('create_webhook'))
        
        # Verificar se já existe para este usuário
        existing = Webhook.query.filter_by(name=name, user_id=current_user.id).first()
        if existing:
            flash('Você já tem um webhook com este nome!', 'error')
            return redirect(url_for('create_webhook'))
        
        # Criar novo webhook
        token = generate_token()
        webhook = Webhook(name=name, token=token, user_id=current_user.id)
        
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
@login_required
def webhook_details(webhook_id):
    # Verificar se o webhook pertence ao usuário
    webhook = Webhook.query.filter_by(id=webhook_id, user_id=current_user.id).first_or_404()
    logs = WebhookLog.query.filter_by(webhook_id=webhook_id).order_by(WebhookLog.timestamp.desc()).limit(50).all()
    return render_template('webhook_details.html', webhook=webhook, logs=logs)

# ROTA PÚBLICA PARA RECEBER WEBHOOKS (sem login)
@app.route('/webhook/<webhook_name>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def receive_webhook(webhook_name):
    # Buscar webhook pelo nome (ativo)
    webhook = Webhook.query.filter_by(name=webhook_name, is_active=True).first()
    
    if not webhook:
        return jsonify({'error': 'Webhook não encontrado'}), 404
    
    # Verificar token se fornecido
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        provided_token = auth_header[7:]
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
@login_required
def toggle_webhook(webhook_id):
    webhook = Webhook.query.filter_by(id=webhook_id, user_id=current_user.id).first_or_404()
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
@login_required
def delete_webhook(webhook_id):
    webhook = Webhook.query.filter_by(id=webhook_id, user_id=current_user.id).first_or_404()
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
@login_required
def api_webhooks():
    webhooks = Webhook.query.filter_by(user_id=current_user.id, is_active=True).all()
    return jsonify([{
        'id': w.id,
        'name': w.name,
        'created_at': w.created_at.isoformat(),
        'url': url_for('receive_webhook', webhook_name=w.name, _external=True)
    } for w in webhooks])

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not current_user.check_password(current_password):
            flash('Senha atual incorreta!', 'error')
            return render_template('change_password.html')
        
        if new_password != confirm_password:
            flash('As senhas não coincidem!', 'error')
            return render_template('change_password.html')
        
        if len(new_password) < 6:
            flash('A nova senha deve ter pelo menos 6 caracteres!', 'error')
            return render_template('change_password.html')
        
        current_user.set_password(new_password)
        db.session.commit()
        flash('Senha alterada com sucesso!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('change_password.html')

# INICIALIZAÇÃO
if __name__ == '__main__':
    print("🚀 Iniciando aplicação...")
    
    # Criar tabelas
    create_tables()
    
    # Executar servidor
    print("🌐 Servidor rodando em: http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
