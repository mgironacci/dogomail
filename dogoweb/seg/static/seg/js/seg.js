var jseg = {};

$(function(){
    $('#b_menus_edit').hide();
    $('#b_menus_delete').hide();
    $('#b_users_edit').hide();
    $('#b_users_delete').hide();

    var clickDTug = function (et, e, dt, indexes) {
        var dtu =  $('#userstable').DataTable();
        var dtg =  $('#groupstable').DataTable();
        var dts =  $('#permstable').DataTable();
        var dtuc = dtu.rows({selected:true}).count();
        var dtgc = dtg.rows({selected:true}).count();
        var dtsc = dts.rows({selected:true}).count();
        var evento = et.split(".")[0];
        var tabla = et.split(".")[1];
        if (tabla == 'user' && dtuc != 0 && ( dtgc != 0 || dtsc != 0 ) ) {
            dtg.rows().deselect();
            dts.rows().deselect();
        } else if (tabla == 'group' && dtgc != 0 && ( dtuc != 0 || dtsc != 0 ) ) {
            dtu.rows().deselect();
            dts.rows().deselect();
        } else if (tabla == 'perm' && dtsc != 0 && ( dtuc != 0 || dtgc != 0 ) ) {
            dtu.rows().deselect();
            dtg.rows().deselect();
        }
        if (evento == 'select') {
            if (dt.rows( { selected: true } ).count() != 0) {
                $('#b_users_edit').show();
                if ( tabla != 'perm' ) {
                    $('#b_users_delete').show();
                }
            }
        } else if (evento == 'deselect') {
            if (dt.rows( { selected: true } ).count() == 0) {
                $('#b_users_edit').hide();
                $('#b_users_delete').hide();
            }
        }
    }

    var clickDTmp = function (et, e, dt, indexes) {
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

    var hideUGP = function () {
        var dtu =  $('#userstable').DataTable();
        var dtg =  $('#groupstable').DataTable();
        var dtp =  $('#permstable').DataTable();
        if (dtu.rows( { selected: true } ).count() == 0 && dtg.rows( { selected: true } ).count() == 0 && dtp.rows( { selected: true } ).count() == 0) {
            $('#b_users_edit').hide();
            $('#b_users_delete').hide();
        }
    }

    var hideMP = function () {
        var dtm =  $('#menustable').DataTable();
        var dtp =  $('#pantstable').DataTable();
        if (dtm.rows( { selected: true } ).count() == 0 && dtp.rows( { selected: true } ).count() == 0) {
            $('#b_menus_edit').hide();
            $('#b_menus_delete').hide();
        }
    }

    $('#userstable')
    .on('select.dt', function ( e, dt, type, indexes ) { clickDTug('select.user', e, dt, indexes); } )
    .on('deselect.dt', function ( e, dt, type, indexes ) { clickDTug('deselect.user', e, dt, indexes); } )
    .DataTable({
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
            { name: "id", orderable: false, searchable: false, visible: false },
            { name: "username" },
            { name: "last_name" },
            { name: "check+is_active", orderable: false, searchable: false }
        ],
        order: [[ 0, "asc" ]],
        select: 'single',
        drawCallback: function( settings ) {
            hideUGP();
        },
        //"paging":   false,
        //"ordering": false,
        //"info":     false,
        //"scrollX":  false,
        //"searching": false,
        //"dom": 'Bfrtip',
        cache: false,
    });
    $('#groupstable')
    .on('select.dt', function ( e, dt, type, indexes ) { clickDTug('select.group', e, dt, indexes); } )
    .on('deselect.dt', function ( e, dt, type, indexes ) { clickDTug('deselect.group', e, dt, indexes); } )
    .DataTable({
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
            { name: "id", orderable: false, searchable: false, visible: false },
            { name: "name" },
            { name: "count+user_set", searchable: false },
            { name: "count+permissions", searchable: false }
        ],
        order: [[ 0, "asc" ]],
        select: true,
        drawCallback: function( settings ) {
            hideUGP();
        },
        //"paging":   false,
        //"ordering": false,
        //"info":     false,
        //"scrollX":  false,
        //"searching": false,
        //"dom": 'Bfrtip',
        cache: false,
    });
    $('#permstable')
    .on('select.dt', function ( e, dt, type, indexes ) { clickDTug('select.perm', e, dt, indexes); } )
    .on('deselect.dt', function ( e, dt, type, indexes ) { clickDTug('deselect.perm', e, dt, indexes); } )
    .DataTable({
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
            { name: "id", orderable: false, searchable: false, visible: false },
            { name: "name" },
            { name: "fk+content_type+model" },
            { name: "count+group_set", searchable: false }
        ],
        order: [[ 0, "asc" ]],
        select: true,
        drawCallback: function( settings ) {
            hideUGP();
        },
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
    .on('select.dt', function ( e, dt, type, indexes ) { clickDTmp('select.menu', e, dt, indexes); } )
    .on('deselect.dt', function ( e, dt, type, indexes ) { clickDTmp('deselect.menu', e, dt, indexes); } )
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
            { name: "id", orderable: false, searchable: false },
            { name: "ico+icono", searchable: false, orderable: false },
            { name: "nombre" },
            { name: "orden" },
            { name: "check+activo", searchable: false, orderable: false }
        ],
        order: [[ 3, "asc" ]],
        select: true,
        rowReorder: true,
        drawCallback: function( settings ) {
            hideMP();
        },
        //"paging":   false,
        //"info":     false,
        //"scrollX":  false,
        //"searching": false,
        //"dom": 'Bfrtip',
        cache: false,
    });
    $('#pantstable')
    .on('select.dt', function ( e, dt, type, indexes ) { clickDTmp('select.pant', e, dt, indexes); } )
    .on('deselect.dt', function ( e, dt, type, indexes ) { clickDTmp('deselect.pant', e, dt, indexes); } )
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
            { name: "id", orderable: false, searchable: false, visible: false },
            { name: "ico+icono", orderable: false, searchable: false },
            { name: "nombre" },
            { name: "fk+menu+nombre" },
            { name: "orden" },
            { name: "perm+permiso" },
            { name: "check+activo", orderable: false, searchable: false }
        ],
        order: [[ 4, "asc" ]],
        select: true,
        drawCallback: function( settings ) {
            hideMP();
        },
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
        var dtu =  $('#userstable').DataTable();
        var dtg =  $('#groupstable').DataTable();
        var dts =  $('#permstable').DataTable();
        var dtm =  $('#menustable').DataTable();
        var dtp =  $('#pantstable').DataTable();
        var action = "";
        var ids = [];
        var srows = [];
        if (btnact == 'add-user') { action  = '/seg/users/create/'; }
        if (btnact == 'add-group') { action  = '/seg/groups/create/'; }
        if (btnact == 'add-menu') { action  = '/seg/menus/create/'; }
        if (btnact == 'add-pant') { action  = '/seg/pants/create/'; }
        // Busco en el listado correcto si es edit o delete
        if (btnact == 'edit' || btnact == 'delete' ) {
            if (btnpan == 'menu') {
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
            }
            if (btnpan == 'user') {
                if (dtu.rows( { selected: true } ).count() != 0) {
                    action = '/seg/users/';
                    srows = dtu.rows( { selected: true } );
                    for(var i=0; i<srows.count(); i++) {
                        ids.push(srows.data()[i][0]);
                    }
                } else if (dtg.rows( { selected: true } ).count() != 0) {
                    action = '/seg/groups/';
                    srows = dtg.rows( { selected: true } );
                    for(var i=0; i<srows.count(); i++) {
                        ids.push(srows.data()[i][0]);
                    }
                } else if (dts.rows( { selected: true } ).count() != 0) {
                    action = '/seg/perms/';
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
                    if (data.panel == 'menu') {
                        $('#b_menus_edit').hide();
                        $('#b_menus_delete').hide();
                        $('#menustable').DataTable().ajax.reload();
                        $('#pantstable').DataTable().ajax.reload();
                    }
                    if (data.panel == 'user') {
                        $('#b_users_edit').hide();
                        $('#b_users_delete').hide();
                        $('#userstable').DataTable().ajax.reload();
                        $('#groupstable').DataTable().ajax.reload();
                        $('#permstable').DataTable().ajax.reload();
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
                    if (data.panel == 'menu') {
                        $('#menustable').DataTable().ajax.reload();
                        $('#pantstable').DataTable().ajax.reload();
                    }
                    if (data.panel == 'user') {
                        $('#userstable').DataTable().ajax.reload();
                        $('#groupstable').DataTable().ajax.reload();
                        $('#permstable').DataTable().ajax.reload();
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
