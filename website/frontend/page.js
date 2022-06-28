const BASE_URL = "https://cta-bus-and-train-tracker.s3.amazonaws.com"
const app = new Vue({
  el: '#page',
  data: {
    actualData: [],
    scheduleData: null,
    hoverInfo: {},
  },
  mounted: function(){
    this.selectedDay = formatDate();
    this.getData();
  },
  methods: {
    showRoute: function(evt){
      axios.post('http://127.0.0.1:5000/api/schedule', {
        route: evt.route,
        date: evt.date,
        direction: evt.direction,
      },
      {headers: {'Access-Control-Allow-Origin': '*'}},
      ).then(function(response){
        debugger;
      }.bind(this));
    },
    getData: function(){
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