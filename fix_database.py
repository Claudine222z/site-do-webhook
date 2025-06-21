import os

# Criar pasta instance se não existir
instance_path = os.path.join(os.path.dirname(__file__), 'instance')
if not os.path.exists(instance_path):
    os.makedirs(instance_path, exist_ok=True)
    print(f"✅ Pasta instance criada: {instance_path}")
else:
    print(f"✅ Pasta instance já existe: {instance_path}")

# Testar se consegue criar arquivo
test_file = os.path.join(instance_path, 'test.txt')
try:
    with open(test_file, 'w') as f:
        f.write('teste')
    os.remove(test_file)
    print("✅ Permissões OK - pode criar arquivos")
except Exception as e:
    print(f"❌ Erro de permissões: {e}")
