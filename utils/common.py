import json
from decimal import Decimal
from fastapi.encoders import jsonable_encoder
from fastapi import Request
from urllib.parse import urlparse
from core.database import DB
import utils
from constant import JSON_DICT_FIELD_KEYS, JSON_LIST_FIELD_KEYS, INIT_NEW_HOUSE_PLANNED_RESIDENT_OVERVIEW


def parse_endpoint(url: str, path_params: dict):
    result = urlparse(url).path
    for key, value in path_params.items():
        result = result.replace(f"/{value}", "/{" + key + "}")
    return result


def blank_to_none(data: dict):
    json_str = json.dumps(data, ensure_ascii=False)
    json_str = json_str.replace('""', "null")
    return json.loads(json_str)


def none_to_blank(data: dict):
    if data is None:
        return data

    translated = {}
    for key, value in data.items():
        if isinstance(value, (int, float, Decimal)):
            translated[key] = str(value)
        elif key in JSON_DICT_FIELD_KEYS:
            translated[key] = json.loads(value) if value else INIT_NEW_HOUSE_PLANNED_RESIDENT_OVERVIEW
        elif key in JSON_LIST_FIELD_KEYS:
            translated[key] = json.loads(value) if value else []
        else:
            translated[key] = value
    jsonable_translated = jsonable_encoder(translated)
    json_str = json.dumps(jsonable_translated, ensure_ascii=False)
    json_str = json_str.replace("null", '""')
    return json.loads(json_str)


# accesee log
async def common_insert_c_access_log(db: DB, request: Request, params: dict):
    sql_params = {"id": await db.uuid_short(), "ip": request.client.host, **params}
    await db.execute(utils.gen_insert_sql("c_access_logs", sql_params))
