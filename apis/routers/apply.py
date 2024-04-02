import json
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
from core.config import settings


router = APIRouter(route_class=LoggingContextRoute)


@router.get("/application/{c_user_id}")
async def get_application(c_user_id: str, db=Depends(get_db), token: dict = Depends(get_token)):
    try:
        temp = {}
        p_application_header_id = await crud.query_p_application_header_id_with_c_user_id(db, c_user_id)

        p_application_headers = await crud.query_p_application_headers_for_ap(db, p_application_header_id)
        temp["p_application_headers"] = p_application_headers

        p_borrowing_details__1 = await crud.query_p_borrowing_details_for_ap(db, p_application_header_id, 1)
        temp["p_borrowing_details__1"] = p_borrowing_details__1

        if p_application_headers["land_advance_plan"] == "1":
            temp["p_borrowing_details__2"] = await crud.query_p_borrowing_details_for_ap(db, p_application_header_id, 2)

        temp["p_application_banks"] = await crud.query_p_application_banks_for_ap(db, p_application_header_id)

        temp["p_applicant_persons__0"] = await crud.query_p_applicant_persons_for_ap(db, p_application_header_id, 0)

        if p_application_headers["loan_type"] in ["3", "4"]:
            temp["p_applicant_persons__1"] = await crud.query_p_applicant_persons_for_ap(db, p_application_header_id, 1)

        if p_application_headers["join_guarantor_umu"] == "1":
            temp["p_join_guarantors"] = await crud.query_p_join_guarantors_for_ap(db, p_application_header_id)

        p_residents = await crud.query_p_residents_for_ap(db, p_application_header_id)
        if p_residents:
            temp["p_residents"] = p_residents

        if p_application_headers["curr_borrowing_status"] == "1":
            temp["p_borrowings"] = await crud.query_p_borrowings_for_ap(db, p_application_header_id)

        return JSONResponse(status_code=200, content=jsonable_encoder(temp))
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.post("/application")
async def post_application(data_: dict, db=Depends(get_db), token: dict = Depends(get_token)):
    try:
        data = utils.blank_to_none(data_)
        p_application_header_id = None
        # user
        if token["role_type"] == 1:
            p_application_header_id = await crud.insert_p_application_headers(
                db,
                data["p_application_headers"],
                role_type=token["role_type"],
                role_id=token["id"],
                c_user_id=token["id"],
            )
        # sales_person
        if token["role_type"] == 2:
            p_application_header_id = await crud.insert_p_application_headers(
                db,
                data["p_application_headers"],
                role_type=token["role_type"],
                role_id=token["id"],
                s_sales_person_id=token["id"],
            )
        await crud.insert_p_applicant_persons(
            db, data["p_applicant_persons__0"], p_application_header_id, 0, token["role_type"], token["id"]
        )
        if data["p_application_headers"]["loan_type"] in ["3", "4"]:
            await crud.insert_p_applicant_persons(
                db, data["p_applicant_persons__1"], p_application_header_id, 1, token["role_type"], token["id"]
            )
        await crud.insert_p_borrowing_details(
            db, data["p_borrowing_details__1"], p_application_header_id, 1, token["role_type"], token["id"]
        )
        if data["p_application_headers"]["land_advance_plan"] == "1":
            await crud.insert_p_borrowing_details(
                db, data["p_borrowing_details__2"], p_application_header_id, 2, token["role_type"], token["id"]
            )
        await crud.instert_p_application_banks(db, data["p_application_banks"], p_application_header_id)
        if data["p_application_headers"]["join_guarantor_umu"] == "1":
            await crud.insert_p_join_guarantors(
                db, data["p_join_guarantors"], p_application_header_id, token["role_type"], token["id"]
            )
        if data["p_application_headers"]["curr_borrowing_status"] == "1":
            await crud.insert_p_borrowings(
                db, data["p_borrowings"], p_application_header_id, token["role_type"], token["id"]
            )
        if data["p_residents"]:
            await crud.insert_p_residents(
                db, data["p_residents"], p_application_header_id, token["role_type"], token["id"]
            )
        if token["role_type"] == 1:
            await crud.update_c_user_agent_sended(db, token["id"])
            await crud.delete_p_draft_data(db, token["id"])

        apply_no = await crud.query_p_application_header_apply_no(db, p_application_header_id)
        await crud.update_messages_for_user(db, token["id"], p_application_header_id)
        utils.send_email(
            to="info-test@milibank.co.jp",
            template="manager_new_apply_email",
            link=f"{settings.FRONTEND_BASE_URL}/manager/edit-preliminary?id={p_application_header_id}",
        )
        await utils.gen_row_data(p_application_header_id, data_)
        return JSONResponse(status_code=200, content={"apply_no": apply_no})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.put("/application/{c_user_id}")
async def put_application(c_user_id: int, data: dict, db=Depends(get_db), token: dict = Depends(get_token)):
    try:
        step_id = data["step_id"]
        p_application_header_id = await crud.query_p_application_header_id_with_c_user_id(db, c_user_id)

        if step_id == 1:
            await crud.diff_update_p_application_headers_for_ap(
                db, data["p_application_headers"], p_application_header_id, token["role_type"], token["id"]
            )
            await crud.diff_update_p_borrowing_details_for_ap(
                db, data["p_borrowing_details__1"], p_application_header_id, 1, token["role_type"], token["id"]
            )
            await crud.diff_update_p_application_banks_for_ap(
                db, data["p_application_banks"], p_application_header_id, token["role_type"], token["id"]
            )
            if data["p_application_headers"]["land_advance_plan"] == "1":
                await crud.diff_update_p_borrowing_details_for_ap(
                    db, data["p_borrowing_details__2"], p_application_header_id, 2, token["role_type"], token["id"]
                )
        if step_id in [2, 3, 10]:
            await crud.diff_update_p_applicant_persons_for_ap(
                db, data["p_applicant_persons__0"], p_application_header_id, 0, token["role_type"], token["id"]
            )
        if step_id in [4, 5]:
            await crud.diff_update_p_applicant_persons_for_ap(
                db, data["p_applicant_persons__1"], p_application_header_id, 1, token["role_type"], token["id"]
            )
        if step_id == 6:
            await crud.diff_update_p_application_headers_for_ap(
                db, data["p_application_headers"], p_application_header_id, token["role_type"], token["id"]
            )
            await crud.diff_update_p_join_guarantors_for_ap(
                db, data["p_join_guarantors"], p_application_header_id, token["role_type"], token["id"]
            )
        if step_id == 7:
            await crud.diff_update_p_application_headers_for_ap(
                db, data["p_application_headers"], p_application_header_id, token["role_type"], token["id"]
            )
            await crud.diff_update_p_residents_for_ap(
                db, data["p_residents"], p_application_header_id, token["role_type"], token["id"]
            )
        if step_id == 8:
            await crud.diff_update_p_application_headers_for_ap(
                db, data["p_application_headers"], p_application_header_id, token["role_type"], token["id"]
            )
            await crud.diff_update_p_borrowings_for_ap(
                db, data["p_borrowings"], p_application_header_id, token["role_type"], token["id"]
            )
        if step_id == 9:
            await crud.diff_update_p_application_headers_for_ap(
                db, data["p_application_headers"], p_application_header_id, token["role_type"], token["id"]
            )
        if step_id == 11:
            await crud.diff_update_p_application_headers_for_ap(
                db, data["p_application_headers"], p_application_header_id, token["role_type"], token["id"]
            )
            await crud.diff_update_p_applicant_persons_for_ap(
                db, data["p_applicant_persons__1"], p_application_header_id, 1, token["role_type"], token["id"]
            )
        if step_id == 12:
            await crud.diff_update_p_application_headers_for_ap(
                db, data["p_application_headers"], p_application_header_id, token["role_type"], token["id"]
            )

        return JSONResponse(status_code=200, content={"message": "successful"})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.get("/p_application_headers/files")
async def get_p_application_headers_files(c_user_id: str, db=Depends(get_db)):
    try:
        p_application_header_id = await crud.query_p_application_header_id_with_c_user_id(db, c_user_id)

        files = await crud.query_p_application_headers_files_for_ap(db, p_application_header_id)

        return JSONResponse(status_code=200, content=files)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.get("/p_applicant_persons/files")
async def get_p_applicant_persons_files(c_user_id: str, type: int, db=Depends(get_db)):
    try:
        p_application_header_id = await crud.query_p_application_header_id_with_c_user_id(db, c_user_id)

        files = await crud.query_p_applicant_persons_files_for_ap(db, p_application_header_id, type)

        return JSONResponse(status_code=200, content=files)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.get("/p_borrowings/files")
async def get_p_borrowings_files(c_user_id: str, db=Depends(get_db)):
    try:
        p_application_header_id = await crud.query_p_application_header_id_with_c_user_id(db, c_user_id)

        files = await crud.query_p_borrowings_files_for_ap(db, p_application_header_id)

        return JSONResponse(status_code=200, content=files)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )
