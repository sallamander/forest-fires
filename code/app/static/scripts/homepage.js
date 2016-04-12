var homeSvgContainer = document.getElementById('home-svg-container'); 

var container_width = homeSvgContainer.offsetWidth; 
var svg_height = 600; 
var svg_width = 0.95 * container_width; 

var svg = d3.select("#home-svg-container")
            .append("svg") 
            .attr("width", svg_width)
            .attr("height", svg_height); 

var projection = d3.geo.albersUsa()
                   .translate([svg_width/2, svg_height/2])
                   .scale([700]); 

var path = d3.geo.path().projection(projection);
var g = svg.append("g");

d3.json("/static/scripts/data/usa_topo.json", function(error, usa) {

    g.selectAll("path")
        .data(topojson.feature(usa, usa.objects.usa).features)
        .enter()
        .append("path")
        .attr("d", path)
        .style("fill", "#D2D2D2")
        .style("stroke", "#ffffff")
        .on("mouseover", function() {
            d3.select(this)
              .style("fill", "#777"); 
        })
        .on("mouseout", function() {
            d3.select(this)
              .style("fill", "#D2D2D2"); 
        }) 
        .on("click", clicked);

});

var centered; 

function clicked(d) {
  var x, y, k;

  if (d && centered !== d) {
    var centroid = path.centroid(d);
    x = centroid[0];
    y = centroid[1];
    k = 4;
    centered = d;
  } else {
    x = svg_width / 2;
    y = svg_height / 2;
    k = 1;
    centered = null;
  }

  var name = d.properties.name; 
  var name_arr = name.toLowerCase().split(' '); 
  var state_name = name_arr.join('_')
  var filename = state_name + '_topo.json'; 
  g.selectAll("path")
      .classed("active", centered && function(d) { return d === centered; });

  g.selectAll(".county-borders").remove(); 

  g.transition()
      .duration(750)
      .attr("transform", "translate(" + svg_width / 2 + "," + svg_height / 2 + ")scale(" + k + ")translate(" + -x + "," + -y + ")")
      .style("stroke-width", 1.5 / k + "px");

  d3.json('/static/scripts/data/county_data/county_files/' + filename, 
          function(error, county) {
    
    console.log(county.objects); 
    console.log(topojson.feature(county, county.objects[state_name])); 
    g.selectAll(".county-borders")
        .data(topojson.feature(county, county.objects[state_name]).features)
        .enter()
        .append("path")
        .attr("d", path)
        .attr('class', 'county-borders')
        .style("fill", "#D2D2D2")
        .style("stroke", "#ffffff"); 
  }); 
}

