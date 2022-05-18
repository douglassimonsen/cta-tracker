import requests
from bs4 import BeautifulSoup
import boto3
import datetime
import json
from urllib.parse import urlparse
s = requests.session()
s3 = boto3.client("s3")


def load_to_s3(data, as_of, mode, route):
    data = json.dumps(data)
    s3.put_object(
        Body=data,
        Bucket='cta-bus-and-train-tracker',
        Key=f'schedules/{mode}/{route}/{as_of}.json',
    )


def get_routes():
    def parse_row(row):
        return [x.text.strip() for x in row.children if x.text.strip() != '']

    resp = s.get('https://www.transitchicago.com/search/?contenttype=Route')
    page = BeautifulSoup(resp.text, 'lxml')
    pages = int(page.find("span", {"class": "total"}).text.split()[-1])
    sched_links = []
    for i in range(1, pages + 1):
        resp = s.get(f'https://www.transitchicago.com/search/?contenttype=Route&mpp=24&pg={i}')
        schedules = BeautifulSoup(resp.text, 'lxml').find_all("div", {"class": "hawk-contentTitle"})
        for sched_link in schedules:
            first_link = sched_link.find("a")['href']
            print(first_link)
            resp = s.get(first_link)
            sched_page = BeautifulSoup(resp.text, 'lxml')
            link = sched_page.find(
                lambda tag: tag.name == 'a' and 
                tag.get("href", "").endswith(".htm") and 
                tag.get("id", "").startswith("CT_Main_0_rptAttachments_ctl")
            )
            if link is not None:
                link = link['href']
                sched_links.append('https://' + urlparse(resp.url).hostname + link.replace('\\', '/'))

    for sched_link in sched_links:
        if 'line' in sched_link:
            pass
        else:
            print(sched_link)
            resp = s.get(sched_link)
            page = BeautifulSoup(resp.text, 'lxml')
            info = page.find("table")
            rows = list(info.find_all("tr"))
            columns = parse_row(rows.pop(0))
            table = [dict(zip(columns, parse_row(row))) for row in rows]
            route = page.find("h1").text.split()[-1].replace('#', '')
            as_of = page.find("p").text.split()[-1]
            as_of = datetime.datetime.strptime(as_of, '%m/%d/%Y').strftime("%Y-%m-%d")
            load_to_s3(table, as_of, 'bus', route)


def main():
    get_routes()


if __name__ == '__main__':
    main()