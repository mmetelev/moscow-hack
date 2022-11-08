import pandas as pd
import numpy as np
import random
import os
from datetime import datetime, timedelta


def get_names(female=False):
    df_names = pd.read_csv("fake_data/russian_names.csv", sep=';')
    sex = 'М' if not female else 'Ж'
    df_names = df_names.loc[(df_names.PeoplesCount > 100000) & (df_names.Sex == sex)]
    names = df_names.Name.unique().tolist()
    # names = [n for n in names if n[-1] not in ['а', 'я']]
    return names


def get_surnames(female=False):
    df_names = pd.read_csv("fake_data/russian_surnames.csv", sep=';')
    df_names = df_names.loc[(df_names.PeoplesCount > 100)]
    names = df_names.Surname.unique().tolist()
    names = [n for n in names if n[-2:] not in ['ая', 'ва', 'на']] \
        if not female else [n for n in names if n[-2:] in ['ая', 'ва', 'на']]
    return names


def get_event_data(macro=False):
    if macro:
        with open("fake_data/macro_events.txt", encoding="utf8") as reader:
            data = reader.readlines()
        data = [d.replace('\n', '') for d in data]
        return random.choice(data)

    df = pd.read_csv("fake_data/event_names.csv")
    i = random.randint(0, df.shape[0] - 1)
    return df.iloc[i].tolist()


def get_event_timeframe(gap=6):
    date_start = datetime.now() - timedelta(random.randint(0, gap))
    date_end = datetime.now() + timedelta(random.randint(0, gap))
    return date_start, date_end


def get_entities_for_db(db="kpgz_template", verbose=False, df_path=None):
    entities = []

    if db == "kpgz_template":
        df_path = "./../../data/template_names.csv"
    elif db == "jobs_template":
        df_path = "./../../data/template_clean.csv"

    if df_path is not None and os.path.exists(df_path):
        df = pd.read_csv(df_path, index_col=0)
    else:
        raise ValueError("The dataframe path is incorrect")

    for idx, (i, row) in enumerate(df.iterrows()):
        ent = row.to_dict()
        entities.append(ent)

        if verbose and idx < 100:
            txt = "".join([f"| {k}:{v} |" for k, v in ent.items()])
            print(f"{txt}")

    return entities


if __name__ == '__main__':
    # get_fake_entities_for_users(100)
    # get_fake_entities_for_clients(verbose=True)
    get_entities_for_db(db='jobs_template', verbose=True)
