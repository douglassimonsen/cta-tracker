select '{date}'::date + st.arrival_time as arrival_time,
       st.trip_id,
       st.stop_id,
       st.stop_sequence,
       st.shape_dist_traveled
from cta_tracker.trips t 

left join cta_tracker.calendar c 
on t.service_id = c.service_id

left join cta_tracker.stop_times st 
on t.trip_id = st.trip_id

where t.route_id = '{route}'
and '{date}' between c.start_date and c.end_date
and (
	date_part('dow', '{date}'::date) = 0 and c.sunday is True or
	date_part('dow', '{date}'::date) = 1 and c.monday is True or
	date_part('dow', '{date}'::date) = 2 and c.tuesday is True or
	date_part('dow', '{date}'::date) = 3 and c.wednesday is True or
	date_part('dow', '{date}'::date) = 4 and c.thursday is True or
	date_part('dow', '{date}'::date) = 5 and c.friday is True or
	date_part('dow', '{date}'::date) = 6 and c.saturday is true
)
and direction = '{direction}'