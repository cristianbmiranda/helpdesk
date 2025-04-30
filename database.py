import sqlite3

def criar_banco():
    conn = sqlite3.connect('database/sistema.db')
    cursor = conn.cursor()

    # Remove tabela antiga
    cursor.execute('DROP TABLE IF EXISTS usuarios')

    # Cria tabela com o campo email
    cursor.execute('''
        CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL,
            nome TEXT NOT NULL,
            email TEXT NOT NULL,
            perfil TEXT NOT NULL
        )
    ''')

    # Cria tabela de chamados
    cursor.execute('DROP TABLE IF EXISTS chamados')
    cursor.execute('''
        CREATE TABLE chamados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descricao TEXT NOT NULL,
            setor TEXT NOT NULL,
            prioridade TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Aberto',
            usuario TEXT NOT NULL,
            data_abertura TEXT NOT NULL
        )
    ''')

    # Usuário padrão
    cursor.execute('''
        INSERT INTO usuarios (usuario, senha, nome, email, perfil)
        VALUES ('admin', '1234', 'Administrador', 'admin@email.com', 'tecnico')
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    criar_banco()
