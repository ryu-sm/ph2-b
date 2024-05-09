import base64
import json
import uuid
from constant import BANK_CODE, TOKEN_ROLE_TYPE
from core.database import DB
import crud
import utils
from utils.common import none_to_blank


async def insert_new_s_sales_person(db: DB, name: str, email: str, hashed_pwd: str, s_sales_company_org_id: int):
    id = await db.uuid_short()
    sql_params = {
        "id": id,
        "email": email,
        "name_kanji": name,
        "hashed_pwd": hashed_pwd,
        "status": 1,
    }
    await db.execute(utils.gen_insert_sql("s_sales_persons", sql_params))

    sql_params = {
        "s_sales_person_id": id,
        "s_sales_company_org_id": s_sales_company_org_id,
        "role": 1,
    }
    await db.execute(utils.gen_insert_sql("s_sales_person_s_sales_company_org_rels", sql_params))

    return id


async def check_s_sales_person_with_email(db: DB, email: str):
    sql = f"SELECT CONVERT(id,CHAR) AS id, code, status, DATE_FORMAT(failed_first_at, '%Y-%m-%d %H:%i:%S') as failed_first_at, failed_time, hashed_pwd FROM s_sales_persons WHERE email = '{email}';"
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
    return await db.fetch_one(
        f"SELECT CONVERT(id,CHAR) AS id, code, email, name_kanji, 2 as role_type FROM s_sales_persons WHERE id = {id};"
    )


async def query_s_sales_person_hashed_pwd(db: DB, id: int):
    sql = f"SELECT hashed_pwd FROM s_sales_persons WHERE id = {id};"
    result = await db.fetch_one(sql)
    return result["hashed_pwd"] if result else None


async def update_s_sales_person_password_with_id(db: DB, id: int, hashed_pwd: str):
    sql = f"UPDATE s_sales_persons SET hashed_pwd = '{hashed_pwd}' WHERE id = {id};"
    await db.execute(sql)


async def query_sales_person_access_p_application_headers(db: DB, status: int, role_id: int):
    sbi = await db.fetch_one(f"SELECT id, name FROM s_banks WHERE code = '{BANK_CODE.SBI.value}';")
    orgs = await crud.query_sales_person_below_orgs(db, role_id)

    access_p_application_headers_id = []
    for org in orgs:
        if org["role"] == 1:
            basic_sql = f"""
            SELECT
                CONVERT(p_application_headers.id,CHAR) AS id
            FROM
                p_application_headers
            JOIN
                p_application_banks
                ON
                p_application_banks.p_application_header_id = p_application_headers.id
                AND
                p_application_banks.s_bank_id = {sbi["id"]}
            WHERE
                (
                    p_application_headers.sales_company_id = {org['s_sales_company_org_id']}
                    OR
                    p_application_headers.sales_area_id = {org['s_sales_company_org_id']}
                    OR
                    p_application_headers.sales_exhibition_hall_id = {org['s_sales_company_org_id']}
                )
                AND
                p_application_headers.s_sales_person_id = {role_id}
            """

            if status == 1:
                sql = f"""
                {basic_sql}
                AND
                p_application_headers.unsubcribed IS NULL
                AND
                p_application_banks.provisional_after_result IS NULL
                """
                p_application_headers_basic = await db.fetch_all(sql)
                access_p_application_headers_id = access_p_application_headers_id + [
                    item["id"] for item in p_application_headers_basic
                ]
                print(2)
            if status == 2:
                sql = f"""
                {basic_sql}
                AND
                p_application_headers.unsubcribed IS NULL
                AND
                p_application_banks.provisional_after_result = 1
                """
                p_application_headers_basic = await db.fetch_all(sql)
                access_p_application_headers_id = access_p_application_headers_id + [
                    item["id"] for item in p_application_headers_basic
                ]
                print(3)
            if status == 3:
                sql = f"""
                {basic_sql}
                AND
                (
                    p_application_headers.unsubcribed = 1
                    OR
                    p_application_banks.provisional_after_result in (0, 2, 3, 4, 5)
                )
                """

                p_application_headers_basic = await db.fetch_all(sql)
                access_p_application_headers_id = access_p_application_headers_id + [
                    item["id"] for item in p_application_headers_basic
                ]
                print(4, sql)

        if org["role"] == 9:
            access_orgs = await crud.query_child_s_sales_company_orgs(db, org["s_sales_company_org_id"])
            access_orgs_id = [item["id"] for item in access_orgs]
            basic_sql = f"""
            SELECT
                CONVERT(p_application_headers.id,CHAR) AS id
            FROM
                p_application_headers
            JOIN
                p_application_banks
                ON
                p_application_banks.p_application_header_id = p_application_headers.id
                AND
                p_application_banks.s_bank_id = {sbi["id"]}
            WHERE
                (
                    p_application_headers.sales_company_id IN ({', '.join(access_orgs_id)})
                    OR
                    p_application_headers.sales_area_id IN ({', '.join(access_orgs_id)})
                    OR
                    p_application_headers.sales_exhibition_hall_id IN ({', '.join(access_orgs_id)})
                )

            """
            if status == 1:
                sql = f"""
                {basic_sql}
                AND
                p_application_headers.unsubcribed IS NULL
                AND
                p_application_banks.provisional_after_result IS NULL
                """
                p_application_headers_basic = await db.fetch_all(sql)
                access_p_application_headers_id = access_p_application_headers_id + [
                    item["id"] for item in p_application_headers_basic
                ]
            if status == 2:
                sql = f"""
                {basic_sql}
                AND
                p_application_headers.unsubcribed IS NULL
                AND
                p_application_banks.provisional_after_result = 1
                """
                p_application_headers_basic = await db.fetch_all(sql)
                access_p_application_headers_id = access_p_application_headers_id + [
                    item["id"] for item in p_application_headers_basic
                ]
            if status == 3:
                sql = f"""
                {basic_sql}
                AND
                (
                    p_application_headers.unsubcribed = 1
                    OR
                    p_application_banks.provisional_after_result in (0, 2, 3, 4, 5)
                )
                """
                p_application_headers_basic = await db.fetch_all(sql)
                access_p_application_headers_id = access_p_application_headers_id + [
                    item["id"] for item in p_application_headers_basic
                ]

    access_p_application_headers_id = list(set(access_p_application_headers_id))
    if len(access_p_application_headers_id) == 0:
        return []
    basic_info_sql = f"""
    SELECT
        CONVERT(p_application_headers.id,CHAR) AS id,
        p_application_headers.apply_no,
        DATE_FORMAT(p_application_headers.created_at, '%Y/%m/%d %H:%i:%S') as created_at,
        p_application_headers.pre_examination_status,
        CONVERT(p_application_headers.s_sales_person_id,CHAR) AS s_sales_person_id,
        CONVERT(p_application_headers.s_manager_id,CHAR) AS s_manager_id,
        CONVERT(p_application_headers.sales_company_id,CHAR) AS sales_company_id,
        CONVERT(p_application_headers.loan_type,CHAR) AS loan_type,
        CONVERT(p_application_headers.pair_loan_id,CHAR) AS pair_loan_id,
        null as pair_loan_data,
        CONVERT(p_application_headers.sales_area_id,CHAR) AS sales_area_id,
        CONVERT(p_application_headers.sales_exhibition_hall_id,CHAR) AS sales_exhibition_hall_id,
        CONCAT(p_applicant_persons.last_name_kanji, ' ', p_applicant_persons.first_name_kanji) as name_kanji,
        DATE_FORMAT(p_borrowing_details.desired_borrowing_date, '%Y/%m/%d') as desired_borrowing_date,
        p_borrowing_details.desired_loan_amount,
        '{sbi["name"]}' as bank_name,
        CONVERT(p_application_banks.s_bank_id,CHAR) AS s_bank_id,
        p_application_banks.provisional_status,
        p_application_banks.provisional_result,
        p_application_banks.provisional_after_result,
        CONVERT(p_application_headers.unsubcribed,CHAR) AS unsubcribed
    FROM
        p_application_headers
    LEFT JOIN
        p_application_banks
        ON
        p_application_banks.p_application_header_id = p_application_headers.id
        AND
        p_application_banks.s_bank_id = {sbi["id"]}
    LEFT JOIN
        p_applicant_persons
        ON
        p_applicant_persons.p_application_header_id = p_application_headers.id
        AND
        p_applicant_persons.type = 0
    LEFT JOIN
        p_borrowing_details
        ON
        p_borrowing_details.p_application_header_id  = p_application_headers.id
        AND
        p_borrowing_details.time_type = 1
    WHERE
        p_application_headers.id IN ({','.join(access_p_application_headers_id)})
    """

    general_result = []
    manager_options = await crud.query_manager_options(db)
    for item in await db.fetch_all(f"{basic_info_sql} AND p_application_headers.pair_loan_id is NULL"):
        p_application_header_id = item["id"]
        messages = await db.fetch_all(
            f"SELECT CONVERT(id,CHAR) AS id, viewed FROM c_messages WHERE p_application_header_id = {p_application_header_id}"
        )
        unviewed = 0
        for message in messages:
            if TOKEN_ROLE_TYPE.SALES_PERSON.value in [
                item["viewed_account_type"] for item in json.loads(message["viewed"])
            ]:
                continue
            else:
                unviewed += 1
        general_result.append(
            none_to_blank(
                {
                    **utils.to_mann(item),
                    "unviewed": unviewed,
                    "manager_options": manager_options,
                }
            )
        )
    paired_b_ids = []
    paired_result = []
    pair_data = await db.fetch_all(f"{basic_info_sql} AND p_application_headers.pair_loan_id is NOT NULL")
    for pair_a in pair_data:
        if pair_a["id"] in paired_b_ids:
            continue
        filter = [item for item in pair_data if item["id"] == pair_a["pair_loan_id"]]
        if len(filter) == 0:
            continue
        [pair_b] = filter
        paired_b_ids.append(pair_b["id"])
        p_application_header_id = pair_b["id"]

        messages = await db.fetch_all(
            f"SELECT CONVERT(id,CHAR) AS id, viewed FROM c_messages WHERE p_application_header_id = {p_application_header_id}"
        )
        unviewed_b = 0
        for message in messages:
            if TOKEN_ROLE_TYPE.SALES_PERSON.value in [
                item["viewed_account_type"] for item in json.loads(message["viewed"])
            ]:
                continue
            unviewed_b += 1

        p_application_header_id = pair_a["id"]

        messages = await db.fetch_all(
            f"SELECT CONVERT(id,CHAR) AS id, viewed FROM c_messages WHERE p_application_header_id = {p_application_header_id}"
        )
        unviewed_a = 0
        for message in messages:
            if TOKEN_ROLE_TYPE.SALES_PERSON.value in [
                item["viewed_account_type"] for item in json.loads(message["viewed"])
            ]:
                continue
            unviewed_a += 1

        paired_result.append(
            none_to_blank(
                {
                    **utils.to_mann(pair_a),
                    "unviewed": unviewed_b,
                    "manager_options": manager_options,
                    "pair_loan_data": {
                        **none_to_blank(utils.to_mann(pair_b)),
                        "unviewed": unviewed_b,
                        "manager_options": manager_options,
                    },
                }
            )
        )
    return list({item["id"]: item for item in [*general_result, *paired_result]}.values())


async def query_sales_person_access_p_application_header_id(db: DB, p_application_header_id: int, role_id: int):
    sbi = await db.fetch_one(f"SELECT id, name FROM s_banks WHERE code = '{BANK_CODE.SBI.value}';")
    orgs = await crud.query_sales_person_below_orgs(db, role_id)

    access_p_application_headers_id = []
    for org in orgs:
        if org["role"] == 1:
            basic_sql = f"""
            SELECT
                CONVERT(p_application_headers.id,CHAR) AS id
            FROM
                p_application_headers
            JOIN
                p_application_banks
                ON
                p_application_banks.p_application_header_id = p_application_headers.id
                AND
                p_application_banks.s_bank_id = {sbi["id"]}
            WHERE
                (
                    p_application_headers.sales_company_id = {org['s_sales_company_org_id']}
                    OR
                    p_application_headers.sales_area_id = {org['s_sales_company_org_id']}
                    OR
                    p_application_headers.sales_exhibition_hall_id = {org['s_sales_company_org_id']}
                )
                AND
                p_application_headers.s_sales_person_id = {role_id}
            """
            p_application_headers_basic = await db.fetch_all(basic_sql)
            access_p_application_headers_id = access_p_application_headers_id + [
                item["id"] for item in p_application_headers_basic
            ]

        if org["role"] == 9:
            access_orgs = await crud.query_child_s_sales_company_orgs(db, org["s_sales_company_org_id"])
            access_orgs_id = [item["id"] for item in access_orgs]
            basic_sql = f"""
            SELECT
                CONVERT(p_application_headers.id,CHAR) AS id
            FROM
                p_application_headers
            JOIN
                p_application_banks
                ON
                p_application_banks.p_application_header_id = p_application_headers.id
                AND
                p_application_banks.s_bank_id = {sbi["id"]}
            WHERE
                (
                    p_application_headers.sales_company_id IN ({', '.join(access_orgs_id)})
                    OR
                    p_application_headers.sales_area_id IN ({', '.join(access_orgs_id)})
                    OR
                    p_application_headers.sales_exhibition_hall_id IN ({', '.join(access_orgs_id)})
                )

            """

            p_application_headers_basic = await db.fetch_all(basic_sql)
            access_p_application_headers_id = access_p_application_headers_id + [
                item["id"] for item in p_application_headers_basic
            ]
    if str(p_application_header_id) in access_p_application_headers_id:
        return {"access": True}
    else:
        return {"access": False}


async def query_sales_person_basic_info(db: DB, s_sales_person_id: int):
    sql = f"""
    SELECT
        CONVERT(id,CHAR) AS id,
        email,
        name_kanji,
        direct_phone,
        mobile_phone,
        fax
    FROM
        s_sales_persons
    WHERE
        id = {s_sales_person_id};
    """
    return await db.fetch_one(sql)


async def query_sales_person_below_orgs(db: DB, s_sales_person_id: int):
    sql = f"""
    SELECT
        CONVERT(s_sales_person_s_sales_company_org_rels.s_sales_company_org_id,CHAR) AS s_sales_company_org_id,
        s_sales_person_s_sales_company_org_rels.role,
        s_sales_company_orgs.category
    FROM
        s_sales_person_s_sales_company_org_rels
    JOIN
        s_sales_company_orgs
        ON
        s_sales_company_orgs.id = s_sales_person_s_sales_company_org_rels.s_sales_company_org_id
    WHERE
        s_sales_person_id = {s_sales_person_id};
    """
    return await db.fetch_all(sql)
