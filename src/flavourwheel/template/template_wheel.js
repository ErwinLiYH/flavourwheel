var chartDom = document.getElementById('main');
var myChart = echarts.init(chartDom, null);
var option;

var js_data = JSON.parse(text);
var data = js_data.data

option = {
    textStyle: {
      fontFamily: "Times New Roman"
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
  series: {
    type: 'sunburst',
    data: data,
    radius: [0, '95%'],
    sort: undefined,
    emphasis: {
      focus: 'ancestor'
    },
    levels: [
      {},
      {
        r0: '10%',
        r: '45%',
        itemStyle: {
          borderWidth: 2
        },
        label: {
          rotate: 'radial',
          align: 'right',
          fontSize: 40
        }
      },
      {
        r0: '45%',
        r: '70%',
        label: {
          align: 'right',
          fontSize: 48
        }
      },
      {
        r0: '70%',
        r: '72%',
        label: {
          position: 'outside',
          padding: 3,
          silent: false,
          fontSize: 56
        },
        itemStyle: {
          borderWidth: 3
        }
      }
    ]
  }
};

myChart.setOption(option);

