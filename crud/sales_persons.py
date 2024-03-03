from core.database import DB


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
    sql = f"SELECT s_sales_company_org_id, role FROM s_sales_person_s_sales_company_org_rels WHERE s_sales_person_id = {id};"
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
