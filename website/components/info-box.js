Vue.component('info-box', {
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
          <tr><td>Difference</td><td>{{diffFromSchedule}}</td></tr>
          <tr><td>Headway</td><td>{{headway}}</td></tr>
          <tr><td>Type</td><td>{{tripType}}</td></tr>
        </tbody>
      </table>
    </div>
  `,
  data: function(){
    return {
      stopName: 'test',
      stopTime: '12:34:56 PM',
      diffFromSchedule: '12 mins',
      headway: '13 mins',
      tripType: 'Scheduled',
    }
  }
})