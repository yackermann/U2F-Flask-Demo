from app import app

@app.route('/YOLO')
@app.route('/yolo')
def hello():
    return 'Hello, World!'