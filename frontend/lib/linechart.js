
function loadLineChart(data, field_Name) {
    if (data.length <= 1) return;

    var div = d3.select("#" + field_Name);
	
	
	var parseTime = d3.timeParse("%Y-%m-%d %H:%M:%S");
	
	
	var svg = div.append("svg")  
				 .style("width", 1128)
				 .style("height", 200);
				 
		margin = {top: 10, right: 20, bottom: 20, left: 40},
		width = 1128 - margin.left - margin.right,
		height = 200 - margin.top - margin.bottom,
		g = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");
	
	//scale
	var x = d3.scaleTime().range([0, width]),
		y = d3.scaleLinear().range([height, 0]);

	//Axis
	var xAxis = d3.axisBottom(x);
	var yAxis = d3.axisLeft(y);
	
	//定义直线类型
	var line = d3.line()
		.curve(d3.curveCardinal)
		.x(function(d) { return x( parseTime(d[0]) ); })
		.y(function(d) { return y( d[1] ); });

    // Select the svg element, if it exists.
    var svg = div.selectAll('svg').data([data]);

    //Scale宽度所对应的值
	// x.domain(d3.extent(data, function(d) { return parseTime(d[0]); }));
	x.domain([ parseTime(time_from),parseTime(time_to) ]);

	y.domain([
		d3.min(data, function(d) { return d[1]; }),
		d3.max(data, function(d) { return d[1]; })
	]);

	
    g.append("text")
      .attr("x", width/2 )
      .attr("y", margin.top)
      .attr("dy", ".35em")
      .text("Timeline");
	
	g.append("g")
		.attr("class", "axis axis--x")
		.attr("transform", "translate(0," + height + ")")
		.call(xAxis);

	g.append("g")
		.attr("class", "axis axis--y")
		.call(yAxis)
		.append("text")
		.text("Count")
		.attr("transform", "rotate(-90)")
		.attr("y", 6)
		.attr("dy", "0.71em")
		.attr("fill", "#000");
	
	
	//添加画线的画布
	g.selectAll("time")
		.data([data])
		.enter().append("g")
		.append("path")
		.attr("class", "line")
		.attr("clip-path", "url(#clip)")
        .attr("width",width)
        .attr("height", height)
		.attr("d", line(data));
	
	
	var zoom = d3.zoom()

		.on("zoom", draw)
		.on("end",update_linechart);
	g.append("rect")
		.attr("width", width)
		.attr("height", height)
		.attr("fill", "none")
		.attr("pointer-events", "all")
		.call(zoom);
		
/* 	//添加画刷
	var brush = d3.brushX()
		.extent([[0, 0], [width, height]])
		.on("end", brushed);
    g.append("rect")
		.attr("class", "brush")
		.attr("width", width)
		.attr("height", height)
		.attr("fill", "none")
		.call(brush);
		
	function brushed() {
		
		if (!d3.event.sourceEvent) return; 
		if (!d3.event.selection) return;   
		var d0 = d3.event.selection.map(x.invert,x);
		x.domain(d0);
		svg.select("g.axis.axis--x").call(xAxis);	
		svg.select("path.line").attr("d", line.x(function(d) { return (x(d[0]))}));
     }	 */
		
	function draw() {
	
		var xz = d3.event.transform.rescaleX(x);
		    // domain1 = xz.domain()[0];
		    // domain2 = xz.domain()[1];
		// if( domain1.getTime()<parseTime(time_lowerBound).getTime() )
			// xz.domain([parseTime(time_lowerBound),domain2]);
		// console.log(xz.domain()[0]);
		svg.select("g.axis.axis--x").call(xAxis.scale(xz));
		svg.select("path.line").attr("d", line.x(function(d) { return xz(parseTime(d[0]))}));
	}
	
	function update_linechart() {
		var lower_bound = xAxis.scale().domain()[0];
            upper_bound = xAxis.scale().domain()[1];
		
		time_from = moment(lower_bound).format("YYYY-MM-DD HH:mm:ss");
		time_to = moment(upper_bound).format("YYYY-MM-DD HH:mm:ss");
		
		console.log(time_from);

		heatmap.redraw();
	}
	

}