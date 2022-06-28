import flask
from app import app
import utils
query_dict = {
    'routes': '''
    select distinct route_id, 
        direction,
        case when route_id in ('Blue', 'Brn', 'G', 'Org', 'P', 'Pink', 'Red', 'Y') then 'Rail' else 'Bus' end as mode
    from cta_tracker.trips
    order by route_id, direction
    '''
}

@app.route('/api/routes', methods=['GET', 'POST'])
def api_routes():
    with utils.get_conn() as conn:
        return flask.jsonify(utils.run_query(conn, query_dict['routes']))
