from loguru import logger
from fastapi import APIRouter, Request
from fastapi import Depends
from fastapi.responses import JSONResponse

from core.custom import LoggingContextRoute
from apis.deps import get_db
from apis.deps import get_token
import crud
import utils
from utils.s3 import download_from_s3
from utils import blank_to_none, mann_to, to_mann

from constant import (
    ACCESS_LOG_OPERATION,
    TOKEN_ROLE_TYPE,
    P_APPLICANT_PERSONS_TYPE,
    P_BORROWING_DETAILS_TIME_TYPE,
    LOAN_TYPE,
    LAND_ADVANCE_PLAN,
    JOIN_GUARANTOR_UMU,
    CURR_BORROWING_STATUS,
)

from constant import DEFAULT_200_MSG, DEFAULT_500_MSG

router = APIRouter()


@router.put("/preliminary/s_manager_id")
async def common_update_preliminary_s_manager_id(data: dict, db=Depends(get_db), token=Depends(get_token)):
    try:
        await crud.update_p_application_headers_s_manager_id(
            db, data["p_application_header_id"], data["s_manager_id"], token["role_type"], token["id"]
        )
        return JSONResponse(status_code=200, content={"message": "successful"})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.put("/preliminary/s_sales_person_id")
async def common_update_preliminary_s_sales_person_id(data: dict, db=Depends(get_db), token=Depends(get_token)):
    try:
        await crud.update_p_application_headers_s_sales_person_id(
            db, blank_to_none(data), token["role_type"], token["id"]
        )
        return JSONResponse(status_code=200, content={"message": "successful"})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.put("/preliminary/sales_area_id")
async def common_update_preliminary_sales_area_id(data: dict, db=Depends(get_db), token=Depends(get_token)):
    try:
        result = await crud.update_p_application_headers_sales_area_id(
            db, blank_to_none(data), token["role_type"], token["id"]
        )
        return JSONResponse(status_code=200, content=result)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.put("/preliminary/sales_exhibition_hall_id")
async def common_update_preliminary_sales_exhibition_hall_id(data: dict, db=Depends(get_db), token=Depends(get_token)):
    try:
        result = await crud.update_p_application_headers_sales_exhibition_hall_id(
            db, blank_to_none(data), token["role_type"], token["id"]
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
        preliminary["p_application_headers"] = to_mann(p_application_headers)

        p_borrowing_details__1 = await crud.query_p_borrowing_details_for_ad(
            db, p_application_header_id, P_BORROWING_DETAILS_TIME_TYPE.ONE_TIME.value
        )
        preliminary["p_borrowing_details__1"] = to_mann(p_borrowing_details__1)

        if p_application_headers["land_advance_plan"] == LAND_ADVANCE_PLAN.HOPE.value:
            p_borrowing_details__2 = await crud.query_p_borrowing_details_for_ad(
                db, p_application_header_id, P_BORROWING_DETAILS_TIME_TYPE.TWO_TIME.value
            )
            preliminary["p_borrowing_details__2"] = to_mann(p_borrowing_details__2)

        preliminary["p_application_banks"] = await crud.query_p_application_banks_for_ad(db, p_application_header_id)

        p_applicant_persons__0 = await crud.query_p_applicant_persons_for_ad(
            db, p_application_header_id, P_APPLICANT_PERSONS_TYPE.APPLICANT.value
        )
        preliminary["p_applicant_persons__0"] = to_mann(p_applicant_persons__0)

        if p_application_headers["loan_type"] in [
            LOAN_TYPE.TOTAL_INCOME_EQUITY.value,
            LOAN_TYPE.TOTAL_INCOME_NO_EQUITY.value,
        ]:
            p_applicant_persons__1 = await crud.query_p_applicant_persons_for_ad(
                db, p_application_header_id, P_APPLICANT_PERSONS_TYPE.TOTAL_INCOME.value
            )
            preliminary["p_applicant_persons__1"] = to_mann(p_applicant_persons__1)

        if p_application_headers["join_guarantor_umu"] == JOIN_GUARANTOR_UMU.HAVE.value:
            p_join_guarantors = await crud.query_p_join_guarantors_for_ad(db, p_application_header_id)
            preliminary["p_join_guarantors"] = [to_mann(item) for item in p_join_guarantors]

        p_residents = await crud.query_p_residents_for_ad(db, p_application_header_id)
        if p_residents:
            preliminary["p_residents"] = [to_mann(item) for item in p_residents]

        if p_application_headers["curr_borrowing_status"] == CURR_BORROWING_STATUS.HAVE.value:
            p_borrowings = await crud.query_p_borrowings_for_ad(db, p_application_header_id)
            preliminary["p_borrowings"] = [to_mann(item) for item in p_borrowings]

        preliminary["p_activities"] = await crud.query_p_activities_for_ad(db, p_application_header_id)
        preliminary["files_p_activities"] = await crud.query_files_p_activities_for_ad(db, p_application_header_id)
        preliminary["p_result"] = await crud.query_p_result(db, p_application_header_id)

        return JSONResponse(status_code=200, content=preliminary)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.put("/preliminary/{p_application_header_id}")
async def put_preliminary(
    p_application_header_id: str, data: dict, db=Depends(get_db), token: dict = Depends(get_token)
):
    try:
        main_tab = data.get("mainTab")
        sub_tab = data.get("subTab")
        print("main_tab", main_tab)
        print("sub_tab", sub_tab)
        if main_tab == 1 and sub_tab == 1:
            await crud.diff_update_p_application_headers_for_ad(
                db, mann_to(data["p_application_headers"]), p_application_header_id, token["role_type"], token["id"]
            )
            await crud.diff_update_p_application_banks_for_ad(
                db, data["p_application_banks"], p_application_header_id, token["role_type"], token["id"]
            )
            await crud.diff_update_p_borrowing_details_for_ad(
                db, mann_to(data["p_borrowing_details__1"]), p_application_header_id, 1, token["role_type"], token["id"]
            )
            if data["p_application_headers"]["land_advance_plan"] == "1":
                await crud.diff_update_p_borrowing_details_for_ad(
                    db,
                    mann_to(data["p_borrowing_details__2"]),
                    p_application_header_id,
                    2,
                    token["role_type"],
                    token["id"],
                )

        if main_tab == 1 and sub_tab in [2, 3]:
            await crud.diff_update_p_applicant_persons_for_ad(
                db, mann_to(data["p_applicant_persons__0"]), p_application_header_id, 0, token["role_type"], token["id"]
            )

        if main_tab == 1 and sub_tab == 4:
            if data.get("p_application_headers") is not None:
                await crud.diff_update_p_application_headers_for_ad(
                    db, mann_to(data["p_application_headers"]), p_application_header_id, token["role_type"], token["id"]
                )
                await crud.diff_update_p_application_banks_for_ad(
                    db, data["p_application_banks"], p_application_header_id, token["role_type"], token["id"]
                )
                await crud.diff_update_p_borrowing_details_for_ad(
                    db,
                    mann_to(data["p_borrowing_details__1"]),
                    p_application_header_id,
                    1,
                    token["role_type"],
                    token["id"],
                )
                if data["p_application_headers"]["land_advance_plan"] == "1":
                    await crud.diff_update_p_borrowing_details_for_ad(
                        db,
                        mann_to(data["p_borrowing_details__2"]),
                        p_application_header_id,
                        2,
                        token["role_type"],
                        token["id"],
                    )
            await crud.diff_update_p_join_guarantors_for_ad(
                db,
                [mann_to(item) for item in data["p_join_guarantors"]],
                p_application_header_id,
                token["role_type"],
                token["id"],
            )

        if main_tab == 1 and sub_tab == 5:
            await crud.diff_update_p_application_headers_for_ad(
                db, mann_to(data["p_application_headers"]), p_application_header_id, token["role_type"], token["id"]
            )
            await crud.diff_update_p_residents_for_ad(
                db,
                [mann_to(item) for item in data["p_residents"]],
                p_application_header_id,
                token["role_type"],
                token["id"],
            )
            await crud.diff_update_p_applicant_persons_for_ad(
                db, mann_to(data["p_applicant_persons__0"]), p_application_header_id, 0, token["role_type"], token["id"]
            )
        if main_tab == 1 and sub_tab == 6:
            await crud.diff_update_p_application_headers_for_ad(
                db, mann_to(data["p_application_headers"]), p_application_header_id, token["role_type"], token["id"]
            )
            if data["p_application_headers"]["curr_borrowing_status"] == "1":
                await crud.diff_update_p_borrowings_for_ad(
                    db,
                    [mann_to(item) for item in data["p_borrowings"]],
                    p_application_header_id,
                    token["role_type"],
                    token["id"],
                )
        if main_tab == 1 and sub_tab in [7, 8]:
            await crud.diff_update_p_application_headers_for_ad(
                db, mann_to(data["p_application_headers"]), p_application_header_id, token["role_type"], token["id"]
            )

        if main_tab == 1 and sub_tab == 9:
            await crud.diff_update_p_application_headers_for_ad(
                db, mann_to(data["p_application_headers"]), p_application_header_id, token["role_type"], token["id"]
            )
            await crud.diff_update_p_borrowings_for_ad(
                db,
                [mann_to(item) for item in data["p_borrowings"]],
                p_application_header_id,
                token["role_type"],
                token["id"],
            )
            await crud.diff_update_p_applicant_persons_for_ad(
                db, mann_to(data["p_applicant_persons__0"]), p_application_header_id, 0, token["role_type"], token["id"]
            )

        if main_tab == 2 and sub_tab in [2, 3]:
            await crud.diff_update_p_applicant_persons_for_ad(
                db, mann_to(data["p_applicant_persons__1"]), p_application_header_id, 1, token["role_type"], token["id"]
            )
        if main_tab == 2 and sub_tab == 9:
            if data.get("p_application_headers") is not None:
                await crud.diff_update_p_application_headers_for_ad(
                    db, mann_to(data["p_application_headers"]), p_application_header_id, token["role_type"], token["id"]
                )
                await crud.diff_update_p_application_banks_for_ad(
                    db, data["p_application_banks"], p_application_header_id, token["role_type"], token["id"]
                )
                await crud.diff_update_p_borrowing_details_for_ad(
                    db,
                    mann_to(data["p_borrowing_details__1"]),
                    p_application_header_id,
                    1,
                    token["role_type"],
                    token["id"],
                )

                if data["p_application_headers"]["land_advance_plan"] == "1":
                    await crud.diff_update_p_borrowing_details_for_ad(
                        db,
                        mann_to(data["p_borrowing_details__2"]),
                        p_application_header_id,
                        2,
                        token["role_type"],
                        token["id"],
                    )

            if data.get("p_join_guarantors") is not None:
                await crud.diff_update_p_join_guarantors_for_ad(
                    db,
                    [mann_to(item) for item in data["p_join_guarantors"]],
                    p_application_header_id,
                    token["role_type"],
                    token["id"],
                )

            await crud.diff_update_p_applicant_persons_for_ad(
                db, mann_to(data["p_applicant_persons__1"]), p_application_header_id, 1, token["role_type"], token["id"]
            )

        return JSONResponse(status_code=200, content={"message": "successful"})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.get("/files-view/{p_application_header_id}")
async def get_files_view(
    p_application_header_id: int, type: int, category: str, db=Depends(get_db), token=Depends(get_token)
):
    try:
        result = await crud.query_p_uploaded_files_for_ad_view(db, p_application_header_id, type, category)
        return JSONResponse(status_code=200, content=result)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.get("/p_borrowings/files-view/{p_application_header_id}")
async def get_p_borrowings_files_view(p_application_header_id: int, db=Depends(get_db), token=Depends(get_token)):
    try:
        result = await crud.query_p_borrowings_files_for_ad_view(db, p_application_header_id)
        return JSONResponse(status_code=200, content=result)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.get("/row_data/{p_application_header_id}")
async def get_raw_data(
    p_application_header_id: int, request: Request, db=Depends(get_db), token: dict = Depends(get_token)
):
    try:

        file = utils.download_base64_from_s3(f"{p_application_header_id}/row_data.xlsx")
        p_application_header_basic = await crud.query_p_application_header_basic(db, p_application_header_id)
        await utils.common_insert_c_access_log(
            db,
            request,
            params={
                "apply_no": p_application_header_basic["apply_no"],
                "account_id": token.get("id"),
                "account_type": token.get("role_type"),
                "operation": ACCESS_LOG_OPERATION.DOWNLOAD.value,
                "operation_content": "ローデータダウンロード: ダウンロードした",
            },
        )
        return JSONResponse(status_code=200, content={"src":file})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.get("/edit_histories/{p_application_header_id}")
async def get_update_hitories(
    p_application_header_id: int, update_history_key: str, db=Depends(get_db), token=Depends(get_token)
):
    try:
        histories = await crud.query_field_uodate_histories_for_ad(db, p_application_header_id, update_history_key)
        return JSONResponse(status_code=200, content=histories)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.get("/provisional_status/{p_application_header_id}")
async def get_provisional_status(p_application_header_id: int, db=Depends(get_db), token=Depends(get_token)):
    try:
        result = await crud.query_provisional_status(db, p_application_header_id)
        return JSONResponse(status_code=200, content=result)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )
