import psycopg2
import os
import pathlib
import zipfile
import io
import csv
import boto3
import bz2
import json
os.chdir(pathlib.Path(__file__).parent)
s3 = boto3.client("s3")
envs = json.load(open("../env.json"))

def get_conn():
    return psycopg2.connect(
        **envs['db']
    )


def gen_schema():
    with open("schema.sql") as f:
        schema = f.read().format(envs['user']['access_key'], envs['user']['secret_key'])

    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(schema)
        conn.commit()


def send_to_s3(data, name):
    # data = bz2.compress(data.encode("utf-8"))
    s3.put_object(
        Body=data,
        Bucket='cta-bus-and-train-tracker',
        Key=f'schedules/raw/{name}.csv',
    )



def fill_schema():
    def read_csv(source):
        source_data = zf.read(f"{source}.txt").decode("utf-8")
        routes_raw = io.StringIO()
        routes_raw.write(source_data)
        routes_raw.seek(0)
        return list(csv.DictReader(routes_raw))

    TABLES = ['calendar', 'calendar_dates', 'routes', 'shapes', 'stop_times', 'stops', 'trips']
    with (
        zipfile.ZipFile("sched.zip") as zf,
        get_conn() as conn
    ):
        cursor = conn.cursor()
        for name in TABLES:
            if name in ['calendar', 'calendar_dates', 'routes', 'shapes']:
                continue
            print(name)
            send_to_s3(zf.read(f"{name}.txt").decode("utf-8"), name)
            # wish I knew how to copy compressed files to postgres RDS
            cursor.execute(f'''
                truncate table cta_tracker.{name};
                SELECT aws_s3.table_import_from_s3(
                    'cta_tracker.{name}', 
                    '', 
                    '(format csv, header true, DELIMITER '','', QUOTE ''"'', ESCAPE ''\\'')',
                    '(cta-bus-and-train-tracker,schedules/raw/{name}.csv,us-east-1)', 
                    aws_commons.create_aws_credentials('{envs['user']['access_key']}', '{envs['user']['secret_key']}', '')
                );
            ''')
            conn.commit()


def main():
    gen_schema()
    fill_schema()


if __name__ == "__main__":
    main()