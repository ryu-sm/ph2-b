from core.database import DB
from fastapi import Header, Request
from fastapi import Depends
from deepdiff import DeepDiff
from core.custom import AuthException
from core.config import settings
import utils
import crud


async def get_db() -> DB:
    return DB()


async def get_token(authorization: str = Header(), db: DB = Depends(get_db)):
    payload = utils.parse_token(authorization)
    if payload is None:
        raise AuthException(url="none")

    if payload["role_type"] == 1:
        db_payload = await crud.query_c_user_token_payload(db, payload["id"])
        t_payload = {
            "id": payload.get("id"),
            "email": payload.get("email"),
        }
        if DeepDiff(
            {"id": db_payload.get("id"), "email": db_payload.get("email")},
            t_payload,
        ):
            raise AuthException(url="/login")

    if payload["role_type"] == 2:
        db_payload = await crud.query_s_sales_person_token_payload(db, payload["id"])
        if payload.get("type") == 2:
            tenant_id = await crud.query_azure_access(db, payload.get("id"))
            if settings.TENANT != tenant_id:
                print("/azure-logout?unaccess=1")
                raise AuthException(url="/azure-logout?unaccess=1")
        t_payload = {
            "id": payload.get("id"),
            "email": payload.get("email"),
            "type": payload.get("type"),
            "name_kanji": payload.get("name_kanji"),
            "role_type": payload.get("role_type"),
        }
        if DeepDiff(db_payload, t_payload):
            if payload.get("type") == 2:
                raise AuthException(url="/azure-logout")
            else:
                raise AuthException(url="/sales-person/login")

    if payload["role_type"] == 3:
        db_payload = await crud.query_s_manager_token_payload(db, payload["id"])
        t_payload = {
            "id": payload.get("id"),
            "email": payload.get("email"),
            "name_kanji": payload.get("name_kanji"),
            "role_type": payload.get("role_type"),
        }

        if DeepDiff(db_payload, t_payload):
            raise AuthException(url="/manager/login")

    return payload
