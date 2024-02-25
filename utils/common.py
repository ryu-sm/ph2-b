import json
from decimal import Decimal
from fastapi.encoders import jsonable_encoder
from urllib.parse import urlparse


def parse_endpoint(url: str, path_params: dict):
    try:
        result = urlparse(url).path
        for key, value in path_params.items():
            result = result.replace(f"/{value}", "/{" + key + "}")
        return result
    except Exception:
        return None


def blank_to_none(data: dict):
    json_str = json.dumps(data, ensure_ascii=False)
    json_str = json_str.replace('""', "null")
    return json.loads(json_str)
    # return json_str


def is_numer(obj):
    return isinstance(obj, (int, float, Decimal))


def none_to_blank(data: dict):
    if data is None:
        return data
    data_ = jsonable_encoder(data)
    json_str = json.dumps(data_, ensure_ascii=False)
    json_str = json_str.replace("null", '""')
    temp = json.loads(json_str)
    result = {}
    for key, value in temp.items():
        if is_numer(value):
            result[key] = str(value)
        else:
            result[key] = value
    return result
