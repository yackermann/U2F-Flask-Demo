
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

var u2f_enroll = function(e) {
    if (e.preventDefault) e.preventDefault();

    var user = {
        'username': enroll_form.elements['username'].value,
        'password': enroll_form.elements['password'].value
    }



    return false;
}

var u2f_sign = function(e) {
    if (e.preventDefault) e.preventDefault();

    var user = {
        'username': enroll_form.elements['username'].value,
        'password': enroll_form.elements['password'].value
    }

    if(user['username'] && user['password']){
        $post('/login', user,function(response){
            if(response.status === 'failed'){
                if(response['u2f_sign_required']){
                    $get('/sign', function(serverreq){
                        var req = serverreq.authenticateRequests[0];

                        // Getting AppID
                        var appid = req.appId;
                       
                        // Getting Challenge
                        var challenge = req.challenge;

                        // Formating challenge for U2F key
                        var registeredKeys = [{version: req.version, keyHandle: req.keyHandle}];
                        console.log(req)
                        console.log('Waiting for user action...')
                       
                        u2f.sign(appid, challenge, registeredKeys, function(deviceResponse) {
                            console.log(deviceResponse)
                            console.log('Verifying with server...')
                            
                            $post('/sign', deviceResponse, (response) => console.log(response))

                            return
                        }, 10);
                    });
                }else{
                    console.log(response.error)
                }
            }else{
                console.log('Login successful. No U2F sign required.')
            }
        });
    }

    return false;
}




/* ----- EVENT HANDLERS ----- */

var $id = function(id){
    return document.getElementById(id);
}


/* --- U2F --- */
    var enroll_form = $id('u2f_login_form');
    enroll_form.addEventListener("submit", u2f_enroll);

    var sign_form = $id('u2f_login_form');
    sign_form.addEventListener("submit", u2f_sign);
/* --- U2F END --- */

var login_container = $id('login');
var register_container = $id('register');

var regbutton = $id('switch_to_register');
var loginbutton = $id('switch_to_login');

regbutton.addEventListener('click', function(){
    login_container.className = 'main hidden'
    register_container.className = 'main present'
}, false)

loginbutton.addEventListener('click', function(){
    register_container.className = 'main hidden';
    login_container.className    = 'main present'
}, false)

