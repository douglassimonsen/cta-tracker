const BASE_URL = "https://cta-bus-and-train-tracker.s3.amazonaws.com"
const app = new Vue({
  el: '#page',
  data: {
    formVals: {},
    actualData: [],
    scheduleStops: [],
    stopOrder: [],
    hoverInfo: {},
    showChart: false,
  },
  mounted: function(){
    this.selectedDay = formatDate();
  },
  computed: {
    stopDistance: function(){
      return Object.fromEntries(this.stopOrder.map(x => [x.stop_id, x.shape_dist_traveled]));
    },
  },
  methods: {
    getSchedule: function(){
      return axios.post('http://127.0.0.1:5000/api/schedule', {
        route: this.formVals.route,
        date: this.formVals.date,
        direction: this.formVals.direction,
      },
      {headers: {'Access-Control-Allow-Origin': '*'}},
      ).then(function(response){
        this.scheduleStops = Object.fromEntries(Object.entries(response.data).map(trip_info => {
          [trip_id, trip] = trip_info;
          trip.forEach(stop => {
            stop.arrival_time = new Date(stop.arrival_time);  // casting to actual dates
            stop.shape_dist_traveled = this.stopDistance[stop.stop_id];
          });
          return [
            trip_id,
            trip.filter(x => x.shape_dist_traveled !== undefined),
          ]
        }));
        toCSV(Object.entries(this.scheduleStops).map(x => x[1].map(y => {
          y.trip = x[0]; 
          y.arrival_time = formatDt(y.arrival_time);
          return y;
        })).flat());
      }.bind(this));
    },
    getStopOrder: function(){
      return axios.post('http://127.0.0.1:5000/api/stop_order', {
        route: this.formVals.route,
        direction: this.formVals.direction,
      },
      {headers: {'Access-Control-Allow-Origin': '*'}},
      ).then(function(response){
        this.stopOrder = response.data;
      }.bind(this));
    },
    getData: function(evt){
      this.formVals = evt;
      Promise.all([
        this.getSchedule(),
        this.getStopOrder(),
      ]).then(() => this.showChart = true);
    },
    fillInfoBox: function(evt){
      this.hoverInfo = evt;
    }
  }

});
function ReadCompressed(url){
  return axios.get(
    url, 
    {
      headers: {'Access-Control-Allow-Origin': '*'},
      responseType: 'arraybuffer',
    }
  ).then(function(url, response){
    let inflatedResponse;
    if(url.endsWith(".gz")){
      inflatedResponse = pako.inflate(response.data);
      inflatedResponse = Array.from(inflatedResponse).map((c) => String.fromCharCode(c)).join('');
    }
    else{
      inflatedResponse = bzip2.simple(bzip2.array(new Uint8Array(response.data)));
    }
    let data = JSON.parse(inflatedResponse);
    return data;
  }.bind(null, url));
}
function formatDate(dt){
  if(!dt){
    dt = new Date();
  }
  let year = dt.getFullYear().toString().padStart(2, '0')
  let month = (new Date().getMonth() % 12 + 1).toString().padStart(2, '0');
  let day = dt.getDate().toString().padStart(2, '0')
  return `${year}-${month}-${day}`;
}