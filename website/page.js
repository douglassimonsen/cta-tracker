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
    trackerData: [],
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
        debugger;
        const directions = Object.keys(data.stop_order);
        Object.values(data.stop_order).forEach(x => {x.forEach(y => {y['name'] = data.stops[y.stop_id].name})});
        this.scheduleData = data;
        chart.initialize(
          data.stop_order[this.selectedDirection],
          this.selectedDay,
        );
        chart.addTrips(data.trips, data.stop_order, "blue");
        this.trackerData = data;
        this.routes = [...new Set(data.map(x => x.rn.padStart(3, ' ')))].sort();
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