var jseg = {};

$(function(){
    $('#b_menus_edit').hide();
    $('#b_menus_delete').hide();

    var clickDT = function (et, e, dt, indexes) {
        var dtm =  $('#menustable').DataTable();
        var dtp =  $('#pantstable').DataTable();
        var evento = et.split(".")[0];
        var tabla = et.split(".")[1];
        if (tabla == 'menu' && dtp.rows({selected:true}).count() != 0 && dtm.rows({selected:true}).count() != 0) {
            dtp.rows().deselect();
        } else if (tabla == 'pant' && dtm.rows({selected:true}).count() != 0 && dtp.rows({selected:true}).count() != 0) {
            dtm.rows().deselect();
        }
        if (evento == 'select') {
            if (dt.rows( { selected: true } ).count() != 0) {
                $('#b_menus_edit').show();
                $('#b_menus_delete').show();
            }
        } else if (evento == 'deselect') {
            if (dt.rows( { selected: true } ).count() == 0) {
                $('#b_menus_edit').hide();
                $('#b_menus_delete').hide();
            }
        }
    }

    $('#userstable').DataTable({
        responsive: true,
        serverSide: true,
        ajax: {
            type: "POST",
            url: '/seg/users',
            contentType: 'application/json; charset=utf-8',
            data: function (data) { return data = JSON.stringify(data); }
        },
        language: DTlang,
        columns: [
            { name: "username" },
            { name: "last_name" },
            { name: "is_active", sorting: false, searchable: false }
        ],
        order: [[ 0, "asc" ]],
        select: 'single',
        //"paging":   false,
        //"ordering": false,
        //"info":     false,
        //"scrollX":  false,
        //"searching": false,
        //"dom": 'Bfrtip',
        cache: false,
    });
    $('#groupstable').DataTable({
        responsive: true,
        serverSide: true,
        ajax: {
            type: "POST",
            url: '/seg/groups',
            contentType: 'application/json; charset=utf-8',
            data: function (data) { return data = JSON.stringify(data); }
        },
        language: DTlang,
        columns: [
            { name: "name" },
            { name: "func_users", searchable: false },
            { name: "func_perms", searchable: false }
        ],
        order: [[ 0, "asc" ]],
        select: 'multi',
        //"paging":   false,
        //"ordering": false,
        //"info":     false,
        //"scrollX":  false,
        //"searching": false,
        //"dom": 'Bfrtip',
        cache: false,
    });
    $('#permstable').DataTable({
        responsive: true,
        serverSide: true,
        ajax: {
            type: "POST",
            url: '/seg/perms',
            contentType: 'application/json; charset=utf-8',
            data: function (data) { return data = JSON.stringify(data); }
        },
        language: DTlang,
        columns: [
            { name: "name" },
            { name: "content_type", searchable: false },
            { name: "func_used", searchable: false }
        ],
        order: [[ 0, "asc" ]],
        select: 'multi',
        //"paging":   false,
        //"ordering": false,
        //"info":     false,
        //"scrollX":  false,
        //"searching": false,
        //"dom": 'Bfrtip',
        cache: false,
    });
    // Panel de menus y pantallas
    $('#menustable')
    .on('select.dt', function ( e, dt, type, indexes ) { clickDT('select.menu', e, dt, indexes); } )
    .on('deselect.dt', function ( e, dt, type, indexes ) { clickDT('deselect.menu', e, dt, indexes); } )
    .DataTable({
        responsive: true,
        serverSide: true,
        ajax: {
            type: "POST",
            url: '/seg/menus',
            contentType: 'application/json; charset=utf-8',
            data: function (data) { return data = JSON.stringify(data); }
        },
        language: DTlang,
        //dom: 'Bfrtip',
        //buttons: [ 'create', 'editSingle', 'removeSingle'],
        //buttons: true,
        columns: [
            { name: "id", sorting: false, searchable: false },
            { name: "icono", sorting: false, searchable: false },
            { name: "nombre" },
            { name: "orden" },
            { name: "activo", sorting: false, searchable: false }
        ],
        order: [[ 3, "asc" ]],
        select: true,
        rowReorder: true,
        //"paging":   false,
        //"info":     false,
        //"scrollX":  false,
        //"searching": false,
        //"dom": 'Bfrtip',
        cache: false,
    });
    $('#pantstable')
    .on('select.dt', function ( e, dt, type, indexes ) { clickDT('select.pant', e, dt, indexes); } )
    .on('deselect.dt', function ( e, dt, type, indexes ) { clickDT('deselect.pant', e, dt, indexes); } )
    .DataTable({
        responsive: true,
        serverSide: true,
        ajax: {
            type: "POST",
            url: '/seg/pants',
            contentType: 'application/json; charset=utf-8',
            data: function (data) { return data = JSON.stringify(data); }
        },
        language: DTlang,
        columns: [
            { name: "id", sorting: false, searchable: false, visible: false },
            { name: "icono", sorting: false, searchable: false },
            { name: "nombre" },
            { name: "menu", searchable: false },
            { name: "orden" },
            { name: "permiso", searchable: false },
            { name: "activo", sorting: false, searchable: false }
        ],
        order: [[ 4, "asc" ]],
        select: true,
        //"paging":   false,
        //"ordering": false,
        //"info":     false,
        //"scrollX":  false,
        //"searching": false,
        //"dom": 'Bfrtip',
        cache: false,
    });
    $('#adduser').on('shown.bs.modal', function () {
        $('#l0').focus();
    });
    $('#addgroup').on('shown.bs.modal', function () {
        $('#g0').focus();
    });
    // Llamado al pedir nuevo menu
    $("#popup-modal").on("shown.bs.modal", function () {
        $("#popup-modal .modal-content").html('');
        var btnact = $("#popup-modal").attr('data-action');
        if (typeof btnact == typeof undefined || btnact == false) {
            return false;
        }
        $("#popup-modal").removeAttr('data-action');
        var dtm =  $('#menustable').DataTable();
        var dtp =  $('#pantstable').DataTable();
        var action = "";
        var ids = [];
        var srows = [];
        // Busco en el listado correcto
        if (dtm.rows( { selected: true } ).count() != 0) {
            action = '/seg/menus/';
            srows = dtm.rows( { selected: true } );
            for(var i=0; i<srows.count(); i++) {
                ids.push(srows.data()[i][0]);
            }
        } else if (dtp.rows( { selected: true } ).count() != 0) {
            action = '/seg/pants/';
            srows = dtp.rows( { selected: true } );
            for(var i=0; i<srows.count(); i++) {
                ids.push(srows.data()[i][0]);
            }
        }
        if (btnact == 'add-menu') { action  = '/seg/menus/create/'; }
        if (btnact == 'add-pant') { action  = '/seg/pants/create/'; }
        if (btnact == 'edit')     { action += 'update/'; }
        if (btnact == 'delete')   { action += 'delete/'; }
        if ((btnact == 'edit' || btnact == 'delete') && ids.length >0 ) { action += ids.join(); }
        $.ajax({
            url: action,
            type: 'GET',
            dataType: 'json',
            success: function (data) {
                $("#popup-modal .modal-content").html(data.html_form);
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
                    $('#b_menus_edit').hide();
                    $('#b_menus_delete').hide();
                    $("#popup-modal").modal('hide');
                    $("#popup-modal .modal-content").html('');
                    $('#menustable').DataTable().ajax.reload();
                    $('#pantstable').DataTable().ajax.reload();
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
                    $('#b_menus_edit').hide();
                    $('#b_menus_delete').hide();
                    $('#menustable').DataTable().ajax.reload();
                    $('#pantstable').DataTable().ajax.reload();
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
