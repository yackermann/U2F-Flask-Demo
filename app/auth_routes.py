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

        user = models.Auth.query.filter_by(username=req['username']).first()

        if not user:
            new_user = models.Auth(req['username'], req['password'])
            new_user.commit()
            return jsonify({'status': 'success'})

        else:
            return jsonify({'status': 'failed', 'error': 'User already exists'})


    return jsonify({})

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login/authentication/session management."""
    if request.method == 'POST':
        req = request.json
        if not req.get('username')  or not req.get('password'):
            return jsonify({'status': 'failed', 'error': 'Username or/and password missing'})

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


# FIDO U2F

@app.route('/enroll', methods=['GET', 'POST'])
def u2fenroll():
    """User enroll/u2f/authentication/session management."""

    if not session.get('logged_in', False):
        return jsonify({'status': 'failed', 'error': 'Access denied. You must login'})

    user = models.Auth.query.filter_by(username=session['username']).first()
    
    if user:
        # Get user challenge
        if request.method == 'GET':

            devices = [DeviceRegistration.wrap(device) for device in user.get_u2f_devices()]
            enroll  = start_register(app.config['APPID'], devices)

            session['_u2f_enroll_'] = enroll.json
            return enroll.json

        # Verify User
        elif request.method == 'POST':
            response = request.json

            try:
                binding, cert = complete_register(session.pop('_u2f_enroll_'), response,
                                              [app.config['APPID']])
            except Exception as e:
                return jsonify({'status':'failed', 'error': 'Invalid Challenge!'})
            
            devices = [DeviceRegistration.wrap(device) for device in user.get_u2f_devices()]
            devices.append(binding)
            user.set_u2f_devices([d.json for d in devices])
            user.commit()

            return jsonify({'status': 'success'})

    return jsonify({'status': 'failed', 'error': 'Access denied. You must login'})

@app.route('/sign', methods=['GET', 'POST'])
def u2fsign():
    """User sign/u2f/authentication/session management."""

    if not session.get('authenticated', False):
        return jsonify({'status': 'failed', 'error': 'Access denied. You must login'})

    user = models.Auth.query.filter_by(username=session['username']).first()

    if user:

        # Get user challenge
        if request.method == 'GET':
            devices = [DeviceRegistration.wrap(device) for device in user.get_u2f_devices()]
            challenge = start_authenticate(devices)
            session['_u2f_challenge_'] = challenge.json
            return challenge.json

        # Verify User
        elif request.method == 'POST':
            signature = request.json

            devices = [DeviceRegistration.wrap(device) for device in user.get_u2f_devices()]

            challenge = session.pop('_u2f_challenge_')
            try:
                counter, touch = verify_authenticate(devices, challenge, signature, [app.config['APPID']])
            except Exception as e:
                return jsonify({'status':'failed', 'error': 'Invalid Signature!'})

            session['logged_in'] = True
            return jsonify({
                # FIDO U2F protocol specifies x01 is true for user touch. 
                # Need to convert to bool before include to JSON
                'touch': bool(touch), 
                'counter': counter,
                'status': 'success'
            })

    return jsonify({'status': 'failed', 'error': 'Access denied. You must login'})

# TODO -> Implement facets
@app.route('/facets.json')
def facets():
    return jsonify({
      "trustedFacets" : [{
        "version": { "major": 1, "minor" : 0 },
        "ids": [
            "https://localhost:5000"
        ]
      }]
    })