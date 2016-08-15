    
var el = {
    'devices'            : '#devices',
    'devices_list'       : '#devices_tbody',
    'panels'             : '.panel',
    'logout'             : '.logout',
    'newdevice'          : '.newdevice',
    'login_log'          : '#login_log',
    'devices_log'        : '#devices_log',
    'register_log'       : '#register_log',
    'u2f_register_form'  : '#u2f_register_form',
    'u2f_login_form'     : '#u2f_login_form',
    'login_panel'        : '#login',
    'register_panel'     : '#register',
    'switch_to_register' : '#switch_to_register',
    'switch_to_login'    : '#switch_to_login'
}
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


var show_devices = function(){
    $get('/devices', function(data) {

        if(!data.error){
            var devices = data.devices;
            for(var i = 0; i < devices.length; i++){
                var device = devices[i];
                var new_device = '<tr id="' + device.id + '">'
                +     '<td>' + device.id.substr(0, 15) + '</td>'
                +     '<td>' + device.index + '</td>'
                +     '<td><a href="#" class="button remove_device" data-id="' + device.id + '">Delete key</a></td>'
                + '</tr>';

                $(el.devices_list).append(new_device);
            }
        }
    });
}

var remove_device = function(caller) {
    
    var logger   = new Logger(el.devices_log)
    var id       = $(caller.currentTarget).data('id');
    var short_id = id.substr(0,15);

    logger.log('Confirming removal of ' + id);

    var sure = confirm('Are you sure you want to remove ' + short_id + '?');
    if(sure) {
        logger.log('Removing ' + short_id);
        $delete('/devices', {'id': id}, function(response) {
            if(!response.error) {
                $('#' + id).remove();
                logger.log('Successfully removed ' + short_id + '!');
            }else{
                logger.log('Failed');
                logger.log(response.error);
            }
        })
    }else{
        logger.log('Canceled');
    }
}


var login_user = function() {
    $(el.panels).addClass('hidden');
    $(el.devices).removeClass('hidden');
    show_devices();
}

var register_device = function(){
    var logger = new Logger(el.devices_log)
    clear_textareas();
    $get('/enroll', function(request){
        if(!request.error){
            locked = true;

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
                    
                    $post('/enroll', deviceResponse,  function(response){
                        if(!response.error){
                            logger.log('Success!');
                            logger.log(response)
                            clear_devices();
                            show_devices();
                        }else{
                            logger.log('Failed');
                            logger.log(response.error);
                        }
                    })
                }

            }, 10);
        }else{
            locked = false;
            logger.log('Failed');
            logger.log(response.error);
        }
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


    var logger = new Logger(el.register_log);

    if(user['username'] && user['password'] && !locked){
        clear_textareas();

        $post('/register', user, function(response){
            if(!response.error){

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
                        logger.log(response);

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

    var logger = new Logger(el.login_log);

    if(user['username'] && user['password'] && !locked){
        clear_textareas();
        
        logger.log('Loggin in...')

        $post('/login', user,function(response){
            if(!response.error){
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
                    logger.log('Success');
                    logger.log('No U2F required');
                    setTimeout(function(){
                        login_user();
                    }, 1500);
                }
            }else{
                logger.log('Fail');
                logger.log(response.error);
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

var clear_devices = function() {
    $(el.devices_list)
        .children()
        .remove();
}

/* ----- EVENT HANDLERS ----- */

/* --- U2F --- */
    var enroll_form = $(el.u2f_register_form);
    enroll_form.submit(u2f_enroll);



    var sign_form = $(el.u2f_login_form);
    sign_form.submit(u2f_sign);
/* --- U2F END --- */

    var login_container = $(el.login_panel);
    var register_container = $(el.register_panel);

    $(el.switch_to_register).on('click', function(){
        $(el.panels).addClass('hidden');
        register_container.removeClass('hidden');
        clear_textareas();
        clear_inputs();
        locked = false;
    })

    $(el.switch_to_login).on('click', function(){
        $(el.panels).addClass('hidden');
        login_container.removeClass('hidden');
        clear_textareas();
        clear_inputs();
        locked = false;
    })

    $(el.newdevice).on('click', register_device);
    $(document).on('click', '.remove_device', remove_device);

    /*----- Logout button -----*/
    $(el.logout).on('click', function() {
        $get('/logout', function(){
            clear_devices();
            $(el.panels).addClass('hidden');
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