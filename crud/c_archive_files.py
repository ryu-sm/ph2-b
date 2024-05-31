import base64
import json
import uuid
from constant import P_UPLOAD_FILE_TYPE
from core.database import DB
import crud
import utils
from utils.common import none_to_blank
from utils.s3 import delete_from_s3, upload_to_s3, download_from_s3
from core.config import settings


async def insert_c_archive_files(db: DB, files: list, s_sales_person_id: int):
    below_orgs = await crud.query_sales_person_below_orgs_basic(db, s_sales_person_id)
    s_sales_company_org_root_id = await crud.query_s_sales_company_orgs_root_id(
        db, below_orgs[0].get("s_sales_company_org_id")
    )
    c_archive_file_id = await db.uuid_short()
    c_archive_file_sql_params = {
        "id": c_archive_file_id,
        "s_sales_company_org_id": s_sales_company_org_root_id,
        "s_sales_person_id": s_sales_person_id,
    }
    await db.execute(utils.gen_insert_sql("c_archive_files", c_archive_file_sql_params))

    for file in files:
        c_archive_uploaded_file_id = await db.uuid_short()
        c_archive_uploaded_file_sql_params = {
            "id": c_archive_uploaded_file_id,
            "owner_id": s_sales_person_id,
            "record_id": c_archive_file_id,
            "s3_key": f"{s_sales_company_org_root_id}/{s_sales_person_id}/{c_archive_uploaded_file_id}",
            "file_name": file["name"],
        }
        utils.upload_base64_file_s3(
            f"{c_archive_uploaded_file_sql_params.get('s3_key')}/{c_archive_uploaded_file_sql_params.get('file_name')}",
            file["src"],
            settings.C_ARCHIVE_UPLOADED_FILES_BUCKET_NAME,
        )
        await db.execute(utils.gen_insert_sql("c_archive_uploaded_files", c_archive_uploaded_file_sql_params))


async def query_c_archive_files_for_s_sales_person(db: DB, s_sales_person_id):
    sql = f"SELECT CONVERT(s_sales_company_org_id,CHAR) AS s_sales_company_org_id, role FROM s_sales_person_s_sales_company_org_rels WHERE s_sales_person_id = {s_sales_person_id};"
    orgs = await db.fetch_all(sql)
    access_ids = []
    for org in orgs:
        if org["role"] == 1:
            access_ids.append(str(s_sales_person_id))
        if org["role"] == 9:
            s_sales_persons = await crud.query_orgs_access_s_sales_persons(db, org["s_sales_company_org_id"])
            s_sales_persons_id = [item["value"] for item in s_sales_persons]
            access_ids += s_sales_persons_id
    sql = f"""
    SELECT
        CONVERT(c_archive_files.id,CHAR) AS id,
        DATE_FORMAT(c_archive_files.created_at, '%Y/%m/%d %H:%i') as created_at,
        s_sales_persons.name_kanji as s_sales_person_name,
        c_archive_files.note as note,
        s_sales_company_orgs.name as org_name,
        CONVERT(s_sales_company_orgs.id,CHAR) as org_id,
        CONVERT(s_sales_persons.id,CHAR) as s_sales_person_id
    FROM
        c_archive_files
    LEFT JOIN
        s_sales_persons
        ON
        s_sales_persons.id = c_archive_files.s_sales_person_id
    LEFT JOIN
        s_sales_company_orgs
        ON
        s_sales_company_orgs.id = c_archive_files.s_sales_company_org_id
    WHERE
        c_archive_files.deleted is NULL
        AND
        c_archive_files.s_sales_person_id in ({', '.join(list(set(access_ids)))})
    ORDER BY c_archive_files.created_at DESC;
    """
    basic = await db.fetch_all(sql)

    c_archive_files = []

    for item in basic:
        sql = f"SELECT file_name FROM c_archive_uploaded_files WHERE record_id = {item['id']} AND deleted is NULL;"
        files = await db.fetch_all(sql)
        c_archive_files.append(
            none_to_blank({**item, "file_names": [item["file_name"] for item in files], "files_num": len(files)})
        )

    return c_archive_files


async def query_c_archive_files_for_manager(db: DB):
    sql = f"""
    SELECT
        CONVERT(c_archive_files.id,CHAR) AS id,
        DATE_FORMAT(c_archive_files.created_at, '%Y/%m/%d %H:%i') as created_at,
        s_sales_persons.name_kanji as s_sales_person_name,
        c_archive_files.note as note,
        s_sales_company_orgs.name as org_name,
        CONVERT(s_sales_company_orgs.id,CHAR) as org_id,
        CONVERT(s_sales_persons.id,CHAR) as s_sales_person_id
    FROM
        c_archive_files
    LEFT JOIN
        s_sales_persons
        ON
        s_sales_persons.id = c_archive_files.s_sales_person_id
    LEFT JOIN
        s_sales_company_orgs
        ON
        s_sales_company_orgs.id = c_archive_files.s_sales_company_org_id
    WHERE
        c_archive_files.deleted is NULL
    ORDER BY c_archive_files.created_at DESC;
    """
    basic = await db.fetch_all(sql)

    c_archive_files = []

    for item in basic:
        sql = f"SELECT file_name FROM c_archive_uploaded_files WHERE record_id = {item['id']} AND deleted is NULL;"
        files = await db.fetch_all(sql)
        c_archive_files.append(
            none_to_blank({**item, "file_names": [item["file_name"] for item in files], "files_num": len(files)})
        )

    return c_archive_files


async def query_c_archive_file(db: DB, id: int):
    sql = f"""
    SELECT
        CONVERT(id,CHAR) AS id,
        s3_key,
        file_name
    FROM
        c_archive_uploaded_files
    WHERE
        record_id = {id}
        AND
        deleted is NULL;
    """
    files_info = await db.fetch_all(sql)
    files = []
    for file_info in files_info:
        src = utils.generate_presigned_url(
            f"{file_info['s3_key']}/{file_info['file_name']}", settings.C_ARCHIVE_UPLOADED_FILES_BUCKET_NAME
        )
        files.append({"id": file_info["id"], "name": file_info["file_name"], "src": src})
    return files


async def delete_c_archive_file(db: DB, id: int):
    await db.execute(f"UPDATE c_archive_uploaded_files SET deleted = 1 WHERE record_id = {id};")
    await db.execute(f"UPDATE c_archive_files SET deleted = 1 WHERE id = {id};")


async def delete_c_archive_file_for_sub(db: DB, id: int):
    await db.execute(f"UPDATE c_archive_uploaded_files SET deleted = 1 WHERE id = {id};")
    file = await db.fetch_one(f"SELECT record_id FROM c_archive_uploaded_files WHERE id = {id};")
    files = await db.fetch_all(
        f"SELECT id FROM c_archive_uploaded_files WHERE deleted is NULL AND record_id = {file['record_id']};"
    )
    if len(files) == 0:
        await db.execute(f"UPDATE c_archive_files SET deleted = 1 WHERE id = {file['record_id']};")


async def update_c_archive_file_note(db: DB, id: int, note: str):
    await db.execute(f"UPDATE c_archive_files SET note = '{note}' WHERE id = {id};")
