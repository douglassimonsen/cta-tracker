import zipfile
import requests
import boto3
import json
import csv
import io
import bz2
from pprint import pprint as print
import os; os.chdir(os.path.dirname(os.path.abspath(__file__)))
s = requests.session()
s3 = boto3.client("s3")
# Retrieved from https://www.transitchicago.com/downloads/sch_data/
DOW = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']


def load_to_s3(data, path):
    data = bz2.compress(json.dumps(data).encode("utf-8"))
    s3.put_object(
        Body=data,
        Bucket='cta-bus-and-train-tracker',
        Key=path,
        ACL='public-read',
    )


def get_data():
    with open("sched.zip", "wb") as f:
        f.write(requests.get("https://www.transitchicago.com/downloads/sch_data/google_transit.zip").content)


def read_csv(source):
    with zipfile.ZipFile("sched.zip") as zf:
        source_data = zf.read(source).decode("utf-8")
        routes_raw = io.StringIO()
        routes_raw.write(source_data)
        routes_raw.seek(0)
        return list(csv.DictReader(routes_raw))


def parse_data():
    def parse_shapes():
        raw_shapes = read_csv("shapes.txt")
        shapes = {}
        for row in raw_shapes:
            shapes.setdefault(row['shape_id'], []).append(row)
        return shapes

    def parse_routes():
        return read_csv("routes.txt")

    def parse_stops():
        raw_stops = read_csv("stops.txt")
        return {
            row['stop_id']: {
                "name": row['stop_name'],
                "lat": row['stop_lat'],
                "lon": row['stop_lon']
            }
            for row in raw_stops
        }

    def parse_stop_times():
        stop_times_raw = read_csv("stop_times.txt")
        stop_times = {}
        for row in stop_times_raw:
            stop_times.setdefault(row['trip_id'], []).append(row)
        return stop_times

    def parse_trips():
        raw_trips = read_csv("trips.txt")
        route_schedules = parse_route_days()
        trips = {}
        for trip in raw_trips:
            schedule = route_schedules[trip['service_id']]
            print(schedule)
            exit()
            trips.setdefault(trip['route_id'], []).append({
                k: trip[k] 
                for k in ['trip_id', 'direction', 'shape_id', 'direction', 'service_id']
            })
        return trips

    def get_trip_info(route, route_trips):
        route_stops = set()
        route_orders = {}
        for trip in route_trips:
            trip['stop_times'] = stop_times[trip['trip_id']]
            if trip['direction'] not in route_orders or len(trip['stop_times']) > len(route_orders[trip['direction']]):  # now we're choosing the longest per direction
                route_orders[trip['direction']] = [{"stop_id": x['stop_id'], 'dist': x['shape_dist_traveled']} for x in trip['stop_times']]
            route_stops.update([x['stop_id'] for x in stop_times[trip['trip_id']]])
        return route_trips, route_stops, route_orders

    def parse_route_days():
        data = read_csv("calendar.txt")
        return {row['service_id']: row for row in data}

    modes = {
        '3': 'bus',
        '1': 'rail'
    }

    # shapes = parse_shapes()
    routes = parse_routes()
    trips = parse_trips()
    stops = parse_stops()
    stop_times = parse_stop_times()

    ret = []
    full_stop_orders = {}
    for route in routes:
        print(route['route_id'])
        route_trips, route_stops, route_orders = get_trip_info(route, trips[route['route_id']])
        # shape_ids = set(x['shape_id'] for x in route_trips)
        full_stop_orders[route['route_id']] = {
            'orders': route_orders,
            'stops': {stop: stops[stop] for stop in route_stops},
        }
        route_ret = {
            'id': route['route_id'],
            'name': route['route_long_name'],
            'color': route['route_color'],
            # 'shapes': { shape_id: shapes[shape_id] for shape_id in shape_ids},
            'stops': {stop: stops[stop] for stop in route_stops},
            'stop_order': route_orders,
            'trips': route_trips
        }
        load_to_s3(
            route_ret,
            f"schedules/{modes[route['route_type']]}/{route['route_id']}/latest.bz2"
        )
    load_to_s3(
        full_stop_orders,
        'schedules/stop_order/latest.bz2',
    )


def main():
    # get_data()
    parse_data()


if __name__ == '__main__':
    main()