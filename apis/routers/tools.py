from fastapi import APIRouter, Depends
import utils
from core.config import settings
from apis.deps import get_db
from core.database import DB
from utils import download_from_s3

router = APIRouter()


@router.post("/link-for-qrcode/{org_id}")
async def gen_link_for_qrcode(org_id: int):
    data = {"s_sales_company_org_id": f"{org_id}"}
    token = utils.gen_token(data, 525600)
    return f"{settings.FRONTEND_BASE_URL}?token={token}"


@router.get("/file_reload/{p_application_header_id}")
async def file_reload(p_application_header_id: int, db: DB = Depends(get_db)):
    try:
        bowrring_key = ["p_borrowings__I"]
        header_key = ["G", "J"]
        header_to_person_key = ["S"]
        person_key = [
            "p_applicant_persons__0__E",
            "p_applicant_persons__0__K",
            "p_applicant_persons__1__E",
            "p_applicant_persons__1__K",
            "p_applicant_persons__0__B__a",
            "p_applicant_persons__0__B__b",
            "p_applicant_persons__0__H__a",
            "p_applicant_persons__0__H__b",
            "p_applicant_persons__1__B__a",
            "p_applicant_persons__1__B__b",
            "p_applicant_persons__1__H__a",
            "p_applicant_persons__1__H__b",
            "p_applicant_persons__0__A__02",
            "p_applicant_persons__0__C__01",
            "p_applicant_persons__0__C__02",
            "p_applicant_persons__0__C__03",
            "p_applicant_persons__0__C__04",
            "p_applicant_persons__0__C__05",
            "p_applicant_persons__0__D__01",
            "p_applicant_persons__0__D__02",
            "p_applicant_persons__0__D__03",
            "p_applicant_persons__0__F__01",
            "p_applicant_persons__0__F__02",
            "p_applicant_persons__0__F__03",
            "p_applicant_persons__1__A__02",
            "p_applicant_persons__1__C__01",
            "p_applicant_persons__1__C__02",
            "p_applicant_persons__1__C__03",
            "p_applicant_persons__1__C__04",
            "p_applicant_persons__1__C__05",
            "p_applicant_persons__1__D__01",
            "p_applicant_persons__1__D__02",
            "p_applicant_persons__1__D__03",
            "p_applicant_persons__1__F__01",
            "p_applicant_persons__1__F__02",
            "p_applicant_persons__1__F__03",
            "p_applicant_persons__0__A__01__a",
            "p_applicant_persons__0__A__01__b",
            "p_applicant_persons__0__A__03__a",
            "p_applicant_persons__0__A__03__b",
            "p_applicant_persons__1__A__01__a",
            "p_applicant_persons__1__A__01__b",
            "p_applicant_persons__1__A__03__a",
            "p_applicant_persons__1__A__03__b",
        ]

        for s3_key__ in person_key:
            new_type = 0 if "__0__" in s3_key__ else 1

            p_applicant_persons = await db.fetch_one(
                f"select id from p_applicant_persons where p_application_header_id = {p_application_header_id} and type = {new_type}"
            )
            print(p_applicant_persons)
            if p_applicant_persons is None:
                print(999)
                continue
            p_applicant_person_id = p_applicant_persons["id"]

            sql = f"select * from p_uploaded_files_bk where p_application_header_id = {p_application_header_id} and s3_key like '%/{s3_key__}';"

            files = await db.fetch_all(sql)

            if len(files) == 0:
                continue
            for file in files:
                file_base64 = download_from_s3(file["file_name"])
                print(file_base64)
                return {"sec": file_base64}

    except Exception as e:
        raise e
