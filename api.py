from flask import Flask, jsonify, redirect, request
from flask_pydantic_spec import FlaskPydanticSpec
from datetime import date
from dateutil.relativedelta import relativedelta
from models import db_session, Livros, Emprestimos, Usuarios
from datetime import date
from dateutil.relativedelta import relativedelta
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, desc

app = Flask(__name__)
spec = FlaskPydanticSpec('Flask',
                         title='Flask API',
                         version='1.0.0')
spec.register(app)
app.secret_key = 'chave_secreta'

@app.route('/')
def index():
    return redirect('/consultar_livros')


@app.route('/consultar_usuarios', methods=['GET'])
def consultar_usuarios():
    try:
        usuarios = db_session.execute(select(Usuarios)).scalars().all()

        lista_usuarios = []
        for usuario in usuarios:
            lista_usuarios.append(usuario.get_usuario())

        return jsonify({'usuarios_cadastrados': lista_usuarios})
    except Exception as e:
        return jsonify({'error': 'Erro ao consultar usuários', 'detalhes': str(e)}), 500


@app.route('/consultar_livros')
def consultar_livros():
    try:
        lista_livros = select(Livros)
        lista_livros = db_session.execute(lista_livros).scalars()
        result = []
        for livro in lista_livros:
            result.append(livro.get_livro())
        db_session.close()
        db_session.close()



        return jsonify({'livrosnocatalogodabiblioteca': result})
    except IntegrityError as e:
        return jsonify({'error': str(e)})


@app.route('/cadastrar_livro', methods=['POST'])
def cadastrar_livro():
    if request.method == 'POST':
        dados = request.get_json()
        titulo = dados['titulo']
        autor = dados['autor']
        resumo = dados['resumo']
        isbn = dados['isbn']
        isbn_existente = select(Livros)
        isbn_existente = db_session.execute(isbn_existente.filter_by(ISBN=isbn)).first()
        if isbn_existente:
            return jsonify({'isbn já existente': isbn_existente})
        if not titulo:
            return jsonify({"error": 'campo titulo vazio'}, 400)
        if not autor:
            return jsonify({"error": 'campo autor vazio'}, 400)
        if not resumo:
            return jsonify({"error": 'campo resumo vazio'}, 400)
        if not isbn:
            return jsonify({"error": 'campo ISBN vazio'}, 400)
        else:
            try:
                isbn = int(isbn)
                livro_salvado = Livros(titulo=titulo,
                                       autor=autor,
                                       resumo=resumo,
                                       ISBN=isbn,
                                       status=True)
                livro_salvado.save()
                if livro_salvado.status:
                    status_emprestimo = 'Está disponivel para emprestimo'
                else:
                    status_emprestimo = 'Livro não está disponivel para emprestimo'
                return jsonify({
                    'titulo': livro_salvado.titulo,
                    'autor': livro_salvado.autor,
                    'resumo': livro_salvado.resumo,
                    'status': status_emprestimo,
                    'ISBN': livro_salvado.ISBN
                })
            except IntegrityError as e:
                return jsonify({'error': str(e)}), 500

@app.route('/cadastrar_usuario', methods=['POST'])
def cadastrar_usuario():
    if request.method == 'POST':
        dados = request.get_json()
        nome = dados['titulo']
        cpf = dados['autor']
        endereco = dados['resumo']

        cpf_ja_cadastrado = select(Usuarios)
        cpf_ja_cadastrado = db_session.execute(cpf_ja_cadastrado.filter_by(CPF=cpf)).first()
        if cpf_ja_cadastrado:
            return jsonify({"error": 'CPF ja cadastrado'})

        endereco_ja_cadastrado = select(Usuarios)
        endereco_ja_cadastrado = db_session.execute(endereco_ja_cadastrado.filter_by(endereco=endereco)).first()
        if endereco_ja_cadastrado:
            return jsonify({"error": 'endereco ja cadastrado'})
        if not nome:
            return jsonify({"error": 'campo nome vazio'}, 400)
        if not cpf:
            return jsonify({"error": 'campo cpf vazio'}, 400)
        if not endereco:
            return jsonify({"error": 'campo endereco vazio'}, 400)
        else:
            try:
                usuario_salvado = Usuarios(nome=nome,
                                           CPF=cpf,
                                           endereco=endereco)
                usuario_salvado.save()
                return jsonify({
                    'titulo': usuario_salvado.nome,
                    'autor': usuario_salvado.CPF,
                    'resumo': usuario_salvado.endereco})
            except IntegrityError as e:
                return jsonify({'error': str(e)})

@app.route('/cadastrar_emprestimo', methods=['POST'])
def cadastrar_emprestimo():
    try:
        data_emprestimo = date.today()
        data_de_devolucao = data_emprestimo + relativedelta(weeks=5)

        dados = request.get_json()
        isbn = dados['isbn']
        id_usuario = dados['id_usuario']



        id_usuario = int(id_usuario)
        if not isbn or not id_usuario:
            return jsonify({'error': 'Campos ISBN e id_usuario são obrigatórios'}), 400
        usuario = select(Emprestimos)
        usuario_com_emprestimos = db_session.execute(usuario.filter_by(id_usuario=id_usuario)).scalar()

        isbn = int(isbn)


        livro = db_session.execute(select(Livros).filter_by(ISBN=isbn)).scalar()
        if not livro:
            return jsonify({'error': 'Livro não encontrado'}), 404

        if not livro.status:
            return jsonify({'error': 'Livro não está disponível para empréstimo'}), 400

        usuario = db_session.get(Usuarios, id_usuario)
        if not usuario:
            return jsonify({'error': 'Usuário não encontrado'}), 404


        emprestimo = Emprestimos(
            data_emprestimo=data_emprestimo,
            data_de_devolucao=data_de_devolucao,
            ISBN_livro=isbn,
            id_usuario=id_usuario
        )
        emprestimo.save()


        livro.status = False
        livro.save()

        return jsonify({
            'data_emprestimo': emprestimo.data_emprestimo,
            'data_de_devolucao': emprestimo.data_de_devolucao,
            'ISBN_livro': emprestimo.ISBN_livro,
            'id_usuario': emprestimo.id_usuario
        })
    except IntegrityError as e:
        db_session.rollback()
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': 'Erro ao cadastrar empréstimo', 'detalhes': str(e)}), 500


@app.route('/atualizar_usuario/<id>', methods=['PUT'])
def editar_usuario(id):

    try:
        id = int(id)
        # usuario_editado = db_session.execute(select(Usuarios).where(Usuarios.id_usuario == id)).scalar()
        usuario = select(Usuarios)
        # fazer a busca do banco, filtrando o id:
        usuario_editado = db_session.execute(usuario.filter_by(id=id)).scalar()

        if not usuario_editado:
            return jsonify({
                "teste": "Não foi possível encontrar o usuário!"
            })

        if request.method == 'PUT':
            # atualizar e verificar se tem algo nos campos
            if (not request.form.get('nome') and not request.form.get('CPF')
                    and not request.form.get('endereco')):
                return jsonify({
                    # se tiver nulo retorna :
                    "erro": "Os campos não devem ficar em branco!"
                })

            else:
                # edita o usuario
                CPF = request.form.get('CPF').strip()
                if usuario_editado.CPF != CPF:
                    # vai verificar se nenhum usuario tem esse cpf
                    # scalar retorna o usuario em forma de objeto
                    CPF_existe = db_session.execute(select(Usuarios).where(Usuarios.CPF == CPF)).scalar()

                    if CPF_existe:
                        return jsonify({
                            "erro": "Este CPF já existe!"
                        })
                # o strip remover espaços em branco no início e no fim de uma string
                dados = request.get_json()
                usuario_editado.nome = dados['nome']
                usuario_editado.CPF = dados['CPF']
                usuario_editado.endereco = dados['endereco']
                usuario_editado.save()

                return jsonify({
                    "nome": usuario_editado.nome,
                    "CPF": usuario_editado.CPF,
                    "endereco": usuario_editado.endereco,
                })

    except sqlalchemy.exc.IntegrityError:
        db_session.rollback()
        return jsonify({
            "erro": "Esse CPF já foi cadastrado!"
        })


@app.route('/atualizar_livro/<id>', methods=['PUT'])
def atualizar_livro(id):

    livro = select(Livros)
    livro = db_session.execute(livro.filter_by(id_livro=id)).scalar()
    if not livro:
        return jsonify({'error': 'Livro não encontrado'}), 404
    dados = request.get_json()

    titulo = dados['titulo']
    livro_existente = select(Livros)
    titulo_existente = db_session.execute(livro_existente.filter_by(titulo=titulo)).scalar()
    if titulo_existente:
        return jsonify({'titulo de livro já cadastrado': titulo})
    autor = dados['autor']
    resumo = dados['resumo']
    isbn = dados['isbn']

    if titulo:
        livro.titulo = titulo
    if autor:
        livro.autor = autor
    if resumo:
        livro.resumo = resumo
    if isbn:
        livro.ISBN = isbn

    livro.save()
    return jsonify({'mensagem': 'Livro atualizado com sucesso', 'dados': livro.get_livro()})

@app.route('/emprestimos_por_usuario/<id_usuario>', methods=['GET'])
def emprestimos_por_usuario(id_usuario):
    try:
        emprestimos = db_session.execute(select(Emprestimos).filter_by(id_usuario=id_usuario)).scalars()
        if not emprestimos:
            return jsonify({'mensagem': 'Nenhum empréstimo encontrado para este usuário'})


        lista_emprestimos = []
        for emprestimo in emprestimos:
            lista_emprestimos.append(emprestimo.get_emprestimo())
        return jsonify({'emprestimos': lista_emprestimos})
    except IntegrityError as e:
        db_session.rollback()
        return jsonify({'error': str(e)}), 500
@app.route('/editar_emprestimo/<ISBN>', methods=['PUT'])
def editar_emprestimo(ISBN):
    try:
        ISBN = int(ISBN)
        livro_encontrado = db_session.execute(select(Emprestimos).filter_by(ISBN_livro=ISBN)).scalar()
        if not livro_encontrado:
            return jsonify({'error': 'livro não encontrado'})
        dados = request.get_json()
        id_usuario = dados['id_usuario']
        id_usuario = int(id_usuario)
        usuario_encontrado = db_session.execute(select(Usuarios).filter_by(id=id_usuario)).first()
        if not usuario_encontrado:
            return jsonify({"error":"usuario nao encontrado"})
        livro_encontrado.id_usuario = id_usuario
        livro_encontrado.save()
        return jsonify({"sucesso": "Sucesso"})
    except IntegrityError as e:
        return jsonify({'error': str(e)}), 500
@app.route('/devolver_livro', methods=['PUT'])
def devolver():
    try:
        dados = request.get_json()
        id_usuario = dados['id_usuario']
        isbn_livro = dados['isbn_livro']
        user_existente = db_session.execute(select(Usuarios).filter_by(id=id_usuario)).scalar()
        livro_existente = db_session.execute(select(Livros).filter_by(ISBN=isbn_livro)).scalar()
        if not user_existente:
            return jsonify({'error': 'usuario não encontrado'})
        if not livro_existente:
            return jsonify({'error': 'livro não existente'})
        if livro_existente.status:
            return jsonify({'error':'livro já está devolvido'}),
        livro_existente.status = True
        livro_existente.save()
        return jsonify({'mensagem': 'Livro devolvido com sucesso',
                        'dados': livro_existente.get_livro()})
    except IntegrityError as e:
        return jsonify({'error': str(e)}), 500


# Banco
# Emprestimos, id usuario
# Usuario: cpf, endereço
# livro: /
# //////////////////////////
# proteção: editar emprestimos,
# emprestimos por usuario
# atulizar livro,
# atualizar usuario,
# cadastro de emprestimos,
# cadastro usuario,
# cadastro de livro
# consultar usuarios
# ////////////////
# sem proteção
# consultar livros

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)