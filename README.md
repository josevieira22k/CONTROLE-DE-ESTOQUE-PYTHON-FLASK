# CONTROLE-DE-ESTOQUE-PYTHON-FLASK
Este projeto faz parte das avaliações do curso de graduação em Análise e Desenvolvimento de Sistemas da faculdade UniFecaf.
Disciplina Desenvolvimento Python

1. Descrição do Projeto
Este projeto é uma aplicação web desenvolvida em Flask que permite:

Cadastrar, editar e visualizar produtos no estoque.
Gerenciar a quantidade de produtos, com alertas de quantidade mínima.
Cadastrar e autenticar usuários com diferentes permissões (administrador,comum)
Exibir um painel de controle
Mantém um design consistente usando HTML , CSS (styles.css), e templates Jinja.

2. Estrutura do Projeto
A estrutura básica de diretórios para o projeto pode ser a seguinte:

projeto_estoque/
├── app.py                   
├── app.py                   # Código principal # Código principal do Flask
├── templates/               
├── templates/  
# Diretório para os templates HTML
│   ├── index.html
│   ├── login.html
│   ├── dashboard.html
│   ├── cadastrar_produto.html
│   ├── editar_produto.html
│   └── cadastrar_usuario.html
├── static/
│   └── styles.css           # Estilos CSS para os templates
└── venv/                    # Ambiente virtual Python (opcional)

3. Configuração do Banco de Dados
O projeto utiliza SQLAlchemy com MySQL para gerenciar os dados. As tabelas principais incluem:

Usuario: para armazenar as informações dos usuários (ID, nome de usuário, senha e perfil).

Produto: para manter o registro dos produtos no estoque (ID, nome e quantidade).

A conexão ao banco é configurada no app.py, onde é especificado o URI do banco de dados MySQL.

4. Principais Funcionalidades
   
A. Autenticação de Usuário

A funcionalidade de login valida o nome de usuário e a senha e autentica os usuários usando o sessionFlask.
Usuários com perfil de administrador têm permissões para cadastrar novos usuários e produtos.

B. Gerenciamento de Produtos

Cadastro de Produto : Permite que o administrador adicione produtos ao estoque.
Edição de Produto : Funcionalidade para modificar os dados dos produtos existentes.
Visualização do Estoque : Exibe todos os produtos no estoque, destacando aqueles com baixa quantidade.

C. Painel
Um painel de controle com um resumo das atividades e estado atual do estoque.
Mostra produtos com quantidade baixa para alerta imediato.

D. Gerenciamento de Usuários
Cadastro de Usuário : Apenas administradores podem cadastrar novos usuários.
Sair : Remove a sessão ativa do usuário e redireciona para a página inicial.

5. Modelos HTML e CSS

HTML e Jinja : Cada rota importante possui um template HTML específico com o uso de Jinja para
dashboard.htmlexibe uma lista de produtos com seus respectivos tamanhos.
login.htmlfornece o formulário de login.
CSS : O arquivo styles.cssmantém a consistência visual em todo o site, com estilos para os formulários, botões, tabelas, e alertas.

6. Lógica do Flask (app.py)

O app.pyé o núcleo da aplicação. Nele, configuramos as rotas para cada funcionalidade mencionada, utilizando o SQLAlchemy para as operações no banco de dados. Cada rota geralmente segue a estrutura de:

GET para exibir o formulário ou a página.
POST para processar os dados enviados (por exemplo, sem login ou cadastro).

7. Exemplo de Rota com Autenticação e Renderização de Template

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(username=username).first()
        if usuario and check_password_hash(usuario.senha, senha):
            session['user_id'] = usuario.id
            return redirect(url_for('dashboard'))
        flash('Usuário ou senha incorretos.', 'danger')
    return render_template('login.html')

8. Configuração Inicial e Instalações Necessárias
Para configurar o projeto, é necessário:

Criar um ambiente virtual:
python -m venv venv

Instalar as dependências:
pip install flask flask_sqlalchemy pymysql werkzeug

Configure o banco de dados no MySQL e certifique-se de que o URI não app.config['SQLALCHEMY_DATABASE_URI']esteja correto.

9. Boas Práticas e Testes
   
Verificação de Sessão : Em rotas que desabilitam autenticação, como dashboarde cadastrar_produto, verificamos se o user_idestá presente
Mensagens Flash : Utilizei mensagens flash para fornecer feedback ao usuário, como sucesso ou erro nas ações.
Testes Frequentes : Testar cada funcionalidade isoladamente ajuda a identificar problemas rapidamente.

10. Expansões Futuras
Este projeto pode ser expandido para incluir:

Relatórios em PDF ou CSV de estoque e atividades.
Histórico de alterações no estoque.
Notificações por e-mail para produtos abaixo da quantidade mínima.
Este é um resumo para guiar o desenvolvimento
