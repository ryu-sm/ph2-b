import asyncio
import json
from constant import BANK_CODE, TOKEN_ROLE_TYPE
from core.database import DB
import crud
import utils
from utils.common import none_to_blank


async def update_messages_for_user(db: DB, c_user_id: int, p_application_header_id: int):
    sql = f"UPDATE c_messages SET p_application_header_id = {p_application_header_id} WHERE c_user_id = {c_user_id}"
    await db.execute(sql)


async def query_messages_for_user(db: DB, c_user_id: int):
    result = []
    p_application_headers = await db.fetch_one(f"SELECT id FROM p_application_headers WHERE c_user_id = {c_user_id};")
    if p_application_headers is None:
        sql = f"""
        SELECT
            id,
            c_user_id,
            p_application_header_id,
            sender_type,
            sender_id,
            content,
            viewed,
            DATE_FORMAT(created_at, '%Y/%m/%d %H:%i:%S') as created_at
        FROM
            c_messages
        WHERE
            c_user_id = {c_user_id};
        """
        result = await db.fetch_all(sql)
    else:
        sql = f"""
        SELECT
            id,
            c_user_id,
            p_application_header_id,
            sender_type,
            sender_id,
            content,
            viewed,
            DATE_FORMAT(created_at, '%Y/%m/%d %H:%i:%S') as created_at
        FROM
            c_messages
        WHERE
            p_application_header_id = {p_application_headers['id']};
        """
        result = await db.fetch_all(sql)

    return [none_to_blank({**item, "viewed": json.loads(item["viewed"])}) for item in result]


async def insert_message(db: DB, data: dict, role_type, role_id):
    c_user_id = data.get("c_user_id")
    p_application_header_id = data.get("p_application_header_id")
    content = data.get("content")
    viewed = [{"viewed_account_id": role_id, "viewed_account_type": role_type}]

    await db.execute(
        utils.gen_insert_sql(
            "c_messages",
            {
                "id": await db.uuid_short(),
                "c_user_id": c_user_id,
                "p_application_header_id": p_application_header_id,
                "sender_type": role_type,
                "sender_id": role_id,
                "content": content,
                "viewed": json.dumps(viewed),
            },
        )
    )


async def insert_init_message(db: DB, c_user_id, content):
    await db.execute(
        utils.gen_insert_sql(
            "c_messages",
            {
                "id": await db.uuid_short(),
                "c_user_id": c_user_id,
                "sender_type": TOKEN_ROLE_TYPE.MANAGER.value,
                "content": content,
                "viewed": json.dumps(
                    [
                        {"viewed_account_id": None, "viewed_account_type": TOKEN_ROLE_TYPE.MANAGER.value},
                        {"viewed_account_id": None, "viewed_account_type": TOKEN_ROLE_TYPE.SALES_PERSON.value},
                    ]
                ),
            },
        )
    )


async def update_messages_viewed(db: DB, messages_ids: list, role_type, role_id):
    JOBS = []
    messages = await db.fetch_all(
        f"SELECT CONVERT(id,CHAR) AS id, viewed FROM c_messages WHERE id IN ({', '.join(messages_ids)});"
    )
    for message in messages:
        message_id = message["id"]
        viewed = json.loads(message["viewed"])
        if role_type in [item["viewed_account_type"] for item in viewed]:
            continue
        viewed.append({"viewed_account_id": role_id, "viewed_account_type": role_type})
        sql = f"UPDATE c_messages SET viewed = '{json.dumps(viewed)}' WHERE id = {message_id}"
        JOBS.append(db.execute(sql))
    if JOBS:
        await asyncio.wait(JOBS)


async def query_manager_dashboard_messages(db: DB, role_id):
    manager = await db.fetch_one(f"SELECT role FROM s_managers WHERE id = {role_id};")
    p_application_headers_basic = []
    if manager and manager["role"] == 9:
        p_application_headers_basic = await db.fetch_all("SELECT CONVERT(id,CHAR) AS id FROM p_application_headers;")
    if manager and manager["role"] == 1:
        sql = f"""SELECT CONVERT(id,CHAR) AS id FROM p_application_headers WHERE s_manager_id = {role_id};"""
        p_application_headers_basic = await db.fetch_all(sql)

    access_p_application_headers_ids = [item["id"] for item in p_application_headers_basic]
    un_agent_sended_users = await db.fetch_all("SELECT CONVERT(id,CHAR) AS id FROM c_users WHERE agent_sended = 0;")
    un_agent_sended_users_ids = [item["id"] for item in un_agent_sended_users]

    messages = []
    for id in un_agent_sended_users_ids:
        sql = f"""
        SELECT
            CONVERT(c_users.id,CHAR) AS id,
            c_users.email as name,
            DATE_FORMAT(c_messages.created_at, '%Y/%m/%d %H:%i:%S') as created_at,
            c_messages.content,
            c_messages.viewed
        FROM
            c_messages
        JOIN
            c_users
            ON
            c_messages.c_user_id = c_users.id
        WHERE
            c_users.id = {id}
        ORDER BY created_at DESC;
        """
        message = await db.fetch_one(sql)
        if message:
            if TOKEN_ROLE_TYPE.MANAGER.value in [item["viewed_account_type"] for item in json.loads(message["viewed"])]:
                messages.append({**message, "type": "0", "unviewed": "0"})
            else:
                messages.append({**message, "type": "0", "unviewed": "1"})
    for id in access_p_application_headers_ids:
        sql = f"""
        SELECT
            CONVERT(p_application_headers.id,CHAR) AS id,
            CONCAT(p_applicant_persons.last_name_kanji, ' ', p_applicant_persons.first_name_kanji) as name,
            DATE_FORMAT(c_messages.created_at, '%Y/%m/%d %H:%i:%S') as created_at,
            c_messages.content,
            c_messages.viewed
        FROM
            c_messages
        JOIN
            p_application_headers
            ON
            p_application_headers.id = c_messages.p_application_header_id
        JOIN
            p_applicant_persons
            ON
            p_applicant_persons.p_application_header_id = p_application_headers.id
            AND
            p_applicant_persons.type = 0
        WHERE
            c_messages.p_application_header_id  = {id}
        ORDER BY created_at DESC;
        """
        message = await db.fetch_one(sql)
        if message:
            if TOKEN_ROLE_TYPE.MANAGER.value in [item["viewed_account_type"] for item in json.loads(message["viewed"])]:
                messages.append({**message, "type": "1", "unviewed": "0"})
            else:
                messages.append({**message, "type": "1", "unviewed": "1"})
    return list({item["id"]: item for item in messages}.values())


async def query_message(db: DB, id, type):
    basic_sql = f"""
    SELECT
        id,
        c_user_id,
        p_application_header_id,
        sender_type,
        sender_id,
        content,
        viewed,
        DATE_FORMAT(created_at, '%Y/%m/%d %H:%i:%S') as created_at
    FROM
        c_messages
    """

    if type == "0":
        sql = f"{basic_sql} WHERE c_user_id = {id}"
        result = await db.fetch_all(sql)
        sql = f"""
        SELECT
            CONVERT(id,CHAR) AS id,
            email as name
        FROM 
            c_users
        WHERE
            c_users.id = {id}
        """
        applicant = await db.fetch_one(sql)

        return {
            "applicant": {**applicant, "type": type},
            "messages": [none_to_blank({**item, "viewed": json.loads(item["viewed"])}) for item in result],
        }

    if type == "1":
        sql = f"{basic_sql} WHERE p_application_header_id = {id}"
        result = await db.fetch_all(sql)
        sql = f"""
        SELECT
            CONVERT(p_application_headers.id,CHAR) AS id,
            CONCAT(p_applicant_persons.last_name_kanji, ' ', p_applicant_persons.first_name_kanji) as name
        FROM
            p_application_headers
        LEFT JOIN
            p_applicant_persons
            ON
            p_applicant_persons.p_application_header_id = p_application_headers.id
            AND
            p_applicant_persons.type = 0
        WHERE
            p_application_headers.id = {id};
        """
        applicant = await db.fetch_one(sql)
        return {
            "applicant": {**applicant, "type": type},
            "messages": [none_to_blank({**item, "viewed": json.loads(item["viewed"])}) for item in result],
        }


async def delete_message(db: DB, id: int):
    await db.execute(f"DELETE FROM c_messages WHERE id = {id}")


async def query_sales_person_dashboard_messages(db: DB, role_id: int):
    orgs = await crud.query_sales_person_below_orgs(db, role_id)
    ids = []
    for org in orgs:
        if org["role"] == 1:
            sql = f"""
            SELECT
                CONVERT(p_application_headers.id,CHAR) AS id
            FROM
                p_application_headers
            WHERE
                p_application_headers.s_sales_person_id = {role_id}
            """
            p_application_headers_basic = await db.fetch_all(sql)
            ids = ids + [item["id"] for item in p_application_headers_basic]

        if org["role"] == 9:
            access_orgs = await crud.query_child_s_sales_company_orgs(db, org["s_sales_company_org_id"])
            access_orgs_id = [item["id"] for item in access_orgs]
            sql = f"""
            SELECT
                CONVERT(p_application_headers.id,CHAR) AS id
            FROM
                p_application_headers
            WHERE
                p_application_headers.sales_company_id IN ({', '.join(access_orgs_id)})
                OR
                p_application_headers.sales_area_id IN ({', '.join(access_orgs_id)})
                OR
                p_application_headers.sales_exhibition_hall_id IN ({', '.join(access_orgs_id)})
            """
            p_application_headers_basic = await db.fetch_all(sql)
            ids = ids + [item["id"] for item in p_application_headers_basic]

    messages = []
    for id in list(set(ids)):
        sql = f"""
        SELECT
            CONVERT(p_application_headers.id,CHAR) AS id,
            CONCAT(p_applicant_persons.last_name_kanji, ' ', p_applicant_persons.first_name_kanji) as name,
            DATE_FORMAT(c_messages.created_at, '%Y/%m/%d %H:%i:%S') as created_at,
            c_messages.content,
            c_messages.viewed
        FROM
            c_messages
        JOIN
            p_application_headers
            ON
            p_application_headers.id = c_messages.p_application_header_id
        JOIN
            p_applicant_persons
            ON
            p_applicant_persons.p_application_header_id = p_application_headers.id
            AND
            p_applicant_persons.type = 0
        WHERE
            c_messages.p_application_header_id = {id}
        ORDER BY created_at DESC;
        """
        message = await db.fetch_one(sql)
        if message:
            if TOKEN_ROLE_TYPE.SALES_PERSON.value in [
                item["viewed_account_type"] for item in json.loads(message["viewed"])
            ]:
                messages.append({**message, "type": "1", "unviewed": "0"})
            else:
                messages.append({**message, "type": "1", "unviewed": "1"})
    return messages
