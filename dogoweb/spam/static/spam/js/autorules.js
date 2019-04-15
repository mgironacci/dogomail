var jobj = {};

$(function(){
    $('#ignorerule').hide();
    $('#confirmrule').hide();

    // Limpiamos valores
    $("#id_descripcion").val("");
    $("#id_valor").val("");
    $("#id_mincant").val("");
    $("#id_maxcant").val("");
    $("#id_rcv_from").val("");
    $("#id_rcv_until").val("");

    // Hacemos andar el enter en los campos de texto
    $("#id_descripcion").keyup(function(event) {
        if (event.keyCode === 13) {
            $("#id_btn_buscar").click();
        }
    });
    $("#id_valor").keyup(function(event) {
        if (event.keyCode === 13) {
            $("#id_btn_buscar").click();
        }
    });
    $("#id_mincant").keyup(function(event) {
        if (event.keyCode === 13) {
            $("#id_btn_buscar").click();
        }
    });
    $("#id_maxcant").keyup(function(event) {
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
        var dts =  $('#autorule-table').DataTable();
        var dtsc = dts.rows({selected:true}).count();
        var evento = et.split(".")[0];
        var tabla = et.split(".")[1];
        if (evento == 'select') {
            if (dtsc != 0) {
                $('#ignorerule').show();
                $('#confirmrule').show();
            }
        } else if (evento == 'deselect') {
            if (dtsc == 0) {
                $('#ignorerule').hide();
                $('#confirmrule').hide();
            }
        }
    }

    // Tabla de datos
    $('#autorule-table')
    .on('select.dt', function ( e, dt, type, indexes ) { clickDTs('select.mail', e, dt, indexes); } )
    .on('deselect.dt', function ( e, dt, type, indexes ) { clickDTs('deselect.mail', e, dt, indexes); } )
    .DataTable({
        responsive: true,
        serverSide: true,
        ajax: {
            type: "POST",
            url: '/spam/aurorulessearch/',
            contentType: 'application/json; charset=utf-8',
            data: function ( d ) {
                document.getElementById("gr_msgcant").className = "form-group";
                document.getElementById("id_mincant").className = "form-control";
                document.getElementById("id_maxcant").className = "form-control";
                d['colsearch'] = false;
                d['colhidden'] = [];
                if ($('#id_descripcion').val()) {
                    var valor = $('#id_descripcion').val();
                    d['columns'][3]['search']['value'] = valor;
                    d['colsearch'] = true;
                }
                if ($('#id_valor').val()) {
                    var valor = $('#id_valor').val();
                    d['columns'][4]['search']['value'] = valor;
                    d['colsearch'] = true;
                }
                if ($('#id_mincant').val() && $('#id_maxcant').val()) {
                    var terr = false;
                    try {
                        var v1 = String(parseInt(humanFormat.parse($('#id_mincant').val())));
                    } catch(err) {
                        document.getElementById("gr_msgcant").className = "form-group has-danger";
                        document.getElementById("id_mincant").className = "form-control form-control-danger";
                        terr = true;
                    }
                    try {
                        var v2 = String(parseInt(humanFormat.parse($('#id_maxcant').val())));
                    } catch(err) {
                        document.getElementById("gr_msgcant").className = "form-group has-danger";
                        document.getElementById("id_maxcant").className = "form-control form-control-danger";
                        terr = true;
                    }
                    if(terr) { throw "Numero invalido"; }
                    d['columns'][5]['search']['value'] = v1 + "|" + v2;
                    d['colsearch'] = true;
                } else if ($('#id_mincant').val()) {
                    try {
                        var valor = String(parseInt(humanFormat.parse($('#id_mincant').val()))) + "|";
                        d['columns'][5]['search']['value'] = valor;
                        d['colsearch'] = true;
                    } catch(err) {
                        document.getElementById("gr_msgcant").className = "form-group has-danger";
                        document.getElementById("id_mincant").className = "form-control form-control-danger";
                        throw "Numero invalido";
                    }
                } else if ($('#id_maxcant').val()) {
                    try {
                        var valor = "|" + String(parseInt(humanFormat.parse($('#id_maxcant').val())));
                        d['columns'][5]['search']['value'] = valor;
                        d['colsearch'] = true;
                    } catch(err) {
                        document.getElementById("gr_msgcant").className = "form-group has-danger";
                        document.getElementById("id_maxcant").className = "form-control form-control-danger";
                        throw "Numero invalido";
                    }
                }
                if ($('#id_confirmada').val() > 1) {
                    if($('#id_confirmada').val() == 2) { d['colhidden'].push(['confirmada', 1]); }
                    if($('#id_confirmada').val() == 3) { d['colhidden'].push(['confirmada', 0]); }
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
                    d['colhidden'].push(['hora', valor]);
                    d['colsearch'] = true;
                } else if ($('#id_rcv_from').val()) {
                    var valor = $('#id_rcv_from').val() + tdtz  + "|";
                    d['colhidden'].push(['hora', valor]);
                    d['colsearch'] = true;
                } else if ($('#id_rcv_until').val()) {
                    var valor = "|" + $('#id_rcv_until').val() + tdtz ;
                    d['colhidden'].push(['hora', valor]);
                    d['colsearch'] = true;
                }
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
            { name: "cho+confirmada", orderable: false },
            { name: "datetime+hora" },
            { name: "descripcion" },
            { name: "valor" },
            { name: "int+cantidad" },
            { name: "cho+activo" },
        ],
        order: [[ 2, "desc" ]],
        select: 'os',
        columnDefs: [
            { width: "5%",   "targets": 1 },
            { width: "10%",  "targets": 2 },
            { width: "15%",  "targets": 3 },
            { width: "40%",  "targets": 4 },
            { width: "5%",   "targets": 5 },
            { width: "5%",   "targets": 6 },
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
    /*
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
        var dts =  $('#autorule-table').DataTable();
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
                            $('#autorule-table').DataTable().ajax.reload();
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
                        $('#autorule-table').DataTable().ajax.reload();
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
*/
    var buscar = function() {
        $('#autorule-table').DataTable().draw();
        $('#ignorerule').hide();
        $('#confirmrule').hide();
        $("#id_sender").focus();
    }

    var changeRule = function(laacc) {
        var dts =  $('#autorule-table').DataTable();
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
        var action = '/spam/autorules/' + laacc + '/' + ids.join();
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
