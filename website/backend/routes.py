import flask
from app import app
import utils
query_dict = {
    k: open(f'queries/{k}.sql').read()
    for k in  ['form_data', 'schedule', 'stop_order']
}


@app.route('/api/routes', methods=['GET', 'POST'])
def api_routes():
    with utils.get_conn() as conn:
        return flask.jsonify(utils.run_query(conn, query_dict['form_data']))


@app.route('/api/stop_order', methods=['GET', 'POST'])
def api_stop_order():
    args = flask.request.get_json()
    with utils.get_conn() as conn:
        return flask.jsonify(utils.run_query(conn, query_dict['stop_order'].format(**args)))


@app.route('/api/schedule', methods=['GET', 'POST'])
def api_stops():
    args = flask.request.get_json()
    with utils.get_conn() as conn:
        data = utils.run_query(conn, query_dict['schedule'].format(**args))
    return flask.jsonify(data)