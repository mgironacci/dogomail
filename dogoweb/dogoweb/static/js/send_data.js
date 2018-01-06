function sendData(data,url,responseHandler, errorHandler){
    //Configure ajax
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
    $.ajax({
        url: url,
        method: 'POST',
        dataType: 'json',
        data: data,
	error: errorHandler,     
        success: responseHandler
    });
}
