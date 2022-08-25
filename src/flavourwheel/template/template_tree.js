var chartDom = document.getElementById('main');
var myChart = echarts.init(chartDom, null);
var option;

var js_data = JSON.parse(text);
var data_temp = js_data.data

var data = {"name":"ROOT", "children":data_temp}

var option = {
    textStyle: {
        fontFamily: "Times New Roman"
      },
    tooltip: {
    trigger: 'item',
    triggerOn: 'mousemove'
    },
    toolbox: {
        show: true,
        feature: {
            saveAsImage: {
            show:true,
            type: 'png',
            backgroundColor:'#ffffff',
            name:'result',
            pixelRatio:1
            }
        },
        itemSize:200
    },
    series: [
    {
        type: 'tree',
        data: [data],
        top: "2%",
        left: "8%",
        bottom: "2%",
        right: "15%",
        symbolSize: 25,
        label: {
        position: 'left',
        verticalAlign: 'middle',
        align: 'right',
        fontSize: 35
        },
        leaves: {
        label: {
            position: 'right',
            verticalAlign: 'middle',
            align: 'left'
        }
        },
        emphasis: {
        focus: 'descendant'
        },
        expandAndCollapse: false,
        animationDuration: 550,
        animationDurationUpdate: 750
    }
    ]
}

myChart.setOption(option);