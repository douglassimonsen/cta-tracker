Vue.component('input-form', {
  template: `
  <div style="width:360px">
    <b-form-select v-model="selectedMode" :options="modes" class="mb-2"></b-form-select>
    <b-form-select v-model="selectedRoute" :options="availableRoutes" class="mb-2" :disabled="selectedMode === ''"></b-form-select>
    <b-form-select v-model="selectedDirection" :options="availableDirections" class="mb-2" :disabled="selectedRoute === ''"></b-form-select>
    <b-form-datepicker v-model="selectedDay" class="mb-2"></b-form-datepicker>
    <b-button @click="sendEvent('data')">Download Day's Data (Raw)</b-button>  
    <b-button @click="sendEvent('chart')">Show Route Info</b-button>  
  </div> 
  `,
  data: function(){
    return {
      rawData: [],
      modes: ['Bus', 'Rail'],
      selectedMode: 'Bus',
      selectedDay: '2022-06-23',
      selectedRoute: '8',
      selectedDirection: 'South',
    }
  },
  mounted: function(){
    this.getData();
  },
  computed: {
    availableRoutes: function(){
      let routes = this.rawData.filter(x => x.mode == this.selectedMode).map(x => x.route_id);
      routes = [...new Set(routes)].sort(function(a, b){
        return a.padStart(b.length, ' ') > b.padStart(a.length, ' ') ? 1 : -1;
      });
      return routes;
    },
    availableDirections: function(){
      return this.rawData.filter(x => x.route_id === this.selectedRoute).map(x => x.direction);
    },
  },
  methods: {
    getData: function(){
      axios.get('http://127.0.0.1:5000/api/routes', {}, {headers: {'Access-Control-Allow-Origin': "*"}}).then(function(response){
         this.rawData = response.data;
      }.bind(this));
    },
    sendEvent: function(evt){
      this.$emit('input', {
        route: this.selectedRoute,
        mode: this.selectedMode,
        direction: this.selectedDirection,
        date: this.selectedDay,
        event: evt,
      });
    },
  },
});