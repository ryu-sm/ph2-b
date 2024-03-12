import crud
from core.database import DB


async def update_p_application_headers_s_manager_id(db: DB, p_application_header_id: int, s_manager_id: int):
    await db.execute(
        f"UPDATE p_application_headers SET s_manager_id = {s_manager_id if s_manager_id else 'null'} WHERE id = {p_application_header_id}"
    )


async def update_p_application_headers_s_sales_person_id(db: DB, p_application_header_id: int, s_sales_person_id: int):
    await db.execute(
        f"UPDATE p_application_headers SET s_sales_person_id = {s_sales_person_id if s_sales_person_id else 'null'} WHERE id = {p_application_header_id}"
    )


async def update_p_application_headers_sales_area_id(
    db: DB, p_application_header_id: int, sales_area_id: int, sales_exhibition_hall_id: int
):
    sales_exhibition_halls = await crud.query_child_exhibition_hall_options(db, sales_area_id)
    subUpdate = ""
    if sales_exhibition_hall_id not in [item["value"] for item in sales_exhibition_halls]:
        subUpdate = ", sales_exhibition_hall_id = NULL"
    await db.execute(
        f"UPDATE p_application_headers SET sales_area_id = {sales_area_id if sales_area_id else 'null'} {subUpdate}  WHERE id = {p_application_header_id}"
    )

    return {"sales_exhibition_hall_id": sales_exhibition_hall_id if not subUpdate else subUpdate}


async def update_p_application_headers_sales_exhibition_hall_id(
    db: DB, p_application_header_id: int, sales_exhibition_hall_id: int, s_sales_person_id: int
):
    sales_persons = await crud.query_sales_person_options(db, sales_exhibition_hall_id)
    subUpdate = ""
    if s_sales_person_id not in [item["value"] for item in sales_persons]:
        subUpdate = ", s_sales_person_id = NULL"
    await db.execute(
        f"UPDATE p_application_headers SET sales_exhibition_hall_id = {sales_exhibition_hall_id if sales_exhibition_hall_id else 'null'} {subUpdate}  WHERE id = {p_application_header_id}"
    )

    return {"s_sales_person_id": s_sales_person_id if not subUpdate else subUpdate}


async def delete_pair_laon(db: DB, ids: list):
    await db.execute(f"UPDATE p_application_headers SET pair_loan_id = null WHERE id IN ({','.join(ids)});")


async def set_pair_loan(db: DB, data: dict):
    await db.execute(f"UPDATE p_application_headers SET pair_loan_id = {data['pair_loan_id']} WHERE id = {data['id']};")
    await db.execute(f"UPDATE p_application_headers SET pair_loan_id = {data['id']} WHERE id = {data['pair_loan_id']};")


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
    db: DB, p_application_header_id: int, s_bank_id: int, provisional_after_result: int
):
    sql = f"UPDATE p_application_banks SET provisional_after_result = {provisional_after_result} WHERE p_application_header_id = {p_application_header_id} AND s_bank_id = {s_bank_id};"
    await db.execute(sql)
