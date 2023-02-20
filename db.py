import json
import time

import aioredis
import asyncpg
import psycopg2

import sys
import pathlib

sys.path.append(str(pathlib.Path(__file__).parent.parent.absolute()))

from config import DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT, REDIS_URL, REDIS_DB, \
    REDIS_PASSWORD

redis = aioredis.from_url(REDIS_URL, decode_responses=True, db=REDIS_DB, password=REDIS_PASSWORD)
old_redis = aioredis.from_url('redis://65.21.191.118', decode_responses=True, db=REDIS_DB, password=REDIS_PASSWORD)


async def async_query(q):
    conn = None
    try:
        conn = await asyncpg.connect(
            f'postgres://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}')
        await conn.set_type_codec(
            'json',
            encoder=json.dumps,
            decoder=json.loads,
            schema='pg_catalog'
        )
    except Exception as exc:
        print(exc)
        print(q)

    try:
        if 'select' in q.lower():
            return await conn.fetch(q)
        else:
            return await conn.execute(q)
    except Exception as err:
        if 'no results' not in str(err):
            print("Error:", err)
            print(q)
    finally:
        # Close the connection.
        await conn.close()


def sync_query(q):
    # print(q)
    cur = None
    # while cur == None:
    try:
        con = psycopg2.connect(
            database=DATABASE_NAME,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            host=DATABASE_HOST,
            port=DATABASE_PORT
        )
        cur = con.cursor()
    except Exception as exc:
        print(exc)
        time.sleep(3)
    try:
        cur.execute(q)
        data = cur.fetchall()
    except psycopg2.DatabaseError as err:
        if 'no results' not in str(err):
            print("Error: ", err)
        print("Error: ", err)
    else:
        return data
    finally:
        con.commit()


def eth_pairs():
    return sync_query(f"SELECT * FROM eth_pairs;")
