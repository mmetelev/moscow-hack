import streamlit as st


def main():
    st.info("Здесь будет форма обработки файла")
    st.markdown("#### Пример:")
    with st.form("Обработка сметы"):
        proc_type = st.radio("Выбор ТЗ или КПГЗ", ("ТЗ", "КПГЗ"))
        proc_list = st.selectbox("Выбор листа сметы для обработки", ["Sheet1", "Sheet2"])
        submit = st.form_submit_button("OK")

    if submit:
        st.success("Processing...")


if __name__ == "__main__":
    main()