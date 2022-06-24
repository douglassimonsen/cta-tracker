Vue.component('input-form', {
  template: `
  <div style="width:360px">
    <b-form-select v-model="selectedMode" :options="modes" class="mb-2"></b-form-select>
    <b-form-select v-model="selectedRoute" :options="routes" class="mb-2"></b-form-select>
    <b-form-datepicker v-model="selectedDay" class="mb-2"></b-form-datepicker>
    <b-button @click="sendEvent('data')">Download Day's Data (Raw)</b-button>  
    <b-button @click="sendEvent('chart')">Show Route Info</b-button>  
  </div> 
  `,
  data: function(){
    return {
      modes: ['bus', 'train'],
      selectedMode: 'bus',
      selectedDay: null,
      routes: ['8'],
      selectedRoute: '8',
      selectedDirection: 'South',
    }
  },
  methods: {
    sendEvent: function(evt){
      this.$emit('input', {
        route: this.route,
        mode: this.mode,
        direction: this.direction,
        event: evt,
      });
    },
  },
});