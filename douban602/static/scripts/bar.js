
var svg = d3.select("#bar"),
margin = {top: 20, right: 20, bottom: 30, left: 40},
width = +svg.attr("width") - margin.left - margin.right,
height = +svg.attr("height") - margin.top - margin.bottom;

var x = d3.scaleBand().rangeRound([0, width]).padding(0.1),
y = d3.scaleLinear().rangeRound([height, 0]);

var g = svg.append("g")
.attr("transform", "translate(" + margin.left + "," + margin.top + ")");


var tooltip = d3.select("body")
  .append("div")
  .style("position", "absolute")
  .style("z-index", "10")
  .style("visibility", "hidden")
  // .append("text")
  // .attr("id","hover-info");

function refresh(d){
  textarea = d3.select("body.text");
  console.log(textarea)
}

var data = document
  .getElementsByTagName("span")[0]
  .textContent
  .replace(/\'/g,'\"')
  .replace(/\n/g, ' ')


data= JSON.parse(data);

for (d of data) {

          d.time=parseInt(d.time);
          d.score = parseFloat(d.score);
}

// data = data.each(function(d){
//       })
console.log("data",data);
data = data.sort(function(d1,d2){return parseInt(d1.time)-parseInt(d2.time)})
x.domain(data.map(function(d) { return parseInt(d.time); }));

y.domain([0, d3.max(data, function(d) { return parseInt(d.score); })]);
g.append("g")
  .attr("class", "axis axis--x")
  .attr("transform", "translate(0," + height + ")")
  .call(d3.axisBottom(x));

g.append("g")
  .attr("class", "axis axis--y")
  .call(d3.axisLeft(y))
.append("text")
  .attr("transform", "rotate(-90)")
  .attr("y", 6)
  .attr("dy", "0.71em")
  .attr("text-anchor", "end")
  .text("评分");

g.selectAll(".bar")
.data(data)
.enter().append("rect")
  .attr("class", "bar")
  .attr("x", function(d) { return x(d.time); })
  .attr("y", function(d) { return y(d.score); })
  .attr("width", x.bandwidth())
  .attr("height", function(d) { return height - y(d.score); })
  .on("mouseover", function(d)
      {
        var strs = "电影名："+d.name +"\t\n   导演："+ d.director
          +"\t\n   主演："+ d.stars
          +"   年份:" + d.time;
      return tooltip.style("visibility", "visible").text(strs)})
  .on("mousemove", function(d){return tooltip.style("top",(d3.event.pageY-10)+"px").style("left",(d3.event.pageX+10)+"px");})
  .on("mouseout", function(d)
    {return tooltip.style("visibility", "hidden");})


//   ppend("text")
//   .attr("x",30)
//   .attr("y",100)
//   .attr("font-size",30)
//   .attr("font-family","simsun")
// .append("tspan")
//   .attr("x",30)
//   .attr("dy","1em")
//   .text()
// .append("tspan")
//   .attr("x",30)
//   .attr("dy","1em")
//   .text()
// .append("tspan")
//   .attr("x",30)
//   .attr("dy","1em")
//   .text()
// .append("tspan")
//   .attr("x",30)
//   .attr("dy","1em")
//   .text()})
