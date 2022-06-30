select ss.stop_id, 
       ss.shape_dist_traveled,
       s.stop_name
from cta_tracker.scheduled_stops ss

left join cta_tracker.stops s 
on ss.stop_id = s.stop_id 

where ss.route_id = '{route}'
and ss.direction = '{direction}'
order by ss.stop_sequence 