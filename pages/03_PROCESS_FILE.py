import streamlit as st
import pandas as pd
import os

from utils.streamlit_utils.st_constants import PAGE_CONFIG, CSV_TEMP_PATH

st.set_page_config(**PAGE_CONFIG)


def mark_key_jobs(df, col, chapters):
    patterns = ["мусора",
                "возвратные материалы",
                "пуско-наладочные"]
    try:
        pat = '|'.join(r"\b{}\b".format(x).lower() for x in patterns)
        df["Ключевая работа"] = df.loc[df[col].str.lower().str.contains(pat) == False,]
        return df
    except Exception as e:
        print(f"[{__name__}]", type(e), e)
        return None


def main():
    st.sidebar.info("БЛОК №2: Поиск соответствий в справочниках")
    st.markdown("#### Пример:")
    if "uploaded_df" in st.session_state.keys():
        df = st.session_state["uploaded_df"]
        costs = st.session_state["costs_df"]
        st.markdown("Разбивка затрат по разделам")
        st.dataframe(costs)
        st.markdown("Загруженная смета")
        st.dataframe(df)
    elif os.path.exists(CSV_TEMP_PATH):
        df = pd.read_csv(CSV_TEMP_PATH)
        st.dataframe(df)
    else:
        st.warning("Необходимо загрузить файл сметы на странице загрузки")

    with st.sidebar.form("Обработка сметы"):
        proc_type = st.radio("Выбор ТЗ или КПГЗ", ("ТЗ", "КПГЗ"))
        submit = st.form_submit_button("OK")

    if submit:
        df = mark_key_jobs(df, "")


if __name__ == "__main__":
    main()