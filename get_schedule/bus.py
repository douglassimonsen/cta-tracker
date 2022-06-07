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


def parse_data(typ):
    def get_sources():
            data = read_csv("routes.txt")
            routes = [row for row in data if row['route_type'] == typ]
            trips = read_csv("trips.txt")

            shapes_raw = read_csv("shapes.txt")
            shapes = {}
            for row in shapes_raw:
                shapes.setdefault(row['shape_id'], []).append(row)

            stop_times_raw = read_csv("stop_times.txt")
            stop_times = {}
            for row in stop_times_raw:
                stop_times.setdefault(row['trip_id'], []).append(row)

            for route in routes:
                route_ret = {
                    k: route[k]
                    for k in ['route_short_name', 'route_long_name', 'route_url', 'route_color']
                }
                route_ret['trips'] = {
                    trip['trip_id']: {
                        'stops': stop_times[trip['trip_id']],
                        'shape': shapes[trip['trip_id']],
                    }
                for trip in trips}
                print("\n" * 5)
                # print(route_ret)
                # shape_ids = list(set(t['shape_id'] for t in trips))
                exit()
            print(trips[0])
            exit()


    typ = {
        'Bus': '3',
        'Rail': '1'
    }[typ]
    get_sources()
    print(routes[0])


def main():
    # get_data()
    parse_data('Bus')


if __name__ == '__main__':
    main()