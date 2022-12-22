// Google Pie Chart, wasnt loading correctly outside of this file for some reason
var pieChart;
var pieChartData;
var pieChartOptions;

// Load google charts
google.charts.load('current', {'packages':['corechart']});
google.charts.setOnLoadCallback(drawChart);

// Draw the chart and set the chart values
function drawChart() {
    pieChartData = google.visualization.arrayToDataTable([
        ['Asset', 'Dollar Value'],
        ["Cash", 100000],
    ]);
    

    // Optional; add a title and set the width and height of the chart
    pieChartOptions = {backgroundColor: {fill:"transparent", color:"#000000"}, legend: "none", responsive: true, colors: ["#60DBE1"], pieSliceTextStyle: {color:"#000000", fontSize:20}, vAxis: {
        format: '$#,##0',  // adds a dollar sign before the number
      },};
    
    var formatter = new google.visualization.NumberFormat(
        {prefix: '$'});
    formatter.format(pieChartData,1); // Apply formatter to second column

    // Display the chart inside the <div> element with id="piechart"
    pieChart = new google.visualization.PieChart(document.getElementById('piechart'));
    pieChart.draw(pieChartData, pieChartOptions);
}


    

export { pieChart, pieChartData, pieChartOptions};