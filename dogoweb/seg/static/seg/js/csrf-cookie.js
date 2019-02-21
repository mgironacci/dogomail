function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

var csrftoken = getCookie('csrftoken');

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

function getMyTZ(notz) {
    if(notz) { return "+00"; }
    var dtz = new Date().getTimezoneOffset() / 60;
    var tdtz;
    if(dtz > 0 && dtz < 10)  { tdtz = "-0" + dtz; }
    if(dtz > 9)              { tdtz = "-"  + dtz; }
    if(dtz > 10 && dtz <= 0) { tdtz = "+0" + dtz; }
    if(dtz < -9)             { tdtz = "+"  + dtz; }
    return tdtz;
}