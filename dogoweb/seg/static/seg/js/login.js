
//Barra de progreso
jQuery(document).ajaxStart(function() {
    NProgress.start();
}).ajaxStop(function() {
    NProgress.done();
});


$(document).ready(function(){
    // Show/Hide Password
    $('.password').password({
        eyeClass: '',
        eyeOpenClass: 'icmn-eye',
        eyeCloseClass: 'icmn-eye-blocked'
    });

    // this is the id of the form
    $("#form-login").validate({
        submit : {
            settings: {
                inputContainer: '.form-group',
                errorListClass: 'form-control-error',
                errorClass: 'has-danger'
            },
            // callback: {
            //     onSubmit : function(){ sendData({ password:$("input#password").val(),
            //                                       email:$("input#email").val()
            //                                     }
            //                                     , VALIDATE_LOGIN
            //                                     , function(response) {
            //                                         if(response.status == 'OK'){
            //                                             alert(response.msg);
            //                                         }
            //                                         else {
            //                                             alert("Error:" + response.msg);
            //                                         }
            //                                     }
            //                                     , function() {
            //                                         alert("Un error ha ocurrido");
            //                                     });}
            // } //callback
        }
    });//validate
});//doc.ready
