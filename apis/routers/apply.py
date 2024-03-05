from loguru import logger
from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


from core.custom import LoggingContextRoute
from apis.deps import get_db
from apis.deps import get_token
import crud
import utils


router = APIRouter(route_class=LoggingContextRoute)


@router.post("/application")
async def user_orgs(data_: dict, db=Depends(get_db), token: dict = Depends(get_token)):
    try:
        data = utils.blank_to_none(data_)

        p_application_header_id = None
        if token["role_type"] == 1:
            p_application_header_id = await crud.insert_p_application_headers(
                db, data["p_application_headers"], origin_data=data, c_user_id=token["id"]
            )
        if token["role_type"] == 2:
            p_application_header_id = await crud.insert_p_application_headers(
                db, data["p_application_headers"], s_sales_person_id=token["id"]
            )

        await crud.insert_p_applicant_persons(db, data["p_applicant_persons__0"], p_application_header_id, 0)
        if data["hasIncomeTotalizer"]:
            await crud.insert_p_applicant_persons(db, data["p_applicant_persons__1"], p_application_header_id, 1)

        await crud.insert_p_borrowing_details(db, data["p_borrowing_details__1"], p_application_header_id, time_type=1)
        if data["p_application_headers"]["land_advance_plan"] == "1":
            await crud.insert_p_borrowing_details(
                db, data["p_borrowing_details__2"], p_application_header_id, time_type=2
            )
        await crud.instert_p_application_banks(db, data["p_application_banks"], p_application_header_id)

        if data["hasJoinGuarantor"]:
            await crud.insert_p_join_guarantors(db, data["p_join_guarantors"], p_application_header_id)

        if data["p_application_headers"]["curr_borrowing_status"] == "1":
            await crud.insert_p_borrowings(
                db, data["p_borrowings"], p_application_header_id, token["role_type"], token["id"]
            )

        await crud.insert_p_uploaded_files_main(
            db, data["p_uploaded_files"], p_application_header_id, token["role_type"], token["id"]
        )

        if token["role_type"] == 1:
            await crud.update_c_user_agent_sended(db, token["id"])
            await crud.delete_p_draft_data(db, token["id"])

        apply_no = await crud.query_p_application_header_apply_no(db, p_application_header_id)

        return JSONResponse(status_code=200, content={"apply_no": apply_no})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.put("/application")
async def user_orgs(apply_no: str, data: dict, db=Depends(get_db), token: dict = Depends(get_token)):
    try:

        p_application_header_id = await crud.query_p_application_header_id(db, apply_no)
        if data.get("p_application_headers") is not None:
            await crud.diff_update_p_application_headers_for_ap(
                db, data["p_application_headers"], p_application_header_id, token["role_type"], token["id"]
            )
        if data.get("p_applicant_persons__0") is not None:
            await crud.diff_update_p_applicant_persons_for_ap(
                db, data["p_applicant_persons__0"], p_application_header_id, 0, token["role_type"], token["id"]
            )
        if data.get("p_applicant_persons__1") is not None:
            if data["p_application_headers"]["loan_type"] in ["3", "4"]:
                await crud.diff_update_p_applicant_persons_for_ap(
                    db, data["p_applicant_persons__1"], p_application_header_id, 1, token["role_type"], token["id"]
                )
            else:
                await crud.delete_p_applicant_persons__1(db, p_application_header_id)
        if data.get("p_borrowing_details__1") is not None:
            await crud.diff_update_p_borrowing_details_for_ap(
                db, data["p_borrowing_details__1"], p_application_header_id, 1, token["role_type"], token["id"]
            )
        if data.get("p_borrowing_details__2") is not None:
            if data["p_application_headers"]["land_advance_plan"] == "1":
                await crud.diff_update_p_borrowing_details_for_ap(
                    db, data["p_borrowing_details__2"], p_application_header_id, 2, token["role_type"], token["id"]
                )
            else:
                await crud.delete_p_borrowing_details__1(db, p_application_header_id)
        if data.get("p_application_banks") is not None:
            await crud.diff_update_p_application_banks_for_ap(
                db, data["p_application_banks"], p_application_header_id, token["role_type"], token["id"]
            )
        if data.get("p_join_guarantors") is not None:
            if data["p_application_headers"]["join_guarantor_umu"] == "1":
                await crud.diff_update_p_join_guarantors_for_ap(
                    db, data["p_join_guarantors"], p_application_header_id, token["role_type"], token["id"]
                )
            else:
                await crud.delete_p_join_guarantors(db, p_application_header_id)
        if data.get("p_borrowings") is not None:
            if data["p_application_headers"]["curr_borrowing_status"] == "1":
                await crud.diff_update_p_borrowings_for_ap(
                    db, data["p_borrowings"], p_application_header_id, token["role_type"], token["id"]
                )
            else:
                await crud.delete_p_borrowings_for_ap(db, p_application_header_id)
        if data.get("p_uploaded_files") is not None:
            await crud.diff_p_uploaded_files_for_ap(
                db, data["p_uploaded_files"], p_application_header_id, token["role_type"], token["id"]
            )
        return JSONResponse(status_code=200, content={"apply_no": apply_no})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.get("/application")
async def get_application(apply_no: str, db=Depends(get_db)):
    try:
        temp = {}
        p_application_header_id = await crud.query_p_application_header_id(db, apply_no)

        p_application_headers = await crud.query_p_application_headers_for_ap(db, p_application_header_id)
        temp["p_application_headers"] = p_application_headers

        p_borrowing_details__1 = await crud.query_p_borrowing_details_for_ap(db, p_application_header_id, 1)
        temp["p_borrowing_details__1"] = p_borrowing_details__1

        p_borrowing_details__2 = await crud.query_p_borrowing_details_for_ap(db, p_application_header_id, 2)
        if p_borrowing_details__2:
            temp["p_borrowing_details__2"] = p_borrowing_details__2

        p_application_banks = await crud.query_p_application_banks_for_ap(db, p_application_header_id)
        temp["p_application_banks"] = p_application_banks

        p_applicant_persons__0 = await crud.query_p_applicant_persons_for_ap(db, p_application_header_id, 0)
        temp["p_applicant_persons__0"] = p_applicant_persons__0

        p_applicant_persons__1 = await crud.query_p_applicant_persons_for_ap(db, p_application_header_id, 1)
        if p_applicant_persons__1:
            temp["p_applicant_persons__1"] = p_applicant_persons__1

        p_join_guarantors = await crud.query_p_join_guarantors_for_ap(db, p_application_header_id)
        if p_join_guarantors:
            temp["p_join_guarantors"] = p_join_guarantors

        p_residents = await crud.query_p_residents_for_ap(db, p_application_header_id)
        if p_residents:
            temp["p_residents"] = p_residents

        p_borrowings = await crud.query_p_borrowings_for_ap(db, p_application_header_id)
        if p_borrowings:
            temp["p_borrowings"] = p_borrowings

        return JSONResponse(status_code=200, content=jsonable_encoder(temp))
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.get("/application/img")
async def get_application(apply_no: str, db=Depends(get_db)):
    try:
        p_application_header_id = await crud.query_p_application_header_id(db, apply_no)

        p_uploaded_files = await crud.query_p_uploaded_files_main(db, p_application_header_id)

        return JSONResponse(status_code=200, content=p_uploaded_files)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.get("/p_borrowings")
async def get_application(apply_no: str, db=Depends(get_db)):
    try:
        p_application_header_id = await crud.query_p_application_header_id(db, apply_no)

        p_borrowings = await crud.query_p_borrowings_for_ap(db, p_application_header_id)

        return JSONResponse(status_code=200, content=p_borrowings)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )
