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
    for root, _, files in os.walk('package'):
        for in_file in files:
            full_path = os.path.join(root, in_file)
            f.write(full_path, full_path[8:])  # removing the root "package/" part of the path
zipped_data = open('deploy.zip', 'rb').read()
s3.put_object(
    Body=zipped_data,
    Bucket='cta-bus-and-train-tracker',
    Key=f'config/package.zip',
)