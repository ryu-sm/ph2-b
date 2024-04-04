import base64
from fastapi import APIRouter, Depends
import utils
from core.config import settings
from apis.deps import get_db
from core.database import DB
from utils import download_from_s3, upload_to_s3

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
            new_key = s3_key__.split("__0__" if "__0__" in s3_key__ else "__1__")[-1]

            p_applicant_persons = await db.fetch_one(
                f"select id from p_applicant_persons where p_application_header_id = {p_application_header_id} and type = {new_type}"
            )
            print(p_applicant_persons)
            if p_applicant_persons is None:
                continue
            p_applicant_person_id = p_applicant_persons["id"]

            sql = f"select * from p_uploaded_files_bk where p_application_header_id = {p_application_header_id} and s3_key like '%/{s3_key__}';"

            files = await db.fetch_all(sql)

            if len(files) == 0:
                continue
            for file in files:
                old_file = download_from_s3(file["file_name"])
                p_upload_file_id = await db.uuid_short()

                sub_fields = ["id", "p_application_header_id", "owner_type", "owner_id", "record_id", "type"]
                sub_values = [
                    f"{p_upload_file_id}",
                    f"{p_application_header_id}",
                    f"{file['owner_type']}",
                    f"{file['owner_id']}",
                    f"{p_applicant_person_id}",
                    f"{new_type}",
                ]

                s3_key = f"{p_application_header_id}/{p_upload_file_id}/{new_key}"
                file_name = old_file["name"]

                sub_fields.append("s3_key")
                sub_fields.append("file_name")
                sub_values.append(f"'{s3_key}'")
                sub_values.append(f"'{file_name}'")

                # file_content = base64.b64decode(old_file["src"].split(",")[1])

                # upload_to_s3(f"{s3_key}/{file_name}", file_content)

                sql = f"INSERT INTO p_uploaded_files ({', '.join(sub_fields)}) VALUES ({', '.join(sub_values)});"
                # return {"sql": sql}

        for s3_key__ in header_key:
            new_type = 0
            new_key = s3_key__.split("/")[-1]

            sql = f"select * from p_uploaded_files_bk where p_application_header_id = {p_application_header_id} and s3_key like '%/{s3_key__}';"

            files = await db.fetch_all(sql)

            if len(files) == 0:
                continue
            for file in files:
                old_file = download_from_s3(file["file_name"])
                p_upload_file_id = await db.uuid_short()

                sub_fields = ["id", "p_application_header_id", "owner_type", "owner_id", "record_id", "type"]
                sub_values = [
                    f"{p_upload_file_id}",
                    f"{p_application_header_id}",
                    f"{file['owner_type']}",
                    f"{file['owner_id']}",
                    f"{p_application_header_id}",
                    f"{new_type}",
                ]

                s3_key = f"{p_application_header_id}/{p_upload_file_id}/{new_key}"
                file_name = old_file["name"]

                sub_fields.append("s3_key")
                sub_fields.append("file_name")
                sub_values.append(f"'{s3_key}'")
                sub_values.append(f"'{file_name}'")

                # file_content = base64.b64decode(old_file["src"].split(",")[1])

                # upload_to_s3(f"{s3_key}/{file_name}", file_content)

                sql = f"INSERT INTO p_uploaded_files ({', '.join(sub_fields)}) VALUES ({', '.join(sub_values)});"
                return {"sql": sql}

    except Exception as e:
        raise e
