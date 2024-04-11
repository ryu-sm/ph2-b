from loguru import logger
from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import JSONResponse


from core.custom import LoggingContextRoute
from apis.deps import get_db
from apis.deps import get_token
import crud
import utils
import schemas


router = APIRouter(route_class=LoggingContextRoute)


@router.post("/sales-person/c_archive_files")
async def sales_person_insert_c_archive_files(data: dict, db=Depends(get_db), token=Depends(get_token)):
    try:
        await crud.insert_c_archive_files(
            db,
            data["files"],
            data["s_sales_person_id"],
            data["s_sales_company_org_id"],
            token["role_type"],
            token["id"],
        )

        return JSONResponse(status_code=200, content={"message": "successful"})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.get("/sales-person/c_archive_files")
async def query_c_archive_files(db=Depends(get_db), token=Depends(get_token)):
    try:
        c_archive_files = await crud.query_c_archive_files_for_s_sales_person(db, s_sales_person_id=token["id"])

        return JSONResponse(status_code=200, content=c_archive_files)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.get("/manager/c_archive_files")
async def query_c_archive_files(db=Depends(get_db), token=Depends(get_token)):
    try:
        c_archive_files = await crud.query_c_archive_files_for_manager(db)

        return JSONResponse(status_code=200, content=c_archive_files)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.get("/c_archive_files/{id}")
async def sales_person_insert_c_archive_files(id: int, db=Depends(get_db), token=Depends(get_token)):
    try:
        c_archive_file = await crud.query_c_archive_file(db, id)

        return JSONResponse(status_code=200, content=c_archive_file)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.delete("/c_archive_files/{id}")
async def sales_person_insert_c_archive_files(id: int, db=Depends(get_db), token=Depends(get_token)):
    try:
        await crud.delete_c_archive_file(db, id)

        return JSONResponse(status_code=200, content={"message": "successful"})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.delete("/c_archive_file/{id}")
async def sales_person_insert_c_archive_files(id: int, db=Depends(get_db), token=Depends(get_token)):
    try:
        has_files = await crud.delete_c_archive_file_for_sub(db, id)

        return JSONResponse(status_code=200, content={"has_file": has_files})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.put("/c_archive_file/{id}/note")
async def sales_person_update_c_archive_file_note(id: int, data: dict, db=Depends(get_db), token=Depends(get_token)):
    try:
        has_files = await crud.update_c_archive_file_note(db, id, data["note"])

        return JSONResponse(status_code=200, content={"has_file": has_files})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )
