import pandas as pd

from utils.query_tools import find_column_names
from utils.pattern_search import find_columns, find_address
from utils.chapter_search import extract_chapters, extract_costs, insert_chapters


def get_xls_sheets(xls):
    xls_file = pd.ExcelFile(xls)
    return xls_file.sheet_names


def crop_columns(df, use_new_names=False):
    try:
        columns = ["раздел", "наименование", "шифр", "ед. изм.", "кол-во", "ВСЕГО"]
        columns = [c.upper() for c in columns]
        cols = find_column_names(df)
        df = df.reset_index(drop=True).loc[:, cols]
        # удаление строковых значений из колонок с числовыми значениями
        df.iloc[:, 3] = df.iloc[:, 3].apply(pd.to_numeric, errors='coerce')
        df.iloc[:, -1] = df.iloc[:, -1].apply(pd.to_numeric, errors='coerce')
        # замена названий колонок, если указана данная опция
        df.columns = columns if use_new_names else df.columns
        return df
    except Exception as e:
        print(f"[{__name__}]", type(e), e)
        return df


def process_xls(xls, sheet):
    df = pd.read_excel(xls, sheet_name=sheet)
    df = df.dropna(axis=1, how='all')

    # Извлечем названия разделов в словарь с сортировкой по индексу
    chapters = extract_chapters(df)

    # Извлечем стоимость по каждому из разделов
    costs = extract_costs(df)

    # Найдем расположение шапки таблицы в смете по названию двух ключевых колонок
    (row1, col1), (row2, col2), (row3, col3), (row4, col4) = find_columns(df)

    # Найдем адрес
    address = find_address(df, row4, col4)

    if not row2 is None:
        # Удаляем пустые строки и строки разбивки под работой
        df_new = df.loc[~df[col2].isna() & df[col1].apply(lambda x: len(str(x)) > 6)]
        # Заполняем колонку с итоговым значением стоимости по последнему (итоговому) значению
        df_new.loc[:, col3] = df[col3].fillna(method='bfill')
        # Удалим все пустые столбцы
        df_new = df_new.dropna(axis=1, how='all')
        # Сохраним названия колонок из найденной шапки
        columns = [str(c).replace("\n", " ").replace("- ", "").strip() \
                   for c in df_new.iloc[0].tolist()]

        # Вычислим ширину таблици по последнему столбцу с итоговой расценкой
        num_columns = list(df.columns).index(col3)

        # Меняем названия колонок на названия из шапки
        df_new.columns = columns

        # Форматируем таблицу: удаляем старую шапку и пустые столбцы
        df_new = df_new.iloc[1:, :num_columns + 1]
        df_new = df_new.dropna(axis=1, how='all')
        # df_new = drop_na_columns(df_new)

        if chapters is not None:
            df_new = insert_chapters(chapters, df_new)

        return df, df_new, costs, chapters, address