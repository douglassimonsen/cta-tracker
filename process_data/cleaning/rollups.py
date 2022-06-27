import json
import datetime
import bz2
import boto3
s3_bucket = boto3.resource("s3").Bucket('cta-bus-and-train-tracker')
s3_client = boto3.client("s3")


def rollup(folder: str, today: str=None):
    if today is None:
        today = (datetime.datetime.utcnow() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    ret = []
    for obj in s3_bucket.objects.filter(Prefix=f'{folder}/{today}'):
        resp = s3_client.get_object(Bucket='cta-bus-and-train-tracker', Key=obj.key)['Body'].read()
        data = json.loads(bz2.decompress(resp))
        for row in data:
            row['source'] = obj.key
        ret.append(data)
    ret = [row for chunk in ret for row in chunk]
    ret = json.dumps(ret)
    ret = bz2.compress(ret.encode())
    s3_client.put_object(
        Body=ret,
        Bucket='cta-bus-and-train-tracker',
        Key=f'{folder}/rollup/{today}.bz2',
    )


def historical_recalc(folder):
    day_dict = {}
    days  = {x.key.split('/')[1] for x in s3_bucket.objects.filter(Prefix=folder)}
    for d in sorted(days):
        print(folder, d)
        rollup(folder, d)

def main():
    for x in ['traintracker', 'bustracker']:
        rollup(x)


if __name__ == '__main__':
    main()