import json
from core.database import DB
import crud


async def check_s_sales_person_with_email(db: DB, email: str):
    sql = f"SELECT CONVERT(id,CHAR) AS id, code, status, failed_first_at, failed_time, hashed_pwd FROM s_sales_persons WHERE email = '{email}';"
    return await db.fetch_one(sql)


async def update_s_sales_person_password_with_email(db: DB, email: str, hashed_pwd: str):
    sql = f"UPDATE s_sales_persons SET hashed_pwd = '{hashed_pwd}', status = 1, failed_first_at = null, failed_time = 0 WHERE email = '{email}';"
    await db.execute(sql)


async def update_s_sales_person_status_locked(db: DB, id: int):
    sql = f"UPDATE s_sales_persons SET status = 2, failed_time = 5 WHERE id = {id};"
    await db.execute(sql)


async def update_s_sales_person_failed_time(db: DB, id: int, failed_time: int = 1):
    sql = f"UPDATE s_sales_persons SET failed_time = {failed_time} WHERE id = {id};"
    await db.execute(sql)


async def update_s_sales_person_failed_first_at(db: DB, id: int, failed_time: int = 1):
    sql = (
        f"UPDATE s_sales_persons SET failed_first_at = CURRENT_TIMESTAMP, failed_time = {failed_time} WHERE id = {id};"
    )

    await db.execute(sql)


async def query_s_sales_person_token_payload(db: DB, id: int):
    sql = (
        f"SELECT CONVERT(id,CHAR) AS id, code, email, name_kanji, 2 as role_type FROM s_sales_persons WHERE id = {id};"
    )
    basic = await db.fetch_one(sql)
    sql = f"SELECT CONVERT(s_sales_company_org_id,CHAR) AS s_sales_company_org_id, role FROM s_sales_person_s_sales_company_org_rels WHERE s_sales_person_id = {id};"
    orgs = await db.fetch_all(sql)
    basic["orgs"] = orgs
    return basic


async def query_s_sales_person_hashed_pwd(db: DB, id: int):
    sql = f"SELECT hashed_pwd FROM s_sales_persons WHERE id = {id};"
    result = await db.fetch_one(sql)
    return result["hashed_pwd"] if result else None


async def update_s_sales_person_password_with_id(db: DB, id: int, hashed_pwd: str):
    sql = f"UPDATE s_sales_persons SET hashed_pwd = '{hashed_pwd}' WHERE id = {id};"
    await db.execute(sql)


async def query_sales_person_access_p_application_headers(db: DB, status: int, orgs: list, role_id: int):
    p_application_headers = await crud.query_manager_access_p_application_headers(db, status, role_id)
    all = []
    for org in orgs:
        if org["role"] == 1:  # 一般
            role_1_l = list(filter(lambda x: x["s_sales_person_id"] == role_id, p_application_headers))

            all = [*all, *role_1_l]

        if org["role"] == 9:  # 管理
            role_1_l = list(filter(lambda x: x["s_sales_person_id"] == role_id, p_application_headers))
            all = [*all, *role_1_l]
            s_sales_company_orgs = await crud.query_child_s_sales_company_orgs(
                db, parent_id=org["s_sales_company_org_id"]
            )
            s_sales_company_orgs_id = [item["id"] for item in s_sales_company_orgs]
            orgs_l = list(
                filter(
                    lambda x: x["sales_company_id"] in s_sales_company_orgs_id
                    or x["sales_area_id"] in s_sales_company_orgs_id
                    or x["sales_exhibition_hall_id"] in s_sales_company_orgs_id,
                    p_application_headers,
                )
            )
            all = [*all, *orgs_l]
    unique_data = list({item["id"]: item for item in all}.values())
    return unique_data
