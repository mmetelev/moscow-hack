import sqlite3
import contextlib
from tqdm import tqdm

from queries import *
from get_entities import *


DB_FILENAME = 'mock.db'
DROP_QUERY_EVENTS = """DROP TABLE IF EXISTS events"""
DROP_QUERY_TASKS = """DROP TABLE IF EXISTS tasks"""

if os.path.exists(DB_FILENAME):
    os.remove(DB_FILENAME)

with contextlib.closing(sqlite3.connect(DB_FILENAME)) as con:
    cur = con.cursor()
    cur.execute(DROP_QUERY_EVENTS)
    cur.execute(DROP_QUERY_TASKS)
    cur.execute(CREATE_TEMPLATE_JOBS_TABLE_QUERY)
    cur.execute(CREATE_TEMPLATE_KPGZ_TABLE_QUERY)
    con.commit()

with contextlib.closing(sqlite3.connect(DB_FILENAME)) as con: # auto-closes
    DB_TABLE = 'kpgz_template'
    ENTITIES = get_entities_for_db(db=DB_TABLE)

    with con: # auto-commits
        cur = con.cursor()
        for i, ent in tqdm(enumerate(ENTITIES)):
            kpgz_code, kpgz_name, template_name = ent.values()
            # print("ENTITY:", entity_cmp)
            cur.execute(f"INSERT INTO {DB_TABLE} (kpgz_code, kpgz_name, template_name) "
                        "VALUES (?, ?, ?)",
                        [kpgz_code, kpgz_name, template_name])
            if i % 10 == 0:
                con.commit()

print(f"{DB_TABLE} was built successfully. Testing...")
with contextlib.closing(sqlite3.connect(DB_FILENAME)) as con: # auto-closes
    cur = con.cursor()
    cur.execute(f'''
        SELECT * 
        FROM {DB_TABLE} LIMIT 10''')
    result = cur.fetchall()
print(result)

with contextlib.closing(sqlite3.connect(DB_FILENAME)) as con: # auto-closes
    DB_TABLE = 'jobs_template'
    ENTITIES = get_entities_for_db(db=DB_TABLE)

    with con: # auto-commits
        cur = con.cursor()
        for i, ent in tqdm(enumerate(ENTITIES)):
            job_code, spgz_name, kpgz_code, kpgz_name, template_name = ent.values()
            # print("ENTITY:", entity_cmp)
            cur.execute(f"INSERT INTO {DB_TABLE} (job_code, job_name, kpgz_id) "
                        "VALUES (?, ?, ?)",
                        [job_code, spgz_name, kpgz_code])
            if i % 10 == 0:
                con.commit()

print(f"{DB_TABLE} was built successfully. Testing...")
with contextlib.closing(sqlite3.connect(DB_FILENAME)) as con: # auto-closes
    cur = con.cursor()
    cur.execute(f'''
        SELECT * 
        FROM {DB_TABLE} LIMIT 10''')
    result = cur.fetchall()
print(result)




