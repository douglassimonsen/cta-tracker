const day = '2022-06-10';
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
function initialize(stations){
  const container = d3.select("div#chart");
  body = container.append("svg")
      .attr("id", "string-chart")
      .attr("width", SIZE.width)
      .attr("height", SIZE.height)
      .style("background-color", "aliceblue")
      .style("margin", "20px");
  
  MARGIN.left = 20 + stations.reduce((a, b) => Math.max(a, b.name.length * 4.4), 0);
  const yScale = d3.scaleLinear().domain(d3.extent(stations, (d) => d.dist)).range([SIZE.height - MARGIN.bottom, MARGIN.top]);
  body.append("g")
      .attr("class", "y-axis")
      .attr("transform", `translate(${MARGIN.left}, 0)`)
      .call(d3.axisLeft(yScale)
              .tickValues(stations.map(x => x.dist))
              .tickFormat(function(d, i){return stations[i].name})
      );
  const dayParsed = new Date(day + 'T00:00:00');
  const xScale = d3.scaleTime().domain([
    new Date(+dayParsed - 1000 * 60 * 60 * 3),
    new Date(+dayParsed + 1000 * 60 * 60 * 27), // +- 3 hours around the date
  ]).range([MARGIN.left, SIZE.width - MARGIN.right]);
  body.append("g").attr("transform", `translate(0, ${SIZE.height - MARGIN.bottom})`).call(d3.axisBottom(xScale));
}


const chart = {
  initialize: initialize,
};