var jsobj = {};

$( document ).ready(function() {

    Highcharts.setOptions({
        global: {
            useUTC: false
            //timezoneOffset: 3 * 60
            //timezone: 'America/Argentina/Cordoba'
        }
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
    }
    reloadT();
    jsobj.reloadT = reloadT;

}); 