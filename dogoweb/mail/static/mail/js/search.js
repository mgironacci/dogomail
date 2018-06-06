var jseg = {};

$(function(){

    var clickDTs = function (et, e, dt, indexes) {
        var dts =  $('#mails-table').DataTable();
        var dtsc = dts.rows({selected:true}).count();
        var evento = et.split(".")[0];
        var tabla = et.split(".")[1];
        if (evento == 'select') {
            var dtsn = dts.rows({selected:true}).data()[0][1];
            var dtsd = dts.rows({selected:true}).data()[0][2];
            var dtse = dts.rows({selected:true}).data()[0][3];
            $('#mail-name').html(dtsn);
            $('#mail-dns').html(dtsd);
            $('#mail-stat').html(dtse);
            $('#mail-panel').show();
        } else if (evento == 'deselect') {
            $('#mail-panel').hide();
        }
    }

    // Servidores
    $('#mails-table')
    .on('select.dt', function ( e, dt, type, indexes ) { clickDTs('select.mail', e, dt, indexes); } )
    .on('deselect.dt', function ( e, dt, type, indexes ) { clickDTs('deselect.mail', e, dt, indexes); } )
    .DataTable({
        responsive: true,
        serverSide: true,
        ajax: {
            type: "POST",
            url: '/mail/search/',
            contentType: 'application/json; charset=utf-8',
            data: function (data) { return data = JSON.stringify(data); }
        },
        language: DTlang,
        //dom: 'Bfrtip',
        //buttons: [ 'create', 'editSingle', 'removeSingle'],
        //buttons: true,
        columns: [
            { name: "id", orderable: false, searchable: false },
            { name: "estado" },
            { name: "rcv_time" },
            { name: "sender" },
            { name: "ip_orig" },
            { name: "subject" },
            { name: "sizemsg" },
        ],
        order: [[ 1, "asc" ]],
        select: 'single',
        //rowReorder: true,
        /*drawCallback: function( settings ) {
            hideMP();
        },*/
        //"paging":   false,
        //"info":     false,
        //"scrollX":  false,
        //"searching": false,
        //"dom": 'Bfrtip',
        cache: false,
    });
    // Llamado al pedir nuevo menu
    $("#popup-modal").on("shown.bs.modal", function () {
        $("#popup-modal .modal-content").html('');
        var btnact = $("#popup-modal").attr('data-action').split('.')[0];
        var btnpan = $("#popup-modal").attr('data-action').split('.')[1];
        if (typeof btnact == typeof undefined || btnact == false) {
            return false;
        }
        $("#popup-modal").removeAttr('data-action');
        // Obtengo las tablas
        var dts =  $('#mails-table').DataTable();
        var action = "";
        var ids = [];
        var srows = [];
        if (btnact == 'add') {
            if (btnpan == 'mail') {
                action  = '/mail/domains/create/';
            }
        }
        // Busco en el listado correcto si es edit o delete
        if (btnact == 'edit' || btnact == 'delete' ) {
            if (btnpan == 'mail') {
                if (dts.rows( { selected: true } ).count() != 0) {
                    action = '/mail/domains/';
                    srows = dts.rows( { selected: true } );
                    for(var i=0; i<srows.count(); i++) {
                        ids.push(srows.data()[i][0]);
                    }
                }
            }
            if (btnact == 'edit')   { action += 'update/'; }
            if (btnact == 'delete') { action += 'delete/'; }
            if (ids.length > 0)     { action += ids.join(); }
        }
        $.ajax({
            url: action,
            type: 'GET',
            dataType: 'json',
            success: function (data) {
                if (data.mensaje) {
                    $("#popup-modal").modal('hide');
                    $.notify({
                        icon: data.mensaje.icon,
                        title: ' ',
                        message: data.mensaje.msg
                    },{
                        type: data.mensaje.tipo,
                        placement: {
                            from: "bottom",
                            align: "center"
                        },
                        newest_on_top: true,
                        mouse_over: 'pause'
                    });
                } else {
                    $("#popup-modal .modal-content").html(data.html_form);
                }
            }
        });
    });
    // Llamado al darle submit
    $("#popup-modal").on("submit", function () {
        var form = $('#modal-form');
        $.ajax({
            url: form.attr("action"),
            data: form.serialize(),
            type: 'POST',
            dataType: 'json',
            success: function (data) {
                if (data.form_is_valid) {
                    if (data.snext == 'yes') {
                        $("#popup-modal .modal-content").html(data.html_form);
                    } else {
                        $("#popup-modal").modal('hide');
                        if (data.panel == 'mail') {
                            $('#mails-table').DataTable().ajax.reload();
                            $('#mail-panel').hide();
                        }
                    }
                }
                else {
                    $("#popup-modal .modal-content").html(data.html_form);
                }
                if (data.mensaje) {
                    $.notify({
                        icon: data.mensaje.icon,
                        title: ' ',
                        message: data.mensaje.msg
                    },{
                        type: data.mensaje.tipo,
                        placement: {
                            from: "bottom",
                            align: "center"
                        },
                        newest_on_top: true,
                        mouse_over: 'pause'
                    });
                }
            }
        });
        return false;
    });

    var saltaEdit = function (npk) {
        var form = $('#modal-form');
        var action = form.attr("action")+npk;
        $.ajax({
            url: action,
            type: 'GET',
            dataType: 'json',
            success: function (data) {
                $("#popup-modal .modal-content").html(data.html_form);
            }
        });
    }

    var salvaNext = function (npk) {
        var form = $('#modal-form');
        $('#snext').val(npk);
        $.ajax({
            url: form.attr("action"),
            data: form.serialize(),
            type: 'POST',
            dataType: 'json',
            success: function (data) {
                if (data.form_is_valid) {
                    if (data.panel == 'mail') {
                        $('#mails-table').DataTable().ajax.reload();
                    }
                    if (data.snext == 'new') {
                        $("#popup-modal .modal-content").html('');
                    } else if (data.snext != '') {
                        saltaEdit(data.snext);
                        return;
                    } else {
                        $("#popup-modal").modal('hide');
                        $("#popup-modal .modal-content").html('');
                        return;
                    }
                }
                $("#popup-modal .modal-content").html(data.html_form);
            }
        });
    }

    jseg.saltaEdit = saltaEdit;
    jseg.salvaNext = salvaNext;
});
