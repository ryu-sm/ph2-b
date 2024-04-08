from loguru import logger
from datetime import datetime
from fastapi import APIRouter, Request
from fastapi import Depends
from fastapi.responses import JSONResponse

from constant import DEFAULT_200_MSG, DEFAULT_500_MSG
from core.config import settings
from core.custom import LoggingContextRoute
from apis.deps import get_db
from apis.deps import get_token
import crud
import utils
import schemas
from utils.data_check import manager_data_check


router = APIRouter(route_class=LoggingContextRoute)


@router.post("/manager/password/verify-email")
async def manager_send_reset_password_verify_email(data: schemas.VerifyEmail, db=Depends(get_db)):
    try:
        is_exist = await crud.check_s_manager_with_email(db, email=data.email)
        if not is_exist:
            return JSONResponse(status_code=400, content={"message": "user email is not exist."})
        token = utils.gen_token({"email": data.email}, expires_delta=settings.JWT_VERIFY_EMAIL_TOKEN_EXP)
        utils.send_email(
            to=data.email,
            template="manager_send_reset_password_verify_email",
            link=f"{settings.FRONTEND_BASE_URL}/manager/reset-password?token={token}",
        )
        return JSONResponse(status_code=200, content={"message": "reset password email send successful."})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.post("/manager/password")
async def manager_reset_password(data: schemas.ResetPasswordManager, db=Depends(get_db)):
    try:
        payload = utils.parse_token(data.token)
        if payload is None:
            return JSONResponse(status_code=400, content={"message": "token is invalid."})
        await crud.update_s_manager_password_with_email(
            db, email=payload["email"], hashed_pwd=utils.hash_password(data.password)
        )
        return JSONResponse(status_code=200, content={"message": "reset password successful."})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.put("/manager/password")
async def manager_up_password(data: dict, request: Request, db=Depends(get_db), token=Depends(get_token)):
    try:
        if not utils.verify_password(data["password"], await crud.query_s_manager_hashed_pwd(db, token["id"])):
            return JSONResponse(status_code=412, content={"massage": "curr password is wrong."})
        await crud.update_s_manager_password_with_id(
            db, id=token["id"], hashed_pwd=utils.hash_password(data["new_password"])
        )
        await utils.common_insert_c_access_log(
            db, request, params={"body": data}, status_code=200, response_body=DEFAULT_200_MSG
        )
        return JSONResponse(status_code=200, content=DEFAULT_200_MSG)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(status_code=500, content=DEFAULT_500_MSG)


@router.post("/manager/token")
async def manager_login(data: dict, request: Request, db=Depends(get_db)):
    try:
        is_exist = await crud.check_s_manager_with_email(db, email=data["email"])
        if not is_exist:
            return JSONResponse(status_code=400, content={"message": "user email is not exist."})
        if is_exist["status"] == 2:
            return JSONResponse(status_code=423, content={"message": "account is locked."})
        if not utils.verify_password(data["password"], is_exist["hashed_pwd"]):
            if is_exist["failed_first_at"]:
                if (datetime.now() - is_exist["failed_first_at"]).seconds < 300 and is_exist["failed_time"] == 4:
                    await crud.update_s_manager_status_locked(db, id=is_exist["id"])
                    return JSONResponse(status_code=423, content={"message": "account is locked."})
                else:
                    await crud.update_s_manager_failed_time(
                        db, id=is_exist["id"], failed_time=is_exist["failed_time"] + 1
                    )
            else:
                await crud.update_s_manager_failed_time(db, id=is_exist["id"])
            return JSONResponse(status_code=400, content={"message": "email or password is invalid."})
        access_token = utils.gen_token(
            payload=await crud.query_s_manager_token_payload(db, id=is_exist["id"]),
            expires_delta=settings.JWT_ACCESS_TOKEN_EXP,
        )
        await utils.common_insert_c_access_log(
            db, request, params={"body": data}, status_code=200, response_body={"access_token": "*******"}
        )
        return JSONResponse(status_code=200, content={"access_token": access_token})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(status_code=500, content=DEFAULT_500_MSG)


@router.delete("/manager/token")
async def manager_logout(request: Request, db=Depends(get_db), token=Depends(get_token)):
    try:
        await utils.common_insert_c_access_log(db, request, status_code=200, response_body=DEFAULT_200_MSG)
        return JSONResponse(status_code=200, content=DEFAULT_200_MSG)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(status_code=500, content=DEFAULT_500_MSG)


@router.get("/manager/preliminaries")
async def manager_get_access_applications(status: int, db=Depends(get_db), token=Depends(get_token)):

    try:
        p_application_headers_basic_list = await crud.query_manager_access_p_application_headers(
            db, status, token["id"]
        )
        return JSONResponse(status_code=200, content=p_application_headers_basic_list)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.put("/manager/un-pair-loan")
async def un_pair_laon(data: dict, db=Depends(get_db), token=Depends(get_token)):
    try:
        await crud.delete_pair_laon(db, data.values(), token["role_type"], token["id"])
        return JSONResponse(status_code=200, content={"message": "successful"})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.put("/manager/set-pair-loan")
async def set_pair_laon(data: dict, db=Depends(get_db), token=Depends(get_token)):
    try:
        await crud.set_pair_loan(db, data, token["role_type"], token["id"])
        return JSONResponse(status_code=200, content={"message": "successful"})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.get("/manager/memos")
async def get_memos(id: int, db=Depends(get_db), token=Depends(get_token)):
    try:
        memos = await crud.query_memos(db, id)
        return JSONResponse(status_code=200, content=memos)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.post("/manager/memo")
async def new_memo(data: dict, db=Depends(get_db), token=Depends(get_token)):
    try:
        await crud.insert_memo(db, data["p_application_header_id"], token["id"], data["content"])
        return JSONResponse(status_code=200, content={"message": "successful"})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.put("/manager/memo")
async def new_memo(data: dict, db=Depends(get_db), token=Depends(get_token)):
    try:
        await crud.update_memo(db, data["id"], data["content"])
        return JSONResponse(status_code=200, content={"message": "successful"})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.put("/manager/provisional_after_result")
async def update_provisional_after_result(data: dict, db=Depends(get_db), token=Depends(get_token)):
    try:
        await crud.update_p_application_banks_provisional_after_result(
            db,
            data["p_application_header_id"],
            data["s_bank_id"],
            data["provisional_after_result"],
            token["role_type"],
            token["id"],
        )
        return JSONResponse(status_code=200, content={"message": "successful"})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.put("/manager/provisional_result")
async def update_provisional_result(data: dict, db=Depends(get_db), token=Depends(get_token)):
    try:
        await crud.update_p_application_banks_pprovisional_result(
            db,
            data["p_application_header_id"],
            data["s_bank_id"],
            data["provisional_result"],
            data["R"],
            token["role_type"],
            token["id"],
        )
        return JSONResponse(status_code=200, content={"message": "successful"})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.patch("/manager/provisional_result")
async def delete_provisional_result(data: dict, db=Depends(get_db), token=Depends(get_token)):
    try:
        await crud.delete_p_application_banks_pprovisional_result(
            db,
            data["p_application_header_id"],
            data["s_bank_id"],
            data["p_upload_file_id"],
        )
        return JSONResponse(status_code=200, content={"message": "successful"})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.put("/manager/approver_confirmation")
async def update_approver_confirmation(data: dict, db=Depends(get_db), token=Depends(get_token)):
    try:
        await crud.update_p_application_headers_approver_confirmation(
            db, data["p_application_header_id"], data["approver_confirmation"]
        )
        return JSONResponse(status_code=200, content={"message": "successful"})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.put("/manager/pre_examination_status")
async def update_pre_examination_status(data: dict, db=Depends(get_db), token=Depends(get_token)):
    try:
        if data["pre_examination_status"] == 3:
            errors = manager_data_check(data["preliminary"])

            if errors:
                return JSONResponse(status_code=400, content=errors)
        await crud.update_p_application_headers_pre_examination_status(
            db, data["p_application_header_id"], data["pre_examination_status"]
        )
        return JSONResponse(status_code=200, content={"message": "successful"})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )
