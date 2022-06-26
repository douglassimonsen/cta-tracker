import psycopg2
import os
import pathlib
import zipfile
import io
import csv
os.chdir(pathlib.Path(__file__).parent)


def get_conn():
    return psycopg2.connect(
        host='td1x07mp41zaccz.cuxgafgbioui.us-east-1.rds.amazonaws.com',
        port=5432,
        dbname='postgres',
        user='postgres',
        password='postgres1',
    )


def gen_schema():
    with open("schema.sql") as f:
        schema = f.read()

    with get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(schema)


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
        conn.set_isolation_level(0)
        cursor = conn.cursor()
        for name in TABLES:
            print(name)
            data = read_csv(name)
            columns = ", ".join(f'"{c}"' for c in data[0].keys())
            values = ", ".join(f'%({c})s' for c in data[0].keys())
            command = f"insert into cta_tracker.{name} ({columns}) values ({values})"
            cursor.executemany(command, data)
            conn.commit()


def main():
    gen_schema()
    fill_schema()


if __name__ == "__main__":
    main()