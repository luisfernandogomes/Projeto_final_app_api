import requests
from api import *
def get_usuarios():
    url = "http://10.135.232.36:5000/consultar_usuarios"
    response = requests.get(url)
    if response.status_code == 200:
        dados = response.json()
        # print(dados['usuarios_cadastrados'])
        # for u in dados['usuarios_cadastrados']:
        #     print(u['CPF'])
        # return jsonify({'sucesso': u['CPF']})
        return dados['usuarios_cadastrados']

def get_livros():
    url = "http://10.135.232.36:5000/consultar_livros"
    response = requests.get(url)
    if response.status_code == 200:
        dados = response.json()
        # print(dados)
        for l in dados['livrosnocatalogodabiblioteca']:
            print(f"livros no catalogo da biblioteca: {l['titulo']} ISBN: {l['ISBN']}")
            # if l['status']:
            #     print('está emprestado')
    else:
        print("error, api não iniciada")
# get_livros()
def post_livro(titulo, autor, resumo, isbn):
    url = "http://10.135.232.36:5000/cadastrar_livro"
    livro = {"titulo": titulo,
             "autor": autor,
             "resumo": resumo,
             "isbn": isbn}
    response = requests.post(url, json=livro)
    if response.status_code == 200:
        print("Livro cadastrado com sucesso!")
        dados_post = response.json()
        print(dados_post)
    else:
        print("Erro ao cadastrar livro!")
# post_livro('titulo','autor','resumo',47795753892)
def devolver_livro(isbn, id_usuario):
    url = "http://10.135.232.36:5000/devolver_livro"
    devolucao = {"isbn_livro": isbn,
                 "id_usuario": id_usuario
                 }
    response = requests.post(url, json=devolucao)
    if response.status_code == 200:
        print("Livro devolvido com sucesso!")
        dados_post = response.json()
        print(dados_post)
    else:
        print("Erro ao devolver livro!")
# devolver_livro(95478,1)
def cadastrar_emprestimos(id_usuario,isbn):
    url = "http://10.135.232.36:5000/cadastrar_emprestimo"
    emprestimo = {"id_usuario": id_usuario,
                  "isbn": isbn}
    response = requests.post(url, json=emprestimo)
    if response.status_code == 200:
        print("Emprestimo cadastrado com sucesso!")
        dados_post = response.json()
        print(dados_post)
    else:
        print('algo deu errado fudeu')
# cadastrar_emprestimos(1,95478)
def get_emprestimos_por_usuario(id_usuario):
    url = f"http://10.135.232.36:5000/emprestimos_por_usuario/{id_usuario}"
    response = requests.get(url)
    if response.status_code == 200:
        dados = response.json()

        for emprestimo in dados['emprestimos']:
            print(emprestimo)
    else:
        print('fudeu')
# get_emprestimos_por_usuario(1)

def editar_emprestimo(ISBN,id_usuario):
    url = f"http://10.135.232.36:5000/editar_emprestimo/{ISBN}"
    emprestimo = {"id_usuario":id_usuario}
    response = requests.put(url, json=emprestimo)
    if response.status_code == 200:
        print('sucesso')
        dados_post = response.json()
        print(dados_post)
    else:
        print(response.status_code)
# editar_emprestimo(95478,1)
def put_livro(id,titulo, autor, resumo, isbn):
    url = f"http://10.135.232.36:5000/atualizar_livro/{id}"
    livro = {"titulo": titulo,
             "autor": autor,
             "resumo": resumo,
             "isbn": isbn}
    response = requests.put(url, json=livro)
    if response.status_code == 200:
        print("Livro editado com sucesso!")
        dados_post = response.json()
        print(dados_post["dados"])
    else:
        print(response.status_code)
# put_livro(1,'tituloeditado','autoratualizado','resumoatualizado',999)
# def put_usuario()

