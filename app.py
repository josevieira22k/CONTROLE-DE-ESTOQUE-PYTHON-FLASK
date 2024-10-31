from flask import Flask, render_template, request, redirect, url_for, flash, session
import MySQLdb
from flask_mysqldb import MySQL

# Inicialização da aplicação Flask
app = Flask(__name__)
app.secret_key = "chave_secreta_estoque"  # Define uma chave secreta para a sessão da aplicação

# Configurações do MySQL para conexão com o banco de dados
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'estoque'

# Instância do MySQL com as configurações definidas acima
mysql = MySQL(app)

# Rota para a página inicial de login
@app.route('/')
def login():
    return render_template('login.html')  # Renderiza o template HTML de login

# Rota para autenticação de usuário
@app.route('/auth', methods=['POST'])
def auth():
    # Obtém os dados do formulário de login
    username = request.form['username']
    senha = request.form['senha']
    
    # Busca no banco de dados o usuário com as credenciais fornecidas
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE username=%s AND senha=%s", (username, senha))
    user = cursor.fetchone()
    
    # Verifica se o usuário foi encontrado
    if user:
        # Armazena dados na sessão se o login for bem-sucedido
        session['username'] = user[1]
        session['perfil'] = user[3]  # Salva o perfil do usuário (admin ou comum) na sessão
        flash('Login bem-sucedido!', 'success')  # Exibe mensagem de sucesso
        return redirect(url_for('dashboard'))
    else:
        flash('Credenciais inválidas!', 'danger')  # Exibe mensagem de erro
        return redirect(url_for('login'))

# Rota para o dashboard
@app.route('/dashboard')
def dashboard():
    # Verifica se o usuário está logado
    if 'username' in session:
        cursor = mysql.connection.cursor()
        # Obtém o total de produtos no estoque
        cursor.execute("SELECT COUNT(*) FROM produtos")
        total_produtos = cursor.fetchone()[0]

        # Obtém a quantidade de produtos com estoque abaixo do limite
        cursor.execute("SELECT COUNT(*) FROM produtos WHERE quantidade < 10")
        produtos_baixa_quantidade = cursor.fetchone()[0]

        # Renderiza o template do dashboard com dados do estoque
        return render_template('dashboard.html', total_produtos=total_produtos, baixa_quantidade=produtos_baixa_quantidade)
    else:
        return redirect(url_for('login'))  # Redireciona para login se não estiver logado

# Rota para cadastrar produto
@app.route('/cadastrar_produto', methods=['GET', 'POST'])
def cadastrar_produto():
    if 'username' in session:
        if request.method == 'POST':
            # Obtém dados do formulário de cadastro de produto
            nome = request.form.get('nome')
            descricao = request.form.get('descricao')
            quantidade = request.form.get('quantidade')
            preco = request.form.get('preco')
            quantidade_minima = request.form.get('quantidade_minima')

            # Verifica se todos os campos foram preenchidos
            if not all([nome, descricao, quantidade, preco, quantidade_minima]):
                flash('Todos os campos devem ser preenchidos!', 'danger')
                return redirect(url_for('cadastrar_produto'))

            try:
                # Insere o novo produto no banco de dados
                cursor = mysql.connection.cursor()
                cursor.execute("INSERT INTO produtos (nome, descricao, quantidade, preco, quantidade_minima) VALUES (%s, %s, %s, %s, %s)", 
                               (nome, descricao, int(quantidade), float(preco), int(quantidade_minima)))
                mysql.connection.commit()
                flash('Produto cadastrado com sucesso!', 'success')
                return redirect(url_for('dashboard'))
            except MySQLdb.Error as e:
                # Reverte alterações no banco em caso de erro
                mysql.connection.rollback()
                flash(f'Erro ao cadastrar produto: {str(e)}', 'danger')
                return redirect(url_for('cadastrar_produto'))

        return render_template('cadastrar_produto.html')
    else:
        return redirect(url_for('login'))

# Rota para visualizar estoque
@app.route('/visualizar_estoque', methods=['GET'])
def visualizar_estoque():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Obtém termo de pesquisa do formulário (caso exista)
    search_query = request.args.get('search', '')
    
    # Realiza a busca no banco de dados pelo nome do produto se houver termo de pesquisa
    if search_query:
        produtos = buscar_produtos_por_nome(search_query)
        if not produtos:
            flash('Nenhum produto encontrado com esse nome.', 'warning')
    else:
        produtos = obter_produtos()

    return render_template('visualizar_estoque.html', produtos=produtos)

# Função auxiliar para buscar produtos pelo nome
def buscar_produtos_por_nome(nome):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM produtos WHERE nome LIKE %s", ('%' + nome + '%',))
    return cursor.fetchall()

# Função auxiliar para obter todos os produtos
def obter_produtos():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM produtos")
    return cursor.fetchall()

# Rota para editar produto
@app.route('/editar_produto/<int:id>', methods=['GET', 'POST'])
def editar_produto(id):
    if 'username' in session:
        cursor = mysql.connection.cursor()
        if request.method == 'POST':
            # Obtém dados atualizados do formulário
            nome = request.form.get('nome').strip()
            descricao = request.form.get('descricao').strip()
            quantidade = request.form.get('quantidade').strip()
            preco = request.form.get('preco').strip()
            quantidade_minima = request.form.get('quantidade_minima').strip()

            # Valida se todos os campos estão preenchidos
            if not all([nome, descricao, quantidade, preco, quantidade_minima]):
                flash('Todos os campos devem ser preenchidos!', 'danger')
                return redirect(url_for('editar_produto', id=id))

            try:
                # Atualiza o produto no banco de dados
                cursor.execute(
                    "UPDATE produtos SET nome=%s, descricao=%s, quantidade=%s, preco=%s, quantidade_minima=%s WHERE id=%s",
                    (nome, descricao, int(quantidade), float(preco), int(quantidade_minima), id)
                )
                mysql.connection.commit()
                flash('Produto atualizado com sucesso!', 'success')
                return redirect(url_for('visualizar_estoque'))
            except MySQLdb.Error as e:
                mysql.connection.rollback()
                flash(f'Erro ao atualizar produto: {str(e)}', 'danger')
                return redirect(url_for('editar_produto', id=id))

        cursor.execute("SELECT * FROM produtos WHERE id=%s", (id,))
        produto = cursor.fetchone()
        return render_template('editar_produto.html', produto=produto)
    else:
        return redirect(url_for('login'))

# Rota para excluir produto
@app.route('/excluir_produto/<int:id>')
def excluir_produto(id):
    if 'username' in session:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM produtos WHERE id=%s", (id,))
        mysql.connection.commit()
        flash('Produto excluído com sucesso!', 'success')
        return redirect(url_for('visualizar_estoque'))
    else:
        return redirect(url_for('login'))

# Rota para cadastrar usuário
@app.route('/cadastrar_usuario', methods=['GET', 'POST'])
def cadastrar_usuario():
    if 'username' in session and session['perfil'] == 'admin':
        if request.method == 'POST':
            username = request.form['username']
            senha = request.form['senha']
            perfil = request.form['perfil']

            # Insere o novo usuário no banco de dados
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO usuarios (username, senha, perfil) VALUES (%s, %s, %s)", 
                           (username, senha, perfil))
            mysql.connection.commit()

            flash('Usuário cadastrado com sucesso!', 'success')
            return redirect(url_for('dashboard'))

        return render_template('cadastrar_usuario.html')
    else:
        return redirect(url_for('login'))

# Rota para visualizar produtos em falta
@app.route('/produtos_em_falta')
def produtos_em_falta():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Obtém produtos com quantidade abaixo do limite
    produtos = get_produtos_em_falta()
    return render_template('produtos_em_falta.html', produtos=produtos)

# Função auxiliar para buscar produtos com baixa quantidade
def get_produtos_em_falta():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, nome, descricao, quantidade, preco FROM produtos WHERE quantidade < quantidade_minima")
    produtos = cursor.fetchall()
    cursor.close()
    return produtos

# Rota para logout
@app.route('/logout')
def logout():
    # Remove dados de sessão ao sair
    session.pop('username', None)
    session.pop('perfil', None)
    flash('Você saiu com sucesso!', 'success')
    return redirect(url_for('login'))

# Executa a aplicação Flask
if __name__ == "__main__":
    app.run(debug=True)
