from flask import Flask, render_template, request, jsonify
import json
from datetime import datetime
import os

app = Flask(__name__)

POSTS_FILE = 'posts.json'

def carregar_posts():
    if not os.path.exists(POSTS_FILE):
        with open(POSTS_FILE, 'w') as f:
            json.dump([], f)
    with open(POSTS_FILE, 'r') as f:
        return json.load(f)

def salvar_posts(posts):
    with open(POSTS_FILE, 'w') as f:
        json.dump(posts, f, indent=4)

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
        novo_post = {
            'data': datetime.now().strftime('%d/%m/%Y %H:%M'),
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
    app.run(debug=True)
