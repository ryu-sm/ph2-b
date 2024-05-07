from constant import MANN_TRANSLATE_FIELDS


def mann_to(data: dict):
    if data is None:
        return {}
    new_data = {**data}
    for field in MANN_TRANSLATE_FIELDS:
        if field in data and data[field]:
            new_data[field] = str(int(data[field]) * 10000)
    return new_data


def to_mann(data: dict):
    if data is None:
        return {}
    new_data = {**data}
    for field in MANN_TRANSLATE_FIELDS:
        if field in data and data[field]:
            new_data[field] = str(int(int(data[field]) / 10000))
    return new_data
