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

d3.json('/static/data/model_preds.json', function(json){
	for (i = 0; i < json.length; i++) {
    	a = json[i]
	}

	console.log(a)
})






