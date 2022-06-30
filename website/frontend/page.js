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
        console.log(this.stopDistance);
        Object.values(response.data).forEach(trip => {
          trip.forEach(stop => {
            stop.arrival_time = new Date(stop.arrival_time);  // casting to actual dates
            stop.shape_dist_traveled = this.stopDistance[stop.stop_id];
          });
        });
        this.scheduleStops = response.data;
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
      return;
      Promise.all([
        ReadCompressed(`${BASE_URL}/schedules/rail/Blue/latest.bz2`),
        ReadCompressed(`${BASE_URL}/traintracker/rollup/2022-06-13.bz2`),
      ]).then(function(data){
        return;
        [this.scheduleData, this.actualData] = data
        const directions = Object.keys(this.scheduleData.stop_order);
        Object.values(this.scheduleData.stop_order).forEach(x => {x.forEach(y => {y['name'] = this.scheduleData.stops[y.stop_id].name})});
      }.bind(this))
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