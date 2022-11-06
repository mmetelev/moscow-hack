import re
from sortedcontainers import SortedDict


def closest_item(sdict, key):
    if len(sdict) == 0:
        raise KeyError('No items in {sdict.__class__.__name__}')

    if len(sdict) == 1:
        return next(iter(sdict.items()))

    idx_before = next(sdict.irange(minimum=key), None)
    idx_after = next(sdict.irange(maximum=key, reverse=True), None)

    if idx_before is None:
        idx = idx_after

    elif idx_after is None:
        idx = idx_before
    else:
        idx = min(idx_before, idx_after, key=lambda x: abs(x - key))

    return idx, sdict[idx]


def define_chapter(idx, sdict):
    key, value = closest_item(sdict, idx)
    return key, value


def define_chapter_df(row, sdict):
    idx = row.name
    return define_chapter(idx, sdict)[1][0]


def _delete_substring_from_column(df, col, substring):
    df[col] = df[col].apply(lambda s: str(s).replace(substring, "").strip())
    return df


def _delete_substrings_from_column(df, col, substrings):
    for ss in substrings:
        df[col] = df[col].apply(lambda s: str(s).replace(ss, "").strip())
    return df


def extract_costs(df):
    def _calculate_quantity(unit, total):
        if type(total) is float and type(unit) is float:
            return total / unit
        else:
            return 0

    try:
        patterns = ["Итого по разделу", "Итого по подразделу"]
        pat = '|'.join(r"\b{}\b".format(x) for x in patterns)
        costs = df.loc[df.iloc[:, 0].str.contains(pat) == True,].dropna(axis=1, how='all')
        costs = costs.iloc[:, :3]
        costs = drop_na_columns(costs)

        if costs.size == 0:
            print("Costs cannot be extracted")
            return None

        if costs.shape[1] == 3:
            costs.columns = ["Итого по разделу", "Стоимость единицы", "Полная стоимость"]
            costs["Количество"] = costs.apply(
                lambda x: _calculate_quantity(x["Стоимость единицы"],
                                              x["Полная стоимость"]), axis=1)
        elif costs.shape[1] == 2:
            costs.columns = ["Итого по разделу", "Полная стоимость"]
            costs["Количество"] = 1

        elif costs.shape[1] == 1:
            costs.columns = ["Итого по разделу", ]

        costs = _delete_substrings_from_column(costs, col="Итого по разделу", substrings=["Итого по разделу: ",
                                                                                          "Итого по подразделу: "])

        return costs

    except Exception as e:
        print(type(e), e)
        return None


def extract_chapters(df):
    patterns = ["раздел", "подраздел", "Раздел", "Подраздел"]
    try:
        pat = '|'.join(r"\b{}\b".format(x).lower() for x in patterns)
        chapters = df.loc[df.iloc[:, 0].str.lower().str.contains(pat) == True,] \
            .dropna(axis=1, how='all').T.to_dict('list')
        chapters = SortedDict(chapters)
        return chapters
    except Exception as e:
        print(f"[{__name__}]", type(e), e)
        return None


def insert_chapters(chapters, df):
    try:
        df["Раздел"] = df.apply(define_chapter_df, args=(chapters,), axis=1)
        df.columns = [str(col).strip().replace('\n', '') if not str(col) == 'nan' else str(idx)
                      for idx, col in enumerate(df.columns)]
        df = df[df.columns[:-1].insert(0, df.columns[-1])]
        df = _delete_substrings_from_column(df, col="Раздел", substrings=["Раздел:", "Подраздел:",
                                                                          "Раздел: ", "Подраздел: "])
        return df
    except Exception as e:
        print(type(e), e)
        return df


def drop_na_columns(df, na_percent=0.5):
    columns_to_drop = []
    for col in df.columns:
        if df[col].isnull().sum() > df.shape[0] * na_percent:
            columns_to_drop.append(col)

    print(f"{len(columns_to_drop)} columns are dropped")
    df = df.drop(columns_to_drop, axis=1)
    return df


def _clean_chapter_list(chapter_list, verbose=True):
    cleaned = []
    for chapter_name in chapter_list:
        chapter_clean = [x for x in chapter_name.split() if not any(c.isdigit() for c in x)]
        chapter_clean = " ".join(chapter_clean).strip()
        cleaned.append(chapter_clean)
    chapter_list = cleaned
    chapter_list = [re.sub(r'\([^)]*\)', '', c) for c in chapter_list]
    chapter_list = [c.replace(".", "").replace(" -", "").replace(")", "").replace("( -)", "").strip()
                    for c in chapter_list]
    print("CLEANED:", chapter_list) if verbose else None
    return chapter_list


def filter_by_chapter(df, chapter_selected):
    try:
        if type(chapter_selected) is not list:
            chapter_selected = [chapter_selected, ]

        df_res0 = df.loc[df["Раздел"].isin(chapter_selected)]

        return df_res0
    except Exception as e:
        print(type(e), e)
