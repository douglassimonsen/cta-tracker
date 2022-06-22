import boto3
import json
import bz2
import datetime
import requests
import bs4
import concurrent.futures
s3 = boto3.client("s3")
stops = json.load(open('train-stops.json'))
stops = set(stop for line in stops.values() for stop in line.values())


def get_traintracker(stop_id: int):
    try:
        resp = requests.get(f'https://www.transitchicago.com/traintracker/arrivaltimes/?sid={stop_id}', timeout=30).text
    except requests.ReadTimeout:
        return []

    ret = []
    response_at = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
    page = bs4.BeautifulSoup(resp, 'html.parser')
    for train in page.find_all("a", {"class": "estimated-arrivals-line"}):
        print(stop_id)
        estimate_type = train.find("use")
        if estimate_type is not None:  # in the case where there's no estimate at all (just "---"), there's no estimate type
            estimate_type = estimate_type['xlink:href']
        ret.append({
            'route': train.find('span', {'class': "ea-line-title-top"}).text.strip(),
            "destination": train.find("span", {"class": "ea-line-title-bottom"}).text.strip(),
            "wait_time": train.find("span", {"class": "ea-line-time"}).text.strip(),
            "estimate_type": estimate_type,
            'stop_id': stop_id,
            'response_at': response_at
        })
    return ret


def get_data():
    jobs = []
    ret = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for stop in stops:
            jobs.append(executor.submit(get_traintracker, stop_id=stop))
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
        Key=f'traintracker/{chunk_timestamp}.bz2',
    )    


def main():
    data = get_data()
    print(len(data))
    save_data(data)


if __name__ == '__main__':
    main()