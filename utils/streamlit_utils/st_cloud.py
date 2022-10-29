import shutil
import os
import streamlit as st

LOCAL_ZIPDIR_PATH = "./backup/"
ROOT_DIR = "./"


def _convert_datetime_string(datetime_string, string_format='%Y-%m-%d %H-%M-%S'):
    from datetime import datetime
    datetime_obj = datetime.strptime(datetime_string, string_format)
    return datetime_obj


def _get_duration_between_timestamps(tm_now: str, tm_then: str, mode='hours', verbose=False):
    last = _convert_datetime_string(tm_then)
    now = _convert_datetime_string(tm_now)
    duration = now - last

    if verbose:
        print(duration)

    duration_in_sec = duration.total_seconds()
    duration_in_hours = divmod(duration_in_sec, 3600)[0]

    if mode == 'seconds':
        return duration_in_sec
    elif mode == 'hours':
        return duration_in_hours


def st_download(file_path, alt_name='backup.zip'):
    with open(file_path, "rb") as reader:
        data = reader.read()

    st.download_button("Download backup file", data, alt_name)


def get_size_mb(filename):
    os.path.getsize(filename) >> 20
    return f"{filename.tgz} MB"


def format_bucket_files(bucket_files):
    formatted_dict = {}

    for file, size_in_bytes in bucket_files.items():
        size_in_mb = f"file size: {round(size_in_bytes / (1024 * 1024), 2)} MB"
        formatted_dict.update({file: size_in_mb})

    return formatted_dict


def create_zip_file(dir_names, output_filename=None, prefix=''):
    if os.path.exists(LOCAL_ZIPDIR_PATH):
        shutil.rmtree(LOCAL_ZIPDIR_PATH)

    os.makedirs(LOCAL_ZIPDIR_PATH, exist_ok=True)

    for dir_name in dir_names:
        dest_name = os.path.join(LOCAL_ZIPDIR_PATH, os.path.basename(dir_name))
        shutil.copytree(src=dir_name, dst=dest_name)

    if output_filename is None:
        output_filename = f"backup-{prefix}"
        output_filename = os.path.join(ROOT_DIR, "JSONS", output_filename)

    shutil.make_archive(output_filename, 'zip', LOCAL_ZIPDIR_PATH)
    output_filename_zipped = f"{output_filename}.zip"

    return output_filename_zipped


if __name__ == "__main__":
    pass
