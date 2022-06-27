import flask
from app import app
import utils
query_dict = {
    'routes': '''
    select distinct route_id, direction 
    from cta_tracker.trips
    order by route_id, direction    
    '''
}

@app.route('/api/routes')
def api_routes():
    with utils.get_conn() as conn:
        return flask.jsonify(utils.run_query(conn, query_dict['routes']))
