/**
 * Created by billy-dev on 2014-10-19.
 */
var baseUrl = 'http://127.0.0.1:8000/';
var username;
var password;
var loginstring;

var doJoin = function() {
    var name = $("#name").val();
    username = $("#username").val()
    password = $("#password").val();
    $.ajax({
        type: 'post',
        url: baseUrl+'api/user/create/',
        data: {
            username:username,
            name:name,
            password:password
        },
        success:function(){
            alert("OK");
            location.href = "login.html";
        },
        error: function(msg){
            alert("Error!");
        }
    });
}

var goAdmin = function() {
    location.href = baseUrl + "admin/";
}

var doLogin = function() {
    username = $('#username').val();
    password = $('#password').val();
    loginstring = "Basic" + Base64.encode(username+":"+password);

    $.ajax({
        type: 'get',
        url: baseUrl + 'api/login/',
        beforeSend: function(req) {
            req.setRequestHeader("Authorization", loginstring);
        },
        success: function(data) {
            alert("Login Success");
            setLoginString();
            window.location = 'timeline.html';
        },
        error: function(){
            alert("Fail to get data!");
        }
    });
}

//-------------------------------------------------------------------------------
/*
    http://www.w3schools.com/js/js_cookies.asp

    replace new cookie code
 */
function setCookie(cname, cvalue, exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays*24*60*60*1000));
    var expires = "expires="+d.toUTCString();
    document.cookie = cname + "=" + cvalue + "; " + expires;

//    var expire = new Date();
//    expire.setDate(expire.getDate()+day);
//    cookies = name + '=' + escape(value) + '; path=/';
//    if (typeof day != 'undefined') {
//        cookies += ';expires=' + expire.toUTCString() + ';';
//    }
//    document.cookie = cookies;
}

function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i=0; i<ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1);
        if (c.indexOf(name) != -1) return c.substring(name.length,c.length);
    }
    return "";
//    name = name + '=';
//    var cookieData = document.cookie;
//    var start = cookieData.indexOf(name);
//    var value = '';
//    if (start != -1) {
//        start += name.length;
//        var end = cookieData.indexOf(';', start);
//        if (end == -1) {
//            end = cookieData.length;
//        }
//        value = cookieData.substring(start, end);
//    }
//    return unescape(value);
}

function checkCookie() {
    var username=getCookie("username");
    if (username!="") {
        alert("Welcome again " + username);
    }else{
        username = prompt("Please enter your name:", "");
        if (username != "" && username != null) {
            setCookie("username", username, 365);
        }
    }
}
//-------------------------------------------------------------------------------
function getLoginString(){
    loginstring = getCookie('loginstring');
    username = getCookie('username');
}

function setLoginString() {
    setCookie('loginstring', loginstring, 1);
    setCookie('username', username, 1);
}

function resetLoginString() {
    setCookie('loginstring', '', -1);
    setCookie('username', '', -1);
}

function checkLoginString() {
    if (loginstring == ""){
        history.back();
    }
}
