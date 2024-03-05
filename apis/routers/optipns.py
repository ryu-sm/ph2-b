from typing import Optional
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


@router.get("/sales_person_options")
async def get_sales_person_options(parent_id: int, db=Depends(get_db)):
    try:
        sales_person_options = await crud.query_sales_person_options(db, parent_id)
        return JSONResponse(status_code=200, content=sales_person_options)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.get("/sales_exhibition_hall_options")
async def get_sales_exhibition_hall_options(parent_id: int, db=Depends(get_db)):
    try:
        sales_exhibition_hall_options = await crud.query_child_exhibition_hall_options(db, parent_id)
        return JSONResponse(status_code=200, content=sales_exhibition_hall_options)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.get("/pair_loan_options")
async def get_pair_loan_options(id: int, db=Depends(get_db)):
    try:
        pair_loan_options = await crud.query_pair_loan_options(db, id)
        return JSONResponse(status_code=200, content=pair_loan_options)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )
