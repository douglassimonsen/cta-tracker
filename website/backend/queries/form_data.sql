select distinct route_id, 
    direction,
    case when route_id in ('Blue', 'Brn', 'G', 'Org', 'P', 'Pink', 'Red', 'Y') then 'Rail' else 'Bus' end as mode
from cta_tracker.trips
order by route_id, direction