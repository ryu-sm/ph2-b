from loguru import logger
from datetime import datetime
from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import JSONResponse

from core.config import settings
from core.custom import LoggingContextRoute
from apis.deps import get_db
from apis.deps import get_token
import crud
import utils

router = APIRouter(route_class=LoggingContextRoute)


@router.put("/preliminarie/s_manager_id")
async def common_update_preliminarie_s_manager_id(data: dict, db=Depends(get_db), token=Depends(get_token)):

    try:
        await crud.update_p_application_headers_s_manager_id(db, data["p_application_header_id"], data["s_manager_id"])
        return JSONResponse(status_code=200, content={"message": "successful"})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.put("/preliminarie/s_sales_person_id")
async def common_update_preliminarie_s_sales_person_id(data: dict, db=Depends(get_db), token=Depends(get_token)):

    try:
        await crud.update_p_application_headers_s_sales_person_id(
            db, data["p_application_header_id"], data["s_sales_person_id"]
        )
        return JSONResponse(status_code=200, content={"message": "successful"})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.put("/preliminarie/sales_area_id")
async def common_update_preliminarie_sales_area_id(data: dict, db=Depends(get_db), token=Depends(get_token)):

    try:
        result = await crud.update_p_application_headers_sales_area_id(
            db, data["p_application_header_id"], data["sales_area_id"], data["sales_exhibition_hall_id"]
        )
        return JSONResponse(status_code=200, content=result)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.put("/preliminarie/sales_exhibition_hall_id")
async def common_update_preliminarie_sales_exhibition_hall_id(data: dict, db=Depends(get_db), token=Depends(get_token)):

    try:
        result = await crud.update_p_application_headers_sales_exhibition_hall_id(
            db, data["p_application_header_id"], data["sales_exhibition_hall_id"], data["s_sales_person_id"]
        )
        return JSONResponse(status_code=200, content=result)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )
