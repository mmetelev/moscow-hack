import streamlit as st
import pandas as pd
import os

from utils.streamlit_utils.st_constants import PAGE_CONFIG, CSV_TEMP_PATH

st.set_page_config(**PAGE_CONFIG)


@st.experimental_memo
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')


def st_edit_entry(df, entry, col):
    df_params = df.loc[df[col] == entry]
    new_params = {}

    for idx, row in df_params.iterrows():
        for key, val in row.items():
            st.markdown("----")
            new_param = st.text_input(f"* {key}", value=val)
            new_params[key] = new_param
            df_params.loc[idx, key] = new_param

    return df_params


def main():
    st.sidebar.info("БЛОК №3 & №4: Редактирование и подтверждение обработанной сметы")
    col_smeta = 'Наименование работ и затрат'

    if "processed_df" in st.session_state.keys():
        df = st.session_state["processed_df"]
        placeholder0 = st.empty()

        with placeholder0:
            st.dataframe(df)

        entry = st.selectbox("Выберите запись для редактирования", df[col_smeta])
        df_view = df.loc[df[col_smeta]==entry]
        st.dataframe(df_view)
        placeholder1 = st.empty()
        placeholder2 = st.empty()
        if st.checkbox("Редактировать"):
            df_update = st_edit_entry(df, entry, col_smeta)

            with placeholder1:
                st.markdown("#### Новое значение:")
            with placeholder2:
                st.dataframe(df_update)

            df.update(df_update)
            with placeholder0:
                st.dataframe(df)

        try:
            csv = convert_df(df)
            # df.to_csv("./data/temp.csv", index=False)
            st.sidebar.download_button("Скачать файл в формате .csv", csv, "smeta.csv", "text/csv", key='download-csv')
        except Exception as e:
            st.code(type(e), e)

    else:
        st.warning("Необходимо загрузить и обработать файл сметы")


if __name__ == "__main__":
    main()
