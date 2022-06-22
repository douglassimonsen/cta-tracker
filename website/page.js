const BASE_URL = "https://cta-bus-and-train-tracker.s3.amazonaws.com"
new Vue({
  el: '#page',
  data: {
    modes: ['bus', 'train'],
    selectedMode: 'bus',
    selectedDay: null,
    routes: ['8'],
    selectedRoute: '8',
    selectedDirection: 'South',
    actualData: [],
    scheduleData: null,
  },
  mounted: function(){
    this.selectedDay = formatDate();
    this.getData();
  },
  methods: {
    showRoute: function(){},
    getData: function(){
      Promise.all([
        ReadCompressed(`${BASE_URL}/schedules/rail/Blue/latest.gz`),
        ReadCompressed(`${BASE_URL}/traintracker/rollup/2022-06-13.bz2`),
      ]).then(function(data){
        [schedule, actual] = data
        const directions = Object.keys(schedule.stop_order);
        Object.values(schedule.stop_order).forEach(x => {x.forEach(y => {y['name'] = schedule.stops[y.stop_id].name})});
        this.scheduleData = schedule;
        chart.initialize(
          schedule.stop_order[this.selectedDirection],
          this.selectedDay,
        );
        chart.addTrips(schedule.trips, schedule.stop_order, "blue");
        this.trackerData = data;
      }.bind(this))
    },
    debug: function(){
      debugger;
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