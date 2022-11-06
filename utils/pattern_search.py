import re

def find_columns(df):
    col_to_find1 = 'Наименование работ и затрат'
    col_to_find2 = 'Шифр'
    col_to_find3 = 'ВСЕГО'
    col_to_find4 = 'по адресу'

    row1, row2, row3, row4 = None, None, None, None
    col1, col2, col3, col4 = None, None, None, None
    for col in df.columns:

        try:
            if df[col].str.contains(col_to_find1).any():
                row1 = df[df[col].str.contains(col_to_find1) == True].index.tolist()[0]
                col1 = col

            if df[col].str.contains(col_to_find2).any():
                row2 = df[df[col].str.contains(col_to_find2) == True].index.tolist()[0]
                col2 = col

            if df[col].str.contains(col_to_find3).any():
                row3 = df[df[col].str.contains(col_to_find3) == True].index.tolist()[0]
                col3 = col

            if df[col].str.contains(col_to_find4).any() and row4 is None:
                row4 = df[df[col].str.contains(col_to_find4) == True].index.tolist()[0]
                col4 = col

            if row1 is not None and row2 is not None and row3 is not None and row4 is not None:
                break

        except Exception as e:
            print(type(e), e)
            pass

    return (row1, col1), (row2, col2), (row3, col3), (row4, col4)


def find_address(df, row, col):
    if row is None or col is None:
        print("ADDRESS NOT FOUND:", col, row)
        return
    try:
        # address = df[col][df[col].str.contains('по адресу').fillna(False)].tolist()[0].split('по адресу')[1]
        address = df.iloc[row][col].split('по адресу')[1]
        address = re.sub(r'[?|$|!:]', r'', address).strip()
    except Exception as e:
        address = None
        print("ADDRESS NOT FOUND:", type(e), e)
    return address
