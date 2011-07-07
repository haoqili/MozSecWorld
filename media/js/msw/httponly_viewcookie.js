// viewCookie() taken from getCookie() in http://www.java2s.com/Code/JavaScript/Development/Cookiesetdeletegetvalueandcreate.htm 
function getCookieVal (offset) {
    var endstr = document.cookie.indexOf (";", offset);
    if (endstr == -1) { endstr = document.cookie.length; }
    return unescape(document.cookie.substring(offset, endstr));
}
function viewCookie (name) {
    var arg = name + "=";
    var alen = arg.length;
    var clen = document.cookie.length;
    var i = 0;
    var cookie = "";
    while (i < clen) {
        var j = i + alen;
        if (document.cookie.substring(i, j) == arg) {
             cookie = getCookieVal (j);
        }
        i = document.cookie.indexOf(" ", i) + 1;
        if (i == 0) break; 
    }
    alert(cookie);
}

document.getElementById("name1").addEventListener('click', function(){ viewCookie("name1") }, false);
document.getElementById("name2").addEventListener('click', function(){ viewCookie("name2") }, false);
