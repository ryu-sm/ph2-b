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


from templates.user_register_init_message import INIT_MESSAGE

router = APIRouter(route_class=LoggingContextRoute)


@router.post("/sales-person/password/verify-email")
async def sales_person_send_reset_password_verify_email(data: schemas.VerifyEmail, db=Depends(get_db)):
    try:
        is_exist = await crud.check_s_sales_person_with_email(db, email=data.email)
        if not is_exist:
            return JSONResponse(status_code=400, content={"message": "user email is not exist."})
        token = utils.gen_token({"email": data.email}, expires_delta=settings.JWT_VERIFY_EMAIL_TOKEN_EXP)
        utils.send_email(
            to=data.email,
            template="sales_person_send_reset_password_verify_email",
            link=f"{settings.FRONTEND_BASE_URL}/sales-person/reset-password?token={token}",
        )
        return JSONResponse(status_code=200, content={"message": "reset password email send successful."})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.post("/sales-person/password")
async def sales_person_reset_password(data: schemas.ResetPasswordManager, db=Depends(get_db)):
    try:
        payload = utils.parse_token(data.token)
        if payload is None:
            return JSONResponse(status_code=400, content={"message": "token is invalid."})
        await crud.update_s_sales_person_password_with_email(
            db, email=payload["email"], hashed_pwd=utils.hash_password(data.password)
        )
        return JSONResponse(status_code=200, content={"message": "reset password successful."})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.put("/sales-person/password")
async def sales_person_up_password(data: dict, request: Request, db=Depends(get_db), token=Depends(get_token)):
    try:
        if not utils.verify_password(data["password"], await crud.query_s_sales_person_hashed_pwd(db, token["id"])):
            return JSONResponse(status_code=412, content={"massage": "curr password is wrong."})
        await crud.update_s_sales_person_password_with_id(
            db, id=token["id"], hashed_pwd=utils.hash_password(data["new_password"])
        )

        return JSONResponse(status_code=200, content=DEFAULT_200_MSG)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(status_code=500, content=DEFAULT_500_MSG)


@router.post("/sales-person/token")
async def sales_person_login(data: dict, request: Request, db=Depends(get_db)):
    try:
        is_exist = await crud.check_s_sales_person_with_email(db, email=data["email"])
        if not is_exist:
            return JSONResponse(status_code=400, content={"message": "user email is not exist."})
        if is_exist["status"] == 2:
            return JSONResponse(status_code=423, content={"message": "account is locked."})
        if not utils.verify_password(data["password"], is_exist["hashed_pwd"]):
            if is_exist["failed_first_at"]:
                if (datetime.now() - is_exist["failed_first_at"]).seconds < 300 and is_exist["failed_time"] == 4:
                    await crud.update_s_sales_person_status_locked(db, id=is_exist["id"])
                    return JSONResponse(status_code=423, content={"message": "account is locked."})
                else:
                    await crud.update_s_sales_person_failed_time(
                        db, id=is_exist["id"], failed_time=is_exist["failed_time"] + 1
                    )
            else:
                await crud.update_s_sales_person_failed_time(db, id=is_exist["id"])
            return JSONResponse(status_code=400, content={"message": "email or password is invalid."})
        access_token = utils.gen_token(
            payload=await crud.query_s_sales_person_token_payload(db, id=is_exist["id"]),
            expires_delta=settings.JWT_ACCESS_TOKEN_EXP,
        )
        await utils.common_insert_c_access_log(
            db, request, params={"body": data}, status_code=200, response_body={"access_token": "*******"}
        )
        return JSONResponse(status_code=200, content={"access_token": access_token})
    except Exception as err:
        logger.exception(err)
        return JSONResponse(status_code=500, content=DEFAULT_500_MSG)


@router.delete("/sales-person/token")
async def sales_person_logout(email: str, request: Request, db=Depends(get_db), token=Depends(get_token)):
    try:
        await utils.common_insert_c_access_log(
            db, request, params={"query": {"email": email}}, status_code=200, response_body=DEFAULT_200_MSG
        )
        return JSONResponse(status_code=200, content=DEFAULT_200_MSG)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(status_code=500, content=DEFAULT_500_MSG)


@router.get("/sales-person/preliminaries")
async def sales_person_get_access_applications(status: int, db=Depends(get_db), token=Depends(get_token)):

    try:
        preliminaries = await crud.query_sales_person_access_p_application_headers(
            db, status, token["orgs"], token["id"]
        )

        return JSONResponse(status_code=200, content=preliminaries)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.get("/sales-person/{s_sales_person_id}")
async def sales_person_get_access_applications(s_sales_person_id: int, db=Depends(get_db), token=Depends(get_token)):

    try:
        s_sales_person = await crud.query_sales_person_basic_info(db, s_sales_person_id)

        return JSONResponse(status_code=200, content=s_sales_person)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )
