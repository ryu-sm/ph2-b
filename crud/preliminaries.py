import json
import crud
from core.database import DB
from utils import none_to_blank
import crud


async def query_manager_access_p_application_headers(db: DB, status: int, role_id: int):
    sbi = await db.fetch_one("SELECT id, name FROM s_banks WHERE code = '0038';")
    sbi_id = sbi["id"]

    basic_sql = f"""
    SELECT
        CONVERT(p_application_headers.id,CHAR) AS id,
        p_application_headers.apply_no,
        DATE_FORMAT(p_application_headers.created_at, '%Y/%m/%d %h:%m:%S') as created_at,
        p_application_headers.pre_examination_status,
        CONVERT(p_application_headers.s_sales_person_id,CHAR) AS s_sales_person_id,
        CONVERT(p_application_headers.s_manager_id,CHAR) AS s_manager_id,
        p_application_headers.sales_company_id,
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
        p_application_banks.s_bank_id = {sbi_id}
    LEFT JOIN
        p_applicant_persons
        ON
        p_applicant_persons.p_application_header_id = p_application_headers.id
        AND
        p_applicant_persons.type = 0
    LEFT JOIN
        p_borrowing_details
        ON
        p_borrowing_details.p_application_header_id = p_application_headers.id
        AND
        p_borrowing_details.time_type = 1
    """
    general_data = await db.fetch_all(f"{basic_sql} WHERE p_application_headers.pair_loan_id is NULL; ")
    pair_data = await db.fetch_all(f"{basic_sql} WHERE p_application_headers.pair_loan_id is NOT NULL; ")
    manager_options = await crud.query_manager_options(db)
    paired_b_ids = []
    paired = []
    for pair_a in pair_data:
        if pair_a["id"] in paired_b_ids:
            continue
        filter = [item for item in pair_data if item["id"] == pair_a["pair_loan_id"]]
        if len(filter) == 0:

            continue
        [pair_b] = filter
        paired_b_ids.append(pair_b["id"])
        sales_company_id = pair_b["sales_company_id"]
        area_options = await crud.query_child_area_options(db, sales_company_id)
        p_application_header_id = pair_b["id"]

        messages = await db.fetch_all(
            f"SELECT CONVERT(id,CHAR) AS id, viewed FROM c_messages WHERE p_application_header_id = {p_application_header_id}"
        )
        unviewed = 0
        for message in messages:
            if role_id in json.loads(message["viewed"]):
                continue
            unviewed += 1
        paired.append(
            none_to_blank(
                {
                    **pair_a,
                    "pair_loan_data": {
                        **none_to_blank(pair_b),
                        "unviewed": unviewed,
                        "area_options": area_options,
                        "manager_options": manager_options,
                    },
                }
            )
        )

    paired_tab_1 = []
    paired_tab_2 = []
    paired_tab_3 = []
    for group in paired:
        if (group["provisional_after_result"] == "" and group["unsubcribed"] == "1") or (
            group["pair_loan_data"]["provisional_after_result"] == "" and group["unsubcribed"] == "1"
        ):

            paired_tab_1.append(group)
        elif group["provisional_after_result"] == "1" and group["pair_loan_data"]["provisional_after_result"] == "1":
            paired_tab_2.append(group)
        else:
            paired_tab_3.append(group)
    result = []

    for item in general_data:
        sales_company_id = item["sales_company_id"]
        area_options = await crud.query_child_area_options(db, sales_company_id)
        p_application_header_id = item["id"]

        messages = await db.fetch_all(
            f"SELECT CONVERT(id,CHAR) AS id, viewed FROM c_messages WHERE p_application_header_id = {p_application_header_id}"
        )
        unviewed = 0
        for message in messages:
            if role_id in json.loads(message["viewed"]):
                continue
            unviewed += 1
        result.append(
            none_to_blank(
                {**item, "unviewed": unviewed, "area_options": area_options, "manager_options": manager_options}
            )
        )

    if status == 1:
        filted = [x for x in result if x["unsubcribed"] == "1" and x["provisional_after_result"] == ""]

        return [*filted, *paired_tab_1]
    if status == 2:
        filted = [x for x in result if x["unsubcribed"] == "1" and x["provisional_after_result"] == "1"]
        return [*filted, *paired_tab_2]
    if status == 3:
        filted = [
            x for x in result if x["unsubcribed"] == "0" or x["provisional_after_result"] in ["0", "2", "3", "4", "5"]
        ]
        return [*filted, *paired_tab_3]


async def query_sales_person_access_p_application_headers(db: DB, status: int, orgs: list, role_id: int):
    p_application_headers = await query_manager_access_p_application_headers(db, status, role_id)
    print(p_application_headers)
    all = []
    for org in orgs:
        if org["role"] == 1:
            role_1_l = list(filter(lambda x: x["s_sales_person_id"] == role_id, p_application_headers))
            all = [*all, *role_1_l]

        if org["role"] == 9:
            role_1_l = list(filter(lambda x: x["s_sales_person_id"] == role_id, p_application_headers))
            all = [*all, *role_1_l]
            s_sales_company_orgs = await crud.query_child_s_sales_company_orgs(
                db, parent_id=org["s_sales_company_org_id"]
            )
            s_sales_company_orgs_id = [[item["id"] for item in s_sales_company_orgs]]
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
    return unique_data


async def update_p_application_headers_s_manager_id(db: DB, p_application_header_id: int, s_manager_id: int):
    await db.execute(
        f"UPDATE p_application_headers SET s_manager_id = {s_manager_id if s_manager_id else 'null'} WHERE id = {p_application_header_id}"
    )


async def update_p_application_headers_s_sales_person_id(db: DB, p_application_header_id: int, s_sales_person_id: int):
    await db.execute(
        f"UPDATE p_application_headers SET s_sales_person_id = {s_sales_person_id if s_sales_person_id else 'null'} WHERE id = {p_application_header_id}"
    )


async def update_p_application_headers_sales_area_id(db: DB, p_application_header_id: int, sales_area_id: int):
    await db.execute(
        f"UPDATE p_application_headers SET sales_area_id = {sales_area_id if sales_area_id else 'null'} WHERE id = {p_application_header_id}"
    )


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
