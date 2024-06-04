import json
from typing import Optional
from loguru import logger
from datetime import datetime
from fastapi import APIRouter, Request
from fastapi import Depends
from fastapi.responses import JSONResponse
import pytz
import requests
from core.config import settings
from constant import ACCESS_LOG_OPERATION, DEFAULT_200_MSG, DEFAULT_500_MSG, TOKEN_ROLE_TYPE
from core.config import settings
from core.custom import LoggingContextRoute
from apis.deps import get_db
from apis.deps import get_token
import crud
import utils
import schemas
from jose import jwt


router = APIRouter(route_class=LoggingContextRoute)


@router.post("/sales-person/verify-email")
async def sales_person_send_verify_email(data: dict, db=Depends(get_db)):
    try:
        is_exist = await crud.check_s_sales_person_with_email(db, email=data["email"])
        if is_exist:
            return JSONResponse(status_code=400, content={"message": "user email is exist."})
        token = utils.gen_token(data, expires_delta=settings.JWT_VERIFY_EMAIL_TOKEN_EXP)
        utils.send_email(
            to=data["email"],
            template="user_send_verify_email",
            link=f"{settings.FRONTEND_BASE_URL}/sales-person/register?token={token}",
        )
        return JSONResponse(status_code=200, content=DEFAULT_200_MSG)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(status_code=500, content=DEFAULT_500_MSG)


@router.post("/sales-person")
async def sales_person_register(data: dict, request: Request, db=Depends(get_db)):
    try:
        new_sales_person_id = await crud.insert_new_email_s_sales_person(
            db,
            hashed_pwd=utils.hash_password(data["password"]),
            name=data["email"],
            email=data["email"],
            s_sales_company_org_id=data["s_sales_company_org_id"],
        )
        payload = await crud.query_s_sales_person_token_payload(db, id=new_sales_person_id)
        access_token = utils.gen_token(
            payload=payload,
            expires_delta=settings.JWT_ACCESS_TOKEN_EXP,
        )
        await utils.common_insert_c_access_log(
            db,
            request,
            params={
                "account_id": new_sales_person_id,
                "account_type": TOKEN_ROLE_TYPE.SALES_PERSON.value,
                "operation": ACCESS_LOG_OPERATION.REGISTER.value,
            },
        )
        return JSONResponse(status_code=200, content={"access_token": access_token})

    except Exception as err:
        logger.exception(err)
        return JSONResponse(status_code=500, content=DEFAULT_500_MSG)


@router.post("/azure/sales-person")
async def sales_person_register(data: dict, request: Request, db=Depends(get_db)):
    try:
        new_sales_person_id = await crud.insert_new_azure_s_sales_person(
            db,
            name=data["name"],
            email=data["email"],
            s_sales_company_org_id=data["s_sales_company_org_id"],
        )
        payload = await crud.query_s_sales_person_token_payload(db, id=new_sales_person_id)
        access_token = utils.gen_token(
            payload=payload,
            expires_delta=settings.JWT_ACCESS_TOKEN_EXP,
        )
        await utils.common_insert_c_access_log(
            db,
            request,
            params={
                "account_id": new_sales_person_id,
                "account_type": TOKEN_ROLE_TYPE.SALES_PERSON.value,
                "operation": ACCESS_LOG_OPERATION.REGISTER.value,
            },
        )
        return JSONResponse(status_code=200, content={"access_token": access_token})

    except Exception as err:
        logger.exception(err)
        return JSONResponse(status_code=500, content=DEFAULT_500_MSG)


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


@router.post("/azure/sales-person/login/{code}")
async def sales_person_azure_login(request: Request, code: Optional[str] = None, db=Depends(get_db)):
    try:

        token_res = requests.post(
            url=f"https://login.microsoftonline.com/{settings.TENANT}/oauth2/v2.0/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "authorization_code",
                "client_id": settings.CLIENT_ID,
                "client_secret": settings.CLIENT_SECRET,
                "code": code,
                "redirect_uri": settings.REDIRECT_URI,
            },
        )

        logger.info("token_res:", token_res.json())

        if str(token_res.status_code) != "200":
            return JSONResponse(status_code=400, content={"message": "azure error"})

        token_body = json.loads(token_res.text)
        access_token = token_body.get("access_token")

        access_token_payload = jwt.get_unverified_claims(access_token)

        tid = access_token_payload.get("tid")

        s_sales_company_org_id = await crud.query_azure_register_org(db, tid)

        if s_sales_company_org_id is None:
            return JSONResponse(status_code=409, content={"message": "azure error"})

        info_res = requests.get(
            url=f"https://graph.microsoft.com/v1.0/me",
            headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
        )

        logger.info("info_res:", info_res.json())

        if str(info_res.status_code) != "200":
            return JSONResponse(status_code=408, content={"message": "azure error"})

        info_body = json.loads(info_res.text)
        email = info_body.get("userPrincipalName")
        display_name = info_body.get("displayName")
        if email is None:
            return JSONResponse(status_code=408, content={"message": "azure error"})

        is_exist = await crud.check_s_sales_person_with_email(db, email=email)

        if is_exist:
            payload = await crud.query_s_sales_person_token_payload(db, id=is_exist["id"])
            access_token = utils.gen_token(
                payload=payload,
                expires_delta=settings.JWT_ACCESS_TOKEN_EXP,
            )
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
        else:

            return JSONResponse(
                status_code=202,
                content={
                    "email": email,
                    "name": display_name,
                    "s_sales_company_org_id": s_sales_company_org_id,
                },
            )

    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.post("/azure/sales-person/s_sales_company_org")
async def sales_person_azure_login(data: dict, request: Request, db=Depends(get_db)):
    try:
        await crud.updated_new_azure_s_sales_person_status(db, data["sales_person_id"], data["s_sales_company_org_id"])
        payload = await crud.query_s_sales_person_token_payload(db, id=data["sales_person_id"])
        access_token = utils.gen_token(
            payload=payload,
            expires_delta=settings.JWT_ACCESS_TOKEN_EXP,
        )
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
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


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
                if (
                    datetime.strptime(
                        datetime.now().astimezone(pytz.timezone("Asia/Tokyo")).strftime("%Y-%m-%d %H:%M:%S"),
                        "%Y-%m-%d %H:%M:%S",
                    )
                    - datetime.strptime(is_exist["failed_first_at"], "%Y-%m-%d %H:%M:%S")
                ).seconds < 300 and is_exist["failed_time"] == 4:
                    await crud.update_s_sales_person_status_locked(db, id=is_exist["id"])
                    return JSONResponse(status_code=423, content={"message": "account is locked."})
                else:
                    await crud.update_s_sales_person_failed_time(
                        db, id=is_exist["id"], failed_time=is_exist["failed_time"] + 1
                    )
            else:
                await crud.update_s_sales_person_failed_first_at(db, id=is_exist["id"])
            return JSONResponse(status_code=400, content={"message": "email or password is invalid."})
        payload = await crud.query_s_sales_person_token_payload(db, id=is_exist["id"])
        access_token = utils.gen_token(
            payload=payload,
            expires_delta=settings.JWT_ACCESS_TOKEN_EXP,
        )
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


@router.delete("/sales-person/token")
async def sales_person_logout(request: Request, db=Depends(get_db), token=Depends(get_token)):
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


@router.get("/sales-person/preliminaries")
async def sales_person_get_access_applications(status: int, db=Depends(get_db), token=Depends(get_token)):

    try:
        preliminaries = await crud.query_sales_person_access_p_application_headers(db, status, token["id"])

        return JSONResponse(status_code=200, content=preliminaries)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.get("/sales-person/preliminariy/access/{p_application_header_id}")
async def sales_person_get_access_application_id(
    p_application_header_id: int, db=Depends(get_db), token=Depends(get_token)
):

    try:
        access = await crud.query_sales_person_access_p_application_header_id(db, p_application_header_id, token["id"])
        return JSONResponse(status_code=200, content=access)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.get("/sales-person/preliminaries/file")
async def sales_person_get_access_applications(status: int, db=Depends(get_db), token=Depends(get_token)):

    try:
        preliminaries = await crud.query_sales_person_access_p_application_headers(db, status, token["id"])

        file = await utils.preliminaries_output(preliminaries)
        return JSONResponse(status_code=200, content=file)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.get("/sales-person/below-orgs")
async def sales_person_get_access_applications(db=Depends(get_db), token=Depends(get_token)):

    try:
        orgs = await crud.query_sales_person_below_orgs_basic(db, token["id"])

        return JSONResponse(status_code=200, content=orgs)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.get("/sales-person/orgs")
async def sales_person_get_access_applications(s_sales_person_id: int, db=Depends(get_db), token=Depends(get_token)):
    try:
        orgs = await crud.query_sales_person_below_orgs(db, s_sales_person_id)

        return JSONResponse(status_code=200, content=orgs)
    except Exception as err:
        logger.exception(err)
        return JSONResponse(
            status_code=500, content={"message": "An unknown exception occurred, please try again later."}
        )


@router.get("/sales-person/host-org")
async def sales_person_get_access_applications(db=Depends(get_db), token=Depends(get_token)):
    try:
        org = await crud.query_sales_person_host_orgs(db, token["id"])

        return JSONResponse(status_code=200, content=org)
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
