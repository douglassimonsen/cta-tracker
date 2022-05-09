import json
import requests
import bs4
import datetime
import bz2
stops = json.load(open('bus-stops.json'))
stops = set(stop['id'] for route_data in stops.values() for dir_stops in route_data['stops'].values() for stop in dir_stops)


def get_bustracker(stop_id: int):
    ret = []
    resp = requests.get(f'http://www.ctabustracker.com/bustime/eta/getStopPredictionsETA.jsp?route=all&stop={stop_id}').text
    response_at = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
    if '<noPredictionMessage>' in resp:
        return ret
    page = bs4.BeautifulSoup(resp, 'lxml')
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
        ret.append(row)
    return ret


def get_data():
    ret = []
    for stop in list(stops)[:20]:
        ret.append(get_bustracker(stop))
    return [row for chunk in ret for row in chunk]


def save_data(data: list[dict]):
    data = json.dumps(data)
    data = bz2.compress(data.encode())
    chunk_timestamp = datetime.datetime.utcnow()
    chunk_timestamp -= datetime.timedelta(minutes=chunk_timestamp.minute % 5, seconds=chunk_timestamp.second)
    chunk_timestamp = chunk_timestamp.strftime("%Y-%m-%dT%H-%M-%S")
    with open(f'data/{chunk_timestamp}.bz2', 'wb') as f:
        f.write(data)


def main():
    data = get_data()
    save_data(data)


if __name__ == "__main__":
    main()