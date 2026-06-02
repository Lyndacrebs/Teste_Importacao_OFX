from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html') #o que essa linhas faz? pra que serve o render_template?

@app.route('/upload', methods=['POST']) #pra que serve o route?
def upload():
    file = request.files['file'] #pra que serve o request?

    file.save(f'uploads/{file.filename}') #salva o upload dentro de um diretório no projeto