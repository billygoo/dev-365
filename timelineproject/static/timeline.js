/**
 * Created by billy-dev on 2014-10-19.
 */
var baseUrl = 'http://192.168.0.13:8000/';
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
            location.href = "/home/login";
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
    loginstring = "Basic " + Base64.encode(username+":"+password);

    $.ajax({
        type: 'get',
        url: baseUrl + 'api/login/',
        beforeSend: function(req) {
            req.setRequestHeader('Authorization', loginstring);
        },
        success: function(data) {
            alert("Login Success");
            setLoginString();
            window.location = '/home/timeline/';
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
    document.cookie = cname + "=" + cvalue + ";path=/; " + expires;

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

var doLogout = function() {
    resetLoginString();
    window.location = "/home/login";
}

var doWriteTimeline=function() {
    var msg = $("#writearea").val();
    $.ajax({
        type:'post',
        url:baseUrl+'api/timeline/create',
        data:{message:msg},
        beforeSend: function (request) {
            request.setRequestHeader('Authorization', loginstring);
        },
        success: function () {
            alert("OK");
            doReload();
        },
        error: function (msg) {
            alert("Fail to write data!")
        }
    });
}

var doGetTimeline = function() {
    $.ajax({
        type:'get',
        url: baseUrl + 'api/timeline/',
        beforeSend: function (req) {
            req.setRequestHeader("Authorization", loginstring);
        },
        success: function(data) {
            for (var i in data.items) {
                doAppend(data.items[i]);
            }
            $("#total").html(data.total_count);
            $("#mine").html($('[name=deleteMsg]').length - 1);
            $("#username").html(username);
            $("#writearea").val("");
        },
        error: function() {
            alert("Fail to get data!")
        }
    });
}

var doAppend = function(data) {
    node = $("#msgTemplate").clone();

    $(".name", node).append(data.username);
    $(".content", node).append(data.message);
    $(".data", node).append(data.created);
    $(".like", node).prepend(data.liked + "  ");
    $("#like", node).attr("value", data.id);

    if(username == data.username) {
        $("[name=deleteMsg]", node).attr("value", data.id);
    } else {
        $("[name=deleteMsg]", node).remove();
    }
    node.show();
    $("#timelinearea").append(node);
}

var doReload = function() {
    doClear();
    doGetTimeline();
}

var doClear = function() {
    $("#timelinearea").html("");
}

var doDeleteTimeline = function () {
    var id = $(this).val() + "/";

    $.ajax({
        type:'post',
        url:baseUrl+'api/timeline/'+ id + '/delete/',
        beforeSend: function (request) {
            request.setRequestHeader('Authorization', loginstring);
        },
        success: function () {
            doReload();
        },
        error: function (msg) {
            alert("Fail to write data!")
        }
    });
}

var doSearchTimeline = function () {
    $.ajax({
        type:'post',
        url:baseUrl+'api/timeline/find/',
        data:{query:$("#search").val()},
        beforeSend: function (request) {
            request.setRequestHeader('Authorization', loginstring);
        },
        success: function () {
            doClear()
            for (var i in data) {
                doAppend(data[i]);
            }
            $("#total").html(data.total_count);
            $("#mine").html($('[name=deleteMsg]').length - 1);
            $("#search").val("");
        },
        error: function (msg) {
            alert("Fail to get data!")
        }
    });
}