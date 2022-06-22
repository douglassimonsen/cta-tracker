import boto3
import datetime
import json
import bz2
s3_client = boto3.client("s3")
DT_FORMAT = '%Y-%m-%dT%H:%M:%S'


def condense_estimates(estimates):
    estimates = list(sorted(estimates, key=lambda est: est['estimated_arrival']))
    chunked_estimates = []
    last_estimate = None
    for i, estimate in enumerate(estimates):
        if last_estimate is None:
            last_estimate = {
                'estimated_arrival': estimate['estimated_arrival'],
                'index': i
            }
        elif estimate['estimated_arrival'] > last_estimate['estimated_arrival'] + datetime.timedelta(minutes=15):
            chunked_estimates.append(
                estimates[last_estimate['index']:i]
            )
            last_estimate = {
                'estimated_arrival': estimate['estimated_arrival'],
                'index': i
            }
    chunked_estimates.append(
        estimates[last_estimate['index']:]
    )
    return chunked_estimates


def summarize(estimate_chunk):
    ret = estimate_chunk.pop(-1)
    ret['previous_estimates'] = [
        {
            'response_diff': (estimate['response_at'] - estimate_chunk[-1]['response_at']).total_seconds(),
            'estimate_diff': (estimate['estimated_arrival'] - estimate_chunk[-1]['estimated_arrival']).total_seconds(),
        } for estimate in estimate_chunk
    ]
    ret['response_at'] = ret['response_at'].strftime(DT_FORMAT)
    ret['estimated_arrival'] = ret['estimated_arrival'].strftime(DT_FORMAT)
    return ret


def load_to_s3(data):
    yesterday = (datetime.datetime.utcnow() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    data = json.dumps(data)
    data = bz2.compress(data.encode())
    s3_client.put_object(
        Body=data,
        Bucket='cta-bus-and-train-tracker',
        Key=f'bustracker/parsed/{yesterday}.bz2',
    )


def get_raw(dt, transit_mode):
    def deserialize_bus(row):
        row['response_at'] = datetime.datetime.strptime(row['response_at'], DT_FORMAT)
        row['pt'] = int(row['pt']) if row['pt'] != '&nbsp;' else 0
        row['estimated_arrival'] = row['response_at'] + datetime.timedelta(minutes=row['pt'])
        return {
            'route': row['rn'],
            'destination': row['rd'],
            'response_at': row['response_at'],
            'estimated_arrival': row['estimated_arrival'],
            'estimate_type': '#icon-wifi',
            'stop_id': row['stop_id'],
            'vehicle_id': row['v'],
        }

    def deserialize_train(row):
        row['response_at'] = datetime.datetime.strptime(row['response_at'], DT_FORMAT)
        row['wait_time'] = 0 if row['wait_time'] in ('Due', '< 1 min', '---', 'Delayed') else int(row['wait_time'].split(' ')[0]) 
        row['estimated_arrival'] = row['response_at'] + datetime.timedelta(minutes=row['wait_time'])
        return {
            'route': row['route'].split()[0],
            'destination': row['destination'],
            'response_at': row['response_at'],
            'estimated_arrival': row['estimated_arrival'],
            'estimate_type': row['estimate_type'],
            'stop_id': row['stop_id'],
            'vehicle_id': row['route'].split()[2],
        }

    raw = s3_client.get_object(
        Bucket='cta-bus-and-train-tracker', 
        Key=f'{transit_mode}tracker/rollup/{dt}.bz2',
    )['Body'].read()
    data = json.loads(bz2.decompress(raw))
    deserializer = {'bus': deserialize_bus, 'train': deserialize_train}[transit_mode]
    return [deserializer(row) for row in data]


def process_data(data):
    stop_info = {}
    for row in data:
        stop_info.setdefault((row['route'], row['destination'], row['stop_id'], row['vehicle_id']), []).append(row)
    ret = {}
    for key, estimates in stop_info.items():
        grouped_estimates = condense_estimates(estimates)
        ret.setdefault(key[0], {}).setdefault(key[1], []).extend(summarize(x) for x in grouped_estimates)
    for route, route_info in ret.items():
        for direction, direction_info in route_info.items():
            print(direction_info[0])
            exit()


def train_preprocessing(data):
    for row in data:
        if row['route'] in ('Orange', 'Brown', 'Pink'):
            row['destination'] = 'Loop'
    return data


def bus_preprocessing(data):
    return data


def get_schedule_stops():
    raw = s3_client.get_object(
        Bucket='cta-bus-and-train-tracker', 
        Key=f'schedules/stop_order/latest.bz2',
    )['Body'].read()
    return json.loads(bz2.decompress(raw))


def main():
    yesterday = (datetime.datetime.utcnow() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    schedule_stops = get_schedule_stops()
    for typ in ['train', 'bus']:
        data = get_raw(yesterday, typ)
        data = {'train': train_preprocessing, 'bus': bus_preprocessing}[typ](data)
        data = process_data(data)
        print
        exit()
        load_to_s3(data)


if __name__ == '__main__':
    main()