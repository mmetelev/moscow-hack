import pandas as pd
import streamlit as st

from utils.reference_search import find_in_reference_book

TSN_PATH = "./data/tsn.csv"
SN_PATH = "./data/sn.csv"


def main():
    st.sidebar.info("Справочники ТСН и СН")
    spravochnik = st.sidebar.radio("Выберите справочник для отображения", ("ТСН", "СН",))
    if spravochnik == "ТСН":
        df = pd.read_csv(TSN_PATH)
        st.dataframe(df)
    elif spravochnik == "СН":
        df = pd.read_csv(SN_PATH)
        st.dataframe(df)
    elif spravochnik == "ТСН+СН":
        df1 = pd.read_csv(SN_PATH)
        df2 = pd.read_csv(SN_PATH)
        df = pd.concat((df1, df2))
        st.dataframe(df)
    st.info(f"DATAFRAME: {df.shape}")
    job_name = st.text_input("Введите наименование работ", max_chars=180, value="Устройство верхнего покрытия")
    col_result = "Наименование работ и затрат"
    results = find_in_reference_book(job_name,
                                     df_reference=df,
                                     col_result=col_result)
    st.markdown("### Результаты поиска:")

    if results is not None:
        filter_result = st.multiselect("Выберите все подходящие позиции", results)
        cols_to_search = ["Наименование работ и затрат", "Наименование СПГЗ", "Шифр расценки и коды ресурсов"]
        col_result = st.selectbox("В каком столбце искать результат:", cols_to_search)
        # filter_result = None if col_result == "Все" else filter_result
        results = find_in_reference_book(job_name,
                                         df_reference=df,
                                         col_result=col_result,
                                         job_name_filter=filter_result)
        st.code(results)

        try:
            df_view = df.loc[df[col_result].isin(results)]
            st.dataframe(df_view)
        except Exception as e:
            print(type(e), e)

    else:
        txt = "Ничего не найдено, попробуйте использовать другой справочник" \
            if not spravochnik == "ТСН+СН" else "Ничего не найдено"
        st.warning(f"{txt}")


if __name__ == "__main__":
    main()
