import os.path
import uuid
import json
import numpy as np

from utils.process_xlsx import process_xls, crop_columns


def serialise_ordered_dict(ordered_dict):
    """ Serialises an ordered dict to a json string
    :param ordered_dict: ordered dict
    :return: json string
    """
    new_dict = {}
    for key, value in ordered_dict.items():
        if isinstance(value, np.ndarray):
            new_dict[key] = value.tolist()
        else:
            new_dict[key] = value
    return json.dumps(new_dict, indent=4)


def get_result(config):
    default_values = {
        'user_file': 'nan',
        'user_address': 'nan',
        'sheet_number': 0,
        'address': 'true',
        'reference': 'КПГЗ',
        'save_data': 'false',
    }

    response_dict = {
        'parameters': default_values,
        'df': None,
        'costs': None,
        'address': None,
        'chapters': None}

    for key, val in default_values.items():
        if key in config:
            default_values[key] = config[key]

    if os.path.exists(default_values['user_file']):
        file_uploaded = default_values['user_file']
        sheet_with_data = default_values['sheet_number']
        df_raw, df, costs, chapters, address = process_xls(file_uploaded, sheet_with_data)

        response_dict['address'] = address
        response_dict['chapters'] = chapters

        if costs is not None:
            costs_path = f"./data/temp-{uuid.uuid4()}-costs.json"
            costs.to_json(costs_path, orient='records', lines=True)
            response_dict['costs'] = costs_path

        if df is not None:
            df = crop_columns(df)
            df_path = f"./data/temp-{uuid.uuid4()}-df.csv"
            df.to_csv(df_path, index=False)
            response_dict['df'] = df_path

    out = json.dumps(response_dict)

    return out
