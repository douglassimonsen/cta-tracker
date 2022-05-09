import requests
import bs4
import json


def get_routes():
    resp = requests.get('http://www.ctabustracker.com/bustime/eta/eta.jsp').text
    routes = resp.split('new cd.Route( //@24')[1:]
    route_dict = {}
    for route in routes:
        route = [x.strip()[1:-2] for x in route.split('\n')[:5]]
        route_dict[route[4]] = route[1]
    return route_dict


def get_stops(route_id):
    resp = requests.get(
        'http://www.ctabustracker.com/bustime/map/getDirectionsStopsForRoute.jsp',
        params={'route': route_id, 'key': '0.4174186326026963'},
    ).text
    payload = bs4.BeautifulSoup(resp, 'lxml')
    directions = payload.find_all('direction')
    ret = {}
    for direction in directions:
        dir_name = direction.find('name').text
        stop_list = []
        for stop in direction.find_all('stop'):
            stop_list.append({
                'name': stop.find('name').text,
                'id': stop.find('id').text
            })
        ret[dir_name] = stop_list
    return ret


route_dict = get_routes()
stop_dict = {}
for route_name, route_id in route_dict.items():
    stop_dict[route_id] = {
        "stops": get_stops(route_id),
        "name": route_name
    }
json.dump(stop_dict, open('bus-stops.json', 'w'), indent=4)