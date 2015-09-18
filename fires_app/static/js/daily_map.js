//Create SVG element
w = 1000
h = 500
var svg = d3.select("#daily-map")
			.append("svg")
			.attr("width", w)
			.attr("height", h)
			.style("background", "#000")
			.style("border-radius", "15px")
			.style("position", "relative")
			.style("top", "-10em");

var projection = d3.geo.albersUsa()
						.translate([w/2, h/2])
						.scale([w]); 	

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


