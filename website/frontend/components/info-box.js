Vue.component('info-box', {
  props: ['info'],
  template: `
    <div id="info-box">
      <table>
        <thead>
          <tr>
            <th colspan=2>Stop Info</th>
          </tr>
        </thead>
        <tbody>
          <tr><td>Stop</td><td>{{stopName}}</td></tr>
          <tr><td>Time</td><td>{{stopTime}}</td></tr>
          <tr><td>Difference</td><td>{{diffFromSchedule}} mins</td></tr>
          <tr><td>Headway</td><td>{{headway}} mins</td></tr>
          <tr><td>Type</td><td>{{tripType}}</td></tr>
        </tbody>
      </table>
    </div>
  `,
  computed: {
    stopName: function(){
      return this.info.stopName || 'Idk';
    },
    stopTime: function(){
      return formatDt(this.info.stopTime) || 'Idk';
    },
    diffFromSchedule: function(){
      return round(this.info.diffFromSchedule, 2) || 'Idk';
    },
    headway: function(){
      return round(this.info.headway, 2) || 'Idk';
    },
    tripType: function(){
      return this.info.tripType || 'Idk';
    },
  },
});