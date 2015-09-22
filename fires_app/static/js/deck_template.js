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
	//Width and height
	var w = 500;
	var h = 300;
	var barPadding = 1;

    fin_model = json.gradient_boosting
    non_fires = fin_model[0]
    fires = fin_model[1]

    var fires_dict = []; 
    var non_fires_dict = []; 

    for (i = 0; i < fires.length; i++) {
    	fires_dict.push({x : i, y: fires[i]})
    	non_fires_dict.push({x : i, y: non_fires[i]})
	}; 

	var dataset = [
		fires_dict, 
		non_fires_dict
	]; 

	var stack = d3.layout.stack(); 
	stack(dataset); 

	//Set up scales
	var xScale = d3.scale.ordinal()
		.domain(d3.range(dataset[0].length))
		.rangeRoundBands([0, w], 0.05);

	var yScale = d3.scale.linear()
		.domain([0,				
			d3.max(dataset, function(d) {
				return d3.max(d, function(d) {
					return d.y0 + d.y;
				});
			})
		])
		.range([0, h]);
		
	//Easy colors accessible via a 10-step ordinal scale
	var colors = d3.scale.category10();

	//Create SVG element
	var svg = d3.select("body")
				.append("svg")
				.attr("width", w)
				.attr("height", h);

	// Add a group for each row of data
	var groups = svg.selectAll("g")
		.data(dataset)
		.enter()
		.append("g")
		.style("fill", function(d, i) {
			return colors(i);
		});
	

	var rects = groups.selectAll("rect")
		.data(function(d) {return d; })
		.enter()
		.append("rect")
		.attr("x", function(d, i) {
			return xScale(i); 
		})
		.attr("y", function(d) {
			return yScale(d.y0); 
		})
		.attr("height", function(d) {
			return yScale(d.y); 
		})
		.attr("width", xScale.rangeBand());

	svg.selectAll("text")
	   .data(dataset)
	   .enter()
	   .append("text")
	   .text(function(d) {
	   		return d;
	   })
	   .attr("text-anchor", "middle")
	   .attr("x", function(d, i) {
	   		return i * (w / dataset.length) + (w / dataset.length - barPadding) / 2;
	   })
	   .attr("y", function(d) {
	   		return h - (d * 4) + 14;
	   })
	   .attr("font-family", "sans-serif")
	   .attr("font-size", "11px")
	   .attr("fill", "white");

})






