import json
import datetime
import bz2
import boto3
s3_bucket = boto3.resource("s3").Bucket('cta-bus-and-train-tracker')
s3_client = boto3.client("s3")


def main():
    today = datetime.datetime.utcnow().strftime("%Y-%m-%d")  # will need to switch to yesterday in PROD
    ret = []
    for obj in s3_bucket.objects.filter(Prefix=f'bustracker/{today}'):
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
        Key=f'bustracker/rollup/{today}.bz2',
    )


if __name__ == '__main__':
    main()