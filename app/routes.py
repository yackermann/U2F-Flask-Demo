from app import app
from os import urandom

@app.route('/YOLO')
@app.route('/yolo')
def hello():
    return 'Hello, World!'

@app.route('/random')
def rand():
    SIZE = 32

    return urandom(SIZE)