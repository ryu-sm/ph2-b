from loguru import logger
from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import JSONResponse
from core.custom import LoggingContextRoute
from apis.deps import get_db
from apis.deps import get_token
import crud

from typing import Optional


router = APIRouter(route_class=LoggingContextRoute)


@router.get("/orgs")
async def user_orgs(s_sales_company_org_id: Optional[int] = None, db=Depends(get_db)):
    try:
        orgs = await crud.query_s_sales_company_orgs(db, s_sales_company_org_id)
        return JSONResponse(status_code=200, content=orgs)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.get("/orgs")
async def user_orgs(s_sales_company_org_id: Optional[int] = None, db=Depends(get_db)):
    try:
        orgs = await crud.query_s_sales_company_orgs(db, s_sales_company_org_id)
        return JSONResponse(status_code=200, content=orgs)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.get("/orgs-info")
async def get_parents_orgs_for_ap_with_id(
    s_sales_company_org_id: Optional[int] = None, db=Depends(get_db), token=Depends(get_token)
):
    try:
        orgs_infos = await crud.query_parents_orgs_for_ap_with_id(db, s_sales_company_org_id)
        return JSONResponse(status_code=200, content=orgs_infos)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.get("/orgs/category")
async def get_orgs_with_categories(categories: str, db=Depends(get_db), token=Depends(get_token)):
    try:
        orgs = await crud.query_s_sales_company_orgs_with_categories(db, categories)
        return JSONResponse(status_code=200, content=orgs)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.get("/azure/orgs/{category}")
async def get_orgs_with_categories(category: str, db=Depends(get_db)):
    try:
        orgs = await crud.query_s_sales_company_orgs_with_categories(db, category)
        return JSONResponse(status_code=200, content=orgs)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.get("/orgs/children")
async def get_children_orgs_with_category(
    category: str, parent_id: Optional[int] = None, db=Depends(get_db), token=Depends(get_token)
):
    try:
        if parent_id is None:
            orgs = await crud.query_s_sales_company_orgs_with_categories(db, category)
            return JSONResponse(status_code=200, content=orgs)
        else:
            orgs = await crud.query_children_s_sales_company_orgs_with_category(db, parent_id, category)
            return JSONResponse(status_code=200, content=orgs)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.get("/orgs/s_sales_persons")
async def get_orgs_access_s_sales_persons(orgs_id: Optional[int] = None, db=Depends(get_db), token=Depends(get_token)):
    try:
        if orgs_id is None:
            orgs = await crud.query_all_sales_person_options(db)
            return JSONResponse(status_code=200, content=orgs)
        else:
            orgs = await crud.query_orgs_access_s_sales_persons(db, orgs_id)
            return JSONResponse(status_code=200, content=orgs)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )
