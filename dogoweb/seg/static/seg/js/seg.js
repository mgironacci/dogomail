var jseg = {};

$(function(){
    $('#b_menus_edit').hide();
    $('#b_menus_delete').hide();

    var clickDT = function (evento, e, dt, indexes) {
        if (evento == 'select.menu') {
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
    $('#menustable')
    .on('select.dt', function ( e, dt, type, indexes ) { clickDT('select.menu', e, dt, indexes); } )
    .on('deselect.dt', function ( e, dt, type, indexes ) { clickDT('deselect', e, dt, indexes); } )
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
    $('#pantstable').DataTable({
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
        select: 'multi',
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
    $("#menu-modal").on("shown.bs.modal", function () {
        $("#menu-modal .modal-content").html('');
        var btnact = $("#menu-modal").attr('data-action');
        if (typeof btnact == typeof undefined || btnact == false) {
            return false;
        }
        $("#menu-modal").removeAttr('data-action');
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
            srows = dtm.rows( { selected: true } );
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
                $("#menu-modal .modal-content").html(data.html_form);
            }
        });
    });
    // Llamado al darle submit
    $("#menu-modal").on("submit", function () {
        var form = $('#menu-form');
        $.ajax({
            url: form.attr("action"),
            data: form.serialize(),
            type: 'POST',
            dataType: 'json',
            success: function (data) {
                if (data.form_is_valid) {
                    $('#b_menus_edit').hide();
                    $('#b_menus_delete').hide();
                    $("#menu-modal").modal('hide');
                    $("#menu-modal .modal-content").html('');
                    $('#menustable').DataTable().ajax.reload();
                    $('#pantstable').DataTable().ajax.reload();
                }
                else {
                    $("#menu-modal .modal-content").html(data.html_form);
                }
            }
        });
        return false;
    });

    var saltaEdit = function (npk) {
        var form = $('#menu-form');
        var action = form.attr("action")+npk;
        $.ajax({
            url: action,
            type: 'GET',
            dataType: 'json',
            success: function (data) {
                $("#menu-modal .modal-content").html(data.html_form);
            }
        });
    }

    var salvaNext = function (npk) {
        var form = $('#menu-form');
        $('#snext').val(npk);
        $.ajax({
            url: form.attr("action"),
            data: form.serialize(),
            type: 'POST',
            dataType: 'json',
            success: function (data) {
                if (data.form_is_valid) {
                    $('#menustable').DataTable().ajax.reload();
                    $('#pantstable').DataTable().ajax.reload();
                    if (data.snext == 'new') {
                        $("#menu-modal .modal-content").html('');
                    } else if (data.snext != '') {
                        saltaEdit(data.snext);
                        return;
                    } else {
                        $("#menu-modal").modal('hide');
                        $("#menu-modal .modal-content").html('');
                        return;
                    }
                }
                $("#menu-modal .modal-content").html(data.html_form);
            }
        });
    }

    jseg.saltaEdit = saltaEdit;
    jseg.salvaNext = salvaNext;
});
