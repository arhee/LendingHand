var width = 900;
var height = 500;


d3.select("div#chart")
  .append("svg")
  //.attr("height", height)
  //.attr("width", width);

var data = [];

// Find all the grades in the loans
var grade_obj = {};
for (i=0; i<loans.length; i++){
    grade_obj[loans[i].grade] = true;
}

// Initialize the data array
for (var grade in grade_obj){
    data.push({
        key: grade,
        values: []
    });
}

// A function to sort the arrays by grade
function compare(a,b) {
  if (a.key < b.key)
    return -1;
  else if (a.key > b.key)
    return 1;
  else 
    return 0;
}

// Sort the arrays
data.sort(compare);

// Grade index
grade_idx_obj = {};
for (i=0; i<data.length; i++){
    grade = data[i].key;
    grade_idx_obj[grade] = i;
}

// Add data points to the data array
for (i=0; i<loans.length; i++){
    grade_idx = grade_idx_obj[loans[i].grade];
    data[grade_idx].values.push({
        x: loans[i].variance,
        y: loans[i].exp_int_rate,
        size: 1,
        id_val: loans[i]['id']
    });
}

 
var chart;
nv.addGraph(function() {
    chart = nv.models.scatterChart()
        .showDistX(true)
        .showDistY(true)
        .useVoronoi(true)
        .color(d3.scale.category10().range())
        .duration(300)
        // Changing xlim/ylim
        .forceY([-40, 20])
        .forceX([0.05, 0.12])

    ;

    chart.pointRange([100,100]);

    chart.dispatch.on('renderEnd', function(){
        console.log('render complete');
    });

    chart.xAxis
        .tickFormat(d3.format('.02f'))
        .axisLabel('Risk (Variance)');

    chart.yAxis
        .tickFormat(d3.format('.02f'))
        .axisLabel('Net Annualized Return (NAR)');

    d3.select('svg')
        .datum(data)
        .call(chart)
        //.style({ 'width': width, 'height': height });

    nv.utils.windowResize(chart.update);    
    chart.dispatch.on('stateChange', function(e) { ('New State:', JSON.stringify(e)); });


    chart.scatter.dispatch.on('elementClick', function(e) {
        function OpenInNewTab(url) {
            var win = window.open(url, '_blank');
            win.focus();
        }

     var url = "https://www.lendingclub.com/browse/loanDetail.action?loan_id=" + e.point.id_val;
     OpenInNewTab(url);
     
     //window.location.href = url;
     });


    //chart.tooltip.contentGenerator(function(d) { return d['point']});

    return chart;
});

