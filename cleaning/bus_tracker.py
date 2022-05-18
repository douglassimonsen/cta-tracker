import boto3
import datetime
import json
import bz2
import zlib
s3_client = boto3.client("s3")
DT_FORMAT = '%Y-%m-%dT%H:%M:%S'

def deserialize(row):
    row['response_at'] = datetime.datetime.strptime(row['response_at'], DT_FORMAT)
    row['pt'] = int(row['pt']) if row['pt'] != '&nbsp;' else 0
    row['estimated_arrival'] = row['response_at'] + datetime.timedelta(minutes=row['pt'])
    return row


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
    ret['estimates'] = [
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
    data = zlib.compress(data.encode())
    s3_client.put_object(
        Body=data,
        Bucket='cta-bus-and-train-tracker',
        Key=f'bustracker/parsed/{yesterday}.zlib',
    )


def main():
    yesterday = (datetime.datetime.utcnow() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    raw = s3_client.get_object(
        Bucket='cta-bus-and-train-tracker', 
        Key=f'bustracker/rollup/{yesterday}.bz2',
    )['Body'].read()
    data = json.loads(bz2.decompress(raw))
    data = [deserialize(row) for row in data]
    stop_info = {}
    for row in data:
        stop_info.setdefault((row['rn'], row['stop_id'], row['v']), []).append(row)

    ret = []
    for estimates in stop_info.values():
        grouped_estimates = condense_estimates(estimates)
        ret.extend(summarize(x) for x in grouped_estimates)
    load_to_s3(ret)


if __name__ == '__main__':
    main()