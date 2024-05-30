from loguru import logger
from datetime import datetime
from fastapi import APIRouter
from fastapi import Request
from fastapi import Depends
from fastapi.responses import JSONResponse
import pytz

from core.config import settings
from apis.deps import get_db
from apis.deps import get_token
import crud
import utils
import schemas

from constant import DEFAULT_200_MSG, DEFAULT_500_MSG, ACCESS_LOG_OPERATION, ORG_OTHER_ID, TOKEN_ROLE_TYPE
from templates.user_register_init_message import INIT_MESSAGE

router = APIRouter()


@router.post("/user/verify-email")
async def user_send_verify_email(data: dict, db=Depends(get_db)):
    try:
        is_exist = await crud.check_c_user_with_email(db, email=data["email"])
        if is_exist:
            return JSONResponse(status_code=400, content={"message": "user email is exist."})
        token = utils.gen_token(data, expires_delta=settings.JWT_VERIFY_EMAIL_TOKEN_EXP)
        utils.send_email(
            to=data["email"],
            template="user_send_verify_email",
            link=f"{settings.FRONTEND_BASE_URL}/register?token={token}",
        )
        return JSONResponse(status_code=200, content=DEFAULT_200_MSG)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(status_code=500, content=DEFAULT_500_MSG)


@router.post("/user")
async def user_register(data: dict, request: Request, db=Depends(get_db)):
    try:
        payload = utils.parse_token(data["token"])

        if payload is None:
            return JSONResponse(status_code=407, content={"message": "token is invalid."})
        if payload.get("s_sales_company_org_id"):
            is_exist_s_sales_company = await crud.check_user_register_s_sales_company_org_id(
                db, payload.get("s_sales_company_org_id")
            )
            if is_exist_s_sales_company is None:
                return JSONResponse(status_code=408, content={"message": "s_sales_company_org_id is invalid."})
        is_exist = await crud.check_c_user_with_email(db, email=payload["email"])
        if is_exist:
            return JSONResponse(status_code=400, content={"message": "user email is exist."})
        new_user_id = await crud.insert_new_c_user(
            db,
            email=payload["email"],
            hashed_pwd=utils.hash_password(data["password"]),
            s_sales_company_org_id=payload.get("s_sales_company_org_id") or ORG_OTHER_ID,
        )
        await crud.insert_init_message(db, c_user_id=new_user_id, content=INIT_MESSAGE)
        access_token = utils.gen_token(
            payload=await crud.query_c_user_token_payload(db, c_user_id=new_user_id),
            expires_delta=settings.JWT_ACCESS_TOKEN_EXP,
        )
        await utils.common_insert_c_access_log(
            db,
            request,
            params={
                "account_id": new_user_id,
                "account_type": 1,
                "operation": ACCESS_LOG_OPERATION.REGISTER.value,
            },
        )
        return JSONResponse(status_code=200, content={"access_token": access_token})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(status_code=500, content=DEFAULT_500_MSG)


@router.post("/user/password/verify-email")
async def user_send_reset_password_verify_email(data: schemas.VerifyEmail, db=Depends(get_db)):
    try:
        is_exist = await crud.check_c_user_with_email(db, email=data.email)
        if not is_exist:
            return JSONResponse(status_code=400, content={"message": "user email is not exist."})
        token = utils.gen_token({"email": data.email})
        utils.send_email(
            to=data.email,
            template="user_send_reset_password_verify_email",
            link=f"{settings.FRONTEND_BASE_URL}/reset-password?token={token}",
        )
        return JSONResponse(status_code=200, content={"message": "reset password email send successful."})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.post("/user/password")
async def user_reset_password(data: schemas.ResetPasswordUser, db=Depends(get_db)):
    try:
        payload = utils.parse_token(data.token)
        if payload is None:
            return JSONResponse(status_code=400, content={"message": "token is invalid."})
        await crud.update_c_user_password_with_email(
            db, email=payload["email"], hashed_pwd=utils.hash_password(data.password)
        )
        return JSONResponse(status_code=200, content={"message": "reset password successful."})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.post("/user/token")
async def user_login(data: dict, request: Request, db=Depends(get_db)):
    try:
        is_exist = await crud.query_c_user_with_email(db, email=data["email"])
        if not is_exist:
            return JSONResponse(status_code=400, content={"message": "user email is not exist."})
        if is_exist["status"] == 2:
            return JSONResponse(status_code=423, content={"message": "account is locked."})
        if not utils.verify_password(data["password"], is_exist["hashed_pwd"]):
            if is_exist["failed_first_at"]:
                if (
                    datetime.strptime(
                        datetime.now().astimezone(pytz.timezone("Asia/Tokyo")).strftime("%Y-%m-%d %H:%M:%S"),
                        "%Y-%m-%d %H:%M:%S",
                    )
                    - datetime.strptime(is_exist["failed_first_at"], "%Y-%m-%d %H:%M:%S")
                ).seconds < 300 and is_exist["failed_time"] == 4:
                    await crud.update_c_user_status_locked(db, id=is_exist["id"])
                    return JSONResponse(status_code=423, content={"message": "account is locked."})
                else:
                    await crud.update_c_user_failed_time(db, id=is_exist["id"], failed_time=is_exist["failed_time"] + 1)
            else:
                await crud.update_c_user_failed_first_at(db, id=is_exist["id"])
            return JSONResponse(status_code=400, content={"message": "email or password is invalid."})
        payload = await crud.query_c_user_token_payload(db, c_user_id=is_exist["id"])
        access_token = utils.gen_token(payload=payload, expires_delta=settings.JWT_ACCESS_TOKEN_EXP)

        if is_exist["failed_first_at"] or is_exist["failed_first_at"]:
            await crud.reset_c_user_failed_infos(db, is_exist["id"])
        await utils.common_insert_c_access_log(
            db,
            request,
            params={
                "account_id": payload.get("id"),
                "account_type": payload.get("role_type"),
                "operation": ACCESS_LOG_OPERATION.LOGIN.value,
            },
        )
        return JSONResponse(status_code=200, content={"access_token": access_token})

    except Exception as err:
        logger.exception(err)
        return JSONResponse(status_code=500, content=DEFAULT_500_MSG)


@router.delete("/user/token")
async def user_logout(request: Request, db=Depends(get_db), token=Depends(get_token)):
    try:
        await utils.common_insert_c_access_log(
            db,
            request,
            params={
                "account_id": token.get("id"),
                "account_type": token.get("role_type"),
                "operation": ACCESS_LOG_OPERATION.LOGOUT.value,
            },
        )
        return JSONResponse(status_code=200, content=DEFAULT_200_MSG)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(status_code=500, content=DEFAULT_500_MSG)


@router.put("/user/password")
async def user_up_password(data: dict, request: Request, db=Depends(get_db), token=Depends(get_token)):
    try:
        user_id = token.get("id")
        if not utils.verify_password(data["password"], await crud.query_c_user_hashed_pwd(db, user_id)):
            return JSONResponse(status_code=412, content={"massage": "curr password is wrong."})
        await crud.update_c_user_password_with_id(db, id=user_id, hashed_pwd=utils.hash_password(data["new_password"]))
        return JSONResponse(status_code=200, content=DEFAULT_200_MSG)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(status_code=500, content=DEFAULT_500_MSG)


@router.post("/user/email/verify-email")
async def user_send_change_email_verify_email(data: dict, db=Depends(get_db), token=Depends(get_token)):
    try:
        user_id = token.get("id")
        curr_db_user = await crud.query_c_user_basic_info(db, id=user_id)
        if data.get("email") != curr_db_user["email"]:
            return JSONResponse(status_code=412, content={"massage": "curr email is wrong."})
        is_exist = await crud.query_c_user_with_email(db, email=data.get("new_email"))
        if is_exist:
            return JSONResponse(status_code=400, content={"massage": "new email is exist."})
        token = utils.gen_token({"id": user_id, "new_email": data.get("new_email")})
        utils.send_email(
            to=data.get("new_email"),
            template="user_send_change_email_verify_email",
            link=f"{settings.FRONTEND_BASE_URL}/change-email?token={token}",
        )
        return JSONResponse(status_code=200, content=DEFAULT_200_MSG)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(status_code=500, content=DEFAULT_500_MSG)


@router.put("/user/email")
async def user_change_email(data: dict, request: Request, db=Depends(get_db)):
    try:
        payload = utils.parse_token(data["token"])
        if payload is None:
            return JSONResponse(status_code=401, content={"message": "token is invalid."})
        curr_db_user = await crud.query_c_user_basic_info(db, id=payload["id"])
        if payload["new_email"] == curr_db_user["email"]:
            return JSONResponse(status_code=401, content={"message": "token is invalid."})
        await crud.update_c_user_email(db, id=payload["id"], new_email=payload["new_email"])
        access_token = utils.gen_token(
            payload=await crud.query_c_user_token_payload(db, c_user_id=payload["id"]),
            expires_delta=settings.JWT_ACCESS_TOKEN_EXP,
        )

        return JSONResponse(status_code=200, content={"access_token": access_token})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(status_code=500, content=DEFAULT_500_MSG)


@router.delete("/user")
async def user_withdrawal(request: Request, db=Depends(get_db), token=Depends(get_token)):
    try:
        await crud.delete_c_user(db, id=token.get("id"))
        await utils.common_insert_c_access_log(
            db,
            request,
            params={
                "account_id": token.get("id"),
                "account_type": token.get("role_type"),
                "operation": ACCESS_LOG_OPERATION.UNSUBCRIBED.value,
            },
        )

        return JSONResponse(status_code=200, content=DEFAULT_200_MSG)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(status_code=500, content=DEFAULT_500_MSG)


@router.post("/user/draft")
async def user_save_draft(data: dict, db=Depends(get_db), token=Depends(get_token)):
    try:
        await crud.upsert_p_draft_data(db, token.get("id"), data)
        return JSONResponse(status_code=200, content=DEFAULT_200_MSG)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(status_code=500, content=DEFAULT_500_MSG)


@router.get("/user/draft")
async def user_get_draft(db=Depends(get_db), token=Depends(get_token)):
    try:
        data = await crud.query_p_draft_data(db, token.get("id"))
        return JSONResponse(status_code=200, content=data)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(status_code=500, content=DEFAULT_500_MSG)


@router.get("/user/s_sales_company_org_id")
async def user_get_draft(db=Depends(get_db), token=Depends(get_token)):
    try:
        data = await crud.query_user_s_sales_company_org_id(db, token.get("id"))
        return JSONResponse(status_code=200, content=data)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(status_code=500, content=DEFAULT_500_MSG)
