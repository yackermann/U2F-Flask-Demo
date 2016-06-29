from app import app, db, models
from flask import jsonify, request, session

# U2F Libs
from u2flib_server.jsapi import DeviceRegistration
from u2flib_server.u2f import (start_register, complete_register, start_authenticate, verify_authenticate)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User register/authentication/session management."""

    if request.method == 'POST':
        req = request.json

        if not req.get('username')  or not req.get('password'):
            return jsonify({'status': 'failed', 'error': 'Username or/and password missing'})

        req['username'] = req['username'].lower()
        user = models.Auth.query.filter_by(username=req['username']).first()

        if not user:
            new_user = models.Auth(req['username'], req['password'])
            new_user.commit()
            return jsonify({'status': 'success'})

        else:
            # If user has no U2F devices
            if user.get_u2f_devices() == []:
                return jsonify({'status': 'failed', 'u2f_enroll_required': True})

            return jsonify({'status': 'failed', 'error': 'User already exists'})


    return jsonify({})

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login/authentication/session management."""
    if request.method == 'POST':
        req = request.json
        if not req.get('username')  or not req.get('password'):
            return jsonify({'status': 'failed', 'error': 'Username or/and password missing'})

        req['username'] = req['username'].lower()
        user = models.Auth.query.filter_by(username=req['username']).first()

        if user:
            if user.check_password(req['password']):
                session['authenticated'] = True
                session['username']      = user.username

                if user.get_u2f_devices() == []:
                    session['logged_in'] = True
                    return jsonify({'status': 'success'})
                else:
                    return jsonify({'status': 'failed', 'u2f_sign_required': True})
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
    session.pop('logged_in'     , None)
    session.pop('username'      , None)
    session.pop('authenticated' , None)
    return jsonify({'status': 'success'})
