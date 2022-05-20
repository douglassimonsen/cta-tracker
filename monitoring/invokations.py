import boto3
import datetime
logs = boto3.client("cloudwatch", region_name='us-east-1')


def get_logs():
    for resp in [[x['MetricName'], x['Dimensions']] for x in logs.list_metrics(
         Namespace='AWS/Lambda'
    )['Metrics']]:
        print(resp)
        pass
    response = logs.get_metric_data(
        MetricDataQueries=[
            {
                'Id': 'm1',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/Lambda',
                        'MetricName': 'Invocations',
                        'Dimensions': [
                            {
                                'Name': 'FunctionName',
                                'Value': 'test'
                            },
                            {
                                "Name": "Resource",
                                "Value": "test",
                            }
                        ]
                    },
                    'Period': 60,
                    "Stat": "Sum",
                },
            },
        ],
        StartTime=datetime.datetime.today() - datetime.timedelta(days=1),
        EndTime=datetime.datetime.today() + datetime.timedelta(days=1),
    )
    print(response)
    exit()

