const MARGIN = {
  left: 20,
  right: 20,
  top: 20,
  bottom: 20
}
const SIZE = {
  height: 800,
  width: 1200,
}
const graphFuncs = {
  yG: null,
  yScale: null,
  yAxis: null,
  xG: null,
  xScale: null,
  xAxis: null,
  daySelected: null,
  line: null,
  body: null,
  visual: null,
}
Vue.component('chart', {
  template: `<div id="chart"></div>`,
})
function initialize(stations, day){
  const container = d3.select("div#chart");
  graphFuncs.body = container.append("svg")
      .attr("id", "string-chart")
      .attr("width", SIZE.width)
      .attr("height", SIZE.height)
      .style("background-color", "aliceblue")
      .style("margin", "20px").append("g");
  graphFuncs.visual = graphFuncs.body.append("g");
  MARGIN.left = 20 + stations.reduce((a, b) => Math.max(a, b.name.length * 4.4), 0);
  graphFuncs.yScale = d3.scaleLinear().domain(d3.extent(stations, d => +d.dist)).range([SIZE.height - MARGIN.bottom, MARGIN.top]);
  graphFuncs.yAxis = d3.axisLeft(graphFuncs.yScale)
                       .tickValues(stations.map(x => x.dist))
                       .tickFormat(function(d, i){return stations[i].name});
  graphFuncs.yG = graphFuncs.body.append("g");
  graphFuncs.yG.attr("class", "y-axis")
            .attr("transform", `translate(${MARGIN.left}, 0)`)
            .call(graphFuncs.yAxis);

  graphFuncs.day = day;
  graphFuncs.daySelected = new Date(day + 'T00:00:00');
  graphFuncs.xScale = d3.scaleTime().domain([
    new Date(+graphFuncs.daySelected - 1000 * 60 * 60 * 3),
    new Date(+graphFuncs.daySelected + 1000 * 60 * 60 * 27), // +- 3 hours around the date
  ]).range([MARGIN.left, SIZE.width - MARGIN.right]);
  graphFuncs.line = d3.line().x(d => graphFuncs.xScale(new Date(day + 'T' + d.arrival_time))).y(d => graphFuncs.yScale(d.shape_dist_traveled));
  graphFuncs.xG = graphFuncs.body.append("g")
  graphFuncs.xAxis = d3.axisBottom(graphFuncs.xScale);
  graphFuncs.xG.attr("transform", `translate(0, ${SIZE.height - MARGIN.bottom})`).call(graphFuncs.xAxis);

  let zoom = d3.zoom().on("zoom", function(evt){
    evt.transform.k = Math.max(evt.transform.k, 1);
    evt.transform.x = clamp(evt.transform.x, (evt.transform.k - 1) * -(SIZE.width - MARGIN.right), (evt.transform.k - 1) * -MARGIN.left);
    evt.transform.y = clamp(evt.transform.y, (evt.transform.k - 1) * -(SIZE.height - MARGIN.bottom), (evt.transform.k - 1) * -MARGIN.top);
    graphFuncs.xG.call(graphFuncs.xAxis.scale(evt.transform.rescaleX(graphFuncs.xScale)));
    graphFuncs.yG.call(graphFuncs.yAxis.scale(evt.transform.rescaleY(graphFuncs.yScale)));
    graphFuncs.visual.attr("transform", evt.transform);
    d3.selectAll(".stop-point").attr("r", 10 / evt.transform.k);
    d3.selectAll(".line").attr("stroke-width", 2 / evt.transform.k);
  });
  container.call(zoom);
}
function addTrips(trips, stop_order, color){
  graphFuncs.visual.selectAll(".line").append("g")
      .data(trips.slice(0, 5)).enter().append("path")
      .attrs({
        "d": d => graphFuncs.line(d.stop_times),
        "fill": "none",
        "stroke": color,
        "stroke-width": 2,
        "class": "line",
      });
  graphFuncs.visual.selectAll(".stop-group").data(trips.slice(0, 5)).enter()
                 .append("g").attrs({
                  "line-index": (_, i) => i,
                  "line-type": "schedule",
                 }).selectAll(".stop-point").data(d => d.stop_times).enter()
                 .append("circle").attrs({
                  "cx": d => graphFuncs.xScale(new Date(graphFuncs.day + 'T' + d.arrival_time)),
                  "cy": d => graphFuncs.yScale(d.shape_dist_traveled),
                  "fill": "blue",
                  "stop-index": (_, i) => i,
                  "opacity": .5,
                  "r": 10,
                  "class": "stop-point",
                 }).on("mouseover", function(trips, evt){
                  let lineIndex = +evt.target.parentElement.getAttribute("line-index");
                  let stopIndex = +evt.target.getAttribute("stop-index");
                  let lineType = evt.target.parentElement.getAttribute("line-type");
                  InfoBox(trips[lineIndex], stopIndex);
                 }.bind(null, trips))
}
function InfoBox(tripInfo, stopIndex){}
const chart = {
  initialize: initialize,
  addTrips: addTrips,
};
function clamp(a, b, c){
  return Math.min(Math.max(a, b), c);
}