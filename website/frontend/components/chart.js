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
  yHover: null,
  xG: null,
  xScale: null,
  xAxis: null,
  xHover: null,
  daySelected: null,
  line: null,
  body: null,
  visual: null,
}
Vue.component('chart', {
  props: ["scheduleStops", "stopOrder", "selectedDay"],
  template: `<div id="chart"></div>`,
  mounted: function(){
    this.initialize();
    this.addTrips(this.scheduleList, "blue");
  },
  computed: {
    dayParsed: function(){
      return new Date(this.selectedDay + 'T00:00:00');
    },
    scheduleList: function(){
      return Object.values(this.scheduleStops);
    }
  },
  methods: {
    initialize: function(){
      const container = d3.select("div#chart");
      graphFuncs.body = container.append("svg")
          .attr("id", "string-chart")
          .attr("width", SIZE.width)
          .attr("height", SIZE.height)
          .style("background-color", "aliceblue")
          .style("margin", "20px").append("g");
      graphFuncs.visual = graphFuncs.body.append("g");
      MARGIN.left = 20 + this.stopOrder.reduce((a, b) => Math.max(a, b.stop_name.length * 4.4), 0);
      graphFuncs.yScale = d3.scaleLinear().domain(d3.extent(this.stopOrder, d => +d.shape_dist_traveled)).range([SIZE.height - MARGIN.bottom, MARGIN.top]);
      graphFuncs.yAxis = d3.axisLeft(graphFuncs.yScale)
                           .tickValues(this.stopOrder.map(x => x.shape_dist_traveled))
                           .tickFormat((d, i) => this.stopOrder[i].stop_name);
      graphFuncs.yG = graphFuncs.body.append("g");
      graphFuncs.yG.attr("class", "y-axis")
                .attr("transform", `translate(${MARGIN.left}, 0)`)
                .call(graphFuncs.yAxis);
    
      graphFuncs.xScale = d3.scaleTime().domain([
        new Date(+this.dayParsed - 1000 * 60 * 60 * 3),
        new Date(+this.dayParsed + 1000 * 60 * 60 * 27), // +- 3 hours around the date
      ]).range([MARGIN.left, SIZE.width - MARGIN.right]);
      graphFuncs.line = d3.line().x(d => graphFuncs.xScale(d.arrival_time)).y(d => graphFuncs.yScale(d.shape_dist_traveled));
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

      
      graphFuncs.xHover = graphFuncs.visual.append("path").attrs({
        'class': 'x-hover line',
        'stroke': 'black',
        'stroke-width': 1,
        "stroke-dasharray": "10,10",
      });      
      graphFuncs.yHover = graphFuncs.visual.append("path").attrs({
        'class': 'y-hover line',
        'stroke': 'black',
        'stroke-width': 1,
        "stroke-dasharray": "10,10",
      });      
    },
    addTrips: function(trips, color){
      graphFuncs.visual.selectAll(".line").append("g")
          .data(trips).enter().append("path")
          .attrs({
            "d": d => graphFuncs.line(d),
            "fill": "none",
            "stroke": color,
            "stroke-width": 2,
            "class": "line",
          });
      graphFuncs.visual.selectAll(".stop-group").data(trips).enter()
                     .append("g").attrs({
                      "line-index": (_, i) => i,
                      "line-type": "schedule",
                     }).selectAll(".stop-point").data(d => d).enter()
                     .append("circle").attrs({
                      "cx": d => graphFuncs.xScale(d.arrival_time),
                      "cy": d => graphFuncs.yScale(d.shape_dist_traveled),
                      "fill": "blue",
                      "stop-index": (_, i) => i,
                      "opacity": .5,
                      "r": 7,
                      "class": "stop-point",
                     }).on("mouseover", function(trips, evt){
                      let lineIndex = +evt.target.parentElement.getAttribute("line-index");
                      let stopIndex = +evt.target.getAttribute("stop-index");
                      this.sendInfoBox("Scheduled", trips[lineIndex], stopIndex);
                      this.createHoverLines(
                        trips[lineIndex][stopIndex].arrival_time,
                        +trips[lineIndex][stopIndex].shape_dist_traveled,
                      );
                     }.bind(this, trips)).on("mouseout", function(){
                      graphFuncs.xHover.attr("opacity", 0);
                      graphFuncs.yHover.attr("opacity", 0);
                     })
    },
    createHoverLines: function(x, y){
      graphFuncs.xHover.attrs({
        'd': graphFuncs.line([{arrival_time: x, shape_dist_traveled: graphFuncs.yScale.domain()[0]}, {arrival_time: x, shape_dist_traveled: graphFuncs.yScale.domain()[1]}]),
        "opacity": 1,
      });
      graphFuncs.yHover.attrs({
        'd': graphFuncs.line([{arrival_time: graphFuncs.xScale.domain()[0], shape_dist_traveled: y}, {arrival_time: graphFuncs.xScale.domain()[1], shape_dist_traveled: y}]),
        "opacity": 1,
      });
    },
    sendInfoBox: function(tripType, tripInfo, stopIndex){
      this.$emit("hover", {
        stopName: this.stopOrder.find(x => x.stop_id === tripInfo[stopIndex].stop_id)?.stop_name,
        stopTime: tripInfo[stopIndex].arrival_time,
        diffFromSchedule: Math.random() * 10,
        headway: Math.random() * 10,
        tripType: tripType,
      });
    },
  },
});