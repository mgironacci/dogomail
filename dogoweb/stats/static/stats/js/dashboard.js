var jsobj = {};

$( document ).ready(function() {

    Highcharts.setOptions({
        global: {
            useUTC: false
            //timezoneOffset: 3 * 60
            //timezone: 'America/Argentina/Cordoba'
        }
    });

    $('#topsender-table')
    .DataTable({
        responsive: false,
        serverSide: true,
        ajax: {
            type: "POST",
            url: '/stats/dogo/tops/',
            contentType: 'application/json; charset=utf-8',
            data: function ( d ) {
                var ahora = new Date();
                var aayer = new Date();
                aayer.setDate(aayer.getDate() - 1);
                var PPGh = getFullDate(ahora)+' '+getSimpleTime(ahora)+' '+getTZ();
                var PPGd = getFullDate(aayer)+' '+getSimpleTime(aayer)+' '+getTZ();
                var PPGi = '1d';
                d['desde'] = PPGd;
                d['hasta'] = PPGh;
                d['intervalo'] = PPGi;
                //console.log(d);
                return JSON.stringify(d);
            }
        },
        language: DTlang,
        columns: [
            { name: "sender" },
            { name: "total" },
            { name: "delivered" },
            { name: "rejected" },
        ],
        order: [[ 1, "desc" ]],
        columnDefs: [
            { width: "60%", "targets": 0 },
            { width: "10%", "targets": 1 },
            { width: "10%", "targets": 2 },
            { width: "10%", "targets": 3 },
        ],
        dom: "t",
        select: false,
        searching: false,
        paging: false,
        cache: false,
    });

    $('#toprecipient-table')
    .DataTable({
        responsive: false,
        serverSide: true,
        ajax: {
            type: "POST",
            url: '/stats/dogo/topr/',
            contentType: 'application/json; charset=utf-8',
            data: function ( d ) {
                var ahora = new Date();
                var aayer = new Date();
                aayer.setDate(aayer.getDate() - 1);
                var PPGh = getFullDate(ahora)+' '+getSimpleTime(ahora)+' '+getTZ();
                var PPGd = getFullDate(aayer)+' '+getSimpleTime(aayer)+' '+getTZ();
                var PPGi = '1d';
                d['desde'] = PPGd;
                d['hasta'] = PPGh;
                d['intervalo'] = PPGi;
                //console.log(d);
                return JSON.stringify(d);
            }
        },
        language: DTlang,
        columns: [
            { name: "recipient" },
            { name: "total" },
            { name: "delivered" },
            { name: "rejected" },
        ],
        order: [[ 1, "desc" ]],
        columnDefs: [
            { width: "60%", "targets": 0 },
            { width: "10%", "targets": 1 },
            { width: "10%", "targets": 2 },
            { width: "10%", "targets": 3 },
        ],
        dom: "t",
        select: false,
        searching: false,
        paging: false,
        cache: false,
    });

    var reloadT = function () {
        var ahora = new Date();
        var aayer = new Date();
        aayer.setDate(aayer.getDate() - 1);
        var PPGh = getFullDate(ahora)+' '+getSimpleTime(ahora)+' '+getTZ();
        var PPGd = getFullDate(aayer)+' '+getSimpleTime(aayer)+' '+getTZ();
        var PPGi = '1d';
        for ( g in rgrafs ) {
            var gg = rgrafs[g].split('-');
            $.post("/stats/dogo/grafs/", JSON.stringify({ grafico: rgrafs[g], desde: PPGd, hasta: PPGh, intervalo: PPGi }), function(jdatos, jstatus) {
                $(jdatos.migraf).highcharts(jdatos);
            }, "json");
        }
        $('#topsender-table').DataTable().ajax.reload();
        $('#toprecipient-table').DataTable().ajax.reload();
    }
    reloadT();
    jsobj.reloadT = reloadT;

}); 