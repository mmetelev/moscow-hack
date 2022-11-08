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


@st.experimental_memo
def get_df_tz():
    df_path = "./data/template_names.csv"
    df = pd.read_csv(df_path)
    return df


def get_all_jobs(tz_code):
    df_path = "./data/template_clean.csv"
    df = pd.read_csv(df_path, index_col=0)
    df = df.loc[df.kpgz_code == tz_code]
    return df


def st_tz_search():
    df = get_df_tz()
    tz_names = df.kpgz_name.unique().tolist()
    tz = st.selectbox("Выберите нужный шаблон ТЗ", tz_names)
    codes = df.loc[df.kpgz_name == tz].kpgz_code.tolist()
    if len(codes) == 1:
        code = codes[0]
    else:
        code = st.selectbox("Выберите код ТЗ", codes)
    st.success(f"Код выбранного шаблона: {code}")
    jobs_df = get_all_jobs(code)
    return jobs_df


def main():
    st.sidebar.info("БЛОК №2: Поиск соответствий в справочниках")
    st.markdown("#### Пример:")
    if "uploaded_df" in st.session_state.keys():
        df = st.session_state["uploaded_df"]
        costs = st.session_state["costs_df"]
        with st.expander("Разбивка затрат по разделам"):
            st.dataframe(costs)
        with st.expander("Загруженная смета"):
            st.dataframe(df)
    elif os.path.exists(CSV_TEMP_PATH):
        df = pd.read_csv(CSV_TEMP_PATH)
        st.dataframe(df)
    else:
        st.warning("Необходимо загрузить файл сметы на странице загрузки")

    proc_type = st.sidebar.radio("Выбор ТЗ или КПГЗ", ("ТЗ", "КПГЗ"))
    # df = mark_key_jobs(df, "")
    if proc_type == "КПГЗ":
        st.sidebar.markdown("#### Выберите требуемый КПГЗ")
    elif proc_type == "ТЗ":
        st.sidebar.markdown("#### Выберите требуемый шаблон ТЗ")
        jobs_df = st_tz_search()
        st.dataframe(jobs_df, use_container_width=True)


if __name__ == "__main__":
    main()
