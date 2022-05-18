import boto3
import os; os.chdir(os.path.dirname(os.path.abspath(__file__)))
s3 = boto3.client("s3")
page = open("page.html").read()
s3.put_object(
    Body=page,
    Bucket='cta-bus-and-train-tracker',
    Key=f'page.html',
    ACL='public-read',
    ContentType='text/html'
)