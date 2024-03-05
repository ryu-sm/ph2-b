import json
from core.database import DB


async def check_c_user_with_email(db: DB, email: str):
    sql = f"SELECT CONVERT(id,CHAR) AS id FROM c_users WHERE email = '{email}';"
    return await db.fetch_one(sql)


async def query_c_user_with_email(db: DB, email: str):
    sql = f"""
    SELECT
        CONVERT(id,CHAR) AS id,
        email,
        CONVERT(s_sales_company_org_id,CHAR) AS s_sales_company_org_id,
        status,
        failed_first_at,
        failed_time,
        hashed_pwd
    FROM
        c_users
    WHERE
        email = '{email}';
    """
    return await db.fetch_one(sql)


async def insert_new_c_user(db: DB, email: str, hashed_pwd: str, s_sales_company_org_id: int):
    id = await db.uuid_short()
    sql = f"""
    INSERT INTO c_users (id, email, hashed_pwd, s_sales_company_org_id, status)
    VALUES ({id}, '{email}', '{hashed_pwd}', {s_sales_company_org_id if s_sales_company_org_id else 'null'}, 1);
    """
    await db.execute(sql)
    return id


async def update_c_user_password_with_email(db: DB, email: str, hashed_pwd: str):
    sql = f"UPDATE c_users SET hashed_pwd = '{hashed_pwd}', status = 1, failed_first_at = null, failed_time = 0 WHERE email = '{email}';"
    await db.execute(sql)


async def update_c_user_password_with_id(db: DB, id: int, hashed_pwd: str):
    sql = f"UPDATE c_users SET hashed_pwd = '{hashed_pwd}' WHERE id = {id};"
    await db.execute(sql)


async def update_c_user_failed_first_at(db: DB, id: int, failed_time: int = 1):
    sql = f"UPDATE c_users SET failed_first_at = CURRENT_TIMESTAMP, failed_time = {failed_time} WHERE id = {id};"
    await db.execute(sql)


async def update_c_user_status_locked(db: DB, id: int):
    sql = f"UPDATE c_users SET status = 2, failed_time = 5 WHERE id = {id};"
    await db.execute(sql)


async def update_c_user_failed_time(db: DB, id: int, failed_time: int = 1):
    sql = f"UPDATE c_users SET failed_time = {failed_time} WHERE id = {id};"
    await db.execute(sql)


async def update_c_user_email(db: DB, id: int, new_email: str):
    sql = f"UPDATE c_users SET email = '{new_email}' WHERE id = {id};"
    await db.execute(sql)


async def update_c_user_agent_sended(db: DB, id: int):
    sql = f"UPDATE c_users SET agent_sended = 1 WHERE id = {id};"
    await db.execute(sql)


async def query_c_user_basic_info(db: DB, id: int):
    sql = f"""
    SELECT
        CONVERT(id,CHAR) AS id,
        email,
        CONVERT(s_sales_company_org_id,CHAR) AS s_sales_company_org_id,
        status,
        failed_first_at,
        failed_time
    FROM
        c_users
    WHERE
        id = {id};
    """
    return await db.fetch_one(sql)


async def reset_c_user_failed_infos(db: DB, id: int):
    sql = f"UPDATE c_users SET failed_first_at = null, failed_time = 0 WHERE id = {id};"
    await db.execute(sql)


async def query_c_user_hashed_pwd(db: DB, id: int):
    sql = f"SELECT hashed_pwd FROM c_users WHERE id = {id};"
    result = await db.fetch_one(sql)

    return result["hashed_pwd"] if result else None


async def delete_c_user(db: DB, id: int):
    sql = f"DELETE FROM p_drafts WHERE c_user_id = {id};"
    await db.execute(sql)
    sql = f"UPDATE p_application_headers SET c_user_id = NUll, unsubcribed = 1 WHERE c_user_id = {id};"
    print(sql)
    await db.execute(sql)
    sql = f"DELETE FROM c_users WHERE id = {id};"
    await db.execute(sql)


async def query_c_user_token_payload(db: DB, c_user_id: int):
    sql = f"""
    SELECT
        CONVERT(c_users.id,CHAR) AS id,
        c_users.email,
        CONVERT(c_users.s_sales_company_org_id,CHAR) AS s_sales_company_org_id,
        c_users.agent_sended,
        p_drafts.data as has_draft,
        p_application_headers.apply_no,
        p_application_headers.pre_examination_status,
        s_sales_company_orgs.display_pdf,
        1 as role_type
    FROM
        c_users
    LEFT JOIN
        p_drafts
        ON
        p_drafts.c_user_id = c_users.id
    LEFT JOIN
        p_application_headers
        ON
        p_application_headers.c_user_id = c_users.id
    LEFT JOIN
        s_sales_company_orgs
        ON
        s_sales_company_orgs.id = c_users.s_sales_company_org_id
    WHERE
        c_users.id = {c_user_id};
    """
    result = await db.fetch_one(sql)
    result["has_draft"] = bool(result["has_draft"])
    # if result["s_sales_company_org_id"] is None:
    #     result["s_sales_company_org_id"] = "100713166408778466"
    return result


async def query_p_draft_data(db: DB, c_user_id: int):
    sql = f"SELECT data FROM p_drafts WHERE c_user_id = {c_user_id};"
    p_draft = await db.fetch_one(sql)
    return json.loads(p_draft["data"])


async def upsert_p_draft_data(db: DB, c_user_id: int, data: dict):
    sql = f"SELECT COUNT(id) as isExist FROM p_drafts WHERE c_user_id = {c_user_id};"
    p_draft = await db.fetch_one(sql)
    if p_draft["isExist"]:
        sql = f"UPDATE p_drafts SET data = '{json.dumps(data, ensure_ascii=False)}' WHERE c_user_id = {c_user_id};"
        await db.execute(sql)
    else:
        id = await db.uuid_short()
        sql = f"INSERT INTO p_drafts (id, c_user_id, data) VALUE ({id}, {c_user_id}, '{json.dumps(data, ensure_ascii=False)}');"
        await db.execute(sql)


async def delete_p_draft_data(db: DB, c_user_id: int):
    sql = f"DELETE FROM p_drafts WHERE c_user_id = {c_user_id};"
    await db.execute(sql)
