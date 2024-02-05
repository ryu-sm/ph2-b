import json
from core.database import DB


async def check_c_user_with_email(db: DB, email: str):
    sql = f"SELECT id FROM c_users WHERE c_users.email = '{email}';"
    return await db.fetch_one(sql)


async def query_c_user_with_email(db: DB, email: str):
    sql = f"SELECT id, email, s_sales_company_org_id, status, failed_first_at, failed_time, first_login, hashed_pwd FROM c_users WHERE c_users.email = '{email}';"
    return await db.fetch_one(sql)


async def insert_new_c_user(db: DB, email: str, hashed_pwd: str, s_sales_company_org_id: int):
    id = await db.uuid_short()
    sql = f"""
    INSERT INTO c_users (id, email, hashed_pwd, s_sales_company_org_id, status)
    VALUES ({id}, '{email}', '{hashed_pwd}', {s_sales_company_org_id if s_sales_company_org_id else 'null'}, 1);
    """
    await db.execute(sql)
    return id


async def update_c_user_first_login(db: DB, id: int):
    sql = f"UPDATE c_users SET first_login = 1 WHERE c_users.id = {id};"
    await db.execute(sql)


async def update_c_user_password_with_email(db: DB, email: str, hashed_pwd: str):
    sql = f"UPDATE c_users SET hashed_pwd = '{hashed_pwd}', status = 1, failed_first_at = null, failed_time = 0 WHERE c_users.email = '{email}';"
    await db.execute(sql)


async def update_c_user_password_with_id(db: DB, id: int, hashed_pwd: str):
    sql = f"UPDATE c_users SET hashed_pwd = '{hashed_pwd}' WHERE c_users.id = {id};"
    await db.execute(sql)


async def update_c_user_failed_first_at(db: DB, id: int, failed_time: int = 1):
    sql = (
        f"UPDATE c_users SET failed_first_at = CURRENT_TIMESTAMP, failed_time = {failed_time} WHERE c_users.id = {id};"
    )
    await db.execute(sql)


async def update_c_user_status_locked(db: DB, id: int):
    sql = f"UPDATE c_users SET status = 2, failed_time = 5 WHERE c_users.id = {id};"
    await db.execute(sql)


async def update_c_user_failed_time(db: DB, id: int, failed_time: int = 1):
    sql = f"UPDATE c_users SET failed_time = {failed_time} WHERE c_users.id = {id};"
    await db.execute(sql)


async def update_c_user_email(db: DB, id: int, new_email: str):
    sql = f"UPDATE c_users SET email = '{new_email}' WHERE c_users.id = {id};"
    await db.execute(sql)


async def query_c_user_basic_info(db: DB, id: int):
    sql = f"SELECT id, email, s_sales_company_org_id, status, failed_first_at, failed_time, first_login FROM c_users WHERE c_users.id = {id};"
    return await db.fetch_one(sql)


async def reset_c_user_failed_infos(db: DB, id: int):
    sql = f"UPDATE c_users SET failed_first_at = null, failed_time = 0 WHERE c_users.id = {id};"
    await db.execute(sql)


async def query_c_user_hashed_pwd(db: DB, id: int):
    sql = f"SELECT hashed_pwd FROM c_users WHERE c_users.id = {id};"
    result = await db.fetch_one(sql)

    return result["hashed_pwd"] if result else None


async def delete_c_user(db: DB, id: int):
    sql = f"DELETE FROM p_drafts WHERE c_user_id = {id};"
    await db.execute(sql)
    sql = f"UPDATE p_application_headers SET c_user_id = null WHERE c_user_id = {id};"
    await db.execute(sql)
    sql = f"DELETE FROM c_users WHERE c_users.id = {id};"
    await db.execute(sql)


async def insert_p_draft(db: DB, c_user_id: int, data: dict):
    id = await db.uuid_short()
    sql = f"INSERT INTO p_drafts (id, c_user_id, data) VALUE ({id}, {c_user_id}, '{json.dumps(data)}');"
    await db.execute(sql)


async def query_c_user_token_payload(db: DB, c_user_id: int):
    sql = f"SELECT id, email, agent_sended, first_login FROM c_users WHERE id = {c_user_id};"
    return await db.fetch_one(sql)


async def query_p_draft_data(db: DB, c_user_id: int):
    sql = f"SELECT data FROM p_drafts WHERE c_user_id = {c_user_id};"
    p_draft = await db.fetch_one(sql)
    return json.loads(p_draft["data"])
