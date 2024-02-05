from core.database import DB
from fastapi import Header
from fastapi import Depends

from core.custom import AuthException

import utils


async def get_db() -> DB:
    return DB()


async def get_user_id(authorization: str = Header(), db=Depends(get_db)):
    payload = utils.parse_token(authorization)
    if payload is None:
        raise AuthException
    else:
        return payload["id"]
