import boto3
import datetime
import time
import json
from collections import defaultdict
logs = boto3.client("logs")


def get_logs():
    response = logs.start_query(
        logGroupName='/aws/lambda/test',
        queryString='''
        filter @type = "REPORT"
        | fields @timestamp as Timestamp, @requestId as RequestID, @logStream as LogStream, @duration as DurationInMS, @billedDuration as BilledDurationInMS, @memorySize/1000000 as MemorySetInMB, @maxMemoryUsed/1000000 as MemoryUsedInMB
        | sort Timestamp desc            
        ''',
        startTime=int((datetime.datetime.today() - datetime.timedelta(days=7)).timestamp()),
        endTime=int((datetime.datetime.today() + datetime.timedelta(days=1)).timestamp()),
        limit=100
    )
    queryID = response['queryId']
    status = 'Scheduled'
    while status in ('Scheduled', 'Running'):
        time.sleep(5)
        response = logs.get_query_results(queryId=queryID)
        status = response['status']
    data = response['results']
    data = [{x['field']: x['value'] for x in row} for row in data]
    return data


def process_insights(data):
    daily_spend = defaultdict(lambda: 0)
    for row in data:
        daily_spend[row['Timestamp'].strftime("%Y-%m-%d")] += 
    print(data[0])
    exit()
    return {
        'memory_usage': [float(x['MemoryUsedInMB']) for x in data],
        'duration': [float(x['BilledDurationInMS']) for x in data],
        'memory_allowed': data[0]['MemorySetInMB']
    }


def main():
    # data = get_logs()
    data = json.load(open("dump_memory.json"))
    for row in data:
        row['Timestamp'] = datetime.datetime.strptime(row['Timestamp'], '%Y-%m-%d %H:%M:%S.%f')
    return process_insights(data)


if __name__ == '__main__':
    print(main())