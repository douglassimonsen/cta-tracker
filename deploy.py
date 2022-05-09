import zipfile
import os
import boto3
main_files = [
    'bus-stops.json',
    'train-stops.json',
    'track_buses.py',
    'track_trains.py',
    'rollups.py',
    'main.py',
]
s3 = boto3.client('s3')
with zipfile.ZipFile('deploy.zip', 'w', zipfile.ZIP_DEFLATED) as f:
    for path in main_files:
        f.write(path, path)
zipped_data = open('deploy.zip', 'rb').read()
layer_data = open('dependency_layer/mypackage.zip', 'rb').read()
s3.put_object(
    Body=layer_data,
    Bucket='cta-bus-and-train-tracker',
    Key=f'config/libraries.zip',
)
s3.put_object(
    Body=zipped_data,
    Bucket='cta-bus-and-train-tracker',
    Key=f'config/package.zip',
)