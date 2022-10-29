import streamlit as st
import pandas as pd
from sortedcontainers import SortedDict


@st.experimental_memo
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')


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


def process_xls(xls):
    df = pd.read_excel(xls)
    df = df.dropna(axis=1, how='all')

    # Извлечем названия разделов в словарь с сортировкой по индексу
    chapters = df.loc[df.iloc[:, 0].str.contains("Раздел") == True,].dropna(axis=1, how='all').T.to_dict('list')
    chapters = SortedDict(chapters)

    # Найдем расположение шапки таблицы в смете по названию двух ключевых колонок
    row1, row2 = None, None
    col1, col2 = None, None

    for col in df.columns:
        col_to_find1 = 'Наименование работ и затрат'
        col_to_find2 = 'Шифр'

        try:
            if df[col].str.contains(col_to_find1).any():
                st.write(f"Найдено название \"{col_to_find1}\"")

                row1 = df[df[col].str.contains(col_to_find1) == True].index.tolist()[0]
                col1 = col
                st.info(f"ROW: {row1} | COLUMN: [{col1}]")

            if df[col].str.contains(col_to_find2).any():
                st.write(f"Найдено название \"{col_to_find2}\"")

                row2 = df[df[col].str.contains(col_to_find2) == True].index.tolist()[0]
                col2 = col
                st.info(f"ROW: {row2} | COLUMN: [{col2}]")

            if row1 is not None and row2 is not None:
                break

        except Exception as e:
            print(type(e), e)
            pass

    if not row2 is None:
        columns = df.iloc[row2].tolist()
        df = df.iloc[row2 + 1:]
        df = df.loc[~df[col2].isna() & df[col1].apply(lambda x: len(str(x)) > 10)]
        df.columns = columns
        df = df.dropna(axis=1, how='all')

        try:
            df["Раздел"] = df.apply(define_chapter_df, args=(chapters,), axis=1)
            df.columns = [str(col).strip().replace('\n', '') if not str(col) == 'nan' else str(idx)
                          for idx, col in enumerate(df.columns)]
            df = df[df.columns[:-1].insert(0, df.columns[-1])]
        except Exception as e:
            st.code(f"Колонка с указанием раздела работ не найдена: {e}")

        st.dataframe(df.head(10))
        csv = convert_df(df)
        st.download_button("Скачать файл в формате .csv", csv, "smeta.csv", "text/csv", key='download-csv')


def main():
    file_uploaded = st.file_uploader("Загрузите смету", type=["xls", "xlsx"], help="Файл формата .xls или .xlsx")
    if file_uploaded is not None:
        process_xls(file_uploaded)


if __name__ == "__main__":
    main()
