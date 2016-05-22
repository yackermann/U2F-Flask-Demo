from app import app
from flask import jsonify, request

users = {}

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User login/authentication/session management."""

    if request.method == 'POST':
        if 'username' not in request.form or 'password' not in request.form:
            return jsonify({'status': 'failed', 'error': 'Username or/and password missing'})

        if request.form['username'] in users:
            return jsonify({'status': 'failed', 'error': 'User already exists'})
        else:
            users[request.form['username']] = {
                'username': request.form['username'],
                'password': request.form['password']
            }
            return jsonify({'status': 'success'})

    return jsonify({})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if 'username' not in request.form or 'password' not in request.form:
            return jsonify({'status': 'failed', 'error': 'Username or/and password missing'})

        if request.form['username'] in users:
            if users[request.form['username']]['password'] == request.form['username']:
                session['logged_in'] = True
                return jsonify({'status': 'success'})
            else:
                return jsonify({'status': 'failed', 'error': 'Username or/and password is incorrect'})
            
        return jsonify({'status': 'failed', 'error': 'Username or/and password is incorrect'})

    return jsonify({})
    
@app.route('/logout')
def logout():
    """User logout/authentication/session management."""
    session.pop('logged_in', None)
    return jsonify({'status': 'success'})

@app.route('/testjson')
def test():
    return jsonify({'hello': 'world'})