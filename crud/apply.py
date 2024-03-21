import json
import typing
import base64
import asyncio
from datetime import datetime
from core.database import DB
from constant import JSON_FIELD_KEYS
import crud
from utils import upload_to_s3, download_from_s3, none_to_blank, delete_from_s3
import utils
from copy import deepcopy


async def insert_p_application_headers(
    db: DB, data: dict, origin_data: dict, role_type, role_id, c_user_id="null", s_sales_person_id="null"
):
    sql = f"SELECT MAX(apply_no) no FROM p_application_headers WHERE created_at  >= '{datetime.strftime(datetime.now(),'%Y-%m-%d')} 00:00:00'"
    last_apply = await db.fetch_one(sql)

    new_apply_no = None
    if last_apply["no"] is None:
        new_apply_no = f"SET{datetime.strftime(datetime.now(),'%Y%m%d')}001"
    else:
        new_no = str(int(last_apply["no"][-3:]) + 1).zfill(3)
        new_apply_no = f"SET{datetime.strftime(datetime.now(),'%Y%m%d')}{new_no}"

    p_application_header_id = await db.uuid_short()
    fields = ["id", "c_user_id", "s_sales_person_id", "apply_no", "origin_data"]
    values = [
        f"{p_application_header_id}",
        f"{c_user_id}",
        f"{s_sales_person_id}",
        f"'{new_apply_no}'",
        f"'{json.dumps(origin_data, ensure_ascii=False)}'",
    ]

    for key, value in data.items():
        if value is None:
            continue
        fields.append(key)
        if key in JSON_FIELD_KEYS:
            values.append(f"'{json.dumps(value, ensure_ascii=False)}'")
        else:
            values.append(f"'{value}'")

    sql = f"INSERT INTO p_application_headers ({', '.join(fields)}) VALUES ({', '.join(values)});"
    await db.execute(sql)
    JOBS = []
    ignoreFields = ["id", "c_user_id", "s_sales_person_id", "apply_no", "origin_data"]
    for field, value in zip(fields, values):
        if field in ignoreFields:
            continue
        id = await db.uuid_short()
        sql = f"""
        INSERT INTO p_activities (id, p_application_header_id, operator_type, operator_id, table_name, field_name, table_id, content, operate_type)
        VALUES ({id}, {p_application_header_id}, {role_type}, {role_id}, 'p_application_headers', '{field}', {p_application_header_id}, {value}, 0);
        """
        JOBS.append(db.execute(sql))
    if JOBS:
        await asyncio.wait(JOBS)
    return p_application_header_id


async def insert_p_applicant_persons(db: DB, data: dict, p_application_header_id: int, type: int, role_type, role_id):
    p_applicant_person_id = await db.uuid_short()
    fields = ["id", "p_application_header_id", "type"]
    values = [f"{p_applicant_person_id}", f"{p_application_header_id}", f"{type}"]
    for key, value in data.items():
        if value is None:
            continue
        fields.append(key)
        if key in JSON_FIELD_KEYS:
            values.append(f"'{json.dumps(value, ensure_ascii=False)}'")
        else:
            values.append(f"'{value}'")

    sql = f"INSERT INTO p_applicant_persons ({', '.join(fields)}) VALUES ({', '.join(values)});"
    await db.execute(sql)
    JOBS = []
    ignoreFields = ["id", "p_application_header_id", "type"]
    for field, value in zip(fields, values):
        if field in ignoreFields:
            continue
        id = await db.uuid_short()
        sql = f"""
        INSERT INTO p_activities (id, p_application_header_id, operator_type, operator_id, table_name, field_name, table_id, content, operate_type)
        VALUES ({id}, {p_application_header_id}, {role_type}, {role_id}, 'p_applicant_persons', '{field}', {p_applicant_person_id}, {value}, 0);
        """
        JOBS.append(db.execute(sql))
    if JOBS:
        await asyncio.wait(JOBS)


async def insert_p_borrowing_details(
    db: DB, data: dict, p_application_header_id: int, time_type: int, role_type, role_id
):
    p_borrowing_detail_id = await db.uuid_short()
    fields = ["id", "p_application_header_id", "time_type"]
    values = [f"{p_borrowing_detail_id}", f"{p_application_header_id}", f"{time_type}"]
    for key, value in data.items():
        if value is None:
            continue
        fields.append(key)
        if key in JSON_FIELD_KEYS:
            values.append(f"'{json.dumps(value, ensure_ascii=False)}'")
        else:
            values.append(f"'{value}'")

    sql = f"INSERT INTO p_borrowing_details ({', '.join(fields)}) VALUES ({', '.join(values)});"
    await db.execute(sql)
    JOBS = []
    ignoreFields = ["id", "p_application_header_id", "type"]
    for field, value in zip(fields, values):
        if field in ignoreFields:
            continue
        id = await db.uuid_short()
        sql = f"""
        INSERT INTO p_activities (id, p_application_header_id, operator_type, operator_id, table_name, field_name, table_id, content, operate_type)
        VALUES ({id}, {p_application_header_id}, {role_type}, {role_id}, 'p_borrowing_details', '{field}', {p_borrowing_detail_id}, {value}, 0);
        """
        JOBS.append(db.execute(sql))
    if JOBS:
        await asyncio.wait(JOBS)


async def instert_p_application_banks(db: DB, data: list, p_application_header_id: int):
    for s_bank_id in data:
        id = await db.uuid_short()
        fields = ["id", "p_application_header_id", "s_bank_id"]
        values = [f"{id}", f"{p_application_header_id}", f"{s_bank_id}"]
        sql = f"INSERT INTO p_application_banks ({', '.join(fields)}) VALUES ({', '.join(values)});"
        await db.execute(sql)


async def insert_p_join_guarantors(db: DB, data: typing.List[dict], p_application_header_id: int, role_type, role_id):
    JOBS = []
    for join_guarantor in data:
        p_join_guarantor_id = await db.uuid_short()
        fields = ["id", "p_application_header_id"]
        values = [f"{p_join_guarantor_id}", f"{p_application_header_id}"]

        for key, value in join_guarantor.items():
            if key == "id":
                continue
            if value is None:
                continue
            fields.append(key)
            if key in JSON_FIELD_KEYS:
                values.append(f"'{json.dumps(value, ensure_ascii=False)}'")
            else:
                values.append(f"'{value}'")

        sql = f"INSERT INTO p_join_guarantors ({', '.join(fields)}) VALUES ({', '.join(values)});"
        await db.execute(sql)
        ignoreFields = ["id", "p_application_header_id"]
        for field, value in zip(fields, values):
            if field in ignoreFields:
                continue
            id = await db.uuid_short()
            sql = f"""
            INSERT INTO p_activities (id, p_application_header_id, operator_type, operator_id, table_name, field_name, table_id, content, operate_type)
            VALUES ({id}, {p_application_header_id}, {role_type}, {role_id}, 'p_join_guarantors', '{field}', {p_join_guarantor_id}, {value}, 0);
            """
            JOBS.append(db.execute(sql))
    if JOBS:
        await asyncio.wait(JOBS)


async def insert_p_borrowings(
    db: DB,
    data: typing.List[dict],
    p_application_header_id: int,
    owner_type: int,
    owner_id: int,
):
    JOBS = []
    for borrowing in data:
        p_borrowing_id = await db.uuid_short()
        fields = ["id", "p_application_header_id"]
        values = [f"{p_borrowing_id}", f"{p_application_header_id}"]

        for key, value in borrowing.items():
            if key == "id":
                continue
            if key == "p_borrowings__I" and len(value) == 0:
                continue
            if key == "p_borrowings__I" and len(value) > 0:
                for file in value:
                    p_uploaded_files_id = await db.uuid_short()
                    p_uploaded_files_fields = ["id", "p_application_header_id", "owner_type", "owner_id"]
                    p_uploaded_files_values = [
                        f"{p_uploaded_files_id}",
                        f"{p_application_header_id}",
                        f"{owner_type}",
                        f"{owner_id}",
                    ]
                    s3_key = f"{p_application_header_id}/{key}"
                    file_name = f"{s3_key}/{p_uploaded_files_id}/{file['name']}"
                    file_content = base64.b64decode(file["src"].split(",")[1])

                    upload_to_s3(file_name, file_content)

                    p_uploaded_files_fields.append("s3_key")
                    p_uploaded_files_fields.append("file_name")

                    p_uploaded_files_values.append(f"'{s3_key}'")
                    p_uploaded_files_values.append(f"'{file_name}'")

                    sql = f"INSERT INTO p_uploaded_files ({', '.join(p_uploaded_files_fields)}) VALUES ({', '.join(p_uploaded_files_values)});"

                    await db.execute(sql)
                continue
            if value is None:
                continue
            fields.append(key)
            if key in JSON_FIELD_KEYS:
                values.append(f"'{json.dumps(value, ensure_ascii=False)}'")
            else:
                values.append(f"'{value}'")

        sql = f"INSERT INTO p_borrowings ({', '.join(fields)}) VALUES ({', '.join(values)});"
        await db.execute(sql)
        ignoreFields = ["id", "p_application_header_id", "p_borrowings__I"]
        for field, value in zip(fields, values):
            if field in ignoreFields:
                continue
            id = await db.uuid_short()
            sql = f"""
            INSERT INTO p_activities (id, p_application_header_id, operator_type, operator_id, table_name, field_name, table_id, content, operate_type)
            VALUES ({id}, {p_application_header_id}, {owner_type}, {owner_type}, 'p_borrowings', '{field}', {p_borrowing_id}, {value}, 0);
            """
            JOBS.append(db.execute(sql))

    if JOBS:
        await asyncio.wait(JOBS)


async def insert_p_residents(db: DB, data: typing.List[dict], p_application_header_id: int, role_type, role_id):
    JOBS = []
    for resident in data:
        p_resident_id = await db.uuid_short()
        fields = ["id", "p_application_header_id"]
        values = [f"{p_resident_id}", f"{p_application_header_id}"]

        for key, value in resident.items():
            if key == "id":
                continue

            if value is None:
                continue
            fields.append(key)
            if key in JSON_FIELD_KEYS:
                values.append(f"'{json.dumps(value, ensure_ascii=False)}'")
            else:
                values.append(f"'{value}'")

        sql = f"INSERT INTO p_residents ({', '.join(fields)}) VALUES ({', '.join(values)});"
        await db.execute(sql)
        ignoreFields = ["id", "p_application_header_id"]
        for field, value in zip(fields, values):
            if field in ignoreFields:
                continue
            id = await db.uuid_short()
            sql = f"""
            INSERT INTO p_activities (id, p_application_header_id, operator_type, operator_id, table_name, field_name, table_id, content, operate_type)
            VALUES ({id}, {p_application_header_id}, {role_type}, {role_id}, 'p_residents', '{field}', {p_resident_id}, {value}, 0);
            """
            JOBS.append(db.execute(sql))

    if JOBS:
        await asyncio.wait(JOBS)


async def insert_p_uploaded_files(
    db: DB, data: typing.Dict[str, list], p_application_header_id: int, owner_type: int, owner_id: int
):
    JOBS = []
    for key, value in data.items():

        if len(value) == 0:
            continue

        for file in value:
            p_uploaded_file_id = await db.uuid_short()
            fields = ["id", "p_application_header_id", "owner_type", "owner_id"]
            values = [f"{p_uploaded_file_id}", f"{p_application_header_id}", f"{owner_type}", f"{owner_id}"]
            s3_key = f"{p_application_header_id}/{key}"
            file_name = f"{s3_key}/{file['name']}"
            file_content = base64.b64decode(file["src"].split(",")[1])

            upload_to_s3(file_name, file_content)

            fields.append("s3_key")
            fields.append("file_name")

            values.append(f"'{s3_key}'")
            values.append(f"'{file_name}'")

            sql = f"INSERT INTO p_uploaded_files ({', '.join(fields)}) VALUES ({', '.join(values)});"
            await db.execute(sql)

            if "A" in key:
                id = await db.uuid_short()
                sql = f"""
                INSERT INTO p_activities (id, p_application_header_id, operator_type, operator_id, table_name, field_name, table_id, content, operate_type)
                VALUES ({id}, {p_application_header_id}, {owner_type}, {owner_id}, 'p_uploaded_files', '{key}', {p_uploaded_file_id}, {f"'{file_name}'"}, 0);
                """
                JOBS.append(db.execute(sql))
    if JOBS:
        await asyncio.wait(JOBS)


async def query_p_application_headers_for_ap(db: DB, p_application_header_id):
    sql = f"""
    SELECT
        apply_no,
        DATE_FORMAT(apply_date, '%Y/%m/%d') as apply_date,
        move_scheduled_date,
        loan_target,
        loan_target_type,
        land_advance_plan,
        loan_type,
        pair_loan_last_name,
        pair_loan_first_name,
        pair_loan_rel_name,
        join_guarantor_umu,
        loan_plus,
        curr_house_lived_year,
        curr_house_lived_month,
        curr_house_residence_type,
        curr_house_floor_area,
        curr_house_owner_name,
        curr_house_owner_rel,
        curr_house_schedule_disposal_type,
        curr_house_schedule_disposal_type_other,
        DATE_FORMAT(curr_house_shell_scheduled_date, '%Y/%m/%d') as curr_house_shell_scheduled_date,
        curr_house_shell_scheduled_price,
        curr_house_loan_balance_type,
        property_publish_url,
        new_house_acquire_reason,
        new_house_acquire_reason_other,
        new_house_self_resident,
        new_house_self_not_resident_reason,
        new_house_planned_resident_overview,
        property_business_type,
        property_prefecture,
        property_city,
        property_district,
        property_apartment_and_room_no,
        property_private_area,
        property_total_floor_area,
        property_land_area,
        property_floor_area,
        property_land_type,
        property_purchase_type,
        property_planning_area,
        property_planning_area_other,
        property_rebuilding_reason,
        property_rebuilding_reason_other,
        property_flat_35_plan,
        property_maintenance_type,
        property_flat_35_tech,
        property_region_type,
        curr_borrowing_status,
        refund_source_type,
        refund_source_type_other,
        refund_source_content,
        refund_source_amount,
        rent_to_be_paid_land_borrower,
        rent_to_be_paid_land,
        rent_to_be_paid_house_borrower,
        rent_to_be_paid_house,
        required_funds_land_amount,
        required_funds_house_amount,
        required_funds_accessory_amount,
        required_funds_additional_amount,
        required_funds_refinance_loan_balance,
        required_funds_upgrade_amount,
        required_funds_loan_plus_amount,
        required_funds_total_amount,
        funding_saving_amount,
        funding_estate_sale_amount,
        funding_other_saving_amount,
        funding_relative_donation_amount,
        funding_loan_amount,
        funding_pair_loan_amount,
        funding_other_amount,
        funding_other_amount_detail,
        funding_total_amount,
        sales_company_id,
        sales_area_id,
        sales_exhibition_hall_id,
        vendor_name,
        vendor_phone
    FROM
        p_application_headers
    WHERE
        id = {p_application_header_id};
    """

    result = await db.fetch_one(sql)
    if result is None:
        return None
    temp = {}
    for key, value in result.items():
        if key in JSON_FIELD_KEYS:
            temp[key] = json.loads(value) if value else []
        else:
            temp[key] = value
    return none_to_blank(temp)


async def query_p_borrowing_details_for_ap(db: DB, p_application_header_id: int, time_type: int):
    sql = f"""
    SELECT
        DATE_FORMAT(desired_borrowing_date, '%Y/%m/%d') as desired_borrowing_date,
        desired_loan_amount,
        bonus_repayment_amount,
        bonus_repayment_month,
        loan_term_year,
        repayment_method
    FROM
        p_borrowing_details
    WHERE
        p_application_header_id = {p_application_header_id}
        AND
        time_type = {time_type};
    """
    if time_type == 1:
        return none_to_blank(await db.fetch_one(sql))

    sql = f"""
    SELECT
        DATE_FORMAT(desired_borrowing_date, '%Y/%m/%d') as desired_borrowing_date,
        desired_loan_amount,
        bonus_repayment_amount
    FROM
        p_borrowing_details
    WHERE
        p_application_header_id = {p_application_header_id}
        AND
        time_type = {time_type};
    """
    return none_to_blank(await db.fetch_one(sql))


async def query_p_application_banks_for_ap(db: DB, p_application_header_id: int):
    sql = f"SELECT CONVERT(s_bank_id,CHAR) AS s_bank_id FROM p_application_banks WHERE p_application_header_id={p_application_header_id};"
    result = await db.fetch_all(sql)
    return [item["s_bank_id"] for item in result]


async def query_p_applicant_persons_for_ap(db: DB, p_application_header_id: int, type: int):
    sql = f"""
    SELECT
        rel_to_applicant_a_name,
        last_name_kanji,
        first_name_kanji,
        last_name_kana,
        first_name_kana,
        gender,
        DATE_FORMAT(birthday, '%Y/%m/%d') as birthday,
        nationality,
        mobile_phone,
        home_phone,
        emergency_contact,
        postal_code,
        prefecture_kanji,
        city_kanji,
        district_kanji,
        other_address_kanji,
        prefecture_kana,
        city_kana,
        district_kana,
        other_address_kana,
        email,
        office_occupation,
        office_occupation_other,
        office_industry,
        office_industry_other,
        office_occupation_detail,
        office_occupation_detail_other,
        office_name_kanji,
        office_department,
        office_phone,
        office_postal_code,
        office_prefecture_kanji,
        office_city_kanji,
        office_district_kanji,
        office_other_address_kanji,
        office_prefecture_kana,
        office_city_kana,
        office_district_kana,
        office_employee_num,
        office_joining_date,
        last_year_income,
        last_year_bonus_income,
        income_sources,
        tax_return,
        tax_return_reasons,
        tax_return_reason_other,
        transfer_office,
        transfer_office_name_kanji,
        transfer_office_name_kana,
        transfer_office_phone,
        transfer_office_postal_code,
        transfer_office_prefecture_kanji,
        transfer_office_city_kanji,
        transfer_office_district_kanji,
        transfer_office_other_address_kanji,
        maternity_paternity_leave,
        maternity_paternity_leave_start_date,
        maternity_paternity_leave_end_date,
        nursing_leave,
        identity_verification_type
    FROM
        p_applicant_persons
    WHERE
        p_application_header_id = {p_application_header_id}
        AND
        type = {type};
    """
    result = await db.fetch_one(sql)
    if result is None:
        return None
    temp = {}
    for key, value in result.items():
        if type == 1 and key == "email":
            continue
        if type == 0 and key == "rel_to_applicant_a_name":
            continue
        if key in JSON_FIELD_KEYS:
            temp[key] = json.loads(value) if value else []
        else:
            temp[key] = value
    return none_to_blank(temp)


async def query_p_join_guarantors_for_ap(db: DB, p_application_header_id: int):
    sql = f"""
    SELECT
        CONVERT(id,CHAR) AS id,
        last_name_kanji,
        first_name_kanji,
        last_name_kana,
        first_name_kana,
        gender,
        rel_to_applicant_a_name,
        DATE_FORMAT(birthday, '%Y/%m/%d') as birthday,
        mobile_phone,
        home_phone,
        postal_code,
        prefecture_kanji,
        city_kanji,
        district_kanji,
        other_address_kanji,
        prefecture_kana,
        city_kana,
        district_kana
    FROM
        p_join_guarantors
    WHERE
        p_application_header_id = {p_application_header_id};
    """
    result = await db.fetch_all(sql)

    return [none_to_blank(item) for item in result]


async def query_p_residents_for_ap(db: DB, p_application_header_id: int):
    sql = f"""
    SELECT
        CONVERT(id,CHAR) AS id,
        last_name_kanji,
        first_name_kanji,
        last_name_kana,
        first_name_kana,
        rel_to_applicant_a_name,
        nationality,
        birthday,
        loan_from_japan_house_finance_agency,
        contact_phone,
        postal_code,
        prefecture_kanji,
        city_kanji,
        district_kanji,
        other_address_kanji,
        prefecture_kana,
        city_kana,
        district_kana
    FROM
        p_residents
    WHERE
        p_application_header_id = {p_application_header_id};
    """
    result = await db.fetch_all(sql)

    return [none_to_blank(item) for item in result]


async def query_p_borrowings_for_ap(db: DB, p_application_header_id: int):
    sql = f"""
    SELECT
        CONVERT(id,CHAR) AS id,
        self_input,
        borrower,
        type,
        lender,
        borrowing_from_house_finance_agency,
        loan_start_date,
        loan_amount,
        curr_loan_balance_amount,
        annual_repayment_amount,
        loan_end_date,
        scheduled_loan_payoff,
        scheduled_loan_payoff_date,
        loan_business_target,
        loan_business_target_other,
        loan_purpose,
        loan_purpose_other,
        category,
        card_expiry_date,
        rental_room_num,
        common_housing,
        estate_setting
    FROM
        p_borrowings
    WHERE
        p_application_header_id = {p_application_header_id};
    """
    result = await db.fetch_all(sql)
    temp = []
    for borrowing in result:
        sql = f"""
        SELECT
            file_name
        FROM
            p_uploaded_files
        WHERE
            p_application_header_id = {p_application_header_id}
            AND
            file_name LIKE '%{p_application_header_id}/p_borrowings__I/{borrowing["id"]}%';
        """
        files_info = await db.fetch_all(sql)
        if len(files_info) > 0:
            files = []
            for file in files_info:
                files.append(download_from_s3(file["file_name"]))
            borrowing["p_borrowings__I"] = files
            temp.append(none_to_blank(borrowing))
        else:
            borrowing["p_borrowings__I"] = []
            temp.append(none_to_blank(borrowing))
    return temp


async def query_p_uploaded_files_for_ap(db: DB, p_application_header_id: int):
    temp_files = {
        "p_applicant_persons__0__H__a": [],
        "p_applicant_persons__0__H__b": [],
        "p_applicant_persons__1__H__a": [],
        "p_applicant_persons__1__H__b": [],
        "G": [],
        "p_applicant_persons__0__A__01__a": [],
        "p_applicant_persons__0__A__01__b": [],
        "p_applicant_persons__0__A__02": [],
        "p_applicant_persons__0__A__03__a": [],
        "p_applicant_persons__0__A__03__b": [],
        "p_applicant_persons__0__B__a": [],
        "p_applicant_persons__0__B__b": [],
        "p_applicant_persons__0__C__01": [],
        "p_applicant_persons__0__C__02": [],
        "p_applicant_persons__0__C__03": [],
        "p_applicant_persons__0__C__04": [],
        "p_applicant_persons__0__C__05": [],
        "p_applicant_persons__0__D__01": [],
        "p_applicant_persons__0__D__02": [],
        "p_applicant_persons__0__D__03": [],
        "p_applicant_persons__0__E": [],
        "p_applicant_persons__0__F__01": [],
        "p_applicant_persons__0__F__02": [],
        "p_applicant_persons__0__F__03": [],
        "p_applicant_persons__0__K": [],
        "p_applicant_persons__1__A__01__a": [],
        "p_applicant_persons__1__A__01__b": [],
        "p_applicant_persons__1__A__02": [],
        "p_applicant_persons__1__A__03__a": [],
        "p_applicant_persons__1__A__03__b": [],
        "p_applicant_persons__1__B__a": [],
        "p_applicant_persons__1__B__b": [],
        "p_applicant_persons__1__C__01": [],
        "p_applicant_persons__1__C__02": [],
        "p_applicant_persons__1__C__03": [],
        "p_applicant_persons__1__C__04": [],
        "p_applicant_persons__1__C__05": [],
        "p_applicant_persons__1__D__01": [],
        "p_applicant_persons__1__D__02": [],
        "p_applicant_persons__1__D__03": [],
        "p_applicant_persons__1__E": [],
        "p_applicant_persons__1__F__01": [],
        "p_applicant_persons__1__F__02": [],
        "p_applicant_persons__1__F__03": [],
        "p_applicant_persons__1__K": [],
        "J": [],
        "S": [],
    }

    for file_key in temp_files.keys():
        sql = f"""
        SELECT
            file_name
        FROM
            p_uploaded_files
        WHERE
            p_application_header_id = {p_application_header_id}
            AND
            owner_type = 1
            AND
            file_name LIKE '%{p_application_header_id}/{file_key}%';
        """
        files_info = await db.fetch_all(sql)
        if len(files_info) > 0:
            files = []
            for file in files_info:
                files.append(download_from_s3(file["file_name"]))
            temp_files[file_key] = files

    return temp_files


async def query_p_application_header_id(db: DB, apply_no: str):
    sql = f"""
    SELECT
        CONVERT(id,CHAR) as id
    FROM
        p_application_headers
    WHERE
        apply_no='{apply_no}';
    """

    result = await db.fetch_one(sql)

    return result["id"]


async def query_p_application_header_apply_no(db: DB, p_application_header_id: int):
    sql = f"""
    SELECT
        apply_no
    FROM
        p_application_headers
    WHERE
        id = {p_application_header_id};
    """

    result = await db.fetch_one(sql)

    return result["apply_no"]


async def diff_update_p_application_headers_for_ap(db: DB, data_: dict, p_application_header_id, role_type, role_id):
    JOBS = []
    data = deepcopy(data_)
    if data_.get("loan_type") != "2":
        data["pair_loan_last_name"] = ""
        data["pair_loan_first_name"] = ""
        data["pair_loan_rel_name"] = ""
    old_p_application_headers = await query_p_application_headers_for_ap(db, p_application_header_id)

    for key, value in data.items():
        if key == "join_guarantor_umu" and value != "1":
            sql = f"DELETE FROM p_join_guarantors WHERE p_application_header_id = {p_application_header_id};"
            await db.execute(sql)
        old_value = old_p_application_headers.get(key, "")
        if value == old_value:
            continue
        if key in JSON_FIELD_KEYS:
            temp = json.dumps(value, ensure_ascii=False)
            if temp == old_value:
                continue
        operate_type = 1
        if not value and old_value:
            operate_type = 0
        if value and not old_value:
            operate_type = 2
        content = value
        if key in JSON_FIELD_KEYS:
            content = json.dumps(value, ensure_ascii=False)
        content = f"'{content}'" if content else f"'{old_value}'"
        id = await db.uuid_short()
        sql = f"""
        INSERT INTO p_activities (id, p_application_header_id, operator_type, operator_id, table_name, field_name, table_id, content, operate_type)
        VALUES ({id}, {p_application_header_id}, {role_type}, {role_id}, 'p_application_headers', '{key}', {p_application_header_id}, {content}, {operate_type});
        """
        JOBS.append(db.execute(sql))
        content = value
        if key in JSON_FIELD_KEYS:
            content = json.dumps(value, ensure_ascii=False)
        content = f"'{content}'" if content else "null"
        sql = f"UPDATE p_application_headers SET {key} = {content} WHERE id = {p_application_header_id}"
        JOBS.append(db.execute(sql))
    if JOBS:
        await asyncio.wait(JOBS)


async def diff_update_p_applicant_persons_for_ap(db: DB, data: dict, p_application_header_id, type, role_type, role_id):
    JOBS = []
    p_applicant_persons_basic = await db.fetch_one(
        f"SELECT id FROM p_applicant_persons WHERE p_application_header_id = {p_application_header_id} AND type = {type}"
    )
    if p_applicant_persons_basic is None:
        data_ = utils.blank_to_none(data)
        await insert_p_applicant_persons(db, data_, p_application_header_id, type)
        return None
    p_applicant_persons_id = p_applicant_persons_basic["id"]
    old_p_applicant_persons = await query_p_applicant_persons_for_ap(db, p_application_header_id, type)

    for key, value in data.items():

        old_value = old_p_applicant_persons.get(key, "")

        if value == old_value:
            continue
        if key in JSON_FIELD_KEYS:
            temp = json.dumps(value, ensure_ascii=False)
            if temp == old_value:
                continue

        operate_type = 1
        if not value and old_value:
            operate_type = 0
        if value and not old_value:
            operate_type = 2

        content = value
        if key in JSON_FIELD_KEYS:
            content = json.dumps(value, ensure_ascii=False)

        content = f"'{content}'" if content else f"'{old_value}'"

        id = await db.uuid_short()
        sql = f"""
        INSERT INTO p_activities (id, p_application_header_id, operator_type, operator_id, table_name, field_name, table_id, content, operate_type)
        VALUES ({id}, {p_application_header_id}, {role_type}, {role_id}, 'p_applicant_persons', '{key}', {p_applicant_persons_id}, {content}, {operate_type});
        """
        JOBS.append(db.execute(sql))
        content = value
        if key in JSON_FIELD_KEYS:
            content = json.dumps(value, ensure_ascii=False)
        content = f"'{content}'" if content else "null"
        sql = f"UPDATE p_applicant_persons SET {key} = {content} WHERE id = {p_applicant_persons_id}"
        JOBS.append(db.execute(sql))
    if JOBS:
        await asyncio.wait(JOBS)


async def diff_update_p_borrowing_details_for_ap(
    db: DB, data: dict, p_application_header_id, time_type, role_type, role_id
):
    JOBS = []
    p_borrowing_details_basic = await db.fetch_one(
        f"SELECT id FROM p_borrowing_details WHERE p_application_header_id = {p_application_header_id} AND time_type = {time_type}"
    )
    if p_borrowing_details_basic is None:
        data_ = utils.blank_to_none(data)
        await insert_p_borrowing_details(db, data_, p_application_header_id, time_type)
        return None
    p_borrowing_details_id = p_borrowing_details_basic["id"]
    old_p_borrowing_details = await query_p_borrowing_details_for_ap(db, p_application_header_id, time_type)

    for key, value in data.items():

        old_value = old_p_borrowing_details.get(key, "")

        if value == old_value:
            continue
        if key in JSON_FIELD_KEYS:
            temp = json.dumps(value, ensure_ascii=False)
            if temp == old_value:
                continue

        operate_type = 1
        if not value and old_value:
            operate_type = 0
        if value and not old_value:
            operate_type = 2

        content = value
        if key in JSON_FIELD_KEYS:
            content = json.dumps(value, ensure_ascii=False)

        content = f"'{content}'" if content else f"'{old_value}'"

        id = await db.uuid_short()
        sql = f"""
        INSERT INTO p_activities (id, p_application_header_id, operator_type, operator_id, table_name, field_name, table_id, content, operate_type)
        VALUES ({id}, {p_application_header_id}, {role_type}, {role_id}, 'p_borrowing_details', '{key}', {p_borrowing_details_id}, {content}, {operate_type});
        """
        JOBS.append(db.execute(sql))
        content = value
        if key in JSON_FIELD_KEYS:
            content = json.dumps(value, ensure_ascii=False)
        content = f"'{content}'" if content else "null"
        sql = f"UPDATE p_borrowing_details SET {key} = {content} WHERE id = {p_borrowing_details_id}"
        JOBS.append(db.execute(sql))
    if JOBS:
        await asyncio.wait(JOBS)


async def diff_update_p_application_banks_for_ap(db: DB, data: list, p_application_header_id, role_type, role_id):
    JOBS = []
    old_p_application_banks = await query_p_application_banks_for_ap(db, p_application_header_id)
    for s_bank_id in data:
        if s_bank_id in old_p_application_banks:
            continue

        p_application_banks_id = await db.uuid_short()

        id = await db.uuid_short()
        sql = f"""
        INSERT INTO p_activities (id, p_application_header_id, operator_type, operator_id, table_name, field_name, table_id, content, operate_type)
        VALUES ({id}, {p_application_header_id}, {role_type}, {role_id}, 'p_application_banks', 's_bank_id', {p_application_banks_id}, '{s_bank_id}', 2);
        """
        JOBS.append(db.execute(sql))
        sql = f"INSERT INTO p_application_banks (id, p_application_header_id, s_bank_id) VALUES ({p_application_banks_id}, {p_application_header_id}, {s_bank_id});"
        JOBS.append(db.execute(sql))

    for s_bank_id in old_p_application_banks:
        if s_bank_id in data:
            continue

        p_application_banks_basic = await db.fetch_one(
            f"SELECT id FROM p_application_banks WHERE p_application_header_id = {p_application_header_id} AND s_bank_id = {s_bank_id}"
        )

        p_application_banks_id = p_application_banks_basic["id"]

        id = await db.uuid_short()
        sql = f"""
        INSERT INTO p_activities (id, p_application_header_id, operator_type, operator_id, table_name, field_name, table_id, content, operate_type)
        VALUES ({id}, {p_application_header_id}, {role_type}, {role_id}, 'p_application_banks', null, {p_application_banks_id}, null, 0);
        """
        JOBS.append(db.execute(sql))
        sql = f"DELETE FROM p_application_banks WHERE id = {p_application_banks_id};"
        JOBS.append(db.execute(sql))
    if JOBS:
        await asyncio.wait(JOBS)


async def diff_update_p_join_guarantors_for_ap(
    db: DB, data: typing.List[dict], p_application_header_id, role_type, role_id
):
    JOBS = []
    old_p_join_guarantors = await query_p_join_guarantors_for_ap(db, p_application_header_id)

    for p_join_guarantor in data:
        filter = [item for item in old_p_join_guarantors if item["id"] == p_join_guarantor["id"]]
        if len(filter) == 0:
            data_ = utils.blank_to_none(p_join_guarantor)
            await insert_p_join_guarantors(db, [data_], p_application_header_id)
            return None
        [old_p_join_guarantor] = filter
        for key, value in p_join_guarantor.items():

            old_value = old_p_join_guarantor.get(key, "")

            if value == old_value:
                continue
            if key in JSON_FIELD_KEYS:
                temp = json.dumps(value, ensure_ascii=False)
                if temp == old_value:
                    continue

            operate_type = 1
            if not value and old_value:
                operate_type = 0
            if value and not old_value:
                operate_type = 2

            content = value
            if key in JSON_FIELD_KEYS:
                content = json.dumps(value, ensure_ascii=False)

            content = f"'{content}'" if content else f"'{old_value}'"

            id = await db.uuid_short()
            sql = f"""
            INSERT INTO p_activities (id, p_application_header_id, operator_type, operator_id, table_name, field_name, table_id, content, operate_type)
            VALUES ({id}, {p_application_header_id}, {role_type}, {role_id}, 'p_join_guarantors', '{key}', {old_p_join_guarantor["id"]}, {content}, {operate_type});
            """
            JOBS.append(db.execute(sql))
            content = value
            if key in JSON_FIELD_KEYS:
                content = json.dumps(value, ensure_ascii=False)
            content = f"'{content}'" if content else "null"
            sql = f"UPDATE p_join_guarantors SET {key} = {content} WHERE id = {old_p_join_guarantor['id']}"
            JOBS.append(db.execute(sql))

    for old_p_join_guarantor in old_p_join_guarantors:
        filter = [item for item in data if item["id"] == old_p_join_guarantor["id"]]
        if len(filter) > 0:
            continue
        id = await db.uuid_short()
        sql = f"""
        INSERT INTO p_activities (id, p_application_header_id, operator_type, operator_id, table_name, field_name, table_id, content, operate_type)
        VALUES ({id}, {p_application_header_id}, {role_type}, {role_id}, 'p_join_guarantors', null, {old_p_join_guarantor['id']}, null, 0);
        """
        JOBS.append(db.execute(sql))
        sql = f"DELETE FROM p_join_guarantors WHERE id = {old_p_join_guarantor['id']};"
        JOBS.append(db.execute(sql))
    if JOBS:
        await asyncio.wait(JOBS)


async def diff_update_p_residents_for_ap(db: DB, data: typing.List[dict], p_application_header_id, role_type, role_id):
    JOBS = []
    old_p_residents = await query_p_residents_for_ap(db, p_application_header_id)

    for p_resident in data:
        filter = [item for item in old_p_residents if item["id"] == p_resident["id"]]
        if len(filter) == 0:
            data_ = utils.blank_to_none(p_resident)
            await insert_p_residents(db, [data_], p_application_header_id)
            return None
        [old_p_resident] = filter
        for key, value in old_p_resident.items():

            old_value = old_p_resident.get(key, "")

            if value == old_value:
                continue
            if key in JSON_FIELD_KEYS:
                temp = json.dumps(value, ensure_ascii=False)
                if temp == old_value:
                    continue

            operate_type = 1
            if not value and old_value:
                operate_type = 0
            if value and not old_value:
                operate_type = 2

            content = value
            if key in JSON_FIELD_KEYS:
                content = json.dumps(value, ensure_ascii=False)

            content = f"'{content}'" if content else f"'{old_value}'"

            id = await db.uuid_short()
            sql = f"""
            INSERT INTO p_activities (id, p_application_header_id, operator_type, operator_id, table_name, field_name, table_id, content, operate_type)
            VALUES ({id}, {p_application_header_id}, {role_type}, {role_id}, 'p_residents', '{key}', {old_p_resident["id"]}, {content}, {operate_type});
            """
            JOBS.append(db.execute(sql))
            content = value
            if key in JSON_FIELD_KEYS:
                content = json.dumps(value, ensure_ascii=False)
            content = f"'{content}'" if content else "null"
            sql = f"UPDATE p_residents SET {key} = {content} WHERE id = {old_p_resident['id']}"
            JOBS.append(db.execute(sql))

    for old_p_resident in old_p_residents:
        filter = [item for item in data if item["id"] == old_p_resident["id"]]
        if len(filter) > 0:
            continue
        id = await db.uuid_short()
        sql = f"""
        INSERT INTO p_activities (id, p_application_header_id, operator_type, operator_id, table_name, field_name, table_id, content, operate_type)
        VALUES ({id}, {p_application_header_id}, {role_type}, {role_id}, 'p_residents', null, {old_p_resident['id']}, null, 0);
        """
        JOBS.append(db.execute(sql))
        sql = f"DELETE FROM p_residents WHERE id = {old_p_resident['id']};"
        JOBS.append(db.execute(sql))
    if JOBS:
        await asyncio.wait(JOBS)


async def diff_update_p_borrowings_for_ap(db: DB, data: typing.List[dict], p_application_header_id, role_type, role_id):
    JOBS = []

    old_p_borrowings = await query_p_borrowings_for_ap(db, p_application_header_id)

    for p_borrowing in data:
        filter = [item for item in old_p_borrowings if item["id"] == p_borrowing["id"]]
        if len(filter) == 0:
            data_ = utils.blank_to_none(p_borrowing)
            await insert_p_borrowings(db, [data_], p_application_header_id, role_type, role_id)
            return None
        [old_p_borrowing] = filter
        for key, value in p_borrowing.items():
            if key == "p_borrowings__I" and len(value) > 0:
                files_name = [item["name"] for item in old_p_borrowing["p_borrowings__I"]]

                for file in value:
                    if file["name"] in files_name:
                        continue
                    p_uploaded_files_id = await db.uuid_short()
                    p_uploaded_files_fields = ["id", "p_application_header_id", "owner_type", "owner_id"]
                    p_uploaded_files_values = [
                        f"{p_uploaded_files_id}",
                        f"{p_application_header_id}",
                        f"{role_type}",
                        f"{role_id}",
                    ]
                    s3_key = f"{p_application_header_id}/{key}"
                    file_name = f"{s3_key}/{old_p_borrowing['id']}/{file['name']}"
                    file_content = base64.b64decode(file["src"].split(",")[1])

                    upload_to_s3(file_name, file_content)

                    p_uploaded_files_fields.append("s3_key")
                    p_uploaded_files_fields.append("file_name")

                    p_uploaded_files_values.append(f"'{s3_key}'")
                    p_uploaded_files_values.append(f"'{file_name}'")

                    sql = f"INSERT INTO p_uploaded_files ({', '.join(p_uploaded_files_fields)}) VALUES ({', '.join(p_uploaded_files_values)});"

                    await db.execute(sql)

                new_files_name = [item["name"] for item in value]

                for old_file in old_p_borrowing["p_borrowings__I"]:
                    if old_file["name"] in new_files_name:
                        continue
                    old_s3_key = f"{p_application_header_id}/{key}"
                    old_file_name = f"{old_s3_key}/{old_p_borrowing['id']}/{old_file['name']}"
                    delete_from_s3(old_file_name)
                    sql = f"DELETE FROM p_uploaded_files WHERE file_name = '{old_file_name}';"
                    await db.execute(sql)
                continue

            old_value = old_p_borrowing.get(key, [])

            if value == old_value:
                continue
            if key in JSON_FIELD_KEYS:
                temp = json.dumps(value, ensure_ascii=False)
                if temp == old_value:
                    continue

            operate_type = 1
            if not value and old_value:
                operate_type = 0
            if value and not old_value:
                operate_type = 2

            content = value
            if key in JSON_FIELD_KEYS:
                content = json.dumps(value, ensure_ascii=False)

            content = f"'{content}'" if content else f"'{old_value}'"

            id = await db.uuid_short()
            sql = f"""
            INSERT INTO p_activities (id, p_application_header_id, operator_type, operator_id, table_name, field_name, table_id, content, operate_type)
            VALUES ({id}, {p_application_header_id}, {role_type}, {role_id}, 'p_borrowings', '{key}', {old_p_borrowing["id"]}, {content}, {operate_type});
            """
            JOBS.append(db.execute(sql))
            content = value
            if key in JSON_FIELD_KEYS:
                content = json.dumps(value, ensure_ascii=False)
            content = f"'{content}'" if content else "null"
            sql = f"UPDATE p_borrowings SET {key} = {content} WHERE id = {old_p_borrowing['id']}"
            JOBS.append(db.execute(sql))

    for old_p_borrowing in old_p_borrowings:
        filter = [item for item in data if item["id"] == old_p_borrowing["id"]]
        if len(filter) > 0:
            continue
        id = await db.uuid_short()
        sql = f"""
        INSERT INTO p_activities (id, p_application_header_id, operator_type, operator_id, table_name, field_name, table_id, content, operate_type)
        VALUES ({id}, {p_application_header_id}, {role_type}, {role_id}, 'p_borrowings', null, {old_p_borrowing['id']}, null, 0);
        """
        JOBS.append(db.execute(sql))
        sql = f"DELETE FROM p_borrowings WHERE id = {old_p_borrowing['id']};"
        JOBS.append(db.execute(sql))

    if JOBS:
        await asyncio.wait(JOBS)


async def diff_p_uploaded_files_for_ap(db: DB, data: dict, p_application_header_id, role_type, role_id):
    JOBS = []

    old_p_uploaded_files = await query_p_uploaded_files_for_ap(db, p_application_header_id)

    for key, value in data.items():
        old_value = old_p_uploaded_files.get(key, [])
        if json.dumps(value, ensure_ascii=False) == json.dumps(old_value, ensure_ascii=False):
            continue
        operate_type = 1
        if len(value) == 0 and len(old_value) > 0:
            operate_type = 0
            for old_file in old_value:
                old_s3_key = f"{p_application_header_id}/{key}"
                old_file_name = f"{old_s3_key}/{old_file['name']}"
                delete_from_s3(old_file_name)
                sql = f"DELETE FROM p_uploaded_files WHERE file_name = '{old_file_name}';"
                await db.execute(sql)
        if len(value) > 0 and len(old_value) == 0:
            operate_type = 2
            for file in value:
                p_uploaded_files_id = await db.uuid_short()
                p_uploaded_files_fields = ["id", "p_application_header_id", "owner_type", "owner_id"]
                p_uploaded_files_values = [
                    f"{p_uploaded_files_id}",
                    f"{p_application_header_id}",
                    f"{role_type}",
                    f"{role_id}",
                ]
                s3_key = f"{p_application_header_id}/{key}"
                file_name = f"{s3_key}/{file['name']}"
                file_content = base64.b64decode(file["src"].split(",")[1])
                upload_to_s3(file_name, file_content)
                p_uploaded_files_fields.append("s3_key")
                p_uploaded_files_fields.append("file_name")
                p_uploaded_files_values.append(f"'{s3_key}'")
                p_uploaded_files_values.append(f"'{file_name}'")
                sql = f"INSERT INTO p_uploaded_files ({', '.join(p_uploaded_files_fields)}) VALUES ({', '.join(p_uploaded_files_values)});"
                await db.execute(sql)
        if len(value) > 0 and len(old_value) > 0:
            files_name = [item["name"] for item in old_value]
            for file in value:
                if file["name"] in files_name:
                    continue
                p_uploaded_files_id = await db.uuid_short()
                p_uploaded_files_fields = ["id", "p_application_header_id", "owner_type", "owner_id"]
                p_uploaded_files_values = [
                    f"{p_uploaded_files_id}",
                    f"{p_application_header_id}",
                    f"{role_type}",
                    f"{role_id}",
                ]
                s3_key = f"{p_application_header_id}/{key}"
                file_name = f"{s3_key}/{file['name']}"
                file_content = base64.b64decode(file["src"].split(",")[1])
                upload_to_s3(file_name, file_content)
                p_uploaded_files_fields.append("s3_key")
                p_uploaded_files_fields.append("file_name")
                p_uploaded_files_values.append(f"'{s3_key}'")
                p_uploaded_files_values.append(f"'{file_name}'")
                sql = f"INSERT INTO p_uploaded_files ({', '.join(p_uploaded_files_fields)}) VALUES ({', '.join(p_uploaded_files_values)});"
                await db.execute(sql)
            new_files_name = [item["name"] for item in value]

            for old_file in old_value:
                if old_file["name"] in new_files_name:
                    continue
                print(999)
                old_s3_key = f"{p_application_header_id}/{key}"
                old_file_name = f"{old_s3_key}/{old_file['name']}"
                delete_from_s3(old_file_name)
                sql = f"DELETE FROM p_uploaded_files WHERE file_name = '{old_file_name}';"
                await db.execute(sql)

        id = await db.uuid_short()
        sql = f"""
        INSERT INTO p_activities (id, p_application_header_id, operator_type, operator_id, table_name, field_name, table_id, content, operate_type)
        VALUES ({id}, {p_application_header_id}, {role_type}, {role_id}, 'p_uploaded_files', null, null, '{key}', {operate_type});
        """
        JOBS.append(db.execute(sql))
    if JOBS:
        await asyncio.wait(JOBS)


async def delete_p_borrowings_for_ap(db: DB, p_application_header_id):
    old_p_borrowings = await query_p_borrowings_for_ap(db, p_application_header_id)
    if len(old_p_borrowings) == 0:
        return
    files = await db.fetch_all(
        f"""SELECT file_name FROM p_uploaded_files WHERE s3_key = '{p_application_header_id}/p_borrowings__I' AND owner_type = 1;"""
    )
    for file in files:
        delete_from_s3(file["file_name"])

    sql = f"DELETE FROM p_uploaded_files WHERE s3_key = '{p_application_header_id}/p_borrowings__I' AND owner_type = 1;"

    await db.execute(sql)

    sql = f"""DELETE FROM p_borrowings WHERE p_application_header_id = {p_application_header_id};"""
    await db.execute(sql)


async def delete_p_applicant_persons__1(db: DB, p_application_header_id):
    p_applicant_persons = await query_p_applicant_persons_for_ap(db, p_application_header_id, 1)

    if p_applicant_persons is None:
        return
    p_applicant_persons_id = p_applicant_persons["id"]

    sql = f"DELETE FROM p_applicant_persons WHERE id = {p_applicant_persons_id};"
    await db.execute(sql)
    if p_applicant_persons["nationality"] == "2":
        sql = f"SELECT file_name FROM p_uploaded_files WHERE s3_key = '{p_applicant_persons_id}/p_applicant_persons__1__H__a';"
        p_uploaded_files = await db.fetch_one(sql)
        delete_from_s3(p_uploaded_files["file_name"])
        sql = f"DELETE FROM p_uploaded_files WHERE s3_key = '{p_applicant_persons_id}/p_applicant_persons__1__H__a';"
        await db.execute(sql)
        sql = f"SELECT file_name FROM p_uploaded_files WHERE s3_key = '{p_applicant_persons_id}/p_applicant_persons__1__H__b';"
        p_uploaded_files = await db.fetch_one(sql)
        delete_from_s3(p_uploaded_files["file_name"])
        sql = f"DELETE FROM p_uploaded_files WHERE s3_key = '{p_applicant_persons_id}/p_applicant_persons__1__H__b';"
        await db.execute(sql)


async def delete_p_borrowing_details__1(db: DB, p_application_header_id):
    sql = (
        f"DELETE FROM p_borrowing_details WHERE p_application_header_id = {p_application_header_id} AND time_type = 2;"
    )
    await db.execute(sql)


async def delete_p_join_guarantors(db: DB, p_application_header_id):
    sql = f"DELETE FROM p_join_guarantors WHERE p_application_header_id = {p_application_header_id};"
    await db.execute(sql)
