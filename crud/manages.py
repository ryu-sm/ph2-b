import base64
import json
from core.database import DB
import crud
from utils.common import none_to_blank
from utils.s3 import delete_from_s3, upload_to_s3


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


async def query_manager_access_p_application_headers(db: DB, status: int, role_id: int):
    sbi = await db.fetch_one("SELECT id, name FROM s_banks WHERE code = '0038';")
    sbi_id = sbi["id"]

    basic_sql = f"""
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
        # sales_company_id = pair_b["sales_company_id"]
        # area_options = await crud.query_child_area_options(db, sales_company_id)
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
                        # "area_options": area_options,
                        "manager_options": manager_options,
                    },
                }
            )
        )

    paired_tab_1 = []
    paired_tab_2 = []
    paired_tab_3 = []
    for group in paired:
        # sales_company_id = group["sales_company_id"]
        # area_options = await crud.query_child_area_options(db, sales_company_id)
        p_application_header_id = group["id"]
        messages = await db.fetch_all(
            f"SELECT CONVERT(id,CHAR) AS id, viewed FROM c_messages WHERE p_application_header_id = {p_application_header_id}"
        )
        unviewed = 0
        for message in messages:
            if role_id in json.loads(message["viewed"]):
                continue
            unviewed += 1
        if (group["provisional_after_result"] == "" and group["unsubcribed"] != "1") or (
            group["pair_loan_data"]["provisional_after_result"] == "" and group["unsubcribed"] != "1"
        ):
            paired_tab_1.append(
                {
                    **group,
                    "unviewed": unviewed,
                    # "area_options": area_options,
                    "manager_options": manager_options,
                }
            )
        elif group["provisional_after_result"] == "1" and group["pair_loan_data"]["provisional_after_result"] == "1":
            paired_tab_2.append(
                {
                    **group,
                    "unviewed": unviewed,
                    # "area_options": area_options,
                    "manager_options": manager_options,
                }
            )
        else:
            paired_tab_3.append(
                {
                    **group,
                    "unviewed": unviewed,
                    # "area_options": area_options,
                    "manager_options": manager_options,
                }
            )
    result = []
    for item in general_data:
        # sales_company_id = item["sales_company_id"]
        # area_options = await crud.query_child_area_options(db, sales_company_id)
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
                {
                    **item,
                    "unviewed": unviewed,
                    # "area_options": area_options,
                    "manager_options": manager_options,
                }
            )
        )

    if status == 1:
        filted = [x for x in result if x["unsubcribed"] != "1" and x["provisional_after_result"] == ""]
        return [*filted, *paired_tab_1]
    if status == 2:
        filted = [x for x in result if x["unsubcribed"] != "1" and x["provisional_after_result"] == "1"]
        return [*filted, *paired_tab_2]
    if status == 3:
        filted = [
            x for x in result if x["unsubcribed"] == "1" or x["provisional_after_result"] in ["0", "2", "3", "4", "5"]
        ]
        return [*filted, *paired_tab_3]


async def update_p_application_headers_approver_confirmation(
    db: DB, p_application_header_id: int, approver_confirmation: int
):
    sql = f"UPDATE p_application_headers SET approver_confirmation = {approver_confirmation} WHERE id = {p_application_header_id};"
    await db.execute(sql)


async def update_p_application_banks_pprovisional_result(
    db: DB, p_application_header_id: int, s_bank_id: int, provisional_result: int, R: list, owner_type, owner_id
):
    sql = f"UPDATE p_application_banks SET provisional_result = {provisional_result} WHERE p_application_header_id = {p_application_header_id} AND s_bank_id = {s_bank_id};"
    await db.execute(sql)

    for file in R:
        p_upload_file_id = await db.uuid_short()

        sub_fields = ["id", "p_application_header_id", "owner_type", "owner_id", "record_id", "type"]
        sub_values = [
            f"{p_upload_file_id}",
            f"{p_application_header_id}",
            f"{owner_type}",
            f"{owner_id}",
            f"{p_application_header_id}",
            "0",
        ]

        s3_key = f"{p_application_header_id}/{p_upload_file_id}/R"
        file_name = file["name"]

        sub_fields.append("s3_key")
        sub_fields.append("file_name")
        sub_values.append(f"'{s3_key}'")
        sub_values.append(f"'{file_name}'")

        file_content = base64.b64decode(file["src"].split(",")[1])

        upload_to_s3(f"{s3_key}/{file_name}", file_content)

        sql = f"INSERT INTO p_uploaded_files ({', '.join(sub_fields)}) VALUES ({', '.join(sub_values)});"
        await db.execute(sql)
        p_activities_id = await db.uuid_short()
        sql = f"""
        INSERT INTO p_activities (id, p_application_header_id, operator_type, operator_id, table_name, field_name, table_id, content, operate_type)
        VALUES ({p_activities_id}, {p_application_header_id}, {owner_type}, {owner_id}, 'p_application_headers', 'R', {p_application_header_id}, '{file["name"]}', 1);
        """
        await db.execute(sql)


async def update_p_application_headers_pre_examination_status(
    db: DB, p_application_header_id: int, pre_examination_status: int
):
    sql = f"UPDATE p_application_headers SET pre_examination_status = {pre_examination_status} WHERE id = {p_application_header_id};"
    await db.execute(sql)


async def delete_p_application_banks_pprovisional_result(
    db: DB, p_application_header_id: int, s_bank_id: int, p_upload_file_id: int
):
    await db.execute(f"UPDATE p_uploaded_files SET deleted = 1 WHERE id = {p_upload_file_id};")

    sql = f"""
    UPDATE p_application_headers
    SET
        pre_examination_status = 4,
        approver_confirmation = NULL
    WHERE
        id = {p_application_header_id};
    """
    await db.execute(sql)

    sql = f"""
    UPDATE p_application_banks
    SET
        provisional_result = NULL
    WHERE
        p_application_header_id = {p_application_header_id}
        AND
        s_bank_id = {s_bank_id};
    """
    await db.execute(sql)
