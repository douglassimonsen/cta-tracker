import matplotlib.pyplot as plt
import matplotlib as mpl
from pprint import pprint
import os
import jinja2
os.chdir(os.path.dirname(__file__))
data = {
    "by_date": {
        "2022-05-16": 0.107317231,
        "2022-05-17": 1.4669655385,
        "2022-05-18": 2.9601648132000005,
        "2022-05-19": 12.2797621136,
        "2022-05-20": 9.770019828999999,
        "2022-05-21": 1.042384512,
        "2022-05-22": 0.9081807231
    },
    "top_5_by_day": {
        "2022-05-16": {
            "other": 0.0,
            "AWS Lambda": 0.0913777598,
            "Amazon Relational Database Service": 0.0124392088,
            "Amazon Simple Storage Service": 0.0035002624,
            "AmazonCloudWatch": 0.0
        },
        "2022-05-17": {
            "other": 0.0,
            "AWS Lambda": 0.9352111374,
            "Amazon Relational Database Service": 0.5281410035,
            "Amazon Simple Storage Service": 0.0036133976,
            "AmazonCloudWatch": 0.0
        },
        "2022-05-18": {
            "other": 0.0001,
            "AWS Lambda": 0.9321340586,
            "Amazon Relational Database Service": 2.0233754271,
            "Amazon Simple Storage Service": 0.0043353275,
            "AmazonCloudWatch": 0.00022
        },
        "2022-05-19": {
            "other": 0.0,
            "AWS Lambda": 0.9478803881,
            "Amazon Relational Database Service": 11.3288652089,
            "Amazon Simple Storage Service": 0.0030165166,
            "AmazonCloudWatch": 0.0
        },
        "2022-05-20": {
            "AWS Cost Explorer": 0.09,
            "other": 0.0,
            "AWS Lambda": 0.9305107013,
            "Amazon Relational Database Service": 8.7464755244,
            "Amazon Simple Storage Service": 0.0030236033,
            "AmazonCloudWatch": 1e-05
        },
        "2022-05-21": {
            "AWS Cost Explorer": 0.14,
            "other": 0.0,
            "AWS Lambda": 0.8993531745,
            "Amazon Simple Storage Service": 0.0030313375,
            "AmazonCloudWatch": 0.0
        },
        "2022-05-22": {
            "other": 0.0,
            "AWS Lambda": 0.9051411902,
            "Amazon Simple Storage Service": 0.0030395329,
            "AmazonCloudWatch": 0.0
        }
    },
    "by_service": {
        "AWS Glue": 0.0,
        "AWS Lambda": 5.6416084099,
        "Amazon Relational Database Service": 22.6392963727,
        "Amazon Simple Storage Service": 0.023559977799999996,
        "AmazonCloudWatch": 0.00023,
        "Amazon Simple Email Service": 0.0001,
        "AWS Cost Explorer": 0.23,
        "AWS Key Management Service": 0.0
    }
}


def daily_spending():
    vals = data['by_date'].values()
    return
    color_func = mpl.cm.ScalarMappable(
        norm=mpl.colors.Normalize(vmin=0, vmax=max(vals)), 
        cmap=mpl.cm.cool
    )
    fig, axs = plt.subplots(figsize = (9, 3)) 
    plt.bar(
        x=data['by_date'].keys(), 
        height=vals, 
        color=[color_func.to_rgba(x) for x in vals]
    )
    plt.show()


def daily_table():
    template = jinja2.Template(open('../templates/table.html').read())
    vals = data['top_5_by_day']
    headers = list(vals.keys())
    index = list(vals[list(vals.keys())[0]].keys())
    table = [[round(vals[day].get(resource, 0), 3) for day in headers] for resource in index]
    table = [[x or '' for x in row] for row in table]
    return template.render(
        index=index,
        headers=headers,
        table=table
    )


def main():
    return {
        'daily_spending': daily_spending(),
        'daily_table': daily_table(),
    }


if __name__ == '__main__':
    main()