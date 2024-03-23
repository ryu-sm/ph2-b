import asyncio
import json
from core.database import DB
import crud
from utils.common import none_to_blank


async def update_messages_for_user(db: DB, c_user_id: int, p_application_header_id: int):
    sql = f"UPDATE c_messages SET p_application_header_id = {p_application_header_id} WHERE c_user_id = {c_user_id}"
    await db.execute(sql)


async def query_messages_for_user(db: DB, c_user_id: int):
    result = []
    p_application_headers = await db.fetch_one(f"SELECT id FROM p_application_headers WHERE c_user_id = {c_user_id};")
    if p_application_headers is None:
        print("with c_user_id")
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
        print("with p_application_header_id")
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


async def insert_message(db: DB, data: dict, sender_type: int, sender_id: int):
    c_user_id = data.get("c_user_id")
    p_application_header_id = data.get("p_application_header_id")
    content = data.get("content")
    viewed = data.get("viewed")

    print(data)
    id = await db.uuid_short()
    sql = f"""
    INSERT INTO c_messages (id, c_user_id, p_application_header_id, sender_type, sender_id, content, viewed)
    VALUES (
        {id}, 
        {c_user_id if c_user_id else 'null'},
        {p_application_header_id if p_application_header_id else 'null'},
        {sender_type},
        {sender_id},
        '{content}',
        '{json.dumps(viewed)}'
    );
    """
    await db.execute(sql)


async def update_messages_viewed(db: DB, messages_ids: list, viewer_id: str):
    JOBS = []

    messages = await db.fetch_all(
        f"SELECT CONVERT(id,CHAR) AS id, viewed FROM c_messages WHERE id IN ({', '.join(messages_ids)});"
    )
    for message in messages:
        message_id = message["id"]
        viewed = json.loads(message["viewed"])
        if viewer_id in viewed:
            continue
        viewed.append(viewer_id)
        sql = f"UPDATE c_messages SET viewed = '{json.dumps(viewed)}' WHERE id = {message_id}"
        JOBS.append(db.execute(sql))
    if JOBS:
        await asyncio.wait(JOBS)


async def query_manager_dashboard_messages(db: DB):
    sql = f"""
    SELECT
        CONVERT(id,CHAR) AS id,
        email as name
    FROM 
        c_users
    WHERE
        agent_sended = 0
    """
    un_agent_sended_users = await db.fetch_all(sql)
    sql = """
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
        p_application_headers.unsubcribed IS NULL
    """
    p_application_headers = await db.fetch_all(sql)

    messages = []

    for user in un_agent_sended_users:
        sql = f"""
        SELECT
            DATE_FORMAT(c_messages.created_at, '%Y/%m/%d %H:%i:%S') as created_at,
            c_messages.content,
            c_messages.viewed
        FROM
            c_messages
        WHERE
            c_messages.c_user_id = {user["id"]}
        ORDER BY created_at DESC;
        """
        result = await db.fetch_one(sql)
        if result is None:
            continue
        messages.append({**result, "viewed": json.loads(result["viewed"]), **user, "type": "0"})

    for p_application_header in p_application_headers:
        sql = f"""
        SELECT
            DATE_FORMAT(c_messages.created_at, '%Y/%m/%d %H:%i:%S') as created_at,
            c_messages.content,
            c_messages.viewed
        FROM
            c_messages
        WHERE
            c_messages.p_application_header_id = {p_application_header["id"]}
        ORDER BY created_at DESC;
        """
        result = await db.fetch_one(sql)
        if result is None:
            continue
        messages.append({**result, "viewed": json.loads(result["viewed"]), **p_application_header, "type": "1"})

    return messages


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


async def query_sales_person_dashboard_messages(db: DB, orgs: list, role_id: int):

    sql = """
    SELECT
        CONVERT(p_application_headers.id,CHAR) AS id,
        CONCAT(p_applicant_persons.last_name_kanji, ' ', p_applicant_persons.first_name_kanji) as name,
        CONVERT(p_application_headers.s_sales_person_id,CHAR) AS s_sales_person_id,
        CONVERT(p_application_headers.sales_area_id,CHAR) AS sales_area_id,
        CONVERT(p_application_headers.sales_exhibition_hall_id,CHAR) AS sales_exhibition_hall_id,
        CONVERT(p_application_headers.sales_company_id,CHAR) AS sales_company_id
    FROM
        p_application_headers
    LEFT JOIN
        p_applicant_persons
        ON
        p_applicant_persons.p_application_header_id = p_application_headers.id
        AND
        p_applicant_persons.type = 0
    WHERE
        p_application_headers.unsubcribed IS NULL
    """
    p_application_headers = await db.fetch_all(sql)
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

    messages = []

    for p_application_header in unique_data:
        sql = f"""
        SELECT
            DATE_FORMAT(c_messages.created_at, '%Y/%m/%d %H:%i:%S') as created_at,
            c_messages.content,
            c_messages.viewed
        FROM
            c_messages
        WHERE
            c_messages.p_application_header_id = {p_application_header["id"]}
        ORDER BY created_at DESC;
        """
        result = await db.fetch_one(sql)
        if result is None:
            continue
        messages.append(
            {
                **result,
                "viewed": json.loads(result["viewed"]),
                "id": p_application_header["id"],
                "name": p_application_header["name"],
                "type": "1",
            }
        )

    return messages
