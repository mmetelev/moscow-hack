import streamlit as st
import pandas as pd

from utils.streamlit_utils.st_markdown import format_str
from utils.streamlit_utils.st_constants import PAGE_CONFIG
from utils.query_tools import find_column_names
from utils.pattern_search import find_columns, find_address
from utils.chapter_search import filter_by_chapter, extract_chapters, extract_costs, insert_chapters

st.set_page_config(**PAGE_CONFIG)


@st.experimental_memo
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')


def st_title(text):
    text = format_str(text, back_color=(225, 255, 225), font_color=(42, 42, 42))
    st.markdown(text, unsafe_allow_html=True)


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


def _crop_columns(df, use_new_names=False):
    columns = ["раздел", "наименование", "шифр", "ед. изм.", "кол-во", "ВСЕГО"]
    columns = [c.upper() for c in columns]
    try:
        if st.checkbox("Отображать в сокращенном формате"):
            cols = find_column_names(df)
            df = df.reset_index(drop=True).loc[:, cols]
            # удаление строковых значений из колонок с числовыми значениями
            df.iloc[:, 3] = df.iloc[:, 3].apply(pd.to_numeric, errors='coerce')
            df.iloc[:, -1] = df.iloc[:, -1].apply(pd.to_numeric, errors='coerce')
            # замена названий колонок, если указана данная опция
            df.columns = columns if use_new_names else df.columns
            return df
        return df
    except Exception as e:
        print(f"[{__name__}]", type(e), e)
        return df


def main():
    st.sidebar.info("БЛОК №1: Обработка загруженной сметы")
    st_title("Загрузка файла сметы")

    file_uploaded = st.file_uploader("Загрузите смету", type=["xls", "xlsx"], help="Файл формата .xls или .xlsx")
    if st.checkbox("Использовать тестовый файл"):
        file_uploaded = "./data/example.xlsx"

    elif st.checkbox("Использовать последний загруженный файл") and "uploaded_df" in st.session_state.keys():
        file_uploaded = "./data/temp.xlsx"

    if file_uploaded is not None:

        if type(file_uploaded) is not str:
            with open("./data/temp.xlsx", 'wb') as f:
                f.write(file_uploaded.getvalue())

        xls_file = pd.ExcelFile(file_uploaded)
        xls_sheets = xls_file.sheet_names
        choice_disabled = False if len(xls_sheets) > 1 else True
        sheet_with_data = st.selectbox("Выберите лист, который содержит смету",
                                       xls_sheets,
                                       disabled=choice_disabled)
        df_raw, df, costs, chapters, address = process_xls(file_uploaded, sheet_with_data)

        if address is not None:
            st.sidebar.success(f"АДРЕС: {address}")

        with st.expander("Необработанные данные"):
            st.dataframe(df_raw)

        st.markdown("----")
        st_title("Обработка файла сметы")

        if costs is not None:
            st.info("Разбивка затрат по разделам")
            st.dataframe(costs)

        st.info("Загруженная смета")

        if chapters is None:
            st.code(f"Колонка с указанием раздела работ не найдена")
        else:
            col_r, col_sr = 'Раздел', "Подраздел"
            chapter_names_raw = [k[0].replace(f"{col_r}: ", "") \
                                     .replace(f"{col_sr}: ", "") \
                                     .replace(f"{col_r}:", "") \
                                     .replace(f"{col_sr}:", "") for k in chapters.values()]

            chapter_selected = st.multiselect("Выберите разделы для отображения",
                                              chapter_names_raw,
                                              # format_func=format_chapter,
                                              default=chapter_names_raw)
            st.code(chapter_selected)
            df_ = filter_by_chapter(df, chapter_selected)
            df = df_ if df_ is not None else df

        if df is not None:
            df = _crop_columns(df)

            try:
                st.dataframe(df.head(100), use_container_width=True)
            except st.StreamlitAPIException:
                st.code(df.head(100))
            csv = convert_df(df)

            # Сохраняем файл на время сессии до загрузки нового
            st.session_state["uploaded_df"] = df
            st.session_state["costs_df"] = costs

            try:
                df.to_csv("./data/temp.csv", index=False)
                st.download_button("Скачать файл в формате .csv", csv, "smeta.csv", "text/csv", key='download-csv')
            except Exception as e:
                st.code(type(e), e)

            # st.markdown("""<a href="http://localhost:8502/PROCESS_FILE" target="_self">
            # <img alt="next" src="https://www.pngmart.com/files/3/Next-Button-PNG-HD.png" width=100></a>""",
            #             unsafe_allow_html=True)


if __name__ == "__main__":
    main()
