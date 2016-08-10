    
var $get = function(url, callback){
    fetch(url, {credentials : 'same-origin'}).then(function(response) {
        return response.json()
    }).then(function(json) {
        callback(json)
    }).catch(function(error) {
        callback({ 'error': error })
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
    }).catch(function (error) {
        callback({ 'error': error })
    })
}

var $delete = function (url, body, callback) {
    fetch(url, {
        method  : 'delete',
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
    }).catch(function (error) {
        callback({ 'error': error })
    })
}



var Logger = function(id) {
    this.textarea = id;
}

Logger.prototype.log = function(text) {
    $logarea = $(this.textarea);
    $logarea.val('> ' + text + '\n' + $logarea.val());
    console.log(text);
}


var U2F_ERROR_CODES = {
    1 : 'OTHER_ERROR',
    2 : 'BAD_REQUEST',
    3 : 'CONFIGURATION_UNSUPPORTED',
    4 : 'DEVICE_INELIGIBLE',
    5 : 'TIMEOUT'
}


var show_devices = function(data){
    if(data.status == 'ok'){
        var devices = data.devices;
        for(var i = 0; i < devices.length; i++){
            var device = devices[i];
            var new_device = '<tr id="' + device.id.substr(0, 16) + '">'
            +     '<td>' + device.id.substr(0, 15) + '</td>'
            +     '<td>' + device.timestamp + '</td>'
            +     '<td><a href="#" class="button remove_device" data-id="' + device.id + '">Delete key</a></td>'
            + '</tr>';

            $('#keys_trs').append(new_device);
        }
    }
}

var remove_device = function(a, b, c) {
    console.log(a,b,c);
}

var login_user = function() {
    $('.main').addClass('hidden');
    $('#devices').removeClass('hidden');
    $get('/devices', show_devices);
}

var register_key = function(){
    $get('/enroll', function(request){
        logger.log('Registering...');
        var registerRequests = request.registerRequests;
        var authenticateRequests = request.authenticateRequests;

        // Getting AppID
        var appid = registerRequests[0].appId;

        logger.log(request);
        logger.log('Waiting for user action...');


        u2f.register(appid, registerRequests, authenticateRequests, function(deviceResponse) {

            locked = false;

            if(deviceResponse.errorCode){
                logger.log('U2F ERROR: ' + U2F_ERROR_CODES[deviceResponse.errorCode]);
            }else{
                logger.log(deviceResponse);
                logger.log('Verifying with server...');
                
                $post('/enroll', deviceResponse,  function(serverResonse){
                    if(serverResonse.status === 'ok'){
                        logger.log('Success!');
                    }else{
                        logger.log('Fail! ' + serverResonse.error);
                    }
                })
            }

        }, 10);
    });
}

var locked = false;

var u2f_enroll = function(e) {
    e.preventDefault();
    e.stopPropagation();

    var user = {
        'username': enroll_form.find('input[name=username]').val(),
        'password': enroll_form.find('input[name=password]').val()
    }


    var logger = new Logger('#register_log');

    if(user['username'] && user['password'] && !locked){
        clear_textareas();

        $post('/register', user, function(response){
            if(response.status === 'ok'){

                logger.log('Registering...');
                locked = true;

                $post('/login', user, function(response){
                    if(response.status !== 'failed'){
                        locked = false;
                        logger.log('Successfully registered!');

                        setTimeout(function(){
                            login_user();
                        }, 1500)

                    }else{
                        logger.log('Login Failed');
                        locked = false;
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
    e.preventDefault();
    e.stopPropagation();

    var user = {
        'username': sign_form.find('input[name=username]').val(),
        'password': sign_form.find('input[name=password]').val()
    }

    var logger = new Logger('#login_log');

    if(user['username'] && user['password'] && !locked){
        clear_textareas();
        
        logger.log('Loggin in...')

        $post('/login', user,function(response){
            
            if(response.status === 'failed'){
                if(response['u2f_sign_required']){

                    logger.log('U2F Required')
                    locked = true;

                    $get('/sign', function(request){
                        var authenticateRequests = request.authenticateRequests;

                        // Getting AppID
                        var appid = authenticateRequests[0].appId;
                       
                        // Getting Challenge
                        var challenge = authenticateRequests[0].challenge;

                        logger.log('Getting challenge...');
                        logger.log(request);
                        logger.log('Waiting for user action...');

                       
                        u2f.sign(appid, challenge, authenticateRequests, function(deviceResponse) {
                            locked = false;

                            if(deviceResponse.errorCode){
                                logger.log('U2F ERROR: ' + U2F_ERROR_CODES[deviceResponse.errorCode]);
                            }else{
                                logger.log(deviceResponse);
                                logger.log('Verifying with server...');
                                
                                $post('/sign', deviceResponse, function(serverResonse){
                                    if(serverResonse.status === 'ok'){
                                        logger.log('Success! Counter ' + serverResonse.counter);

                                        setTimeout(function(){
                                            login_user();
                                        }, 1500)                                    
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
                setTimeout(function(){
                    login_user();
                }, 1500)      
            }
        });
    }

    return false;
}

var clear_textareas = function() {
    var textareas = $('textarea');
    
    for(var i = 0; i < textareas.length; i++)
        textareas[i].value = '';
}

var clear_inputs = function() {
    var inputs = $('input');

    for (var i = 0; i < inputs.length; i++){
        if(inputs[i].type !== 'submit')
            inputs[i].value = '';
    }
}




/* ----- EVENT HANDLERS ----- */

/* --- U2F --- */
    var enroll_form = $('#u2f_register_form');
    enroll_form.submit(u2f_enroll);



    var sign_form = $('#u2f_login_form');
    sign_form.submit(u2f_sign);
/* --- U2F END --- */

    var login_container = $('#login');
    var register_container = $('#register');

    $('#switch_to_register').on('click', function(){
        $('.main').addClass('hidden');
        register_container.removeClass('hidden');
        clear_textareas();
        clear_inputs();
        locked = false;
    })

    $('#switch_to_login').on('click', function(){
        $('.main').addClass('hidden');
        login_container.removeClass('hidden');
        clear_textareas();
        clear_inputs();
        locked = false;
    })

    $(document).on('click', '.remove_device', remove_device);

    /*----- Logout button -----*/
    $('.logout').on('click', function() {
        $get('/logout', function(){
            $('.main').addClass('hidden');
            login_container.removeClass('hidden');
        })

    })

setTimeout(function(){
    $get('/islogged', function(response){
        if(response.status === 'ok'){
            if(response.logged_in)
                login_user();
        }
    })
}, 1000)