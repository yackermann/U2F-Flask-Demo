from app import app, db, models
from flask import jsonify, request, session, abort
import logging


# U2F Libs
from u2flib_server.jsapi import DeviceRegistration
from u2flib_server.u2f import (start_register, complete_register, start_authenticate, verify_authenticate)

LOG_PREFIX = 'U2F:'

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
            logging.info('%s Performing U2F enrollment for %s', LOG_PREFIX, user.username)
            logging.info('%s Getting %s\'s enrollment challenge', LOG_PREFIX, user.username)

            devices = [DeviceRegistration.wrap(device) for device in user.get_u2f_devices()]
            enroll  = start_register(app.config['U2F_APPID'], devices)

            session['_u2f_enroll_'] = enroll.json
            return enroll.json

        # Verify User
        elif request.method == 'POST':
            response = request.json

            logging.info('%s Confirming %s\'s enrollment challenge', LOG_PREFIX, user.username)

            try:
                new_device, cert = complete_register(session.pop('_u2f_enroll_'), response,
                                              [app.config['U2F_APPID']])
                logging.info('%s Successfully enrolled %s\'s U2F device', LOG_PREFIX, user.username)
            except Exception as e:
                logging.warning('%s User %s failed to provide valid signature! %s', LOG_PREFIX, user.username, str(e))
                return jsonify({'status':'failed', 'error': 'Invalid Challenge!'})
            finally:
                pass
            
            # Setting new device counter to 0
            new_device['counter'] = 0

            devices = user.get_u2f_devices()
            devices.append(new_device)
            
            user.set_u2f_devices(devices)
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
            logging.info('%s Performing U2F authentication for %s', LOG_PREFIX, user.username)
            logging.info('%s Getting signature challenge for user: %s', LOG_PREFIX, user.username)

            devices = [DeviceRegistration.wrap(device) for device in user.get_u2f_devices()]
            challenge = start_authenticate(devices)
            session['_u2f_challenge_'] = challenge.json
            return challenge.json

        # Verify User
        elif request.method == 'POST':  
            signature = request.json

            devices   = [DeviceRegistration.wrap(device) for device in user.get_u2f_devices()]
            challenge = session.pop('_u2f_challenge_')

            try:
                counter, touch = verify_authenticate(devices, challenge, signature, [app.config['U2F_APPID']])
                logging.info('%s User %s had successfully signed challenge!', LOG_PREFIX, user.username)
            except Exception as e:
                logging.warning('%s User %s failed to provide valid signature! %s', LOG_PREFIX, user.username, str(e))

                return jsonify({'status':'failed', 'error': 'Invalid Signature!'})
            finally:
                pass

            if user.verify_u2f_counter(signature, counter):
                session['logged_in'] = True
                return jsonify({
                    'status'  : 'success',
                    'counter' : counter
                })
            else:
                return jsonify({'status':'failed', 'error': 'Device clone detected!'})


            

    return jsonify({'status': 'failed', 'error': 'Access denied. You must login'})

@app.route('/facets.json')
def facets():
    if app.config['U2F_ENABLE_FACETS'] and not app.config['U2F_CUSTOM_FACETS_APPID']:
        logging.debug('%s Getting facets', LOG_PREFIX)
        return jsonify({
            "trustedFacets" : [{
                "version": { "major": 1, "minor" : 0 },
                "ids": app.config['U2F_FACETS_LIST']
            }]
        })
    else:
        logging.debug('%s Facets disabled', LOG_PREFIX)
        abort(404)