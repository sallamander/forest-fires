/*

This was for generating the pictures of maps for the deck. 
//Width and height
var w = 500;
var h = 500;

//Create SVG element
var svg = d3.select("body")
			.append("svg")
			.attr("width", w)
			.attr("height", h)
			.style("background", "#000");

var projection = d3.geo.albers()
						.translate([w/2, h/2])
						.scale([w]); 	

var path = d3.geo.path().projection(projection); 
color = d3.rgb(120, 175, 120)

d3.json('/static/data/2014_county.json', function(json){
	svg.selectAll("path")
	.data(json)
	.enter()
	.append("path")
	.attr("d", path)
	.style("fill", color)
	.style('stroke-width', '3');  
}); 
*/

/*
This is for generating something else
*/ 


var margin = {top: 20, right: 50, bottom: 30, left: 80},
    width = 750 - margin.left - margin.right,
    height = 350 - margin.top - margin.bottom;

var x0 = d3.scale.ordinal()
    .rangeRoundBands([0, width], .1);

var x1 = d3.scale.ordinal();

var y = d3.scale.linear()
    .range([height, 0]);

var color = d3.scale.ordinal()
    .range(['#ec5300', '#f97d16', '#ff9750', '#ffb605', '#bd4343']);

var xAxis = d3.svg.axis()
    .scale(x0)
    .orient("bottom");

var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left");

var svg = d3.select("body").append("svg")
	.style("background", "black")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")"); 

d3.csv("/static/data/gboosting_preds.csv", function(error, data) {
	if (error) throw error;

	var probBins = d3.keys(data[0]).filter(function(key) { return key !== "model_name"; });
	probBins.shift()

	data.forEach(function(d) {
		d.probs = probBins.map(function(name) { return {name: name, value: +d[name]}; });
	});

	x0.domain(data.map(function(d) { return d.model_name; }));
	x1.domain(probBins).rangeRoundBands([0, x0.rangeBand()]);
	y.domain([0, d3.max(data, function(d) { return d3.max(d.probs, function(d) { return d.value; }); })]);

	svg.append("g")
	  .attr("class", "x axis")
	  .attr("transform", "translate(0," + height + ")")
	  .call(xAxis)
	  .attr("fill", "white");

	svg.append("g")
	  .attr("class", "y axis")
	  .attr("fill", "white")
	  .call(yAxis)
	  .append("text")
	  .attr("transform", "rotate(-90)")
	  .attr("y", 6)
	  .attr("dy", ".71em")
	  .style("text-anchor", "end"); 

	var model = svg.selectAll(".model")
	  .data(data)
	  .enter().append("g")
	  .attr("class", "g")
	  .attr("transform", function(d) { return "translate(" + x0(d.model_name) + ",0)"; });

	model.selectAll("rect")
	  .data(function(d) { return d.probs; })
	  .enter().append("rect")
	  .attr("width", x1.rangeBand())
	  .attr("x", function(d) { return x1(d.name); })
	  .attr("y", function(d) { return y(d.value); })
	  .attr("height", function(d) { return height - y(d.value); })
	  .style("fill", function(d) { return color(d.name); });

	var legend = svg.selectAll(".legend")
	  .data(probBins.slice().reverse())
	  .enter().append("g")
	  .attr("class", "legend")
	  .attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; });

	legend.append("rect")
	  .attr("x", width - 18)
	  .attr("width", 18)
	  .attr("height", 18)
	  .style("fill", color);

	legend.append("text")
	  .attr("x", width - 24)
	  .attr("y", 9)
	  .attr("dy", ".35em")
	  .style("text-anchor", "end")
	  .text(function(d) { return d; })
	  .attr("fill", "white");
});
	