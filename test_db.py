import os
import sqlite3

# Criar pasta instance
instance_path = os.path.join(os.path.dirname(__file__), 'instance')
if not os.path.exists(instance_path):
    os.makedirs(instance_path, exist_ok=True)
    print(f"✅ Pasta criada: {instance_path}")

# Testar criação do banco
db_path = os.path.join(instance_path, 'test.db')
try:
    conn = sqlite3.connect(db_path)
    conn.execute('CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY)')
    conn.commit()
    conn.close()
    print(f"✅ Banco de teste criado: {db_path}")
    
    # Remover arquivo de teste
    os.remove(db_path)
    print("✅ Teste concluído com sucesso!")
    
except Exception as e:
    print(f"❌ Erro no teste: {e}")
