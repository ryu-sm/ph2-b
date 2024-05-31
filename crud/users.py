import json
from core.database import DB
import utils
from constant import USER_STATUS, AGENT_SENDED, UNSUBCRIBED, BANK_CODE


async def check_c_user_with_email(db: DB, email: str):
    return await db.fetch_one(f"SELECT CONVERT(id,CHAR) AS id FROM c_users WHERE email = '{email}';")


async def query_c_user_with_email(db: DB, email: str):
    sql = f"""
    SELECT
        CONVERT(id,CHAR) AS id,
        email,
        CONVERT(s_sales_company_org_id,CHAR) AS s_sales_company_org_id,
        status,
        DATE_FORMAT(failed_first_at, '%Y-%m-%d %H:%i:%S') as failed_first_at,
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
    sql_params = {"id": id, "email": email, "hashed_pwd": hashed_pwd, "s_sales_company_org_id": s_sales_company_org_id}
    await db.execute(utils.gen_insert_sql("c_users", sql_params))
    return id


async def update_c_user_password_with_email(db: DB, email: str, hashed_pwd: str):
    sql_params = {
        "hashed_pwd": hashed_pwd,
        "status": USER_STATUS.NORMAL.value,
        "failed_first_at": None,
        "failed_time": 0,
    }
    sql_where = {"email": email}
    await db.execute(utils.gen_update_sql("c_users", sql_params, sql_where))


async def update_c_user_password_with_id(db: DB, id: int, hashed_pwd: str):
    sql_params = {"hashed_pwd": hashed_pwd, "failed_first_at": None, "failed_time": 0}
    sql_where = {"id": id}
    await db.execute(utils.gen_update_sql("c_users", sql_params, sql_where))


async def update_c_user_failed_first_at(db: DB, id: int, failed_time: int = 1):
    await db.execute(
        f"UPDATE c_users SET failed_first_at = CURRENT_TIMESTAMP, failed_time = {failed_time} WHERE id = {id};"
    )


async def update_c_user_status_locked(db: DB, id: int):
    sql_params = {"status": USER_STATUS.LOCK.value, "failed_time": 0}
    sql_where = {"id": id}
    await db.execute(utils.gen_update_sql("c_users", sql_params, sql_where))


async def update_c_user_failed_time(db: DB, id: int, failed_time: int = 1):
    sql_params = {"failed_time": failed_time}
    sql_where = {"id": id}
    await db.execute(utils.gen_update_sql("c_users", sql_params, sql_where))


async def update_c_user_email(db: DB, id: int, new_email: str):
    sql_params = {"email": new_email}
    sql_where = {"id": id}
    await db.execute(utils.gen_update_sql("c_users", sql_params, sql_where))


async def update_c_user_agent_sended(db: DB, id: int):
    sql_params = {"agent_sended": AGENT_SENDED.SENDED.value}
    sql_where = {"id": id}
    await db.execute(utils.gen_update_sql("c_users", sql_params, sql_where))


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
    sql_params = {"failed_first_at": None, "failed_time": 0}
    sql_where = {"id": id}
    await db.execute(utils.gen_update_sql("c_users", sql_params, sql_where))


async def query_c_user_hashed_pwd(db: DB, id: int):
    sql = f"SELECT hashed_pwd FROM c_users WHERE id = {id};"
    result = await db.fetch_one(sql)

    return result["hashed_pwd"] if result else None


async def delete_c_user(db: DB, id: int):
    sql = f"DELETE FROM p_drafts WHERE c_user_id = {id};"
    await db.execute(sql)
    sql_params = {"c_user_id": None, "unsubcribed": UNSUBCRIBED.UNSUBCRIBED.value}
    sql_where = {"c_user_id": id}
    await db.execute(utils.gen_update_sql("p_application_headers", sql_params, sql_where))
    sql = f"DELETE FROM c_users WHERE id = {id};"
    await db.execute(sql)


async def query_c_user_token_payload(db: DB, c_user_id: int):

    sql = f"""
    SELECT
        CONVERT(c_users.id,CHAR) AS id,
        c_users.email,
        CONVERT(c_users.s_sales_company_org_id,CHAR) AS s_sales_company_org_id,
        c_users.agent_sended,
        p_drafts.id as has_draft,
        s_sales_company_orgs.display_pdf,
        1 as role_type
    FROM
        c_users
    LEFT JOIN
        p_drafts
        ON
        p_drafts.c_user_id = c_users.id
    LEFT JOIN
        s_sales_company_orgs
        ON
        s_sales_company_orgs.id = c_users.s_sales_company_org_id
    WHERE
        c_users.id = {c_user_id};
    """
    result = await db.fetch_one(sql)
    print(sql)
    result["has_draft"] = bool(result["has_draft"])

    return result


async def query_p_draft_data(db: DB, c_user_id: int):
    sql = f"SELECT data FROM p_drafts WHERE c_user_id = {c_user_id};"
    p_draft = await db.fetch_one(sql)
    return json.loads(p_draft["data"])


async def upsert_p_draft_data(db: DB, c_user_id: int, data: dict):
    p_draft = await db.fetch_one(f"SELECT COUNT(id) as isExist FROM p_drafts WHERE c_user_id = {c_user_id};")
    if p_draft["isExist"]:
        sql = f"UPDATE p_drafts SET data = '{json.dumps(data, ensure_ascii=False)}' WHERE c_user_id = {c_user_id};"
        await db.execute(sql)
    else:
        id = await db.uuid_short()
        sql = f"INSERT INTO p_drafts (id, c_user_id, data) VALUE ({id}, {c_user_id}, '{json.dumps(data, ensure_ascii=False)}');"
        await db.execute(sql)


async def delete_p_draft_data(db: DB, c_user_id: int):
    await db.execute(f"DELETE FROM p_drafts WHERE c_user_id = {c_user_id};")


async def check_user_register_s_sales_company_org_id(db: DB, s_sales_company_org_id):
    return await db.fetch_one(f"SELECT id FROM s_sales_company_orgs WHERE id = '{s_sales_company_org_id}';")


async def query_user_s_sales_company_org_id(db: DB, id):
    return await db.fetch_one(
        f"SELECT CONVERT(s_sales_company_org_id,CHAR) AS s_sales_company_org_id FROM c_users WHERE id = {id};"
    )
