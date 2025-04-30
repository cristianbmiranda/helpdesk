from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = 'chave_secreta_chamados'

# ==========================================
# CONFIGURAÇÃO DE E-MAIL
# ==========================================

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'seu_email@gmail.com'         # Substitua
app.config['MAIL_PASSWORD'] = 'sua_senha_de_app'            # Substitua
app.config['MAIL_DEFAULT_SENDER'] = ('HelpDesk', 'seu_email@gmail.com')

mail = Mail(app)

# ==========================================
# CONEXÃO COM O BANCO
# ==========================================

def get_db_connection():
    conn = sqlite3.connect('database/sistema.db')
    conn.row_factory = sqlite3.Row
    return conn

# ==========================================
# FUNÇÃO DE ENVIO DE E-MAIL
# ==========================================

def enviar_email(destinatario, assunto, corpo):
    try:
        msg = Message(assunto, recipients=[destinatario])
        msg.body = corpo
        mail.send(msg)
    except Exception as e:
        print(f"[ERRO] Falha ao enviar e-mail: {e}")

# ==========================================
# ROTAS
# ==========================================

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM usuarios WHERE usuario = ? AND senha = ?', (usuario, senha)).fetchone()
        conn.close()

        if user:
            session['usuario'] = user['usuario']
            session['nome'] = user['nome']
            session['perfil'] = user['perfil']
            session['email'] = user['email']
            return redirect(url_for('dashboard'))
        else:
            flash('Usuário ou senha incorretos.', 'danger')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'usuario' in session:
        usuario = session['usuario']
        perfil = session['perfil']
        conn = get_db_connection()

        if perfil == 'tecnico':
            chamados = conn.execute('SELECT * FROM chamados ORDER BY data_abertura DESC').fetchall()
        else:
            chamados = conn.execute('SELECT * FROM chamados WHERE usuario = ? ORDER BY data_abertura DESC', (usuario,)).fetchall()

        conn.close()
        return render_template('dashboard.html', nome=session['nome'], chamados=chamados, perfil=perfil)

    return redirect(url_for('login'))

@app.route('/abrir_chamado', methods=['GET', 'POST'])
def abrir_chamado():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    perfil = session['perfil']
    conn = get_db_connection()

    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        setor = request.form['setor']
        prioridade = request.form['prioridade']
        tecnico_responsavel = request.form.get('tecnico_responsavel') if perfil == 'tecnico' else ''
        status = 'Aberto'
        usuario = session['usuario']
        email_usuario = session['email']
        data_abertura = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        conn.execute('''
            INSERT INTO chamados (titulo, descricao, setor, prioridade, status, usuario, data_abertura, tecnico_responsavel)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (titulo, descricao, setor, prioridade, status, usuario, data_abertura, tecnico_responsavel))
        conn.commit()
        conn.close()

        enviar_email(
            destinatario=email_usuario,
            assunto='Confirmação de abertura de chamado - HelpDesk',
            corpo=f'''Olá {usuario},\n\nSeu chamado foi registrado com sucesso!\n\nTítulo: {titulo}\nDescrição: {descricao}\nSetor: {setor}\nPrioridade: {prioridade}\nTécnico Responsável: {tecnico_responsavel or 'Não atribuído'}\nData: {data_abertura}\nStatus: {status}\n\nEquipe HelpDesk'''
        )

        flash('Chamado aberto com sucesso!', 'success')
        return redirect(url_for('dashboard'))

    tecnicos = []
    if perfil == 'tecnico':
        tecnicos = conn.execute("SELECT nome FROM usuarios WHERE perfil = 'tecnico'").fetchall()

    conn.close()
    return render_template('abrir_chamado.html', tecnicos=tecnicos, perfil=perfil)

@app.route('/editar_chamado/<int:id>', methods=['GET', 'POST'])
def editar_chamado(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))

    if session.get('perfil') != 'tecnico':
        flash('Acesso restrito. Apenas técnicos podem editar chamados.', 'danger')
        return redirect(url_for('dashboard'))

    conn = get_db_connection()
    chamado = conn.execute('SELECT * FROM chamados WHERE id = ?', (id,)).fetchone()
    tecnicos = conn.execute("SELECT nome FROM usuarios WHERE perfil = 'tecnico'").fetchall()

    if chamado is None:
        conn.close()
        flash('Chamado não encontrado.', 'warning')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        novo_status = request.form['status']
        novo_tecnico = request.form['tecnico_responsavel']

        conn.execute('''
            UPDATE chamados
            SET status = ?, tecnico_responsavel = ?
            WHERE id = ?
        ''', (novo_status, novo_tecnico, id))
        conn.commit()

        solicitante = chamado['usuario']
        user = conn.execute('SELECT * FROM usuarios WHERE usuario = ?', (solicitante,)).fetchone()
        conn.close()

        if user:
            enviar_email(
                destinatario=user['email'],
                assunto='Atualização de chamado - HelpDesk',
                corpo=f'''Olá {user['nome']},\n\nSeu chamado foi atualizado.\n\nTítulo: {chamado['titulo']}\nNovo Status: {novo_status}\nTécnico Responsável: {novo_tecnico or 'Não definido'}\n\nEquipe HelpDesk'''
            )

        flash('Chamado atualizado com sucesso! E-mail enviado ao solicitante.', 'success')
        return redirect(url_for('dashboard'))

    conn.close()
    return render_template('editar_chamado.html', chamado=chamado, tecnicos=tecnicos)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/cadastrar_usuario', methods=['GET', 'POST'])
def cadastrar_usuario():
    if request.method == 'POST':
        nome = request.form['nome']
        usuario = request.form['usuario']
        senha = request.form['senha']
        email = request.form['email']
        perfil = request.form['perfil']

        conn = get_db_connection()
        try:
            conn.execute('''
                INSERT INTO usuarios (usuario, senha, nome, email, perfil)
                VALUES (?, ?, ?, ?, ?)
            ''', (usuario, senha, nome, email, perfil))
            conn.commit()
            flash('Usuário cadastrado com sucesso!', 'success')
        except sqlite3.IntegrityError:
            flash('Usuário já existe!', 'danger')
        finally:
            conn.close()

        return redirect(url_for('login'))

    return render_template('cadastro_usuario.html')

@app.route('/recuperar_senha', methods=['GET', 'POST'])
def recuperar_senha():
    if request.method == 'POST':
        email = request.form['email']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM usuarios WHERE email = ?', (email,)).fetchone()
        conn.close()

        if user:
            enviar_email(
                destinatario=email,
                assunto='Recuperação de senha - HelpDesk',
                corpo=f'''Olá {user['nome']},\n\nRecebemos uma solicitação de recuperação de senha.\n\nUsuário: {user['usuario']}\n\nEquipe HelpDesk'''
            )
            flash('E-mail enviado com instruções. Verifique sua caixa de entrada.', 'success')
        else:
            flash('E-mail não encontrado.', 'danger')

        return redirect(url_for('login'))

    return render_template('recuperar_senha.html')

# ==========================================
# EXECUÇÃO
# ==========================================

if __name__ == '__main__':
    app.run(debug=True)
