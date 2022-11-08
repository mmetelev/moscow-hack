import sqlite3
import contextlib
import pandas as pd

from utils.reference_search import _get_ngrams

DB_FILENAME = 'mock.db'
DB_TABLE = 'jobs_template'


def find_sent(sent):
    ngrams = _get_ngrams(sent)
    sql_txt = "".join([f"WHERE job_name LIKE \'%{ngram}%\' OR" for ngram in ngrams])
    sql_txt = sql_txt[:-3]

    print(f'''
        SELECT * 
        FROM {DB_TABLE} 
        {sql_txt} 
        LIMIT 10''')

    with contextlib.closing(sqlite3.connect(DB_FILENAME)) as con:  # auto-closes
        cur = con.cursor()
        cur.execute(f'''
            SELECT * 
            FROM {DB_TABLE} 
            {sql_txt} 
            LIMIT 10''')
        # result = cur.fetchall()
        df = pd.DataFrame(cur.fetchall())
        df.columns = [x[0] for x in cur.description]

    return df


if __name__ == "__main__":
    df = find_sent("системе для клинических исследований")
    print(df.job_name.tolist())
