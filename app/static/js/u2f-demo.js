    
var $get = function(url, callback){
    fetch(url, {credentials : 'same-origin'}).then(function(response) {
        return response.json()
    }).then(function(json) {
        callback(json)
    }).catch(function(ex) {
        callback({ 'error': ex })
    })
}

var $post = function (url, body, callback) {
    fetch(url, {
        method  : 'post',
        credentials : 'same-origin',
        headers : {
            'Accept'       : 'application/json',
            'Content-Type' : 'application/json'
        },
        body    : JSON.stringify(body)
    }).then(function (response) {
        return response.json()
    }).then(function (json) {
        callback(json)
    }).catch(function (ex) {
        callback({ 'error': ex })
    })
}

var $id = function(id){
    return document.getElementById(id);
}


var Logger = function(id) {
    this.textarea = id;
}

Logger.prototype.log = function(text) {
    $logarea = $id(this.textarea);
    $logarea.value = '> ' + text + '\n' + $logarea.value;
    console.log(text);
}


var U2F_ERROR_CODES = {
    1 : 'OTHER_ERROR',
    2 : 'BAD_REQUEST',
    3 : 'CONFIGURATION_UNSUPPORTED',
    4 : 'DEVICE_INELIGIBLE',
    5 : 'TIMEOUT'
}

var locked = false;

var u2f_enroll = function(e) {
    if (e.preventDefault) e.preventDefault();


    var user = {
        'username': enroll_form.elements['username'].value,
        'password': enroll_form.elements['password'].value
    }


    var logger = new Logger('register_log');

    if(user['username'] && user['password'] && !locked){
        clear_textareas();

        $post('/register', user, function(response){
            if(response.status === 'success' || response.u2f_enroll_required){

                logger.log('Registering...');
                locked = true;
                $post('/login', user, function(response){
                    if(response.status !== 'failed'){

                        logger.log('Requesting challenge...');

                        $get('/enroll', function(response){
                            logger.log('Registerinsssg...', response);
                            var register = response.registerRequests;
                            var sign     = response.authenticateRequests;

                            // Getting AppID
                            console.log(register, sign)
                            var appid = register[0].appId;
                           
                            // Formating Challenge
                            // var challenge = [{version: req.version, challenge: req.challenge}];

                            logger.log(req);
                            logger.log('Waiting for user action...');

                            u2f.register(appid, register, sign, function(deviceResponse) {
                                locked = false;

                                if(deviceResponse.errorCode){
                                    logger.log('U2F ERROR: ' + U2F_ERROR_CODES[deviceResponse.errorCode]);
                                }else{
                                    logger.log(deviceResponse);
                                    logger.log('Verifying with server...');
                                    
                                    $post('/enroll', deviceResponse,  function(serverResonse){
                                        if(serverResonse.status === 'success'){
                                            logger.log('Success!');
                                        }else{
                                            logger.log('Fail! ' + serverResonse.error);
                                        }
                                    })
                                }

                            }, 10);
                        });
                    }else{
                        logger.log('Login Failed');
                    }
                });
            }else{
                logger.log('Failed');
                logger.log(response.error);
            }
        })
    }

    return false;
}

var u2f_sign = function(e) {
    if (e.preventDefault) e.preventDefault();


    var user = {
        'username': sign_form.elements['username'].value,
        'password': sign_form.elements['password'].value
    }


    var logger = new Logger('login_log');

    if(user['username'] && user['password'] && !locked){
        clear_textareas();
        
        logger.log('Loggin in...')

        $post('/login', user,function(response){
            locked = true;
            if(response.status === 'failed'){
                if(response['u2f_sign_required']){
                    logger.log('U2F Required')

                    $get('/sign', function(serverreq){
                        var req = serverreq.authenticateRequests[0];

                        // Getting AppID
                        var appid = req.appId;
                       
                        // Getting Challenge
                        var challenge = req.challenge;

                        // Formating keyhandle for U2F key
                        var registeredKeys = [{version: req.version, keyHandle: req.keyHandle}];

                        logger.log('Getting challenge...');
                        logger.log(req);
                        logger.log('Waiting for user action...');

                       
                        u2f.sign(appid, challenge, registeredKeys, function(deviceResponse) {
                            locked = false;
                            if(deviceResponse.errorCode){
                                logger.log('U2F ERROR: ' + U2F_ERROR_CODES[deviceResponse.errorCode]);
                            }else{
                                logger.log(deviceResponse);
                                logger.log('Verifying with server...');
                                
                                $post('/sign', deviceResponse, function(serverResonse){
                                    if(serverResonse.status === 'success'){
                                        logger.log('Success! Counter ' + serverResonse.counter);
                                    }else{
                                        logger.log('Fail! ' + serverResonse.error);
                                    }
                                })
                            }
                          
                            return
                        }, 10);
                    });
                }else{
                    logger.log('Fail');
                    logger.log(response.error);
                }
            }else{
                logger.log('Success');
                logger.log('No U2F required');
            }
        });
    }

    return false;
}

var clear_textareas = function() {
    var textareas = document.getElementsByTagName('textarea');
    
    for(var i = 0; i < textareas.length; i++)
        textareas[i].value = '';
}

var clear_inputs = function() {
    var inputs    = document.getElementsByTagName('input');

    for (var i = 0; i < inputs.length; i++){
        if(inputs[i].type !== 'submit')
            inputs[i].value = '';
    }
}




/* ----- EVENT HANDLERS ----- */

/* --- U2F --- */
    var enroll_form = $id('u2f_register_form');
    enroll_form.addEventListener("submit", u2f_enroll);

    var sign_form = $id('u2f_login_form');
    sign_form.addEventListener("submit", u2f_sign);
/* --- U2F END --- */

    var login_container = $id('login');
    var register_container = $id('register');

    var regbutton = $id('switch_to_register');
    var loginbutton = $id('switch_to_login');

    regbutton.addEventListener('click', function(){
        login_container.className    = 'main hidden';
        register_container.className = 'main present';
        clear_textareas();
        clear_inputs();
    }, false)

    loginbutton.addEventListener('click', function(){
        register_container.className = 'main hidden';
        login_container.className    = 'main present';
        clear_textareas();
        clear_inputs();
    }, false)

