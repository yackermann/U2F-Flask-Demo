from app import app, db, models, u2f
from flask import jsonify, request, session
import logging

LOG_PREFIX = 'AUTH:'

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
            logging.debug('%s Registering new user: %s', LOG_PREFIX, req.get('username'))
            
            new_user = models.Auth(req['username'], req['password'])
            new_user.commit()
            return jsonify({'status': 'ok'})

        else:
            logging.debug('%s User %s exists', LOG_PREFIX, req.get('username'))

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
            logging.debug('%s Authenticating user %s', LOG_PREFIX, req.get('username'))
            if user.check_password(req['password']):
                session['authenticated'] = True
                session['username']      = user.username

                if not user.has_u2f_devices():
                    session['logged_in'] = True
                    session['u2f_enroll_authorized'] = True
                    session['u2f_allow_device_management']  = True

                    return jsonify({'status': 'ok'})
                else:
                    session['u2f_sign_required'] = True
                    return jsonify({'status': 'failed', 'u2f_sign_required': True})
            else:
                return jsonify({'status': 'failed', 'error': 'Username or/and password is incorrect'})
            
        logging.debug('%s User %s, does not exist ', LOG_PREFIX, req.get('username'))
        return jsonify({'status': 'failed', 'error': 'Username or/and password is incorrect'})

    return jsonify({})
    
@app.route('/islogged')
def isLogged():
    """User islogged/authentication/session management."""

    logging.debug('%s Checking if user is logged in', LOG_PREFIX) 
    return jsonify({'status' : 'ok', 'logged_in': session.get('logged_in', False)})


@app.route('/logout')
def logout():
    """User logout/authentication/session management."""
    logging.debug('%s Logging out user %s', LOG_PREFIX, session.get('username')) 
    session.pop('logged_in'     , None)
    session.pop('username'      , None)
    session.pop('authenticated' , None)
    u2f.reset_session()

    return jsonify({'status': 'ok'})
