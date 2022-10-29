from datetime import datetime
import os
import ntpath
import pandas as pd

pd.options.mode.chained_assignment = None
VERBOSE = False


def create_table(df_path, row, column_names):
    """
    If table doesn't exist creates new table - IN USE
    """

    is_exist = os.path.exists(df_path)
    folder = os.path.dirname(df_path)
    is_folder_exist = os.path.exists(folder)
    columns = ",".join(column_names)

    if is_exist:
        with open(df_path, "a", encoding="utf-8") as writer:
            writer.write(row + "\n")
    else:
        if not is_folder_exist:
            os.makedirs(folder, exist_ok=True)
        with open(df_path, "w", encoding="utf-8") as writer:
            writer.write(columns + "\n")
            writer.write(row + "\n")

    return True


def create_csv(df_path, columns: tuple):
    columns_row = ",".join(columns)
    with open(df_path, "w", encoding="utf-8") as writer:
        writer.write(columns_row + "\n")


def path_leaf(path: str):
    """
    The function returns folder name or file name without extension
    :param path: str // full path
    :return: str // name
    """
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def get_timestamp(delimiter1="_", delimiter2="-", raw=True):
    """
    The function returns timestamp in the following format:
    YYYY{$d2}MM{$d2}DD{$d1}HH{$d2}MM{$d2}SS
    where $d1 is delimiter1, $d2 is delimiter2
    """
    timestamp_obj = datetime.now()
    if raw:
        return timestamp_obj
    date_str = f"%d{delimiter2}%b{delimiter2}%Y"
    time_str = f"%H{delimiter2}%M{delimiter2}%S"
    time_format = f"{date_str}{delimiter1}{time_str}"
    return timestamp_obj.strftime(time_format)


if __name__ == "__main__":
    print(get_timestamp(raw=False))
