from flask import Flask, render_template, request, jsonify
import json
from datetime import datetime
import os
import locale

app = Flask(__name__)

POSTS_FILE = 'posts.json'

try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except:
    DIAS_PT = ['segunda-feira', 'terca-feira', 'quarta-feira', 'quinta-feira', 'sexta-feira', 'sabado', 'domingo']
    def dia_semana_manual(data):
        return DIAS_PT[data.weekday()]
else:
    DIAS_PT = None

def remover_acentos(texto):
    mapa = str.maketrans(
        "áàãâäéèêëíìîïóòõôöúùûüçÁÀÃÂÄÉÈÊËÍÌÎÏÓÒÕÔÖÚÙÛÜÇ",
        "aaaaaeeeeiiiiooooouuuucAAAAAEEEEIIIIOOOOOUUUUC"
    )
    return texto.translate(mapa)

def carregar_posts():
    if not os.path.exists(POSTS_FILE):
        with open(POSTS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=4)
    with open(POSTS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def salvar_posts(posts):
    with open(POSTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=4)

def atualizar_posts_antigos():
    posts = carregar_posts()
    alterado = False
    for post in posts:
        data_str = post['data']
        try:
            # tenta detectar formato antigo (sem vírgula ou com acento)
            if ',' not in data_str:
                data_original = datetime.strptime(data_str, '%d/%m/%Y %H:%M')
            else:
                # tenta ignorar o dia e pegar só a data numérica
                parte_data = data_str.split(',')[-1].strip()
                data_original = datetime.strptime(parte_data, '%d/%m/%Y %H:%M')
            # cria novo formato
            if DIAS_PT:
                dia_semana = dia_semana_manual(data_original)
            else:
                dia_semana = data_original.strftime('%A').lower()
            dia_semana = remover_acentos(dia_semana).capitalize()
            nova_data = f"{dia_semana}, {data_original.strftime('%d/%m/%Y %H:%M')}"
            # só atualiza se mudou
            if post['data'] != nova_data:
                post['data'] = nova_data
                alterado = True
        except:
            pass
    if alterado:
        salvar_posts(posts)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/posts', methods=['GET'])
def listar_posts():
    posts = carregar_posts()
    return jsonify(posts[::-1])

@app.route('/posts', methods=['POST'])
def adicionar_post():
    texto = request.form.get('texto')
    if texto:
        posts = carregar_posts()
        agora = datetime.now()
        if DIAS_PT:
            dia_semana = dia_semana_manual(agora)
        else:
            dia_semana = agora.strftime('%A').lower()
        dia_semana = remover_acentos(dia_semana).capitalize()
        novo_post = {
            'data': f"{dia_semana}, {agora.strftime('%d/%m/%Y %H:%M')}",
            'texto': texto
        }
        posts.append(novo_post)
        salvar_posts(posts)
        return jsonify({'status': 'ok'})
    return jsonify({'status': 'erro'})

@app.route('/posts/<int:index>', methods=['DELETE'])
def deletar_post(index):
    posts = carregar_posts()
    if 0 <= index < len(posts):
        posts.pop(index)
        salvar_posts(posts)
        return jsonify({'status': 'ok'})
    return jsonify({'status': 'erro'})

if __name__ == '__main__':
    atualizar_posts_antigos()
    app.run(debug=True)
