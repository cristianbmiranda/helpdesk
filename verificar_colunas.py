import sqlite3

conn = sqlite3.connect('database/sistema.db')
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(chamados)")
colunas = cursor.fetchall()

print("\n📋 Colunas na tabela 'chamados':")
for coluna in colunas:
    print(f" - {coluna[1]}")

conn.close()
