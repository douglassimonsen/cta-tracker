const MARGIN = {
  left: 20,
  right: 20,
  top: 20,
  bottom: 20
}
const SIZE = {
  height: 600,
  width: 800,
}
const graphFuncs = {
  yScale: null,
  xScale: null,
  daySelected: null,
}
function initialize(stations, day){
  const container = d3.select("div#chart");
  body = container.append("svg")
      .attr("id", "string-chart")
      .attr("width", SIZE.width)
      .attr("height", SIZE.height)
      .style("background-color", "aliceblue")
      .style("margin", "20px");
  
  MARGIN.left = 20 + stations.reduce((a, b) => Math.max(a, b.name.length * 4.4), 0);
  graphFuncs.yScale = d3.scaleLinear().domain(d3.extent(stations, (d) => d.dist)).range([SIZE.height - MARGIN.bottom, MARGIN.top]);
  body.append("g")
      .attr("class", "y-axis")
      .attr("transform", `translate(${MARGIN.left}, 0)`)
      .call(d3.axisLeft(graphFuncs.yScale)
              .tickValues(stations.map(x => x.dist))
              .tickFormat(function(d, i){return stations[i].name})
      );
  graphFuncs.daySelected = new Date(day + 'T00:00:00');
  graphFuncs.xScale = d3.scaleTime().domain([
    new Date(+graphFuncs.daySelected - 1000 * 60 * 60 * 3),
    new Date(+graphFuncs.daySelected + 1000 * 60 * 60 * 27), // +- 3 hours around the date
  ]).range([MARGIN.left, SIZE.width - MARGIN.right]);
  body.append("g").attr("transform", `translate(0, ${SIZE.height - MARGIN.bottom})`).call(d3.axisBottom(graphFuncs.xScale));
}
function addTrips(trips, stop_order){
  const body = d3.select("#string-chart");
  body.selectAll(".line").append("g").attr("class", "line")
      .data(trips).enter().append("path")
      .attr("d", function(stop_order, d){
        debugger;
        stop_order[d.direction].find(x => x.stop_id === d.stop_times[0].stop_id);
      }.bind(null, stop_order))
      .attr("fill", "none").attr("stroke", "blue").attr("stroke-width", 2)
}

const chart = {
  initialize: initialize,
  addTrips: addTrips,
};