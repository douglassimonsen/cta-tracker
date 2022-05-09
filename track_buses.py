import json
import requests
import bs4
import datetime
import bz2
import concurrent.futures
import boto3
stops = json.load(open('bus-stops.json'))
stops = set(stop['id'] for route_data in stops.values() for dir_stops in route_data['stops'].values() for stop in dir_stops)
s3 = boto3.client("s3")


def get_bustracker(stop_id: int):
    ret = []
    resp = requests.get(f'http://www.ctabustracker.com/bustime/eta/getStopPredictionsETA.jsp?route=all&stop={stop_id}', timeout=15).text
    response_at = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
    if '<noPredictionMessage>' in resp:
        return ret
    page = bs4.BeautifulSoup(resp, 'html.parser')
    for stop in page.find_all("stop"):
        stop_attrs = [x for x in stop.find("pre").children][1:]
        row = {
            x.name: x.text.strip()
            for x in stop_attrs
            if x.name is not None
        }

        if 'mode' in row:
            row['mode'] = int(row['mode'])
        row['response_at'] = response_at
        row['stop_id'] = stop_id
        ret.append(row)
    return ret


def get_data():
    jobs = []
    ret = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for stop in stops:
            jobs.append(executor.submit(get_bustracker, stop_id=stop))
        for future in concurrent.futures.as_completed(jobs):
            ret.append(future.result())
    return [row for chunk in ret for row in chunk]


def save_data(data: list[dict]):
    data = json.dumps(data)
    data = bz2.compress(data.encode())
    chunk_timestamp = datetime.datetime.utcnow()
    chunk_timestamp -= datetime.timedelta(minutes=chunk_timestamp.minute % 5, seconds=chunk_timestamp.second)
    chunk_timestamp = chunk_timestamp.strftime("%Y-%m-%d/%H-%M-%S")
    s3.put_object(
        Body=data,
        Bucket='cta-bus-and-train-tracker',
        Key=f'bustracker/{chunk_timestamp}.bz2',
    )


def main():
    data = get_data()
    print(len(data))
    save_data(data)


if __name__ == "__main__":
    main()