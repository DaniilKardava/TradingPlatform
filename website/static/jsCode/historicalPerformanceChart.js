const chart = LightweightCharts.createChart(document.getElementById("histChart"),{    
    crosshair: {
        mode: LightweightCharts.CrosshairMode.Normal
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

const areaSeries = chart.addAreaSeries();


// This will be a fetch calculating historic PnL of the trader based on their trade history

try{
    (async () => {
        const web3 = new Web3(window.ethereum);
        const connectedAccounts = await web3.eth.getAccounts();
        if (connectedAccounts == 0) {
            chart.applyOptions({watermark:{text:"Please Connect to MetaMask",fontSize: 240,
            color: "rgba(255, 255, 255, .1)",
            visible: true,
            fontFamily: "'Times New Roman', Times, serif"}});
        } 
    })();
} catch {
    chart.applyOptions({watermark:{text:"Please Install MetaMask", fontSize: 240,
    color: "rgba(255, 255, 255, .1)",
    visible: true,
    fontFamily: "'Times New Roman', Times, serif"}});
}

new ResizeObserver(entries => {
    if (entries.length === 0 || entries[0].target !== histChart) { return; }
    const newRect = entries[0].contentRect;
    chart.applyOptions({ height: newRect.height, width: newRect.width });
  }).observe(histChart);

chart.timeScale().fitContent();


export {areaSeries};