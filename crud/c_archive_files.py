import base64
import json
import uuid
from core.database import DB
import crud
from utils.common import none_to_blank
from utils.s3 import delete_from_s3, upload_to_s3, download_from_s3


async def insert_c_archive_files(db: DB, files: list, s_sales_person_id: int, s_sales_company_org_id: int):
    id = await db.uuid_short()
    file_names = []
    for file in files:
        s3_key = f"{s_sales_company_org_id}/{id}"
        file_name = f"{s3_key}/{file['name']}"
        file_content = base64.b64decode(file["src"].split(",")[1])
        upload_to_s3(file_name, file_content)
        file_names.append({"id": str(uuid.uuid4()), "name": file["name"]})

    sql = f"""
    INSERT INTO c_archive_files (id, s_sales_company_org_id, s_sales_person_id, file_names)
    VALUES ({id}, {s_sales_company_org_id}, {s_sales_person_id}, '{json.dumps(file_names, ensure_ascii=False)}');
    """

    await db.execute(sql)


async def query_c_archive_files_for_s_sales_person(db: DB, s_sales_company_org_id: int):
    sql = f"""
    SELECT
        CONVERT(c_archive_files.id,CHAR) AS id,
        DATE_FORMAT(c_archive_files.created_at, '%Y/%m/%d %H:%i') as created_at,
        s_sales_persons.name_kanji as s_sales_person_name,
        c_archive_files.file_names as file_names,
        c_archive_files.note as note,
        s_sales_company_orgs.name as org_name
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
        c_archive_files.s_sales_company_org_id = {s_sales_company_org_id};
    """
    result = await db.fetch_all(sql)

    temp = []

    for item in result:
        files = json.loads(item["file_names"])
        temp.append(none_to_blank({**item, "file_names": files, "files_num": len(files)}))

    return temp


async def query_c_archive_files_for_manager(db: DB):
    sql = f"""
    SELECT
        CONVERT(c_archive_files.id,CHAR) AS id,
        DATE_FORMAT(c_archive_files.created_at, '%Y/%m/%d %H:%i') as created_at,
        s_sales_persons.name_kanji as s_sales_person_name,
        c_archive_files.file_names as file_names,
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
        s_sales_company_orgs.id = c_archive_files.s_sales_company_org_id;
    """
    result = await db.fetch_all(sql)

    temp = []

    for item in result:
        files = json.loads(item["file_names"])
        temp.append(none_to_blank({**item, "file_names": files, "files_num": len(files)}))

    return temp


async def query_c_archive_file(db: DB, id: int):
    sql = f"SELECT id, s_sales_company_org_id, file_names FROM c_archive_files WHERE id = {id};"
    c_archive_file = await db.fetch_one(sql)
    c_archive_file_id = c_archive_file["id"]
    s_sales_company_org_id = c_archive_file["s_sales_company_org_id"]
    files = []
    for file in json.loads(c_archive_file["file_names"]):

        s3_key = f"{s_sales_company_org_id}/{c_archive_file_id}"
        file_name = f"{s3_key}/{file['name']}"

        files.append({**download_from_s3(file_name), "id": file["id"]})
    return files


async def delete_c_archive_file(db: DB, id: int):
    sql = f"SELECT id, s_sales_company_org_id, file_names FROM c_archive_files WHERE id = {id};"
    c_archive_file = await db.fetch_one(sql)

    c_archive_file_id = c_archive_file["id"]
    s_sales_company_org_id = c_archive_file["s_sales_company_org_id"]

    for file in json.loads(c_archive_file["file_names"]):

        s3_key = f"{s_sales_company_org_id}/{c_archive_file_id}"
        file_name = f"{s3_key}/{file['name']}"

        delete_from_s3(file_name)
    await db.execute(f"DELETE FROM  c_archive_files WHERE id = {id};")


async def delete_c_archive_file_for_sub(db: DB, id: int, data: dict):
    sql = f"SELECT id, s_sales_company_org_id, file_names FROM c_archive_files WHERE id = {id};"
    c_archive_file = await db.fetch_one(sql)
    c_archive_file_id = c_archive_file["id"]
    s_sales_company_org_id = c_archive_file["s_sales_company_org_id"]
    files = json.loads(c_archive_file["file_names"])
    un_delete_files = []
    for file in files:
        if file["id"] == data["id"]:
            continue
        else:
            un_delete_files.append(file)

    s3_key = f"{s_sales_company_org_id}/{c_archive_file_id}"
    file_name = f"{s3_key}/{data['name']}"

    delete_from_s3(file_name)

    if len(un_delete_files) == 0:
        await db.execute(f"DELETE FROM  c_archive_files WHERE id = {id};")
    else:
        await db.execute(
            f"UPDATE  c_archive_files SET file_names = '{json.dumps(un_delete_files, ensure_ascii=False)}' WHERE id = {id};"
        )

    return bool(un_delete_files)


async def update_c_archive_file_note(db: DB, id: int, note: str):
    await db.execute(f"UPDATE c_archive_files SET note = '{note}' WHERE id = {id};")
