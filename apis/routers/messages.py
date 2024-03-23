from loguru import logger
from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import JSONResponse


from core.custom import LoggingContextRoute
from apis.deps import get_db
from apis.deps import get_token
import crud
import utils


router = APIRouter(route_class=LoggingContextRoute)


@router.get("/user/messages")
async def get_messages_for_user(db=Depends(get_db), token=Depends(get_token)):
    try:
        messages = await crud.query_messages_for_user(db, c_user_id=token["id"])
        return JSONResponse(status_code=200, content=messages)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.post("/message")
async def insert_message(data: dict, db=Depends(get_db), token=Depends(get_token)):
    try:
        await crud.insert_message(db, utils.blank_to_none(data), token["role_type"], token["id"])
        return JSONResponse(status_code=200, content={"message": "successful"})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.put("/messages")
async def update_messages(data: dict, db=Depends(get_db), token=Depends(get_token)):
    try:
        await crud.update_messages_viewed(db, data["messages_ids"], token["id"])
        return JSONResponse(status_code=200, content={"message": "successful"})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.get("/manager/messages")
async def get_manager_messages(db=Depends(get_db), token=Depends(get_token)):
    try:
        messages = await crud.query_manager_dashboard_messages(db)
        return JSONResponse(status_code=200, content=messages)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.get("/sales-person/messages")
async def get_manager_messages(db=Depends(get_db), token=Depends(get_token)):
    try:
        messages = await crud.query_sales_person_dashboard_messages(db, token["orgs"], token["id"])
        return JSONResponse(status_code=200, content=messages)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.get("/message")
async def get_message(id: str, type: str, db=Depends(get_db), token=Depends(get_token)):
    try:
        message_detail = await crud.query_message(db, id, type)
        return JSONResponse(status_code=200, content=message_detail)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.delete("/message/{id}")
async def delete_message(id: int, db=Depends(get_db), token=Depends(get_token)):
    try:
        await crud.delete_message(db, id)
        return JSONResponse(status_code=200, content={"message": "successful"})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )
