import zipfile
import requests
import boto3
import json
import csv
import io
s = requests.session()
s3 = boto3.client("s3")
# Retrieved from https://www.transitchicago.com/downloads/sch_data/

def load_to_s3(data, as_of, mode, route):
    data = json.dumps(data)
    s3.put_object(
        Body=data,
        Bucket='cta-bus-and-train-tracker',
        Key=f'schedules/{mode}/{route}/{as_of}.json',
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
        stop_times_raw = read_csv("stop_times.txt")
        stop_times = {}
        for row in stop_times_raw:
            stop_times.setdefault(row['trip_id'], []).append(row)
        return stop_times

    def parse_trips():
        raw_trips = read_csv("trips.txt")
        trips = {}
        for trip in raw_trips:
            trips.setdefault(trip['route_id'], []).append({
                k: trip[k] 
                for k in ['trip_id', 'direction_id', 'shape_id', 'direction']
            })
        return trips

    modes = {
        '3': 'Bus',
        '1': 'Rail'
    }

    shapes = parse_shapes()
    routes = parse_routes()
    trips = parse_trips()
    stops = parse_stops()

    ret = []
    for route in routes:
        print(route['route_id'])
        route_trips = trips[route['route_id']]
        for trip in route_trips:
            trip['stops'] = stops[trip['trip_id']]
        shape_ids = set(x['shape_id'] for x in route_trips)
        route_ret = {
            'id': route['route_id'],
            'name': route['route_long_name'],
            'color': route['route_color'],
            'shapes': {
                shape_id: shapes[shape_id]
                for shape_id in shape_ids
            },
            'trips': route_trips
        }
        load_to_s3(
            route_ret,
            'latest',
            modes[route['route_type']],
            route['route_id'],
        )
            


def main():
    # get_data()
    parse_data()


if __name__ == '__main__':
    main()