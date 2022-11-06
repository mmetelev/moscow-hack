import json2table
import json


def json2html(json_file=None, json_path=None, verbose=False):
    if json_path is not None:
        with open(json_path, "r") as f:
            json_file = f.read()
    elif json_file is None:
        raise ValueError("json_file or json_path must be provided")
    data = json.loads(json_file)
    build_direction = "LEFT_TO_RIGHT"
    table_attributes = {"style": "width:80%",
                        "padding": "5px",
                        "border": "1",
                        "borderradius": "5",
                        "class": "table table-striped table-hover",
                        "align": "center",
                        "bgcolor": "#f2f2f2",
                        "bordercolor": "#5da8a8",
                        }
    html = json2table.convert(data,
                              build_direction=build_direction,
                              table_attributes=table_attributes)
    print(html) if verbose else None
    return html


if __name__ == "__main__":
    pass
    # json_path = "test.json"
    # json_file = "{\"key\":\"jfljsdflks\"}"
    # # json2html(json_path=json_path)
    # json2html(json_file=json_file)