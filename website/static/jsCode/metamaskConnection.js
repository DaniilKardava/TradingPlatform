import { pieChart, pieChartData, pieChartOptions } from "./pieChartJS.js";
import { areaSeries } from "./historicalPerformanceChart.js";

var assetName = document.getElementById("metamaskConnection").getAttribute("assetName");

// MM connection
const walletConnectButton = document.getElementById("walletConnect");



async function getConnectedAccount() {
    const web3 = new Web3(window.ethereum);
    const connectedAccounts = await web3.eth.getAccounts();
    const userAddress = connectedAccounts[0];
    if (connectedAccounts.length != 0){

        console.log("connected account");

        walletConnectButton.innerText  = "Wallet Connected";
        walletConnectButton.disabled = true;
        
        // Also set the value inside the hidden input form for orders to the current address:
        document.getElementById("userAddress").setAttribute("value", userAddress);
        // Fetch account info and update values on the page
        const response = await fetch(`/get-user-info?wallet_address=${userAddress}`);
        const result = await response.json();

        console.log(result);

        // Set buying power to cash balance
        var cashAmount = result.cash;
        document.getElementById("buyingPower").innerHTML += ` $${cashAmount.toLocaleString()}`;
        // Load assets owned
        var assetsOwned = JSON.parse(result.assetsOwned);

        try{
            document.getElementById("qtyOwned").innerHTML += ` ${assetsOwned[assetName][0]}`;
            if (assetsOwned[assetName][0] == 0){
                document.getElementById("avgCost").innerHTML += ` $-`;
            } else {
                document.getElementById("avgCost").innerHTML += ` $${(assetsOwned[assetName][1] / assetsOwned[assetName][0]).toLocaleString()}`;
            }
            
        } catch {
            document.getElementById("qtyOwned").innerHTML += ` 0`;
            document.getElementById("avgCost").innerHTML += ` $-`;
        }

        
        // Create pie chart with current holdings
        var dataList = [["Asset", "Dollar Value"], ["Cash", cashAmount]]
        var totalPortfolioValue = 0;

        for (var key in assetsOwned) {
            if (assetsOwned[key][0] != 0){
                // Get data for asset:
                var url = `https://api.pro.coinbase.com/products/${key}-USD/ticker`;
                const pieChartPriceResponse = await fetch(url);
                const pieChartPriceResult = await pieChartPriceResponse.json();
                var assetPrice = pieChartPriceResult["price"];
                // I am also going to calculate total portfolio value here
                // Multiple the asset amount by the asset price
                if (assetsOwned[key][0] > 0){
                    dataList.push([key, (assetsOwned[key][0] * assetPrice)]);
                    totalPortfolioValue += assetsOwned[key][0] * assetPrice;

                } else {
                    var shortPositionValue = (2 * assetsOwned[key][1] / assetsOwned[key][0] - assetPrice) * abs(assetsOwned[key][0]);
                    if (shortPositionValue < 0){
                        dataList.push([key+" (Short, Debt)", (Math.abs(shortPositionValue))]);
                    } else {
                        dataList.push([key+" (Short)", (Math.abs(shortPositionValue))]);
                    }
                    
                    totalPortfolioValue += shortPositionValue;
                }
            }
            
        }

        var colors = chroma.scale(['#60DBE1', '#6097E1', '#60DBE1', '#6097E1']).colors(dataList.length - 1);
        
        var data = google.visualization.arrayToDataTable(dataList);
        var options = {backgroundColor: {fill:"transparent", color:"#000000"}, legend: "none", responsive: true, colors: colors, pieSliceTextStyle: {color:"#000000", fontSize:20}};

        var formatter = new google.visualization.NumberFormat(
            {prefix: '$'});
        formatter.format(data,1); // Apply formatter to second column

        pieChart.draw(data, options); 

        $(window).resize(() => {
            pieChart.draw(data, options);
        });

        // Load trade log
        console.log(result.tradeLog)
        var tradeHistory = JSON.parse(result.tradeLog);
        var logTable = document.getElementById("tradeLogTable");

        var rowsToDisplay = Math.min(tradeHistory.length, 15);

        var color;
        for (var a = 1; a < rowsToDisplay + 1; a++){
            var newRow = logTable.insertRow(-1);
            var tradeTransaction = tradeHistory[tradeHistory.length - a];

            if ( tradeTransaction[1] == "Buy") {
                color = "rgba(0,255,0,.5)";
            } else {
                color = "rgba(255, 0, 0,.5)";
            }
            newRow.style.background = (color);
            for (var i = 0; i < 5; i++){
                var tempCell = newRow.insertCell(i);
                if (i == 0){
                    var date = new Date(tradeTransaction[i] * 1000);
                    tempCell.innerHTML = date.toLocaleString();
                } else if (i == 3) {
                    tempCell.innerHTML = tradeTransaction[i].toFixed(3);
                } else if (i == 4){
                    tempCell.innerHTML = `$${tradeTransaction[i]}`;
                } else {
                    tempCell.innerHTML = tradeTransaction[i];
                }
            }
        }

        // Load historical performance
        var performanceHistory = JSON.parse(result.accountPerformance);
        // Update portfolio performance every day
        var currentTimeStamp = new Date();
        if (performanceHistory[performanceHistory.length - 1]["time"] < currentTimeStamp.getTime() / 1000 - 86400) {
            performanceHistory.push({time:currentTimeStamp.getTime()/ 1000, value:totalPortfolioValue});
        }
        areaSeries.setData(performanceHistory);        

    } else {
        
        // Draw the default chart if no account is connected
        $(window).resize(() => {
            pieChart.draw(pieChartData, pieChartOptions);
        });
    }
}

// If the browser cant make the api call to metamask because it is not installed, reload the chart with default data
try {
    const getConnectedAccountResult = await getConnectedAccount();
    console.log(getConnectedAccountResult);
} catch(error) {
    console.log(error);
    // Draw the default chart if metamask is not installed
    $(window).resize(() => {
        pieChart.draw(pieChartData, pieChartOptions);
    });
}

walletConnectButton.addEventListener("click", async () => {

    var flashMessage = document.getElementById("modal");
    var flashMessageContent = document.getElementById("modalMessage");

    if (typeof window.ethereum !== "undefined") {
        // Request access to the user's Ethereum accounts
        try {
            await window.ethereum.send("eth_requestAccounts");
            walletConnectButton.innerText  = "Wallet Connected";
            walletConnectButton.disabled = true;
        } catch (error) {
            console.error(error);
            if (error.code == -32002) {}
                flashMessageContent.style.background =  "rgba(255,0,0,.8)";
                flashMessageContent.innerHTML = "Metamask connection already pending approval. <button onclick= 'dismissModalAlert()' style='background-color: rgba(0,0,0,0); border: 0px; color:white; position:absolute; right: 5vw;'>&times;</button>";
                flashMessage.style.display = "block";
            return;
        }
    
        // Create a Web3 object
        const web3 = new Web3(window.ethereum);
    
        // Get the user's Ethereum address
        const accounts = await web3.eth.getAccounts();
        const userAddress = accounts[0];
        
        // Click disabled after connection, for new connection check if new sql entry is needed:
        const response = await fetch(`/check-user?wallet_address=${userAddress}`);
        // response : {exists:true/false}
        const result = await response.json();
        if (result.exists) {
            location.reload();
        } else {
            // Create user
            const cashAmount = 100000
            const assetsOwned = {};
            const transactionsMade = [];
            const dateCreated = Math.floor(Date.now() / 1000);
            const portfolioHistory = [{time:dateCreated, value:cashAmount}];

            const response = await fetch(`/add-user?wallet_address=${userAddress}&cashAmount=${cashAmount}&assetsOwned=${JSON.stringify(assetsOwned)}&transactionsMade=${JSON.stringify(transactionsMade)}&portfolioHistory=${JSON.stringify(portfolioHistory)}&dateCreated=${dateCreated}`);
            // response : {success: true/false}
            const result = await response.json();

            if (result.success) {
                flashMessageContent.style.background =  "rgba(0,255,0,.5)";
                flashMessageContent.innerHTML = "Wallet successfully connected. <button onclick= 'dismissModalAlert()' style='background-color: rgba(0,0,0,0); border: 0px; color:white; position:absolute; right: 5vw;'>&times;</button>";
                flashMessage.style.display = "block";

                window.location.replace('/tradeStation');

            } else {
                flashMessageContent.style.background =  "rgba(255,0,0,.8)";
                flashMessageContent.innerHTML = "Failed to add user. Contact us for assistance. <button onclick= 'dismissModalAlert()' style='background-color: rgba(0,0,0,0); border: 0px; color:white; position:absolute; right: 5vw;'>&times;</button>";
                flashMessage.style.display = "block";
            }
        }

    } else {
        flashMessageContent.style.background =  "rgba(255,0,0,.8)";
        flashMessageContent.innerHTML = "Metamask browser extension not installed. <button onclick= 'dismissModalAlert()' style='background-color: rgba(0,0,0,0); border: 0px; color:white; position:absolute; right: 5vw;'>&times;</button>";
        flashMessage.style.display = "block";
    }
    
});

