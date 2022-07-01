select distinct route_id, 
    direction,
    mode
from cta_tracker.trips
order by route_id, direction