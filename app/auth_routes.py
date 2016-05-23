from app import app
from flask import jsonify, request, session

users = {}

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User login/authentication/session management."""

    if request.method == 'POST':
        req = request.json
        if 'username' not in req or 'password' not in req:
            return jsonify({'status': 'failed', 'error': 'Username or/and password missing'})

        if req['username'] in users:
            return jsonify({'status': 'failed', 'error': 'User already exists'})
        else:
            users[req['username']] = {
                'username': req['username'],
                'password': req['password']
            }
            return jsonify({'status': 'success'})

    return jsonify({})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        req = request.json
        if 'username' not in req or 'password' not in req:
            return jsonify({'status': 'failed', 'error': 'Username or/and password missing'})

        if users.get(req['username']):
            if users[req['username']]['password'] == req['username']:
                print(session)

                session['logged_in'] = True
                session['username']  = req['username']

                print(session)
                return jsonify({'status': 'success'})
            else:
                return jsonify({'status': 'failed', 'error': 'Username or/and password is incorrect'})
            
        return jsonify({'status': 'failed', 'error': 'Username or/and password is incorrect'})

    return jsonify({})
    
@app.route('/islogged')
def isLogged():
    print(session)

    return jsonify({'logged_in': session.get('logged_in', False)})


@app.route('/enroll')
def u2fenroll():
    print(users, session)

    if not session.get('logged_in', False):
        return jsonify({'status': 'failed', 'error': 'Access denied. You must login'})


    print(users)
    user = users[session['username']]

    devices = [DeviceRegistration.wrap(device)
               for device in user.get('_u2f_devices_', [])]
    enroll = start_register(app.config['APPID'], devices)
    user['_u2f_enroll_'] = enroll.json
    return enroll.json