from core.database import DB


async def check_s_manager_with_email(db: DB, email: str):
    sql = f"SELECT CONVERT(id,CHAR) AS id, status, failed_first_at, failed_time, hashed_pwd FROM s_managers WHERE email = '{email}';"
    return await db.fetch_one(sql)


async def update_s_manager_password_with_email(db: DB, email: str, hashed_pwd: str):
    sql = f"UPDATE s_managers SET hashed_pwd = '{hashed_pwd}', status = 1, failed_first_at = null, failed_time = 0 WHERE email = '{email}';"
    await db.execute(sql)


async def update_s_manager_status_locked(db: DB, id: int):
    sql = f"UPDATE s_managers SET status = 2, failed_time = 5 WHERE id = {id};"
    await db.execute(sql)


async def update_s_manager_failed_time(db: DB, id: int, failed_time: int = 1):
    sql = f"UPDATE s_managers SET failed_time = {failed_time} WHERE id = {id};"
    await db.execute(sql)


async def update_s_manager_failed_first_at(db: DB, id: int, failed_time: int = 1):
    sql = f"UPDATE s_managers SET failed_first_at = CURRENT_TIMESTAMP, failed_time = {failed_time} WHERE id = {id};"
    await db.execute(sql)


async def query_s_manager_token_payload(db: DB, id: int):
    sql = f"SELECT CONVERT(id,CHAR) AS id, email, name_kanji, role, 3 as role_type FROM s_managers WHERE id = {id};"
    return await db.fetch_one(sql)


async def query_s_manager_hashed_pwd(db: DB, id: int):
    sql = f"SELECT hashed_pwd FROM s_managers WHERE id = {id};"
    result = await db.fetch_one(sql)
    return result["hashed_pwd"] if result else None


async def update_s_manager_password_with_id(db: DB, id: int, hashed_pwd: str):
    sql = f"UPDATE s_managers SET hashed_pwd = '{hashed_pwd}' WHERE id = {id};"
    await db.execute(sql)
