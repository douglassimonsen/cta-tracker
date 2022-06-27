import psycopg2
import json
envs = json.load(open("../../env.json"))


def get_conn():
    return psycopg2.connect(
        **envs['db']
    )


def run_query(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    columns = [x.name for x in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]