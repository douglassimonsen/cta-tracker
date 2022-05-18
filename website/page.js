new Vue({
  el: '#page',
  data: {
    routes: [],
    modes: ['bus', 'train'],
    selectedMode: 'bus',
    selectedDay: null
  },
  mounted: function(){
    this.selectedDay = formatDate();
    debugger;
  },
  methods: {
    getData: function(){
      
    }
  }

});

function formatDate(dt){
  if(!dt){
    dt = new Date();
  }
  let year = dt.getFullYear().toString().padStart(2, '0')
  let month = (new Date().getMonth() % 12 + 1).toString().padStart(2, '0');
  let day = dt.getDate().toString().padStart(2, '0')
  return `${year}-${month}-${day}`;
}