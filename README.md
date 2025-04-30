# HelpDesk - Sistema de Chamados

Sistema web para registro e gerenciamento de chamados técnicos de informática, desenvolvido para uso institucional da Prefeitura de Amambai-MS.

## Funcionalidades

- Cadastro e login de usuários com dois tipos de perfil: comum e técnico
- Abertura de chamados com título, descrição, prioridade e setor
- Dashboard com visualização de chamados conforme o perfil do usuário
- Edição de status e atribuição de técnico responsável (acesso restrito a técnicos)
- Layout responsivo utilizando Bootstrap

## Tecnologias utilizadas

- Python 3
- Flask
- SQLite
- HTML + CSS (Bootstrap)
- Flask-Mail
- Git e GitHub

## Estrutura do projeto

```
helpdesk/
├── app.py
├── database/
│   └── sistema.db
├── templates/
│   ├── login.html
│   ├── dashboard.html
│   ├── abrir_chamado.html
│   ├── editar_chamado.html
│   ├── cadastro_usuario.html
│   └── recuperar_senha.html
├── requirements.txt
├── .gitignore
├── start_helpdesk.bat
```

## Como executar localmente

1. Clone o repositório:
```
git clone https://github.com/cristianbmiranda/helpdesk.git
cd helpdesk
```

2. Crie e ative o ambiente virtual:
```
python -m venv venv
venv\Scripts\activate
```

3. Instale as dependências:
```
pip install -r requirements.txt
```

4. Inicie a aplicação:
```
python app.py
```

Abra no navegador: http://localhost:5000

## Acesso de exemplo

Usuário: admin  
Senha: 1234  
Perfil: técnico

## Licença

Sistema desenvolvido para fins institucionais e educacionais.  
Prefeitura de Amambai-MS - 2025