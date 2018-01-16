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
        cache: false,
    });
});
