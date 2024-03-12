from loguru import logger
from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import JSONResponse

from core.custom import LoggingContextRoute
from apis.deps import get_db
from apis.deps import get_token
import crud


router = APIRouter(route_class=LoggingContextRoute)


@router.put("/preliminaries/s_manager_id")
async def common_update_preliminaries_s_manager_id(data: dict, db=Depends(get_db), token=Depends(get_token)):
    try:
        await crud.update_p_application_headers_s_manager_id(db, data["p_application_header_id"], data["s_manager_id"])
        return JSONResponse(status_code=200, content={"message": "successful"})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.put("/preliminaries/s_sales_person_id")
async def common_update_preliminaries_s_sales_person_id(data: dict, db=Depends(get_db), token=Depends(get_token)):
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


@router.put("/preliminaries/sales_area_id")
async def common_update_preliminaries_sales_area_id(data: dict, db=Depends(get_db), token=Depends(get_token)):
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


@router.put("/preliminaries/sales_exhibition_hall_id")
async def common_update_preliminaries_sales_exhibition_hall_id(
    data: dict, db=Depends(get_db), token=Depends(get_token)
):
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


@router.get("/preliminary/{p_application_header_id}")
async def common_get_preliminary(p_application_header_id: int, db=Depends(get_db), token=Depends(get_token)):
    try:
        preliminary = {}
        p_application_headers = await crud.query_p_application_headers_for_ad(db, p_application_header_id)
        preliminary["p_application_headers"] = p_application_headers

        p_borrowing_details__1 = await crud.query_p_borrowing_details_for_ad(db, p_application_header_id, 1)
        preliminary["p_borrowing_details__1"] = p_borrowing_details__1

        if p_application_headers["land_advance_plan"] == "1":
            preliminary["p_borrowing_details__2"] = await crud.query_p_borrowing_details_for_ad(
                db, p_application_header_id, 2
            )

        preliminary["p_application_banks"] = await crud.query_p_application_banks_for_ad(db, p_application_header_id)

        p_applicant_persons__0 = await crud.query_p_applicant_persons_for_ad(db, p_application_header_id, 0)
        preliminary["p_applicant_persons__0"] = p_applicant_persons__0

        if p_application_headers["loan_type"] in ["3", "4"]:
            preliminary["p_applicant_persons__1"] = await crud.query_p_applicant_persons_for_ad(
                db, p_application_header_id, 1
            )

        if p_application_headers["join_guarantor_umu"] == "1":
            preliminary["p_join_guarantors"] = await crud.query_p_join_guarantors_for_ad(db, p_application_header_id)

        p_residents = await crud.query_p_residents_for_ad(db, p_application_header_id)
        if p_residents:
            preliminary["p_residents"] = p_residents

        if p_application_headers["curr_borrowing_status"] == "1":
            preliminary["p_borrowings"] = await crud.query_p_borrowings_for_ap(db, p_application_header_id)
        for i in range(10000000):
            pass

        return JSONResponse(status_code=200, content=preliminary)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )