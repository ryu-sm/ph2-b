import json
from constant import (
    JSON_DICT_FIELD_KEYS,
    JSON_LIST_FIELD_KEYS,
    INIT_NEW_HOUSE_PLANNED_RESIDENT_OVERVIEW,
    FILE_FIELF_KEYS,
)


def gen_insert_sql(table: str, params: dict):
    fields = []
    values = []

    for field, value in params.items():
        if field in FILE_FIELF_KEYS:
            continue
        if value is not None:
            if field in JSON_DICT_FIELD_KEYS:
                is_init = value == INIT_NEW_HOUSE_PLANNED_RESIDENT_OVERVIEW
                values.append(f"'{json.dumps(value, ensure_ascii=False)}'" if not is_init else "NULL")
                fields.append(field)
                continue
            if field in JSON_LIST_FIELD_KEYS:
                if len(value) == 0:
                    continue
                json_str = json.dumps(value, ensure_ascii=False)
                values.append(f"'{json_str}'")
                fields.append(field)
                continue
            values.append(f"'{value}'")
            fields.append(field)

    return f"INSERT INTO {table} ({', '.join(fields)}) VALUES ({', '.join(values)});"


def gen_update_sql(table: str, params: dict, where: dict):
    up_items = []
    where_items = []

    for field, value in params.items():
        if field in JSON_DICT_FIELD_KEYS:
            is_init = value == INIT_NEW_HOUSE_PLANNED_RESIDENT_OVERVIEW
            t_value = f"'{json.dumps(value, ensure_ascii=False)}'" if value and not is_init else "NULL"
            up_items.append(f"{field} = {t_value}")
            continue
        if field in JSON_LIST_FIELD_KEYS:
            t_value = f"'{json.dumps(value, ensure_ascii=False)}'" if field else "NULL"
            up_items.append(f"{field} = {t_value}")
            continue

        t_value = f"'{value}'" if value else "NULL"
        up_items.append(f"{field} = {t_value}")

    for field, value in where.items():
        where_items.append(f"{field} = '{value}'")

    return f"UPDATE {table} SET {', '.join(up_items)} WHERE {' AND '.join(where_items)};"
