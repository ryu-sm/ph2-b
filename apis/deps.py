from core.database import DB
from fastapi import Header
from fastapi import Depends
from deepdiff import DeepDiff
from core.custom import AuthException

import utils
import crud
import json


async def get_db() -> DB:
    return DB()


async def get_token(authorization: str = Header(), db: DB = Depends(get_db)):
    payload = utils.parse_token(authorization)
    if payload is None:
        raise AuthException

    if payload["role_type"] == 2:
        db_payload = await crud.query_s_sales_person_token_payload(db, payload["id"])
        t_payload = {
            "id": payload["id"],
            "code": payload["code"],
            "email": payload["email"],
            "name_kanji": payload["name_kanji"],
            "role_type": payload["role_type"],
        }
        if DeepDiff(db_payload, t_payload):
            raise AuthException

    if payload["role_type"] == 3:
        db_payload = await crud.query_s_manager_token_payload(db, payload["id"])
        t_payload = {
            "id": payload["id"],
            "email": payload["email"],
            "name_kanji": payload["name_kanji"],
            "role_type": payload["role_type"],
        }

        if DeepDiff(db_payload, t_payload):
            raise AuthException

    return payload
