
var getJSON = function(url, callback){
    fetch(url, {credentials : 'same-origin'}).then(function(response) {
        return response.json()
    }).then(function(json) {
        callback(json)
    }).catch(function(ex) {
        callback({ 'error': ex })
    })
}

var post = function (url, body, callback) {
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


var processForm = function(e) {
    if (e.preventDefault) e.preventDefault();

    console.log(form.elements['username'].value)
    console.log(form.elements['password'].value)

    console.log(getJSON('/enroll', (data) => console.log(data)))
    // You must return false to prevent the default form behavior
    return false;
}

var form = document.getElementById('u2f-reg-form');
if (form.attachEvent)
    form.attachEvent("submit", processForm);
else
    form.addEventListener("submit", processForm);