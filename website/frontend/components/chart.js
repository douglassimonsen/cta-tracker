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
  template: `
    <div>
      <div v-if="scheduleStops">
        <b-button @click="buttonZoom(['00:00:00', '06:00:00'])">Late Night</b-button>
        <b-button @click="buttonZoom(['06:00:00', '09:00:00'])">Morning Rush</b-button>
        <b-button @click="buttonZoom(['09:00:00', '14:00:00'])">Mid Day</b-button>
        <b-button @click="buttonZoom(['14:00:00', '19:00:00'])">Evening Rush</b-button>
        <b-button @click="buttonZoom(['19:00:00', '23:59:59'])">Early Night</b-button>
        <b-button @click="buttonZoom(['00:00:00', '23:59:59'])">All Day</b-button>

      </div>
      <svg id="chart"></svg>
    </div>
  `,
  data: function(){
    return {
      drag: {},
      dragRect: null,
    };
  },
  mounted: function(){
    this.initialize();
    this.generateGraphObjs();
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
      graphFuncs.body = d3.select("svg#chart").attrs({
        width: SIZE.width,
        height: SIZE.height,
        margin: '20px',
      });
      graphFuncs.body.append("rect").attrs({
        width: SIZE.width,
        height: SIZE.height,
        fill: 'aliceblue'
      });
      graphFuncs.body.call(d3.drag()
      .on("drag", dragMove.bind(this))
      .on("start", dragStart.bind(this))
      .on("end", dragEnd.bind(this)));
      graphFuncs.visual = graphFuncs.body.append("g").attr("z-index", 1).attr("fill", "blue");
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
    generateGraphObjs: function(){
      MARGIN.left = 20 + this.stopOrder.reduce((a, b) => Math.max(a, b.stop_name.length * 4.4), 0);
      if(graphFuncs.yScale === null){
        graphFuncs.yScale = d3.scaleLinear().domain(d3.extent(this.stopOrder, d => +d.shape_dist_traveled)).range([SIZE.height - MARGIN.bottom, MARGIN.top]);
      }
      else {
        graphFuncs.yG.remove();
      }
      graphFuncs.yAxis = d3.axisLeft(graphFuncs.yScale)
                            .tickValues(this.stopOrder.map(x => x.shape_dist_traveled))
                            .tickFormat((_, i) => this.stopOrder[i].stop_name);
      graphFuncs.yG = graphFuncs.body.append("g");
      graphFuncs.yG.append("rect").attrs({
        height: SIZE.height,
        width: MARGIN.left,
        fill: 'aliceblue',
        transform: `translate(-${MARGIN.left}, 0)`,
      });
      graphFuncs.yG.attr("class", "y-axis")
                .attr("transform", `translate(${MARGIN.left}, 0)`)
                .call(graphFuncs.yAxis);
      if(graphFuncs.xScale === null){
        graphFuncs.xScale = d3.scaleTime().domain([
          new Date(+this.dayParsed - 1000 * 60 * 60 * 3),
          new Date(+this.dayParsed + 1000 * 60 * 60 * 27), // +- 3 hours around the date
        ]).range([MARGIN.left, SIZE.width - MARGIN.right]);
      } else {
        graphFuncs.xG.remove();
      }
      graphFuncs.line = d3.line().x(d => graphFuncs.xScale(d.arrival_time)).y(d => graphFuncs.yScale(d.shape_dist_traveled));
      graphFuncs.xG = graphFuncs.body.append("g").attr("class", "x-axis");
      graphFuncs.xG.append("rect").attrs({
        height: SIZE.height - MARGIN.bottom,
        width: SIZE.width,
        fill: 'aliceblue',
      }); // background to keep graph from overflowing 
      graphFuncs.xAxis = d3.axisBottom(graphFuncs.xScale);
      graphFuncs.xG.attr("transform", `translate(0, ${SIZE.height - MARGIN.bottom})`).call(graphFuncs.xAxis);  
    },
    buttonZoom(times){
      this.zoom({
        left: new Date(`${this.selectedDay}T${times[0]}`),
        right: new Date(`${this.selectedDay}T${times[1]}`),
      });
    },
    zoom: function(bounds){
      if(bounds.left !== undefined && bounds.right !== undefined){
        graphFuncs.xScale.domain([bounds.left, bounds.right]);
      }
      if(bounds.bottom !== undefined && bounds.top !== undefined){
        graphFuncs.yScale.domain([bounds.bottom, bounds.top]);  // Although the range is flipped, the domain is still normal
      }
      this.dragRect.remove();
      graphFuncs.body.selectAll(".line").remove();
      graphFuncs.body.selectAll(".stop-group").remove();
      this.generateGraphObjs();
      this.addTrips(this.scheduleList, "blue");
    },
    addTrips: function(trips, color){
      graphFuncs.visual.selectAll(".line").append("g").attr("class", "line")
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
                      "class": "stop-group",
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
function shiftEvt(evt){
  return {
    x: evt.sourceEvent.offsetX,
    y: evt.sourceEvent.offsetY,
  }
}
function boundingBox(evt, drag){
  let left = Math.min(evt.x, drag.startX);
  let right = Math.max(evt.x, drag.startX);
  let top = Math.min(evt.y, drag.startY);
  let bottom = Math.max(evt.y, drag.startY);
  return {
    left: left,
    right: right,
    top: top,
    bottom: bottom,
  }
}
function dragMove(evt){
  evt = shiftEvt(evt);
  let bounds = boundingBox(evt, this.drag);
  this.dragRect.attrs({
    stroke: '#000000',
    'stroke-width': '1.5px',
    fill: '#ffffff',
    'fill-opacity': 0.5,
    x: bounds.left,
    y: bounds.top,
    width: (bounds.right - bounds.left),
    height: (bounds.bottom - bounds.top),
  });
}
function dragStart(evt){
  this.drag.startX = evt.sourceEvent.offsetX;
  this.drag.startY = evt.sourceEvent.offsetY;
  this.dragRect = graphFuncs.visual.append("rect");
}
function dragEnd(evt){
  evt = shiftEvt(evt);
  let bounds = boundingBox(evt, this.drag);
  bounds = {
    left: graphFuncs.xScale.invert(bounds.left),
    right: graphFuncs.xScale.invert(bounds.right),
    top: graphFuncs.yScale.invert(bounds.top),
    bottom: graphFuncs.yScale.invert(bounds.bottom),
  }
  this.zoom(bounds);
}
