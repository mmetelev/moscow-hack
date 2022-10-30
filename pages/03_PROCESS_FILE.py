import streamlit as st


def main():
    st.sidebar.info("БЛОК №2: Поиск соответствий в справочниках")
    st.markdown("#### Пример:")
    if "uploaded_df" in st.session_state.keys():
        df = st.session_state["uploaded_df"]
        st.dataframe(df)
    else:
        st.warning("Необходимо загрузить файл сметы на странице загрузки")

    with st.form("Обработка сметы"):
        proc_type = st.radio("Выбор ТЗ или КПГЗ", ("ТЗ", "КПГЗ"))
        submit = st.form_submit_button("OK")

    if submit:
        st.success("Processing...")


if __name__ == "__main__":
    main()