new Vue({
  el: '#page',
  data: {
    modes: ['bus', 'train'],
    selectedMode: 'bus',
    selectedDay: null,
    routes: ['8'],
    selectedRoute: '8',
    trackerData: [],
  },
  mounted: function(){
    this.selectedDay = formatDate();
    this.getData();
  },
  methods: {
    showRoute: function(){

    },
    getData: function(){
      return;
      ReadCompressed('https://cta-bus-and-train-tracker.s3.amazonaws.com/schedules/rail/Blue/latest.gz').then(function(data){
        debugger;
      })
      ReadCompressed('https://cta-bus-and-train-tracker.s3.amazonaws.com/bustracker/parsed/2022-05-17.zlib').then(function(data){
        this.trackerData = data;
        this.routes = [...new Set(data.map(x => x.rn.padStart(3, ' ')))].sort();
      })      
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
  ).then(function(response){
    let inflatedResponse = pako.inflate(response.data);
    let jsonString = Array.from(inflatedResponse).map((c) => String.fromCharCode(c)).join('');
    let data = JSON.parse(jsonString);
    return data;
  })
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