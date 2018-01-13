function randomIntFromInterval(min,max)
{
    return Math.floor(Math.random()*(max-min+1)+min);
}

$( document ).ready(function() {
    console.log('* JS cargado: /static/stats/js/dashboard.js');

    // ===================
    // Chart de gráfico de internet
    let vals_upload = [];
    let vals_download = [];
    let labels = [];

    for(let i = 0; i < 24; i++) {
        labels.push((i < 10) ? '0'+i : i);
        vals_upload.push({value: randomIntFromInterval(350, 1500), meta: 'kbps', });
        vals_download.push({value: randomIntFromInterval(450, 6000), meta: 'kbps', });
    }

    new Chartist.Line(".chart-internet", {
        labels: labels,
        series: [
            vals_upload,
            vals_download
        ]
    }, {
        showPoint: false, // para no mostrar los puntitos
        showArea: true, // Para que muestre el área abajo de las lineas.
        showLabel: true,
        fullWidth: !0,
        chartPadding: {
            right: 40
        },
        plugins: [
            Chartist.plugins.tooltip(),
        ],
    });
    // ===================
    // Chart de gráfico de tortas de consumo general.new Chart($('#chart-pie-consumos')[0].getContext('2d'), {
    new Chart($('#chart-pie-consumos')[0].getContext('2d'), {
        type: 'pie',
        data: {
            labels: [
                "Web",
                "DNS",
                "Otros"
            ],
            datasets: [
                {
                    data: [40, 25, 35],
                    backgroundColor: [
                        "#FF6384",
                        "#36A2EB",
                        "#FFCE56"
                    ],
                    hoverBackgroundColor: [
                        "#FF6384",
                        "#36A2EB",
                        "#FFCE56"
                    ]
                }]
        },
        options: {
             legend: {
                display: false
             },
             tooltips: {
                enabled: true
             }
        }
    });

    new Chart($('#chart-pie-consumos-apps')[0].getContext('2d'), {
        type: 'pie',
        data: {
            labels: [
                "Netflix",
                "Facebook",
                "Google"
            ],
            datasets: [
                {
                    data: [25, 40, 35],
                    backgroundColor: [
                        "#FF6384",
                        "#36A2EB",
                        "#FFCE56"
                    ],
                    hoverBackgroundColor: [
                        "#FF6384",
                        "#36A2EB",
                        "#FFCE56"
                    ]
                }]
        },
        options: {
             legend: {
                display: false
             },
             tooltips: {
                enabled: true
             }
        }
    });
}); 