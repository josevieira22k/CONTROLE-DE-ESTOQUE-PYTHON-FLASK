from flask import Flask, render_template, request, redirect, url_for, flash, session
import MySQLdb
from flask_mysqldb import MySQL

# Inicialização da aplicação Flask
app = Flask(__name__)
app.secret_key = "chave_secreta_estoque"  # Define uma chave secreta para a sessão da aplicação, usada para manter informações do usuário logado

# Configurações de conexão com o banco de dados MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''  # Alterar para a senha correta, se houver
app.config['MYSQL_DB'] = 'estoque'

# Instância do MySQL usando as configurações acima
mysql = MySQL(app)

# Rota para a página inicial de login
@app.route('/')
def login():
    # Renderiza o template de login para autenticação do usuário
    return render_template('login.html')

# Rota para autenticação de usuário
@app.route('/auth', methods=['POST'])
def auth():
    # Obtém os dados enviados no formulário de login
    username = request.form['username']
    senha = request.form['senha']
    
    # Realiza consulta no banco de dados para verificar as credenciais
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE username=%s AND senha=%s", (username, senha))
    user = cursor.fetchone()
    
    # Caso o usuário seja encontrado, configura a sessão e redireciona para o dashboard
    if user:
        session['username'] = user[1]  # Guarda o nome de usuário na sessão
        session['perfil'] = user[3]  # Guarda o perfil do usuário (admin ou comum) na sessão
        flash('Login bem-sucedido!', 'success')  # Exibe mensagem de sucesso
        return redirect(url_for('dashboard'))
    else:
        # Exibe mensagem de erro se as credenciais não forem válidas
        flash('Credenciais inválidas!', 'danger')
        return redirect(url_for('login'))

# Rota para o painel principal (dashboard)
@app.route('/dashboard')
def dashboard():
    # Verifica se o usuário está logado na sessão
    if 'username' in session:
        cursor = mysql.connection.cursor()
        # Conta o número total de produtos no estoque
        cursor.execute("SELECT COUNT(*) FROM produtos")
        total_produtos = cursor.fetchone()[0]

        # Conta produtos com quantidade abaixo do limite
        cursor.execute("SELECT COUNT(*) FROM produtos WHERE quantidade < 10")
        produtos_baixa_quantidade = cursor.fetchone()[0]

        # Renderiza o dashboard com as informações do estoque
        return render_template('dashboard.html', total_produtos=total_produtos, baixa_quantidade=produtos_baixa_quantidade)
    else:
        # Redireciona para login se o usuário não estiver logado
        return redirect(url_for('login'))

# Rota para cadastrar um novo produto
@app.route('/cadastrar_produto', methods=['GET', 'POST'])
def cadastrar_produto():
    # Verifica se o usuário está logado
    if 'username' in session:
        if request.method == 'POST':
            # Obtém os dados do formulário de cadastro
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
                mysql.connection.commit()  # Confirma a inserção no banco
                flash('Produto cadastrado com sucesso!', 'success')
                return redirect(url_for('dashboard'))
            except MySQLdb.Error as e:
                # Em caso de erro, desfaz a transação
                mysql.connection.rollback()
                flash(f'Erro ao cadastrar produto: {str(e)}', 'danger')
                return redirect(url_for('cadastrar_produto'))

        # Renderiza a página de cadastro de produto para requisições GET
        return render_template('cadastrar_produto.html')
    else:
        return redirect(url_for('login'))

# Rota para visualizar todos os produtos no estoque
@app.route('/visualizar_estoque', methods=['GET'])
def visualizar_estoque():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Obtém o termo de busca (se fornecido pelo usuário)
    search_query = request.args.get('search', '')
    
    # Busca no banco de dados pelo nome do produto
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

# Rota para editar um produto existente
@app.route('/editar_produto/<int:id>', methods=['GET', 'POST'])
def editar_produto(id):
    if 'username' in session:
        cursor = mysql.connection.cursor()
        if request.method == 'POST':
            # Coleta dados atualizados do formulário
            nome = request.form.get('nome').strip()
            descricao = request.form.get('descricao').strip()
            quantidade = request.form.get('quantidade').strip()
            preco = request.form.get('preco').strip()
            quantidade_minima = request.form.get('quantidade_minima').strip()

            # Verifica se todos os campos estão preenchidos
            if not all([nome, descricao, quantidade, preco, quantidade_minima]):
                flash('Todos os campos devem ser preenchidos!', 'danger')
                return redirect(url_for('editar_produto', id=id))

            try:
                # Atualiza as informações do produto no banco de dados
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
        produto = cursor.fetchone()  # Busca o produto para edição
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

# Rota para cadastrar um novo usuário (apenas admin)
@app.route('/cadastrar_usuario', methods=['GET', 'POST'])
def cadastrar_usuario():
    if 'username' in session and session['perfil'] == 'admin':
        if request.method == 'POST':
            # Obtém dados do formulário de cadastro de usuário
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

# Rota para visualizar produtos com quantidade baixa
@app.route('/produtos_em_falta')
def produtos_em_falta():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Busca produtos com quantidade abaixo do mínimo
    produtos = get_produtos_em_falta()
    return render_template('produtos_em_falta.html', produtos=produtos)

# Função auxiliar para buscar produtos com baixa quantidade
def get_produtos_em_falta():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, nome, descricao, quantidade, quantidade_minima FROM produtos WHERE quantidade < quantidade_minima")
    return cursor.fetchall()

# Rota para logout
@app.route('/logout')
def logout():
    # Limpa a sessão do usuário logado
    session.clear()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('login'))

# Execução da aplicação
if __name__ == '__main__':
    app.run(debug=True)
