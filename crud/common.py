import json
from core.database import DB


async def insert_c_access_log(
    db: DB,
    account_id: int,
    ip: str,
    url: str,
    endpoint: str,
    method: str,
    params: dict,
    status_code: int,
    response_body: dict,
):
    id = await db.uuid_short()
    sql = f"""
    INSERT INTO c_access_logs (id, account_id, ip, url, endpoint, method, params, status_code, response_body)
    VALUES ({id}, {account_id if account_id else 'null'}, '{ip}', '{url}', '{endpoint}', '{method}', '{json.dumps(params, ensure_ascii=False)}', {status_code},  '{json.dumps(response_body, ensure_ascii=False)}');
    """

    await db.execute(sql)


async def insert_c_message(
    db: DB,
    c_user_id: int = None,
    p_application_header_id: int = None,
    sender_type: int = None,
    sender_id: int = None,
    content: str = None,
    viewed: list = None,
):
    id = await db.uuid_short()
    sql = f"""
    INSERT INTO c_messages (id, c_user_id, p_application_header_id, sender_type, sender_id, content, viewed)
    VALUES (
        {id},
        {c_user_id or 'null'},
        {p_application_header_id or 'null'},
        {sender_type},
        {sender_id or 'null'},
        '{content}',
        '{json.dumps(viewed) if viewed else json.dumps([]) }'
    )
    """
    await db.execute(sql)
