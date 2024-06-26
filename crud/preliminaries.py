import crud
from core.database import DB
import utils
from constant import (
    TOKEN_ROLE_TYPE,
    P_APPLICANT_PERSONS_TYPE,
    P_BORROWING_DETAILS_TIME_TYPE,
    LOAN_TYPE,
    LAND_ADVANCE_PLAN,
    JOIN_GUARANTOR_UMU,
    CURR_BORROWING_STATUS,
    OPERATE_TYPE,
)


async def update_p_application_headers_s_manager_id(
    db: DB, p_application_header_id: int, s_manager_id: int, role_type: int, role_id: int
):
    calc_s_manager_id = s_manager_id if s_manager_id else "NULL"
    await db.execute(
        f"UPDATE p_application_headers SET s_manager_id = {calc_s_manager_id} WHERE id = {p_application_header_id}"
    )
    await db.execute(
        utils.gen_insert_sql(
            "p_activities",
            {
                "id": await db.uuid_short(),
                "p_application_header_id": p_application_header_id,
                "operator_type": role_type,
                "operator_id": role_id,
                "table_name": "p_application_headers",
                "field_name": "s_manager_id",
                "table_id": p_application_header_id,
                "content": s_manager_id,
                "operate_type": OPERATE_TYPE.UPDATE.value,
            },
        )
    )


async def update_p_application_headers_s_sales_person_id(db: DB, data: dict, role_type, role_id):
    p_application_header_id = data.get("p_application_header_id")
    s_sales_person_id = data.get("s_sales_person_id")
    if s_sales_person_id:
        await db.execute(
            f"UPDATE p_application_headers SET s_sales_person_id = {s_sales_person_id} WHERE id = {p_application_header_id}"
        )
    else:
        await db.execute(
            f"UPDATE p_application_headers SET s_sales_person_id = NULL WHERE id = {p_application_header_id}"
        )
    await db.execute(
        utils.gen_insert_sql(
            "p_activities",
            {
                "id": await db.uuid_short(),
                "p_application_header_id": p_application_header_id,
                "operator_type": role_type,
                "operator_id": role_id,
                "table_name": "p_application_headers",
                "field_name": "s_sales_person_id",
                "table_id": p_application_header_id,
                "content": s_sales_person_id,
                "operate_type": OPERATE_TYPE.UPDATE.value,
            },
        )
    )


async def update_p_application_headers_sales_area_id(db: DB, data: dict, role_type, role_id):
    initResult = {"sales_exhibition_hall_id": "", "s_sales_person_id": ""}

    p_application_header_id = data.get("p_application_header_id")
    sales_company_id = data.get("sales_company_id")
    sales_area_id = data.get("sales_area_id")
    sales_exhibition_hall_id = data.get("sales_exhibition_hall_id")
    s_sales_person_id = data.get("s_sales_person_id")

    print(data)

    if sales_area_id:
        subUpdate = ""
        subUpdateKeys = []

        sales_exhibition_halls = await crud.query_children_s_sales_company_orgs_with_category(db, sales_area_id, "E")
        if sales_exhibition_hall_id not in [item["value"] for item in sales_exhibition_halls]:
            p = await db.fetch_one(
                f"SELECT sales_exhibition_hall_id FROM p_application_headers WHERE id = {p_application_header_id}"
            )
            if p and p["sales_exhibition_hall_id"]:
                subUpdate += ", sales_exhibition_hall_id = NULL"
                subUpdateKeys.append("sales_exhibition_hall_id")

            orgs_id = sales_area_id or sales_company_id
            s_sales_persons = await crud.query_orgs_access_s_sales_persons(db, orgs_id)
            if s_sales_person_id not in [item["value"] for item in s_sales_persons]:
                p = await db.fetch_one(
                    f"SELECT s_sales_person_id FROM p_application_headers WHERE id = {p_application_header_id}"
                )
                if p and p["s_sales_person_id"]:
                    subUpdate += ", s_sales_person_id = NULL"
                    subUpdateKeys.append("s_sales_person_id")
            else:
                initResult["s_sales_person_id"] = s_sales_person_id

        else:
            initResult["sales_exhibition_hall_id"] = sales_exhibition_hall_id

            orgs_id = sales_exhibition_hall_id or sales_area_id or sales_company_id
            s_sales_persons = await crud.query_orgs_access_s_sales_persons(db, orgs_id)
            if s_sales_person_id not in [item["value"] for item in s_sales_persons]:
                p = await db.fetch_one(
                    f"SELECT s_sales_person_id FROM p_application_headers WHERE id = {p_application_header_id}"
                )
                if p and p["s_sales_person_id"]:
                    subUpdate += ", s_sales_person_id = NULL"
                    subUpdateKeys.append("s_sales_person_id")
            else:
                initResult["s_sales_person_id"] = s_sales_person_id

        await db.execute(
            f"UPDATE p_application_headers SET sales_area_id = {sales_area_id} {subUpdate} WHERE id = {p_application_header_id}"
        )

        id = await db.uuid_short()
        sql = f"""
        INSERT INTO p_activities (id, p_application_header_id, operator_type, operator_id, table_name, field_name, table_id, content, operate_type)
        VALUES ({id}, {p_application_header_id}, {role_type}, {role_id}, 'p_application_headers', 'sales_area_id', {p_application_header_id}, '{sales_area_id}', 2);
        """
        await db.execute(sql)

        for key in subUpdateKeys:
            id = await db.uuid_short()
            sql = f"""
            INSERT INTO p_activities (id, p_application_header_id, operator_type, operator_id, table_name, field_name, table_id, content, operate_type)
            VALUES ({id}, {p_application_header_id}, {role_type}, {role_id}, 'p_application_headers', '{key}', {p_application_header_id}, NULL, 9);
            """
            await db.execute(sql)

    else:
        initResult["sales_exhibition_hall_id"] = sales_exhibition_hall_id
        initResult["s_sales_person_id"] = s_sales_person_id
        await db.execute(f"UPDATE p_application_headers SET sales_area_id = NULL WHERE id = {p_application_header_id}")
        id = await db.uuid_short()
        sql = f"""
        INSERT INTO p_activities (id, p_application_header_id, operator_type, operator_id, table_name, field_name, table_id, content, operate_type)
        VALUES ({id}, {p_application_header_id}, {role_type}, {role_id}, 'p_application_headers', 'sales_area_id', {p_application_header_id}, NULL, 9);
        """
        await db.execute(sql)
    return utils.none_to_blank(initResult)


async def update_p_application_headers_sales_exhibition_hall_id(db: DB, data: dict, role_type, role_id):
    initResult = {"s_sales_person_id": ""}

    p_application_header_id = data.get("p_application_header_id")
    sales_exhibition_hall_id = data.get("sales_exhibition_hall_id")
    s_sales_person_id = data.get("s_sales_person_id")

    if sales_exhibition_hall_id:
        subUpdate = ""
        subUpdateKeys = []
        s_sales_persons = await crud.query_orgs_access_s_sales_persons(db, sales_exhibition_hall_id)
        if s_sales_person_id is not None and s_sales_person_id not in [item["value"] for item in s_sales_persons]:
            p = await db.fetch_one(
                f"SELECT s_sales_person_id FROM p_application_headers WHERE id = {p_application_header_id}"
            )
            if p and p["s_sales_person_id"]:
                subUpdate += ", s_sales_person_id = NULL"
                subUpdateKeys.append("s_sales_person_id")
        else:
            initResult["s_sales_person_id"] = s_sales_person_id

        await db.execute(
            f"UPDATE p_application_headers SET sales_exhibition_hall_id = {sales_exhibition_hall_id} {subUpdate} WHERE id = {p_application_header_id}"
        )
        id = await db.uuid_short()
        sql = f"""
        INSERT INTO p_activities (id, p_application_header_id, operator_type, operator_id, table_name, field_name, table_id, content, operate_type)
        VALUES ({id}, {p_application_header_id}, {role_type}, {role_id}, 'p_application_headers', 'sales_exhibition_hall_id', {p_application_header_id}, '{sales_exhibition_hall_id}', 2);
        """
        await db.execute(sql)

        for key in subUpdateKeys:
            id = await db.uuid_short()
            sql = f"""
            INSERT INTO p_activities (id, p_application_header_id, operator_type, operator_id, table_name, field_name, table_id, content, operate_type)
            VALUES ({id}, {p_application_header_id}, {role_type}, {role_id}, 'p_application_headers', '{key}', {p_application_header_id}, NULL, 9);
            """
            await db.execute(sql)

    else:
        initResult["s_sales_person_id"] = s_sales_person_id
        await db.execute(
            f"UPDATE p_application_headers SET sales_exhibition_hall_id = NULL  WHERE id = {p_application_header_id}"
        )
        id = await db.uuid_short()
        sql = f"""
        INSERT INTO p_activities (id, p_application_header_id, operator_type, operator_id, table_name, field_name, table_id, content, operate_type)
        VALUES ({id}, {p_application_header_id}, {role_type}, {role_id}, 'p_application_headers', 'sales_exhibition_hall_id', {p_application_header_id}, NULL, 9);
        """
        await db.execute(sql)

    return utils.none_to_blank(initResult)


async def delete_pair_laon(db: DB, ids: list, role_type, role_id):
    await db.execute(f"UPDATE p_application_headers SET pair_loan_id = null WHERE id IN ({','.join(ids)});")

    for id in ids:
        await db.execute(
            utils.gen_insert_sql(
                "p_activities",
                {
                    "id": await db.uuid_short(),
                    "p_application_header_id": id,
                    "operator_type": role_type,
                    "operator_id": role_id,
                    "table_name": "p_application_headers",
                    "field_name": "pair_loan_id",
                    "table_id": id,
                    "content": None,
                    "operate_type": OPERATE_TYPE.UPDATE.value,
                },
            )
        )


async def set_pair_loan(db: DB, data: dict, role_type, role_id):
    await db.execute(f"UPDATE p_application_headers SET pair_loan_id = {data['pair_loan_id']} WHERE id = {data['id']};")
    await db.execute(f"UPDATE p_application_headers SET pair_loan_id = {data['id']} WHERE id = {data['pair_loan_id']};")
    await db.execute(
        utils.gen_insert_sql(
            "p_activities",
            {
                "id": await db.uuid_short(),
                "p_application_header_id": data["pair_loan_id"],
                "operator_type": role_type,
                "operator_id": role_id,
                "table_name": "p_application_headers",
                "field_name": "pair_loan_id",
                "table_id": data["pair_loan_id"],
                "content": data["id"],
                "operate_type": OPERATE_TYPE.UPDATE.value,
            },
        )
    )
    await db.execute(
        utils.gen_insert_sql(
            "p_activities",
            {
                "id": await db.uuid_short(),
                "p_application_header_id": data["id"],
                "operator_type": role_type,
                "operator_id": role_id,
                "table_name": "p_application_headers",
                "field_name": "pair_loan_id",
                "table_id": data["id"],
                "content": data["pair_loan_id"],
                "operate_type": OPERATE_TYPE.UPDATE.value,
            },
        )
    )


async def query_memos(db: DB, p_application_header_id):
    sql = f"""
    SELECT
        CONVERT(p_memos.id,CHAR) AS id,
        DATE_FORMAT(p_memos.created_at, '%Y/%m/%d') as created_at,
        s_managers.name_kanji,
        p_memos.content
    FROM
        p_memos
    JOIN
        s_managers
        ON
        s_managers.id = p_memos.s_manager_id
    WHERE
        p_memos.p_application_header_id = {p_application_header_id};
    """
    return await db.fetch_all(sql)


async def insert_memo(db: DB, p_application_header_id: int, s_manager_id: int, content: str):
    id = await db.uuid_short()
    sql = f"INSERT INTO p_memos (id, p_application_header_id, s_manager_id, content) VALUES ({id}, {p_application_header_id}, {s_manager_id}, '{content}');"
    await db.execute(sql)


async def update_memo(db: DB, memo_id: int, content: str):
    sql = f"UPDATE p_memos SET content = '{content}' WHERE id = {memo_id};"
    await db.execute(sql)


async def update_p_application_banks_provisional_after_result(
    db: DB, p_application_header_id: int, s_bank_id: int, provisional_after_result: int, role_type, role_id
):

    p_application_banks = await db.fetch_one(
        f"SELECT id FROM p_application_banks WHERE p_application_header_id = {p_application_header_id} AND s_bank_id = {s_bank_id};"
    )

    sql = f"UPDATE p_application_banks SET provisional_after_result = {provisional_after_result} WHERE id = {p_application_banks['id']};"
    await db.execute(sql)
    await db.execute(
        utils.gen_insert_sql(
            "p_activities",
            {
                "id": await db.uuid_short(),
                "p_application_header_id": p_application_header_id,
                "operator_type": role_type,
                "operator_id": role_id,
                "table_name": "p_application_banks",
                "field_name": "provisional_after_result",
                "table_id": p_application_banks["id"],
                "content": provisional_after_result,
                "operate_type": OPERATE_TYPE.UPDATE.value,
            },
        )
    )
