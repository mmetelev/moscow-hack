def find_column_names(df):
    cols = df.columns
    keywords = ["раздел",
                "наименование",
                "шифр",
                "п/п",
                "ед. изм.",
                "кол-во",
                "ВСЕГО"]
    result = []

    condition_0 = lambda w, col: w == "раздел" and "раздел" in col.lower()
    condition_1 = lambda w, col: w == "наименование" and "наименование" in col.lower()
    condition_2 = lambda w, col: w == "шифр" and "шифр" in col.lower()
    condition_3 = lambda w, col: w == "п/п" and ("п/п" in col.lower().replace(" ", "") \
                                                 or "п.п" in col.lower().replace(" ", ""))
    condition_4 = lambda w, col: w == "ед. изм." and ("ед.изм." in col.lower().replace(" ", "") \
                                                      or "единиц" in col.lower().replace(" ", "")) \
                                 and "цена" not in col.lower() \
                                 and "кол-во" not in col.lower()
    condition_5 = lambda w, col: w == "кол-во" and ("количество" in col.lower().replace(" ", "") \
                                                    or "кол-во" in col.lower().replace(" ", ""))
    condition_6 = lambda w, col: w == "ВСЕГО" and "ВСЕГО" in col

    for word in keywords:
        for col in cols:
            if condition_0(word, col) \
                    or condition_1(word, col) \
                    or condition_2(word, col) \
                    or condition_3(word, col) \
                    or condition_4(word, col) \
                    or condition_5(word, col) \
                    or condition_6(word, col):
                result.append(col) if col not in result else None
    return result


def get_query_params(df, idx):
    try:
        cols = find_column_names(df)
        params = df.reset_index(drop=True).loc[idx, cols].to_dict()
        return params
    except KeyError:
        print(f"There are only {df.shape[0]} rows in the dataframe")
        return None
    except Exception as e:
        print(type(e), e)
