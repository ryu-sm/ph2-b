from loguru import logger
from datetime import datetime
from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import JSONResponse

from core.config import settings
from core.custom import LoggingContextRoute
from apis.deps import get_db
from apis.deps import get_user_id
import crud
import utils
import schemas


from templates.user_register_init_message import INIT_MESSAGE

router = APIRouter(route_class=LoggingContextRoute)


@router.get("/banks")
async def get_bank_options(db=Depends(get_db)):
    try:
        s_banks = await crud.query_bank_options(db)
        return JSONResponse(status_code=200, content=s_banks)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )
