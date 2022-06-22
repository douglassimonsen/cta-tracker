import boto3
import datetime
from collections import defaultdict
import json
ce = boto3.client('ce')


def get_costs():
    response = ce.get_cost_and_usage(
        TimePeriod={
            'Start': (datetime.datetime.today() - datetime.timedelta(days=7)).strftime("%Y-%m-%d"),
            'End': datetime.datetime.today().strftime("%Y-%m-%d"),
        },
        Granularity='DAILY',
        Metrics=['BlendedCost'],
        GroupBy=[
            {
                'Type': 'DIMENSION',
                'Key': 'SERVICE'
            },
            {
                'Type': 'TAG',
                'Key': 'Project'
            }
        ]
    )
    by_date = defaultdict(lambda: 0)
    by_service = defaultdict(lambda: 0)
    top_5_by_day = defaultdict(lambda: defaultdict(lambda: 0))
    top_5_by_day_final = defaultdict(lambda: defaultdict(lambda: 0))

    for day in response['ResultsByTime']:
        for cost_center in day['Groups']:
            cost = float(cost_center['Metrics']['BlendedCost']['Amount'])
            by_date[day['TimePeriod']['Start']] += cost
            top_5_by_day[day['TimePeriod']['Start']][cost_center['Keys'][0]] += cost
            by_service[cost_center['Keys'][0]] += cost
    top_5_services = [x[0] for x in sorted(by_service.items(), key=lambda x: -x[1])][:5]
    for day, day_dict in top_5_by_day.items():
        for resource, cost in day_dict.items():
            if resource in top_5_services:
                top_5_by_day_final[day][resource] += cost
            else:
                top_5_by_day_final[day]['other'] += cost
    top_5_by_day_final = {
        key1: {
            key2: round(val, 3) for key2, val in val_dict.items()
        } for key1, val_dict in top_5_by_day_final.items()
    }
    return {
        'by_date': by_date,
        'top_5_by_day': top_5_by_day_final,
        'by_service': by_service
    }


def main():
    return json.load(open('dump_cost.json'))
    ret = get_costs()
    json.dump(ret, open('dump_cost.json', 'w'), indent=4)
    return ret


if __name__ == '__main__':
    main()