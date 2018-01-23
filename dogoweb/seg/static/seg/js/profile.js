$(function(){
    $('#accesstable').DataTable({
        responsive: true,
        serverSide: true,
        ajax: {
            type: "POST",
            url: '/seg/accesos',
            contentType: 'application/json; charset=utf-8',
            data: function (data) { return data = JSON.stringify(data); }
        },
        language: DTlang,
        columns: [
            { name: "login_time", searchable: false },
            { name: "logout_time", searchable: false },
            { name: "host", className: "hidden-xs-down" },
            { name: "provider", className: "hidden-lg-down" },
            { name: "country", className: "hidden-md-down" }
        ],
        //"paging":   false,
        //"ordering": false,
        //"info":     false,
        //"scrollX":  false,
        //"searching": false,
        //"dom": 'Bfrtip',
        cache: false
    });
    $('#audittable').DataTable({
        responsive: true,
        serverSide: true,
        ajax: {
            type: "POST",
            url: '/seg/auditoria',
            contentType: 'application/json; charset=utf-8',
            data: function (data) { return data = JSON.stringify(data); }
        },
        language: DTlang,
        columns: [
            { name: "action_time" },
            { name: "action_flag" },
            { name: "object_repr" }
        ],
        //"paging":   false,
        //"ordering": false,
        //"info":     false,
        //"scrollX":  false,
        //"searching": false,
        //"dom": 'Bfrtip',
        cache: false
    });
});
