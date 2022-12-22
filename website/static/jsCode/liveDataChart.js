var assetName = document.getElementById("liveDataChartScript").getAttribute("assetName");
var timeFrame = document.getElementById("timeframeButtons").getAttribute("currentTimeFrame")

const chart = LightweightCharts.createChart(document.getElementById("liveChart"),{    
    crosshair: {
        mode: LightweightCharts.CrosshairMode.Normal
      },
    watermark:{
        text: assetName,
        fontSize: 240,
        color: "rgba(255, 255, 255, .1)",
        visible: true,
        fontFamily: "'Times New Roman', Times, serif"
    },
    layout: {
        background: {
            type: "Solid",
            color: "#000000",   
        },
        textColor: "#FFFFFF"
    },
    grid: {
        vertLines: {
            visible: false,
        },
        horzLines: {
            visible: false,
        }
    },
    
    timeScale: {
        timeVisible: true,
        secondsVisible: true,
    }


    
});


const candlestickSeries = chart.addCandlestickSeries();

// Get historical data with custom timeframe and asset araguments
async function loadCustomData(_granularity, _endDate, _endTimestamp, _totalData) {
    var granularity = _granularity;
    var _startDate = new Date(_endDate.getTime()  - (300 * granularity * 1000));
    var _startTimestamp = Math.floor(_startDate.getTime() / 1000);
        
    for (var i = 0; i < 10; i++){
        var url = `https://api.pro.coinbase.com/products/${assetName}-USD/candles?start=${_startTimestamp}&end=${_endTimestamp}&granularity=${granularity}`;
        var response = await fetch(url);
        var data = await response.json();
        
        if (i == 0){
            _totalData = data;
        } else {
            for (var a = 0; a < data.length; a++){
                _totalData.push(data[a]);
            }  
        }

        _endTimestamp = _startTimestamp;
        _startTimestamp = _endTimestamp - (300 * granularity);
    }

    // Format properly and then reverse:
    for (var a = 0; a < _totalData.length; a ++){
        _totalData[a] = {time:_totalData[a][0], low: _totalData[a][1], high: _totalData[a][2],open: _totalData[a][3],close: _totalData[a][4]}
    }

    return [_totalData.reverse(), granularity];

}

async function getHistoricalData() {

    var currentTime = new Date();
    // Add a minute to catch the most recent data
    var endDate = new Date(currentTime.getTime() + (60 * 1000));
    var endTimestamp = Math.floor(endDate / 1000);
    var totalData;
    var granularity;
    
    // Set the URL for the request
    if (timeFrame == "1mTimeFrame") {

        [totalData, granularity] = await loadCustomData(60, endDate, endTimestamp, totalData);

    } else if (timeFrame == "5mTimeFrame"){

        [totalData, granularity] = await loadCustomData(300, endDate, endTimestamp, totalData);

    } else if (timeFrame == "15mTimeFrame"){

        [totalData, granularity] = await loadCustomData(900, endDate, endTimestamp, totalData);

    } else if (timeFrame == "1hTimeFrame"){

        [totalData, granularity] = await loadCustomData(3600, endDate, endTimestamp, totalData);

    } else if (timeFrame == "6hTimeFrame"){

        [totalData, granularity] = await loadCustomData(21600, endDate, endTimestamp, totalData);

    } else if (timeFrame == "1dTimeFrame"){

        [totalData, granularity] = await loadCustomData(86400, endDate, endTimestamp, totalData);

    }

    candlestickSeries.setData(totalData);
    var recentCandleData  = [];
    // Recent candles are built from scratch, historic data isnt fast enough. Order is very specific here:
    recentCandleData.push(totalData[totalData.length - 1]["open"]); // open
    recentCandleData.push(totalData[totalData.length - 1]["high"]); // low
    recentCandleData.push(totalData[totalData.length - 1]["low"]); // high
    recentCandleData.push(totalData[totalData.length - 1]["close"]); // close
    var recentTimestamp = totalData[totalData.length - 1]["time"];

    return [granularity, recentCandleData, recentTimestamp];
}
  

async function updateData(granularity, recentCandleData, previousTimestamp) {
    var url = `https://api.pro.coinbase.com/products/${assetName}-USD/ticker`;
    var response = await fetch(url);
    var data = await response.json();

    var isoString = data["time"];
    var currentTime = new Date(isoString).getTime();
    var currentTimestamp = Math.floor(currentTime / 1000);

    // Round error?
    var interval = granularity;
    var roundedTimestamp = Math.floor(currentTimestamp / interval) * interval;


    if (roundedTimestamp != previousTimestamp) {
        recentCandleData = [];
    }

    recentCandleData.push(data["price"]);

    var max = -Infinity;
    var min = Infinity;

    for (var i = 0; i < recentCandleData.length; i++) {
        if (recentCandleData[i] > max) {
            max = recentCandleData[i];
        }
        if (recentCandleData[i] < min) {
            min = recentCandleData[i];
          }
    }
    
    closePrice = recentCandleData[recentCandleData.length - 1];
    openPrice = recentCandleData[0];
    
    const bar = {time:roundedTimestamp, low: min, high: max, open: openPrice, close: closePrice}
    candlestickSeries.update(bar);

    return [recentCandleData, roundedTimestamp];
}



async function streamChart(){
    var granularity;
    var recentCandleData;
    var previousTimestamp;
    
    [granularity, recentCandleData, previousTimestamp] = await getHistoricalData();

    setInterval(async () => {
        [recentCandleData, previousTimestamp] = await updateData(granularity, recentCandleData, previousTimestamp);
    },150)
}

try{
    (async () => {
        const web3 = new Web3(window.ethereum);
        const connectedAccounts = await web3.eth.getAccounts();
        if (connectedAccounts != 0) {
            streamChart();
        } else {
            chart.applyOptions({watermark:{text:"Please Connect to MetaMask"}});
        }
    })();
} catch {
    chart.applyOptions({watermark:{text:"Please Install MetaMask"}});
}
    

    


new ResizeObserver(entries => {
    if (entries.length === 0 || entries[0].target !== liveChart) { return; }
    const newRect = entries[0].contentRect;
    chart.applyOptions({ height: newRect.height, width: newRect.width });
  }).observe(liveChart);

chart.timeScale().fitContent();

