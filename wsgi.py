#!/usr/bin/python3
import sys
import os

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(__file__))

# Importar a aplicação
from app import app

# Criar tabelas se não existirem
def init_db():
    try:
        from app import db
        with app.app_context():
            # Criar pasta instance se não existir
            instance_path = os.path.join(os.path.dirname(__file__), 'instance')
            if not os.path.exists(instance_path):
                os.makedirs(instance_path, exist_ok=True)
            
            # Criar tabelas
            db.create_all()
    except Exception as e:
        print(f"Erro ao inicializar banco: {e}")

# Inicializar banco na primeira execução
init_db()

# Aplicação WSGI
application = app

if __name__ == "__main__":
    app.run()
