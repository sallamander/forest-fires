//Create SVG element
var svg = d3.select("svg");
var w = 750; 
var h = 500; 

var projection = d3.geo.albersUsa()
						.translate([w/2, h/2])
						.scale([750]); 	

var path = d3.geo.path().projection(projection); 
color = d3.rgb(120, 175, 120)

d3.json('../static/data/2013_state.json', function(json){
	svg.selectAll("path")
	.data(json)
	.enter()
	.append("path")
	.attr("d", path)
	.style("fill", color)
	.style('stroke-width', '3');  
}); 


