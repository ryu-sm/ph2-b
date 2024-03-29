from loguru import logger
from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import JSONResponse

from core.custom import LoggingContextRoute
from apis.deps import get_db
from apis.deps import get_token
import crud
from utils.s3 import download_from_s3


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
            preliminary["p_borrowings"] = await crud.query_p_borrowings_for_ad(db, p_application_header_id)

        preliminary["p_uploaded_files"] = await crud.query_p_uploaded_files_for_ad(db, p_application_header_id)
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
async def user_orgs(p_application_header_id: str, data: dict, db=Depends(get_db), token: dict = Depends(get_token)):
    try:
        main_tab = data.get("mainTab")
        sub_tab = data.get("subTab")
        print("main_tab", main_tab)
        print("sub_tab", sub_tab)
        if main_tab == 1 and sub_tab == 1:
            await crud.diff_update_p_application_headers_for_ad(
                db, data["p_application_headers"], p_application_header_id, token["role_type"], token["id"]
            )
            await crud.diff_update_p_application_banks_for_ad(
                db, data["p_application_banks"], p_application_header_id, token["role_type"], token["id"]
            )
            await crud.diff_update_p_borrowing_details_for_ad(
                db, data["p_borrowing_details__1"], p_application_header_id, 1, token["role_type"], token["id"]
            )
            if data["p_application_headers"]["loan_type"] in ["1", "2"]:
                await crud.delete_p_applicant_persons__1_for_ad(db, p_application_header_id)
                # TODO: 删除图片

            if data["p_application_headers"]["land_advance_plan"] == "1":
                await crud.diff_update_p_borrowing_details_for_ad(
                    db, data["p_borrowing_details__2"], p_application_header_id, 2, token["role_type"], token["id"]
                )
            else:
                await crud.delete_p_borrowing_details__2_for_ad(db, p_application_header_id)

        if main_tab == 1 and sub_tab in [2, 3]:
            await crud.diff_update_p_applicant_persons_for_ad(
                db, data["p_applicant_persons__0"], p_application_header_id, 0, token["role_type"], token["id"]
            )

        if main_tab == 1 and sub_tab == 4:
            if data.get("p_application_headers") is not None:
                await crud.diff_update_p_application_headers_for_ad(
                    db, data["p_application_headers"], p_application_header_id, token["role_type"], token["id"]
                )

                await crud.diff_update_p_application_banks_for_ad(
                    db, data["p_application_banks"], p_application_header_id, token["role_type"], token["id"]
                )
                await crud.diff_update_p_borrowing_details_for_ad(
                    db, data["p_borrowing_details__1"], p_application_header_id, 1, token["role_type"], token["id"]
                )
                if data["p_application_headers"]["loan_type"] in ["1", "2"]:
                    await crud.delete_p_applicant_persons__1_for_ad(db, p_application_header_id)
                    # TODO: 删除图片

                if data["p_application_headers"]["land_advance_plan"] == "1":
                    await crud.diff_update_p_borrowing_details_for_ad(
                        db, data["p_borrowing_details__2"], p_application_header_id, 2, token["role_type"], token["id"]
                    )
                else:
                    await crud.delete_p_borrowing_details__2_for_ad(db, p_application_header_id)

            await crud.diff_update_p_join_guarantors_for_ad(
                db, data["p_join_guarantors"], p_application_header_id, token["role_type"], token["id"]
            )

        if main_tab == 1 and sub_tab == 5:
            await crud.diff_update_p_application_headers_for_ad(
                db, data["p_application_headers"], p_application_header_id, token["role_type"], token["id"]
            )
            await crud.diff_update_p_residents_for_ad(
                db, data["p_residents"], p_application_header_id, token["role_type"], token["id"]
            )
        if main_tab == 1 and sub_tab == 6:
            await crud.diff_update_p_application_headers_for_ad(
                db, data["p_application_headers"], p_application_header_id, token["role_type"], token["id"]
            )
            if data["p_application_headers"]["curr_borrowing_status"] == "1":
                await crud.diff_update_p_borrowings_for_ad(
                    db, data["p_borrowings"], p_application_header_id, token["role_type"], token["id"]
                )
            else:
                await crud.delete_p_borrowings_for_ad(db, p_application_header_id)
        if main_tab == 1 and sub_tab in [7, 8]:
            await crud.diff_update_p_application_headers_for_ad(
                db, data["p_application_headers"], p_application_header_id, token["role_type"], token["id"]
            )

        if main_tab == 1 and sub_tab == 9:
            await crud.diff_p_uploaded_files_for_ad(
                db, data["p_uploaded_files"], p_application_header_id, token["role_type"], token["id"]
            )
            await crud.diff_update_p_borrowings_files_for_ad(
                db, data["p_borrowings"], p_application_header_id, token["role_type"], token["id"]
            )
            await crud.diff_update_p_applicant_persons_for_ad(
                db, data["p_applicant_persons__0"], p_application_header_id, 0, token["role_type"], token["id"]
            )

        if main_tab == 2 and sub_tab in [2, 3]:
            await crud.diff_update_p_applicant_persons_for_ad(
                db, data["p_applicant_persons__1"], p_application_header_id, 1, token["role_type"], token["id"]
            )
        if main_tab == 2 and sub_tab == 9:
            if data.get("p_application_headers") is not None:
                await crud.diff_update_p_application_headers_for_ad(
                    db, data["p_application_headers"], p_application_header_id, token["role_type"], token["id"]
                )

                if data["p_application_headers"]["land_advance_plan"] == "1":
                    await crud.diff_update_p_borrowing_details_for_ad(
                        db, data["p_borrowing_details__2"], p_application_header_id, 2, token["role_type"], token["id"]
                    )
                else:
                    await crud.delete_p_borrowing_details__2_for_ad(db, p_application_header_id)

            if data.get("p_application_banks") is not None:
                await crud.diff_update_p_application_banks_for_ad(
                    db, data["p_application_banks"], p_application_header_id, token["role_type"], token["id"]
                )
            if data.get("p_borrowing_details__1") is not None:
                await crud.diff_update_p_borrowing_details_for_ad(
                    db, data["p_borrowing_details__1"], p_application_header_id, 1, token["role_type"], token["id"]
                )
            if data.get("p_join_guarantors") is not None:
                await crud.diff_update_p_join_guarantors_for_ad(
                    db, data["p_join_guarantors"], p_application_header_id, token["role_type"], token["id"]
                )
            if data.get("p_applicant_persons__1") is not None:
                await crud.diff_update_p_applicant_persons_for_ad(
                    db, data["p_applicant_persons__1"], p_application_header_id, 1, token["role_type"], token["id"]
                )

            await crud.diff_p_uploaded_files_for_ad(
                db, data["p_uploaded_files"], p_application_header_id, token["role_type"], token["id"]
            )

        return JSONResponse(status_code=200, content={"message": "successful"})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.get("/files-view/{p_application_header_id}")
async def common_get_preliminary(
    p_application_header_id: int, category: str, db=Depends(get_db), token=Depends(get_token)
):
    try:
        result = None
        if "G" in category:
            result = await crud.query_p_uploaded_files_for_ad_view(db, p_application_header_id, "/G")
            return JSONResponse(status_code=200, content=result)
        if "J" in category:
            result = await crud.query_p_uploaded_files_for_ad_view(db, p_application_header_id, "/J")
            return JSONResponse(status_code=200, content=result)
        if "S" in category:
            result = await crud.query_p_uploaded_files_for_ad_view(db, p_application_header_id, "/S")
            return JSONResponse(status_code=200, content=result)
        if "I" in category:
            result = await crud.query_p_borrowings_for_ad_view(db, p_application_header_id)
            return JSONResponse(status_code=200, content=result)

        result = await crud.query_p_uploaded_files_for_ad_view(db, p_application_header_id, category)
        return JSONResponse(status_code=200, content=result)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.get("/row_data/{p_application_header_id}")
async def get_raw_data(p_application_header_id: int, token: dict = Depends(get_token)):
    try:

        file = download_from_s3(f"{p_application_header_id}/row_data.xlsx")
        return JSONResponse(status_code=200, content=file)
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


@router.get("/edit_histories/files/{p_application_header_id}")
async def get_update_hitories(
    p_application_header_id: int, update_history_key: str, db=Depends(get_db), token=Depends(get_token)
):
    try:
        histories = await crud.query_files_field_uodate_histories_for_ad(
            db, p_application_header_id, update_history_key
        )
        return JSONResponse(status_code=200, content=histories)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )
