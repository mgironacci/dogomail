var jobj = {};

$(function(){
    $('#uprule').hide();
    $('#downrule').hide();
    $('#edit').hide();
    $('#delete').hide();

    // Limpiamos valores
    $("#id_sch_nombre").val("");
    $("#id_sch_ip").val("");
    $("#id_sch_remitente").val("");
    $("#id_sch_destino").val("");
    $("#id_sch_asunto").val("");
    $("#id_sch_cuerpo").val("");
    $("#id_sch_cliente").val("");

    // Hacemos andar el enter en los campos de texto
    $("#id_sch_nombre").keyup(function(event) {
        if (event.keyCode === 13) {
            $("#id_btn_buscar").click();
        }
    });
    $("#id_sch_ip").keyup(function(event) {
        if (event.keyCode === 13) {
            $("#id_btn_buscar").click();
        }
    });
    $("#id_sch_remitente").keyup(function(event) {
        if (event.keyCode === 13) {
            $("#id_btn_buscar").click();
        }
    });
    $("#id_sch_destino").keyup(function(event) {
        if (event.keyCode === 13) {
            $("#id_btn_buscar").click();
        }
    });
    $("#id_sch_asunto").keyup(function(event) {
        if (event.keyCode === 13) {
            $("#id_btn_buscar").click();
        }
    });
    $("#id_sch_cuerpo").keyup(function(event) {
        if (event.keyCode === 13) {
            $("#id_btn_buscar").click();
        }
    });
    $("#id_sch_cliente").keyup(function(event) {
        if (event.keyCode === 13) {
            $("#id_btn_buscar").click();
        }
    });


    var clickDTs = function (et, e, dt, indexes) {
        var dts =  $('#rule-table').DataTable();
        var dtsc = dts.rows({selected:true}).count();
        var evento = et.split(".")[0];
        var tabla = et.split(".")[1];
        if (evento == 'select') {
            if (dtsc != 0) {
                $('#add').hide();
                $('#uprule').show();
                $('#downrule').show();
                $('#edit').show();
                $('#delete').show();
            }
        } else if (evento == 'deselect') {
            if (dtsc == 0) {
                $('#add').show();
                $('#uprule').hide();
                $('#downrule').hide();
                $('#edit').hide();
                $('#delete').hide();
            }
        }
    }

    // Tabla de datos
    $('#rule-table')
    .on('select.dt', function ( e, dt, type, indexes ) { clickDTs('select.rule', e, dt, indexes); } )
    .on('deselect.dt', function ( e, dt, type, indexes ) { clickDTs('deselect.rule', e, dt, indexes); } )
    .DataTable({
        responsive: true,
        serverSide: true,
        ajax: {
            type: "POST",
            url: '/spam/rulessearch/',
            contentType: 'application/json; charset=utf-8',
            data: function ( d ) {
                d['colsearch'] = false;
                d['colhidden'] = [];
                if ($('#id_sch_nombre').val()) {
                    var valor = $('#id_sch_nombre').val();
                    d['columns'][3]['search']['value'] = valor;
                    d['colsearch'] = true;
                }
                if ($('#id_sch_activo').val() > 1) {
                    if($('#id_sch_activo').val() == 2) { d['colhidden'].push(['activo', 1]); }
                    if($('#id_sch_activo').val() == 3) { d['colhidden'].push(['activo', 0]); }
                    d['colsearch'] = true;
                }
                if ($('#id_sch_accion').val() && $('#id_sch_accion').val() != '') {
                    var valor = $('#id_sch_accion').val();
                    d['columns'][4]['search']['value'] = valor;
                    d['colsearch'] = true;
                }
                if ($('#id_sch_ip').val()) {
                    var valor = $('#id_sch_ip').val();
                    d['columns'][5]['search']['value'] = valor;
                    d['colsearch'] = true;
                }
                if ($('#id_sch_remitente').val()) {
                    var valor = $('#id_sch_remitente').val();
                    d['columns'][6]['search']['value'] = valor;
                    d['colsearch'] = true;
                }
                if ($('#id_sch_destino').val()) {
                    var valor = $('#id_sch_destino').val();
                    d['columns'][7]['search']['value'] = valor;
                    d['colsearch'] = true;
                }
                if ($('#id_sch_asunto').val()) {
                    var valor = $('#id_sch_asunto').val();
                    d['columns'][8]['search']['value'] = valor;
                    d['colsearch'] = true;
                }
                if ($('#id_sch_cuerpo').val()) {
                    var valor = $('#id_sch_cuerpo').val();
                    d['columns'][9]['search']['value'] = valor;
                    d['colsearch'] = true;
                }
                if ($('#id_sch_cliente').val()) {
                    var valor = $('#id_sch_cliente').val();
                    d['columns'][10]['search']['value'] = valor;
                    d['colsearch'] = true;
                }
                var tdtz = getMyTZ(noTZ);
                console.log(d);
                return JSON.stringify(d);
            }
        },
        language: DTlang,
        //dom: 'Bfrtip',
        //buttons: [ 'create', 'editSingle', 'removeSingle'],
        //buttons: true,
        columns: [
            { name: "id", orderable: false, searchable: false },
            { name: "orden" },
            { name: "check+activo" },
            { name: "nombre" },
            { name: "est+accion" },
            { name: "ip" },
            { name: "remitente" },
            { name: "destino" },
            { name: "asunto" },
            { name: "cuerpo" },
            { name: "fk+cliente" },
            { name: "int+maches" },
        ],
        order: [[ 1, "asc" ]],
        select: 'os',
        columnDefs: [
            { width: "3%",  "targets": 1 },
            { width: "3%",  "targets": 2 },
            { width: "15%", "targets": 3 },
            { width: "4%", "targets": 3 },
        ],
        //rowReorder: true,
        /*drawCallback: function( settings ) {
            hideMP();
        },*/
        //"paging":   false,
        //"info":     false,
        //"scrollX":  true,
        "searching": true,
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
        var dts =  $('#rule-table').DataTable();
        var action = "";
        var ids = [];
        var srows = [];
        if (btnact == 'add') {
            if (btnpan == 'regla') {
                action  = '/spam/rules/create/';
            }
        }
        // Busco en el listado correcto si es edit o delete
        if (btnact == 'edit' || btnact == 'delete' ) {
            if (btnpan == 'regla') {
                if (dts.rows( { selected: true } ).count() != 0) {
                    action = '/spam/rules/';
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
                        if (data.panel == 'regla') {
                            $('#rule-table').DataTable().ajax.reload();
                            buscar();
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
                    if (data.panel == 'regla') {
                        $('#rule-table').DataTable().ajax.reload();
                        buscar();
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
        $('#rule-table').DataTable().draw();
        $('#add').show();
        $('#uprule').hide();
        $('#downrule').hide();
        $('#edit').hide();
        $('#delete').hide();
        $("#id_sch_nombre").focus();
    }

    var changeRule = function(laacc) {
        var dts =  $('#rule-table').DataTable();
        var ids = [];
        var srows = [];
        // Armo array en el listado con ids
        if (dts.rows( { selected: true } ).count() != 0) {
            srows = dts.rows( { selected: true } );
            for(var i=0; i<srows.count(); i++) {
                ids.push(srows.data()[i][0]);
            }
        } else {
            return;
        }
        var action = '/spam/rules/' + laacc + '/' + ids.join();
        $.ajax({
            url: action,
            type: 'GET',
            dataType: 'json',
            success: function (data) {
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
                buscar();
            }
        });

    }

    jobj.buscar = buscar;
    jobj.changeRule = changeRule;
});
