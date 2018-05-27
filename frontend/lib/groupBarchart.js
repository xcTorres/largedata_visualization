
function setGroupBarchart(data , field){
	
	
	var margin = {
	        top : 30,
	        right : 10,
	        bottom : 20,
	        left : 60
	    };
	
	var div = d3.select(field);   
	
	var week = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"];
	var payment = ["Credit card","Cash","Other"];
	
	var width = div.node().getBoundingClientRect().width - margin.left - margin.right;
    var height = div.node().getBoundingClientRect().height - margin.top - margin.bottom;
	
	var svg = div.selectAll('svg').data([data]);
	
    var svg = svg.enter()
			.append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var y = d3.scaleLinear()
			.range([0, width]);
           

    var x = d3.scaleBand().rangeRound([0, height]).paddingInner(0.1);
            
	
	var x1 = d3.scaleBand().padding(0.05);
	
	x.domain(week.map(function (d) {
                return d;
            }));
	
	x1.domain(payment).rangeRound([0, x.bandwidth()]);
	
	y.domain([0, d3.max(data, function (d) {
				return d3.max(week, function(w,i) { return d[i]; });
			})]).nice();
			
	
	var xAxis = d3.axisLeft(x);
	var yAxis = d3.axisTop(y);

    var gy = svg.append("g")
            .attr("class", "y axis")
            .call(yAxis.ticks(null, "s"));
			
			
	var gx = svg.append("g")
            .attr("class", "x axis")
            .call(xAxis)
	
	
	var colors = d3.scaleOrdinal()
    .range(["#98abc5", "#6b486b", "#ff8c00"]);

        //append rects
    var bars = svg.selectAll(".bar")
        .data(data)
        .enter()
		.append("g")
        .attr("transform", function(d,i) { return "translate(0," + x(week[i]) + ")" ; })
		.selectAll("rect")
		.data(function(d) { return payment.map(function(key,i) { return {key: payment[i], value: d[i]}; }); })
		.enter()
        .append("rect")
        .attr("class", "bar")
        .attr("y", function (d) {
            return x1(d.key);
        })
        .attr("height", x1.bandwidth())
        .attr("x", 0)
        .attr("width", function (d) {
            return y(d.value);
        })
		.attr("fill", function(d) {
			return colors(d.key);
		});
		
		
	var legend = svg.append("g")
      .attr("font-family", "sans-serif")
      .attr("font-size", 10)
      .attr("text-anchor", "end")
      .selectAll("g")
      .data(payment.reverse())
      .enter().append("g")
      .attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; });

	legend.append("rect")
      .attr("x", width - 19)
      .attr("width", 19)
      .attr("height", 19)
      .attr("fill", colors);

	legend.append("text")
      .attr("x", width - 24)
      .attr("y", 9.5)
      .attr("dy", "0.32em")
      .text(function(d) { return d; });

}


		    // .each(function (d,i) {
			  
				// var selection = d3.select(this);
				// var state = true;
				// selection.on('mousedown', function () {
					// if (state) {
						// selection.style('fill', colors[1]);
					// } else {
						// selection.style('fill', colors[0]);
					// }
					// state = !state;
					// if(state)
						// day_of_week.push(i);
					// else
						// removeByValue(day_of_week,i);
					
					// div.selectAll("rect").each(function (d) { console.log(d3.select(this).style("fill")) });
					
					// Query();
					// heatmap.redraw();
					

				// });
		   //});
			

    //add a value label to the right of each bar
    // bars.append("text")
            // .attr("class", "label")
            //y position of the label is halfway down the bar
            // .attr("y", function (d) {
                // return x(d[0]) + x.bandwidth() / 2 + 4;
            // })
            //x position is 3 pixels to the right of the bar
            // .attr("x", function (d) {
                // return x(d[1]) + 3;
            // })
            // .text(function (d) {
                // return d.value;
    // });