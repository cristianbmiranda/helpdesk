import sqlite3

conn = sqlite3.connect('database/sistema.db')
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE chamados ADD COLUMN tecnico_responsavel TEXT")
    print("✅ Coluna 'tecnico_responsavel' adicionada com sucesso.")
except sqlite3.OperationalError as e:
    print("❌ Erro:", e)

conn.commit()
conn.close()
