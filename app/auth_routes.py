from app import app
from flask import jsonify, request, session

users = {}

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User register/authentication/session management."""

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
    """User login/authentication/session management."""
    if request.method == 'POST':
        req = request.json
        if not req.get('username')  or not req.get('password'):
            return jsonify({'status': 'failed', 'error': 'Username or/and password missing'})

        if users.get(req['username']):
            if users[req['username']]['password'] == req['username']:
                session['logged_in'] = True
                session['username']  = req['username']
                return jsonify({'status': 'success'})
            else:
                return jsonify({'status': 'failed', 'error': 'Username or/and password is incorrect'})
            
        return jsonify({'status': 'failed', 'error': 'Username or/and password is incorrect'})

    return jsonify({})
    
@app.route('/islogged')
def isLogged():
    """User islogged/authentication/session management."""
    return jsonify({'logged_in': session.get('logged_in', False)})



@app.route('/logout')
def logout():
    """User logout/authentication/session management."""
    session.pop('logged_in', None)
    session.pop('username', None)
    return jsonify({'status': 'success'})


from u2flib_server.jsapi import DeviceRegistration
from u2flib_server.u2f import (start_register, complete_register, start_authenticate, verify_authenticate)
from cryptography.hazmat.primitives.serialization import Encoding

@app.route('/enroll', methods=['GET', 'POST'])
def u2fenroll():
    """User enroll/u2f/authentication/session management."""

    if not session.get('logged_in', False):
        return jsonify({'status': 'failed', 'error': 'Access denied. You must login'})

    user = users[session['username']]

    # Get user challenge
    if request.method == 'GET':

        devices = [DeviceRegistration.wrap(device) for device in user.get('_u2f_devices_', [])]
        enroll  = start_register(app.config['APPID'], devices)
        user['_u2f_enroll_'] = enroll.json
        return enroll.json

    # Verify User
    elif request.method == 'POST':
        data = request.json

        binding, cert = complete_register(user.pop('_u2f_enroll_'), data,
                                          [app.config['APPID']])

        devices = [DeviceRegistration.wrap(device) for device in user.get('_u2f_devices_', [])]
        devices.append(binding)
        user['_u2f_devices_'] = [d.json for d in devices]


        return jsonify({'status': 'success', 'users': users})