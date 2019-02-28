var jobj = {};

$(function(){

    // Limpiamos valores
    $("#id_sender").val("");
    $("#id_recipient").val("");
    $("#id_subject").val("");
    $("#id_ip_orig").val("");
    $("#id_msgids").val("");
    $("#id_minsize").val("");
    $("#id_maxsize").val("");
    $("#id_rcv_from").val("");
    $("#id_rcv_until").val("");

    // Hacemos andar el enter en los campos de texto
    $("#id_sender").keyup(function(event) {
        if (event.keyCode === 13) {
            $("#id_btn_buscar").click();
        }
    });
    $("#id_recipient").keyup(function(event) {
        if (event.keyCode === 13) {
            $("#id_btn_buscar").click();
        }
    });
    $("#id_subject").keyup(function(event) {
        if (event.keyCode === 13) {
            $("#id_btn_buscar").click();
        }
    });
    $("#id_ip_orig").keyup(function(event) {
        if (event.keyCode === 13) {
            $("#id_btn_buscar").click();
        }
    });
    $("#id_msgids").keyup(function(event) {
        if (event.keyCode === 13) {
            $("#id_btn_buscar").click();
        }
    });
    $("#id_minsize").keyup(function(event) {
        if (event.keyCode === 13) {
            $("#id_btn_buscar").click();
        }
    });
    $("#id_maxsize").keyup(function(event) {
        if (event.keyCode === 13) {
            $("#id_btn_buscar").click();
        }
    });
    $("#id_rcv_from").keyup(function(event) {
        if (event.keyCode === 13) {
            $("#id_btn_buscar").click();
        }
    });
    $("#id_rcv_until").keyup(function(event) {
        if (event.keyCode === 13) {
            $("#id_btn_buscar").click();
        }
    });
    $('.datetimepicker-init').datetimepicker({
        widgetPositioning: {
            horizontal: 'left'
        },
        icons: {
            time: "fa fa-clock-o",
            date: "fa fa-calendar",
            up: "fa fa-arrow-up",
            down: "fa fa-arrow-down"
        },
        format: 'YYYY-MM-DD HH:mm:ss',
        locale: LANGCODE
    });
    $('#id_rcv_until').datetimepicker({
            useCurrent: false //Important! See issue #1075
        });
    $("#id_rcv_from").on("dp.change", function (e) {
        $('#id_rcv_until').data("DateTimePicker").minDate(e.date);
    });
    $("#id_rcv_until").on("dp.change", function (e) {
        $('#id_rcv_from').data("DateTimePicker").maxDate(e.date);
    });


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

    // Correos
    $('#mails-table')
    .on('select.dt', function ( e, dt, type, indexes ) { clickDTs('select.mail', e, dt, indexes); } )
    .on('deselect.dt', function ( e, dt, type, indexes ) { clickDTs('deselect.mail', e, dt, indexes); } )
    .DataTable({
        responsive: true,
        serverSide: true,
        ajax: {
            type: "POST",
            url: '/mail/blockedsearch/',
            contentType: 'application/json; charset=utf-8',
            data: function ( d ) {
                document.getElementById("gr_msgsize").className = "form-group";
                document.getElementById("id_minsize").className = "form-control";
                document.getElementById("id_maxsize").className = "form-control";
                d['columns'][1]['search']['value'] = "4";
                d['colsearch'] = true;
                d['colhidden'] = [];
                if ($('#id_sender').val()) {
                    var valor = $('#id_sender').val();
                    d['columns'][3]['search']['value'] = valor;
                    d['colsearch'] = true;
                }
                if ($('#id_recipient').val()) {
                    var valor = $('#id_recipient').val();
                    d['columns'][9]['search']['value'] = valor;
                    d['colsearch'] = true;
                }
                if ($('#id_subject').val()) {
                    var valor = $('#id_subject').val();
                    d['columns'][6]['search']['value'] = valor;
                    d['colsearch'] = true;
                }
                if ($('#id_ip_orig').val()) {
                    var valor = $('#id_ip_orig').val();
                    d['columns'][5]['search']['value'] = valor;
                    d['colsearch'] = true;
                }
                if ($('#id_msgids').val()) {
                    var valor = $('#id_msgids').val();
                    d['columns'][8]['search']['value'] = valor;
                    d['colsearch'] = true;
                }
                if ($('#id_minsize').val() && $('#id_maxsize').val()) {
                    var terr = false;
                    try {
                        var v1 = String(parseInt(humanFormat.parse($('#id_minsize').val())));
                    } catch(err) {
                        document.getElementById("gr_msgsize").className = "form-group has-danger";
                        document.getElementById("id_minsize").className = "form-control form-control-danger";
                        terr = true;
                    }
                    try {
                        var v2 = String(parseInt(humanFormat.parse($('#id_maxsize').val())));
                    } catch(err) {
                        document.getElementById("gr_msgsize").className = "form-group has-danger";
                        document.getElementById("id_maxsize").className = "form-control form-control-danger";
                        terr = true;
                    }
                    if(terr) { throw "Numero invalido"; }
                    d['columns'][7]['search']['value'] = v1 + "|" + v2;
                    d['colsearch'] = true;
                } else if ($('#id_minsize').val()) {
                    try {
                        var valor = String(parseInt(humanFormat.parse($('#id_minsize').val()))) + "|";
                        d['columns'][7]['search']['value'] = valor;
                        d['colsearch'] = true;
                    } catch(err) {
                        document.getElementById("gr_msgsize").className = "form-group has-danger";
                        document.getElementById("id_minsize").className = "form-control form-control-danger";
                        throw "Numero invalido";
                    }
                } else if ($('#id_maxsize').val()) {
                    try {
                        var valor = "|" + String(parseInt(humanFormat.parse($('#id_maxsize').val())));
                        d['columns'][7]['search']['value'] = valor;
                        d['colsearch'] = true;
                    } catch(err) {
                        document.getElementById("gr_msgsize").className = "form-group has-danger";
                        document.getElementById("id_maxsize").className = "form-control form-control-danger";
                        throw "Numero invalido";
                    }
                }
                if ($('#id_es_local').val() > 1) {
                    if($('#id_es_local').val() == 2) { d['colhidden'].push(['es_local', 1]); }
                    if($('#id_es_local').val() == 3) { d['colhidden'].push(['es_local', 0]); }
                    d['colsearch'] = true;
                }
                if ($('#id_es_cliente').val() > 1) {
                    if($('#id_es_cliente').val() == 2) { d['colhidden'].push(['es_cliente', 1]); }
                    if($('#id_es_cliente').val() == 3) { d['colhidden'].push(['es_cliente', 0]); }
                    d['colsearch'] = true;
                }
                var tdtz = getMyTZ(noTZ);
                if ($('#id_rcv_from').val() && $('#id_rcv_until').val()) {
                    var valor = $('#id_rcv_from').val() + tdtz + "|" + $('#id_rcv_until').val() + tdtz ;
                    d['colhidden'].push(['rcv_time', valor]);
                    d['colsearch'] = true;
                } else if ($('#id_rcv_from').val()) {
                    var valor = $('#id_rcv_from').val() + tdtz  + "|";
                    d['colhidden'].push(['rcv_time', valor]);
                    d['colsearch'] = true;
                } else if ($('#id_rcv_until').val()) {
                    var valor = "|" + $('#id_rcv_until').val() + tdtz ;
                    d['colhidden'].push(['rcv_time', valor]);
                    d['colsearch'] = true;
                }
                //console.log(d);
                return JSON.stringify(d);
            }
        },
        language: DTlang,
        //dom: 'Bfrtip',
        //buttons: [ 'create', 'editSingle', 'removeSingle'],
        //buttons: true,
        columns: [
            { name: "id", orderable: false, searchable: false },
            { name: "cho+estado", orderable: false },
            { name: "datetime+rcv_time" },
            { name: "sender" },
            { name: "count+destinatario_set" },
            { name: "ip_orig" },
            { name: "subject" },
            { name: "hb+sizemsg" },
            { name: "msgids" },
            { name: "fks+destinatario_set+receptor" }
        ],
        order: [[ 2, "desc" ]],
        select: 'multi+shift',
        columnDefs: [
            { width: "4%",  "targets": 1 },
            { width: "10%", "targets": 2 },
            { width: "20%", "targets": 3 },
            { width: "4%",  "targets": 4 },
            { width: "8%",  "targets": 5 },
            { width: "30%", "targets": 6 },
            { width: "5%",  "targets": 7 },
        ],
        //rowReorder: true,
        /*drawCallback: function( settings ) {
            hideMP();
        },*/
        //"paging":   false,
        //"info":     false,
        //"scrollX":  true,
        "searching": false,
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

    var buscar = function() {
        $('#mails-table').DataTable().draw();
        $("#id_sender").focus();
    }

    jobj.buscar = buscar;
});
