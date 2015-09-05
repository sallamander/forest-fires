//Width and height
var w = 500;
var h = 500;

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
	console.log(data); 
}); 

