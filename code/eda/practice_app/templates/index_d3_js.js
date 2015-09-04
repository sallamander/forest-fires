//Width and height
var w = 1000;
var h = 500;

//Create SVG element
var svg = d3.select("body")
			.append("svg")
			.attr("width", w)
			.attr("height", h);

var path = d3.geo.path(); 



d3.json('/data/jsons/2013_state.json', function(json){
	svg.selectAll("path")
	.data(json)
	.enter()
	.append("path")
	.attr("d", path); 
}); 