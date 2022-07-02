import requests
import json
import psycopg2
import os, pathlib
os.chdir(pathlib.Path(__file__).parent)
envs = json.load(open("../../env.json"))
ROUTES = {
    'red': 307,
    'blue': 310,
    'brown': 313,
    'green': 312,
    'orange': 314,
    'pink': 311,
    'purple': 308,
    'yellow': 309,
}


def get_conn():
    return psycopg2.connect(
        **envs['db']
    )


def parse_route_stops(route):
    resp = requests.post('https://www.transitchicago.com/ajax/traintracker/ajax.aspx', data={
        'f': 'GetStops',
        'RouteId': ROUTES[route],
    })
    data = json.loads(resp.text)
    return [{
        'stop_id': stop.split(';')[0],
        'stop_name': stop.split(';')[1],
        'route': route,
    } for stop in data['Stops']]


def main():
    data = []
    for route in ROUTES.keys():
        data.extend(parse_route_stops(route))
    for row in data:
        row['scheduled_stop_id'] = 1

    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("truncate cta_tracker.stops_actual")
        cursor.executemany("insert into cta_tracker.stops_actual (stop_id, scheduled_stop_id, stop_name, route) values (%(stop_id)s, %(scheduled_stop_id)s, %(stop_name)s, %(route)s)", data)
        conn.commit()

if __name__ == '__main__':
    main()