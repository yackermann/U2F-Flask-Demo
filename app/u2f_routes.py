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
                new_device, cert = complete_register(session.pop('_u2f_enroll_'), response,
                                              [app.config['APPID']])
            except Exception as e:
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
                counter, touch = verify_authenticate(devices, challenge, signature, [app.config['APPID']])
            except Exception as e:
                print(e)
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