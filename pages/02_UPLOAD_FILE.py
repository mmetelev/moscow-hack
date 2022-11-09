import streamlit as st
import pandas as pd

from utils.streamlit_utils.st_markdown import format_str
from utils.streamlit_utils.st_constants import PAGE_CONFIG
from utils.process_xlsx import process_xls, crop_columns
from utils.chapter_search import filter_by_chapter

st.set_page_config(**PAGE_CONFIG)


@st.experimental_memo
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')


def st_title(text):
    text = format_str(text, back_color=(225, 255, 225), font_color=(42, 42, 42))
    st.markdown(text, unsafe_allow_html=True)


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
            df = crop_columns(df) if st.checkbox("Отображать в сокращенном формате") else df

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
                st.sidebar.download_button("Скачать файл в формате .csv",
                                           csv,
                                           "smeta.csv",
                                           "text/csv",
                                           key='download-csv')
            except Exception as e:
                st.code(type(e), e)

            # st.markdown("""<a href="http://localhost:8502/PROCESS_FILE" target="_self">
            # <img alt="next" src="https://www.pngmart.com/files/3/Next-Button-PNG-HD.png" width=100></a>""",
            #             unsafe_allow_html=True)


if __name__ == "__main__":
    main()
