import requests
import bs4
import json


def get_lines():
    resp = requests.get('https://www.transitchicago.com/traintracker/').text
    page = bs4.BeautifulSoup(resp, 'lxml')
    routes = page.find_all('input', {'value': 'rbRoute'})
    return {
        x['data-classname']: int(x['data-rid'])
        for x in routes
    }


def get_stops(line_id: int):
    resp = requests.post(
        'https://www.transitchicago.com/ajax/traintracker/ajax.aspx',
        data={
            'f': 'GetStops',
            'RouteId': line_id
        }
    ).text
    data = json.loads(resp)
    stops = [x.split(';') for x in data['Stops']]
    return dict([x[1], int(x[0])] for x in stops)


line_data = {}
lines = get_lines()
for line_name, line_id in lines.items():
    line_data[line_name] = get_stops(line_id)
json.dump(line_data, open('train-stops.json', 'w'), indent=4)