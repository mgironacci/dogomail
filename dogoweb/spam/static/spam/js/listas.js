var jseg = {};

$(function(){
    $('#edit').hide();
    $('#delete').hide();

    // Limpiamos valores
    $("#id_sender").val("");
    $("#id_recipient").val("");
    $("#id_ip_orig").val("");
    $("#id_tipo").val("");
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
    $("#id_ip_orig").keyup(function(event) {
        if (event.keyCode === 13) {
            $("#id_btn_buscar").click();
        }
    });
    $("#id_tipo").keyup(function(event) {
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
        var dts =  $('#listas-table').DataTable();
        var dtsc = dts.rows({selected:true}).count();
        var evento = et.split(".")[0];
        var tabla = et.split(".")[1];
        if (evento == 'select') {
            if (dtsc != 0) {
                $('#edit').show();
                $('#delete').show();
            }
        } else if (evento == 'deselect') {
            if (dtsc == 0) {
                $('#edit').hide();
                $('#delete').hide();
            }
        }
    }

    // Servidores
    $('#listas-table')
    .on('select.dt', function ( e, dt, type, indexes ) { clickDTs('select.lista', e, dt, indexes); } )
    .on('deselect.dt', function ( e, dt, type, indexes ) { clickDTs('deselect.lista', e, dt, indexes); } )
    .DataTable({
        responsive: true,
        serverSide: true,
        ajax: {
            type: "POST",
            url: '/spam/list',
            contentType: 'application/json; charset=utf-8',
            data: function ( d ) {
                d['colsearch'] = false;
                d['colhidden'] = [];
                if ($('#id_sender').val()) {
                    var valor = $('#id_sender').val();
                    d['columns'][3]['search']['value'] = valor;
                    d['colsearch'] = true;
                }
                if ($('#id_recipient').val()) {
                    var valor = $('#id_recipient').val();
                    d['columns'][4]['search']['value'] = valor;
                    d['colsearch'] = true;
                }
                if ($('#id_ip_orig').val()) {
                    var valor = $('#id_ip_orig').val();
                    d['columns'][2]['search']['value'] = valor;
                    d['colsearch'] = true;
                }
                if ($('#id_tipo').val() && $('#id_tipo').val() != '') {
                    var valor = $('#id_tipo').val();
                    d['columns'][1]['search']['value'] = valor;
                    d['colsearch'] = true;
                }
                if ($('#id_activo').val() > 1) {
                    if($('#id_activo').val() == 2) { d['colhidden'].push(['activo', 1]); }
                    if($('#id_activo').val() == 3) { d['colhidden'].push(['activo', 0]); }
                    d['colsearch'] = true;
                }
                var tdtz = getMyTZ(noTZ);
                if ($('#id_rcv_from').val() && $('#id_rcv_until').val()) {
                    var valor = $('#id_rcv_from').val() + tdtz + "|" + $('#id_rcv_until').val() + tdtz ;
                    d['colhidden'].push(['creado_el', valor]);
                    d['colsearch'] = true;
                } else if ($('#id_rcv_from').val()) {
                    var valor = $('#id_rcv_from').val() + tdtz  + "|";
                    d['colhidden'].push(['creado_el', valor]);
                    d['colsearch'] = true;
                } else if ($('#id_rcv_until').val()) {
                    var valor = "|" + $('#id_rcv_until').val() + tdtz ;
                    d['colhidden'].push(['creado_el', valor]);
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
            { name: "tipo" },
            { name: "ip" },
            { name: "remitente" },
            { name: "destino" },
            { name: "check+activo", searchable: false, orderable: false },
            { name: "datetime+creado_el" }
        ],
        order: [[ 1, "asc" ]],
        select: true,
        //rowReorder: true,
        /*drawCallback: function( settings ) {
            hideMP();
        },*/
        //"paging":   false,
        //"info":     false,
        //"scrollX":  false,
        searching: false,
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
        var dts =  $('#listas-table').DataTable();
        var action = "";
        var ids = [];
        var srows = [];
        if (btnact == 'add') {
            if (btnpan == 'lista') {
                action  = '/spam/list/create/';
            }
        }
        // Busco en el listado correcto si es edit o delete
        if (btnact == 'edit' || btnact == 'delete' ) {
            if (btnpan == 'lista') {
                if (dts.rows( { selected: true } ).count() != 0) {
                    action = '/spam/list/';
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
                    $("#popup-modal").modal('hide');
                    if (data.panel == 'lista') {
                        $('#listas-table').DataTable().ajax.reload();
                        $('#edit').hide();
                        $('#delete').hide();
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
                    if (data.panel == 'lista') {
                        $('#listas-table').DataTable().ajax.reload();
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
        $('#listas-table').DataTable().draw();
        $("#id_sender").focus();
    }

    jseg.buscar = buscar;
    jseg.saltaEdit = saltaEdit;
    jseg.salvaNext = salvaNext;
});
