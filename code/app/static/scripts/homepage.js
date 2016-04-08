var homeSvgContainer = document.getElementById('home-svg-container'); 

var container_height = homeSvgContainer.offsetHeight; 
var container_width = homeSvgContainer.offsetWidth; 

var svg_height = 500; 
var svg_width = 0.95 * container_width; 

var svg = d3.select("#home-svg-container")
            .append("svg") 
            .attr("width", svg_width)
            .attr("height", svg_height); 

var projection = d3.geo.albersUsa()
                   .translate([svg_width/2, svg_height/2])
                   .scale([700]); 

var path = d3.geo.path().projection(projection);

d3.json('/static/scripts/data/states_2014.geojson', function(json) {

    console.log(json)

    svg.selectAll("path")
        .data(json.features)
        .enter()
        .append("path")
        .attr("d", path)
        .style("fill", "#D2D2D2")
        .style("stroke", "#DCDCDC")
        .on("mouseover", function(d, i) {
            d3.select(this)
              .style("fill", "#777"); 
        })
        .on("mouseout", function() {
            d3.select(this)
              .style("fill", "#D2D2D2"); 
        }); 
}); 
