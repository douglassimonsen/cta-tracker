import requests
from bs4 import BeautifulSoup
import boto3
import datetime
import json
from urllib.parse import urlparse
s = requests.session()
s3 = boto3.client("s3")
# Retrieved from https://www.transitchicago.com/downloads/sch_data/

def load_to_s3(data, as_of, mode, route):
    data = json.dumps(data)
    s3.put_object(
        Body=data,
        Bucket='cta-bus-and-train-tracker',
        Key=f'schedules/{mode}/{route}/{as_of}.json',
    )





def main():
    pass


if __name__ == '__main__':
    main()