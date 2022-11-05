import streamlit as st
import pandas as pd
from sortedcontainers import SortedDict

from utils.streamlit_utils.st_markdown import format_str
from utils.streamlit_utils.st_constants import PAGE_CONFIG

st.set_page_config(**PAGE_CONFIG)


@st.experimental_memo
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')


def st_title(text):
    text = format_str(text, back_color=(225, 255, 225), font_color=(42, 42, 42))
    st.markdown(text, unsafe_allow_html=True)


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


def extract_costs(df):
    def _calculate_quantity(unit, total):
        if type(total) is float and type(unit) is float:
            return total / unit
        else:
            return 0

    try:
        costs = df.loc[df.iloc[:, 0].str.contains("Итого по разделу") == True,].dropna(axis=1, how='all')
        costs = costs.iloc[:, :3]
        costs = drop_na_columns(costs)

        if costs.shape[1] == 3:
            costs.columns = ["Раздел", "Стоимость единицы", "Полная стоимость"]
            costs["Количество"] = costs.apply(
                lambda x: _calculate_quantity(x["Стоимость единицы"],
                                              x["Полная стоимость"]), axis=1)
        elif costs.shape[1] == 2:
            costs.columns = ["Раздел", "Полная стоимость"]
            costs["Количество"] = 1

        elif costs.shape[1] == 1:
            costs.columns = ["Раздел", ]

        if costs.size == 0:
            print("Costs cannot be extracted")
            return None

        return costs

    except Exception as e:
        print(type(e), e)
        return None


def extract_chapters(df):
    try:
        chapters = df.loc[df.iloc[:, 0].str.lower().str.contains("Раздел") == True,]\
            .dropna(axis=1, how='all').T.to_dict('list')
        # chapters = filter_by_chapter(df, ["Раздел", "раздел", "Подраздел", "подраздел"])
        st.code(chapters)
        # chapters = chapters.dropna(axis=1, how='all').T.to_dict('list')
        chapters = SortedDict(chapters)
        return chapters
    except Exception as e:
        print(type(e), e)
        return None


def insert_chapters(chapters, df):
    try:
        df["Раздел"] = df.apply(define_chapter_df, args=(chapters,), axis=1)
        df.columns = [str(col).strip().replace('\n', '') if not str(col) == 'nan' else str(idx)
                      for idx, col in enumerate(df.columns)]
        df = df[df.columns[:-1].insert(0, df.columns[-1])]
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


def filter_by_chapter(df, chapter_selected):
    try:
        pat = '|'.join(r"\b{}\b".format(x) for x in chapter_selected)
        df = df[df['Раздел'].str.contains(pat)]
        return df
    except Exception as e:
        print(type(e), e)


def find_columns(df):
    col_to_find1 = 'Наименование работ и затрат'
    col_to_find2 = 'Шифр'
    col_to_find3 = 'ВСЕГО'

    row1, row2, row3 = None, None, None
    col1, col2, col3 = None, None, None
    for col in df.columns:

        try:
            if df[col].str.contains(col_to_find1).any():
                row1 = df[df[col].str.contains(col_to_find1) == True].index.tolist()[0]
                col1 = col
                st.sidebar.write(f"Найдено название \"{col_to_find1}\"")
                st.sidebar.code(f"ROW: {row1} | COLUMN: [{col1}]")

            if df[col].str.contains(col_to_find2).any():
                row2 = df[df[col].str.contains(col_to_find2) == True].index.tolist()[0]
                col2 = col
                st.sidebar.write(f"Найдено название \"{col_to_find2}\"")
                st.sidebar.code(f"ROW: {row2} | COLUMN: [{col2}]")

            if df[col].str.contains(col_to_find3).any():
                row3 = df[df[col].str.contains(col_to_find3) == True].index.tolist()[0]
                col3 = col
                st.sidebar.write(f"Найдено название \"{col_to_find3}\"")
                st.sidebar.code(f"ROW: {row3} | COLUMN: [{col3}]")

            if row1 is not None and row2 is not None and row3 is not None:
                break

        except Exception as e:
            print(type(e), e)
            pass

    return (row1, col1), (row2, col2), (row3, col3)


def process_xls(xls, sheet):
    df = pd.read_excel(xls, sheet_name=sheet)
    df = df.dropna(axis=1, how='all')

    # Извлечем названия разделов в словарь с сортировкой по индексу
    chapters = extract_chapters(df)
    st.warning(chapters)

    # Извлечем стоимость по каждому из разделов
    costs = extract_costs(df)

    # Найдем расположение шапки таблицы в смете по названию двух ключевых колонок
    (row1, col1), (row2, col2), (row3, col3) = find_columns(df)

    if not row2 is None:
        # Сохраним названия колонок из найденной шапки
        columns = df.iloc[row2].tolist()

        # Вычислим ширину таблици по последнему столбцу с итоговой расценкой
        num_columns = list(df.columns).index(col3)

        # Удаляем пустые строки и строки разбивки под работой
        df_new = df.loc[~df[col2].isna() & df[col1].apply(lambda x: len(str(x)) > 6)]

        # Заполняем колонку с итоговым значением стоимости по последнему (итоговому) значению
        df_new[col3] = df[col3].fillna(method='bfill')

        # Меняем названия колонок на названия из шапки
        df_new.columns = columns

        # Форматируем таблицу: удаляем старую шапку и пустые столбцы
        df_new = df_new.iloc[1:, :num_columns + 2]
        df_new = df_new.dropna(axis=1, how='all')
        df_new = drop_na_columns(df_new)

        if chapters is not None:
            df_new = insert_chapters(chapters, df_new)

        return df_new, costs, chapters


def main():
    st.sidebar.info("БЛОК №1: Обработка загруженной сметы")
    st_title("Загрузка файла сметы")

    file_uploaded = st.file_uploader("Загрузите смету", type=["xls", "xlsx"], help="Файл формата .xls или .xlsx")

    if file_uploaded is not None:
        xls_file = pd.ExcelFile(file_uploaded)
        xls_sheets = xls_file.sheet_names
        choice_disabled = False if len(xls_sheets) > 1 else True
        sheet_with_data = st.selectbox("Выберите лист, который содержит смету",
                                       xls_sheets,
                                       disabled=choice_disabled)
        st.markdown("----")
        st_title("Обработка файла сметы")
        df, costs, chapters = process_xls(file_uploaded, sheet_with_data)

        if costs is not None:
            st.info("Разбивка затрат по разделам")
            st.dataframe(costs)

        st.info("Загруженная смета")

        if chapters is None:
            st.code(f"Колонка с указанием раздела работ не найдена")
        else:
            chapter_names = [k[0].replace("Раздел: ", "") for k in chapters.values()]
            chapter_selected = st.multiselect("Выберите разделы для отображения", chapter_names, default=chapter_names)
            df = filter_by_chapter(df, chapter_selected)

        st.dataframe(df.head(100))
        csv = convert_df(df)

        # Сохраняем файл на время сессии до загрузки нового
        st.session_state["uploaded_df"] = df

        df.to_csv("/data/temp.csv", index=False)
        st.download_button("Скачать файл в формате .csv", csv, "smeta.csv", "text/csv", key='download-csv')

        st.markdown("""<a href="http://localhost:8502/PROCESS_FILE" target="_self"> 
        <img alt="next" src="https://www.pngmart.com/files/3/Next-Button-PNG-HD.png" width=100></a>""",
                    unsafe_allow_html=True)


if __name__ == "__main__":
    main()
