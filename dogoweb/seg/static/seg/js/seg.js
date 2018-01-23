$(function(){
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
        //"paging":   false,
        //"ordering": false,
        //"info":     false,
        //"scrollX":  false,
        //"searching": false,
        //"dom": 'Bfrtip',
        cache: false,
    });
    $('#menustable').DataTable({
        responsive: true,
        serverSide: true,
        ajax: {
            type: "POST",
            url: '/seg/menus',
            contentType: 'application/json; charset=utf-8',
            data: function (data) { return data = JSON.stringify(data); }
        },
        language: DTlang,
        columns: [
            { name: "icono", sorting: false, searchable: false },
            { name: "nombre" },
            { name: "orden" },
            { name: "activo", sorting: false, searchable: false }
        ],
        order: [[ 2, "asc" ]],
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
            { name: "icono", sorting: false, searchable: false },
            { name: "nombre" },
            { name: "menu", searchable: false },
            { name: "orden" },
            { name: "permiso", searchable: false },
            { name: "activo", sorting: false, searchable: false }
        ],
        order: [[ 3, "asc" ]],
        //"paging":   false,
        //"ordering": false,
        //"info":     false,
        //"scrollX":  false,
        //"searching": false,
        //"dom": 'Bfrtip',
        cache: false,
    });
    $('#contrtable').DataTable({
        responsive: true,
        serverSide: true,
        ajax: {
            type: "POST",
            url: '/seg/controls',
            contentType: 'application/json; charset=utf-8',
            data: function (data) { return data = JSON.stringify(data); }
        },
        language: DTlang,
        columns: [
            { name: "nombre" },
            { name: "permiso", searchable: false },
            { name: "activo", sorting: false, searchable: false }
        ],
        order: [[ 0, "asc" ]],
        //"paging":   false,
        //"ordering": false,
        //"info":     false,
        //"scrollX":  false,
        //"searching": false,
        //"dom": 'Bfrtip',
        cache: false,
    });
});