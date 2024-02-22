from loguru import logger
from datetime import datetime
from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import JSONResponse

from core.config import settings
from core.custom import LoggingContextRoute
from apis.deps import get_db
from apis.deps import get_user_id
import crud
import utils
import schemas


from templates.user_register_init_message import INIT_MESSAGE

router = APIRouter(route_class=LoggingContextRoute)


@router.post("/user/verify-email")
async def user_send_verify_email(data: schemas.VerifyEmail, db=Depends(get_db)):
    try:
        is_exist = await crud.check_c_user_with_email(db, email=data.email)
        if is_exist:
            return JSONResponse(status_code=400, content={"message": "user email is exist."})
        token = utils.gen_token(
            {"email": data.email, "s_sales_company_org_id": data.s_sales_company_org_id},
            expires_delta=settings.JWT_VERIFY_EMAIL_TOKEN_EXP,
        )
        utils.send_email(
            to=data.email,
            template="user_send_verify_email",
            link=f"{settings.FRONTEND_BASE_URL}/register?token={token}",
        )
        return JSONResponse(status_code=200, content={"message": "verify email send successful."})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.post("/user")
async def user_register(data: schemas.NewUser, db=Depends(get_db)):
    try:
        payload = utils.parse_token(data.token)
        if payload is None:
            return JSONResponse(status_code=401, content={"message": "token is invalid."})
        is_exist = await crud.check_c_user_with_email(db, email=payload["email"])
        if is_exist:
            return JSONResponse(status_code=400, content={"message": "user email is exist."})
        new_user_id = await crud.insert_new_c_user(
            db,
            email=payload["email"],
            hashed_pwd=utils.hash_password(data.password),
            s_sales_company_org_id=payload["s_sales_company_org_id"],
        )
        await crud.insert_c_message(db, c_user_id=new_user_id, sender_type=3, content=INIT_MESSAGE)
        access_token = utils.gen_token(
            payload=await crud.query_c_user_token_payload(db, c_user_id=new_user_id),
            expires_delta=settings.JWT_ACCESS_TOKEN_EXP,
        )
        return JSONResponse(status_code=200, content={"access_token": access_token})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


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
            return JSONResponse(status_code=401, content={"message": "token is invalid."})
        is_exist = await crud.check_c_user_with_email(db, email=payload["email"])
        if not is_exist:
            return JSONResponse(status_code=400, content={"message": "user email is not exist."})
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
async def user_login(data: schemas.LoginUser, db=Depends(get_db)):
    try:
        is_exist = await crud.query_c_user_with_email(db, email=data.email)
        if not is_exist:
            return JSONResponse(status_code=400, content={"message": "user email is not exist."})
        if is_exist["status"] == 2:
            return JSONResponse(status_code=423, content={"message": "account is locked."})
        if not utils.verify_password(data.password, is_exist["hashed_pwd"]):
            if is_exist["failed_first_at"]:
                if (datetime.now() - is_exist["failed_first_at"]).seconds < 300 and is_exist["failed_time"] == 4:
                    await crud.update_c_user_status_locked(db, id=is_exist["id"])
                    return JSONResponse(status_code=423, content={"message": "account is locked."})
                else:
                    await crud.update_c_user_failed_time(db, id=is_exist["id"], failed_time=is_exist["failed_time"] + 1)
            else:
                await crud.update_c_user_failed_first_at(db, id=is_exist["id"])
            return JSONResponse(status_code=400, content={"message": "email or password is invalid."})
        if is_exist["first_login"] == 0:
            await crud.update_c_user_first_login(db, id=is_exist["id"])
        access_token = utils.gen_token(
            payload=await crud.query_c_user_token_payload(db, c_user_id=is_exist["id"]),
            expires_delta=settings.JWT_ACCESS_TOKEN_EXP,
        )
        if is_exist["failed_first_at"] or is_exist["failed_first_at"]:
            await crud.reset_c_user_failed_infos(db, is_exist["id"])
        return JSONResponse(status_code=200, content={"access_token": access_token})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.delete("/user/token")
async def user_logout(user_id=Depends(get_user_id)):
    try:
        return JSONResponse(status_code=200, content={"message": "logout successful."})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.put("/user/password")
async def user_up_password(data: schemas.UpPasswordUser, db=Depends(get_db), user_id=Depends(get_user_id)):
    try:
        if not utils.verify_password(data.password, await crud.query_c_user_hashed_pwd(db, user_id)):
            return JSONResponse(status_code=412, content={"massage": "curr password is wrong."})
        await crud.update_c_user_password_with_id(db, id=user_id, hashed_pwd=utils.hash_password(data.new_password))
        return JSONResponse(status_code=200, content={"message": "update password successful."})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.post("/user/email/verify-email")
async def user_send_change_email_verify_email(
    data: schemas.UpEmailUser, db=Depends(get_db), user_id=Depends(get_user_id)
):
    try:
        curr_db_user = await crud.query_c_user_basic_info(db, id=user_id)
        if data.email != curr_db_user["email"]:
            return JSONResponse(status_code=412, content={"massage": "curr email is wrong."})
        is_exist = await crud.query_c_user_with_email(db, email=data.new_email)
        if is_exist:
            return JSONResponse(status_code=400, content={"massage": "new email is exist."})
        token = utils.gen_token({"id": user_id, "new_email": data.new_email})
        utils.send_email(
            to=data.new_email,
            template="user_send_change_email_verify_email",
            link=f"{settings.FRONTEND_BASE_URL}/change-email?token={token}",
        )
        return JSONResponse(status_code=200, content={"message": "update password successful."})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.put("/user/email")
async def user_change_email(data: schemas.UpEmailUserConfirm, db=Depends(get_db)):
    try:
        payload = utils.parse_token(data.token)
        if payload is None:
            return JSONResponse(status_code=401, content={"message": "token is invalid."})
        curr_db_user = await crud.query_c_user_basic_info(db, id=payload["id"])
        if payload["new_email"] == curr_db_user["email"]:
            return JSONResponse(status_code=401, content={"message": "token is invalid."})
        await crud.update_c_user_email(db, id=payload["id"], new_email=payload["new_email"])
        return JSONResponse(status_code=200, content={"message": "update password successful."})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.delete("/user")
async def user_withdrawal(db=Depends(get_db), user_id=Depends(get_user_id)):
    try:
        await crud.delete_c_user(db, id=user_id)
        return JSONResponse(status_code=200, content={"message": "withdrawal successful."})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.post("/user/draft")
async def user_save_draft(data: dict, db=Depends(get_db), user_id=Depends(get_user_id)):
    try:
        await crud.upsert_p_draft_data(db, user_id, data)
        return JSONResponse(status_code=200, content={"message": "save successful."})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.get("/user/draft")
async def user_get_draft(db=Depends(get_db), user_id=Depends(get_user_id)):
    try:
        data = await crud.query_p_draft_data(db, user_id)
        return JSONResponse(status_code=200, content=data)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.get("/uuid")
async def get_uuid(db=Depends(get_db)):
    return await db.uuid_short()
