import streamlit as st

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