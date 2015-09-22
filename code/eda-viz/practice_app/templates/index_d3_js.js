//Width and height
var w = 750;
var h = 750;

//Create SVG element
var svg = d3.select("body")
			.append("svg")
			.attr("width", w)
			.attr("height", h);

var projection = d3.geo.albersUsa()
						.translate([w/2, h/2])
						.scale([w]); 	

var path = d3.geo.path().projection(projection); 
color = d3.rgb(120, 175, 120)

d3.json('/data/jsons/2013_state.json', function(json){
	svg.selectAll("path")
	.data(json)
	.enter()
	.append("path")
	.attr("d", path)
	.style("fill", color)
	.style('stroke-width', '3');  
}); 

d3.csv('/data/csvs/fires_2013_lightweight.csv', function(data) {
	svg.selectAll("circle")
	.data(data)
	.enter()
	.append("circle")
	.attr('cx', function(d){
		return projection([d.long, d.lat])[0]; 
	}) 
	.attr('cy', function(d){
		return projection([d.long, d.lat])[1]; 
	})
	.attr("r", 1)
	.style("fill", "red")
}); 

