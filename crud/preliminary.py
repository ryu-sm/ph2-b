import asyncio
import base64
from copy import deepcopy
import json
import typing
import crud
from core.database import DB
from constant import JSON_FIELD_KEYS
from utils import none_to_blank
import crud
from utils.common import blank_to_none
from utils.s3 import delete_from_s3, download_from_s3, upload_to_s3


async def query_p_application_headers_for_ad(db: DB, p_application_header_id):
    sbi = await db.fetch_one("SELECT id, name FROM s_banks WHERE code = '0038';")
    sbi_id = sbi["id"]
    sql = f"""
    SELECT
        CONVERT(p_application_headers.id,CHAR) AS id,
        p_application_headers.apply_no,
        DATE_FORMAT(p_application_headers.created_at, '%Y/%m/%d %H:%i') as created_at,
        DATE_FORMAT(p_application_headers.apply_date, '%Y/%m/%d') as apply_date,
        p_application_headers.move_scheduled_date,
        p_application_headers.loan_target,
        p_application_headers.loan_target_type,
        p_application_headers.land_advance_plan,
        p_application_headers.loan_type,
        p_application_headers.pair_loan_id,
        p_application_headers.pair_loan_last_name,
        p_application_headers.pair_loan_first_name,
        p_application_headers.pair_loan_rel_name,
        p_application_headers.pair_loan_rel,
        p_application_headers.join_guarantor_umu,
        p_application_headers.loan_plus,
        p_application_headers.curr_house_lived_year,
        p_application_headers.curr_house_lived_month,
        p_application_headers.curr_house_residence_type,
        p_application_headers.curr_house_floor_area,
        p_application_headers.curr_house_owner_name,
        p_application_headers.curr_house_owner_rel,
        p_application_headers.curr_house_schedule_disposal_type,
        p_application_headers.curr_house_schedule_disposal_type_other,
        p_application_headers.curr_house_shell_scheduled_date,
        p_application_headers.curr_house_shell_scheduled_price,
        p_application_headers.curr_house_loan_balance_type,
        p_application_headers.property_publish_url,
        p_application_headers.new_house_acquire_reason,
        p_application_headers.new_house_acquire_reason_other,
        p_application_headers.new_house_self_resident,
        p_application_headers.new_house_self_not_resident_reason,
        p_application_headers.new_house_planned_resident_overview,
        p_application_headers.property_business_type,
        p_application_headers.property_postal_code,
        p_application_headers.property_prefecture,
        p_application_headers.property_city,
        p_application_headers.property_district,
        p_application_headers.property_apartment_and_room_no,
        p_application_headers.property_address_kana,
        p_application_headers.property_private_area,
        p_application_headers.property_total_floor_area,
        p_application_headers.property_land_area,
        p_application_headers.property_floor_area,
        p_application_headers.property_land_type,
        p_application_headers.property_type,
        DATE_FORMAT(p_application_headers.property_land_acquire_date, '%Y/%m/%d') as property_land_acquire_date,
        p_application_headers.property_joint_ownership_type,
        p_application_headers.property_building_ratio_numerator,
        p_application_headers.property_building_ratio_denominator,
        p_application_headers.property_land_ratio_numerator,
        p_application_headers.property_land_ratio_denominator,
        p_application_headers.property_purchase_type,
        p_application_headers.property_planning_area,
        p_application_headers.property_planning_area_other,
        p_application_headers.property_rebuilding_reason,
        p_application_headers.property_rebuilding_reason_other,
        p_application_headers.property_flat_35_plan,
        p_application_headers.property_maintenance_type,
        p_application_headers.property_flat_35_tech,
        p_application_headers.property_region_type,
        p_application_headers.curr_borrowing_status,
        p_application_headers.refund_source_type,
        p_application_headers.refund_source_type_other,
        p_application_headers.refund_source_content,
        p_application_headers.refund_source_amount,
        p_application_headers.rent_to_be_paid_land_borrower,
        p_application_headers.rent_to_be_paid_land,
        p_application_headers.rent_to_be_paid_house_borrower,
        p_application_headers.rent_to_be_paid_house,
        p_application_headers.required_funds_land_amount,
        p_application_headers.required_funds_house_amount,
        p_application_headers.required_funds_accessory_amount,
        p_application_headers.required_funds_additional_amount,
        p_application_headers.required_funds_refinance_loan_balance,
        p_application_headers.required_funds_upgrade_amount,
        p_application_headers.required_funds_loan_plus_amount,
        p_application_headers.required_funds_total_amount,
        p_application_headers.funding_saving_amount,
        p_application_headers.funding_estate_sale_amount,
        p_application_headers.funding_other_saving_amount,
        p_application_headers.funding_relative_donation_amount,
        p_application_headers.funding_loan_amount,
        p_application_headers.funding_pair_loan_amount,
        p_application_headers.funding_other_amount,
        p_application_headers.funding_other_amount_detail,
        p_application_headers.funding_total_amount,
        p_application_headers.sales_company_id,
        p_application_headers.sales_area_id,
        p_application_headers.sales_exhibition_hall_id,
        p_application_headers.s_sales_person_id,
        p_application_headers.vendor_name,
        p_application_headers.vendor_phone,
        p_application_headers.pre_examination_status,
        p_application_banks.provisional_status,
        p_application_banks.provisional_result,
        p_application_banks.provisional_after_result,
        p_application_headers.funding_self_amount,
        p_application_headers.property_building_price,
        p_application_headers.property_land_price,
        p_application_headers.property_total_price,
        p_application_headers.funding_other_refinance_amount,
        p_application_headers.funding_other_loan_amount,
        p_application_headers.unsubcribed
    FROM
        p_application_headers
    LEFT JOIN
        p_application_banks
        ON
        p_application_banks.p_application_header_id = p_application_headers.id
        AND
        p_application_banks.s_bank_id = {sbi_id}
    WHERE
        p_application_headers.id = {p_application_header_id};
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


async def query_p_borrowing_details_for_ad(db: DB, p_application_header_id: int, time_type: int):
    sql = f"""
    SELECT
        CONVERT(id,CHAR) AS id,
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
        CONVERT(id,CHAR) AS id,
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


async def query_p_application_banks_for_ad(db: DB, p_application_header_id: int):
    sql = f"SELECT CONVERT(s_bank_id,CHAR) AS s_bank_id FROM p_application_banks WHERE p_application_header_id={p_application_header_id};"
    result = await db.fetch_all(sql)
    return [item["s_bank_id"] for item in result]


async def query_p_applicant_persons_for_ad(db: DB, p_application_header_id: int, type: int):
    sql = f"""
    SELECT
        CONVERT(id,CHAR) AS id,
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
        office_other_address_kana,
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
        identity_verification_type,
        office_employment_type,
        office_name_kana,
        office_role,
        office_head_location,
        office_listed_division,
        office_establishment_date,
        office_capital_stock,
        main_income_source,
        before_last_year_income
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
        if type == 0 and key == "rel_to_applicant_a_name":
            continue
        if key in JSON_FIELD_KEYS:
            temp[key] = json.loads(value) if value else []
        else:
            temp[key] = value
    return none_to_blank(temp)


async def query_p_join_guarantors_for_ad(db: DB, p_application_header_id: int):
    sql = f"""
    SELECT
        CONVERT(id,CHAR) AS id,
        last_name_kanji,
        first_name_kanji,
        last_name_kana,
        first_name_kana,
        gender,
        rel_to_applicant_a_name,
        rel_to_applicant_a,
        rel_to_applicant_a_other,
        DATE_FORMAT(birthday, '%Y/%m/%d') as birthday,
        mobile_phone,
        home_phone,
        emergency_contact,
        email,
        postal_code,
        prefecture_kanji,
        city_kanji,
        district_kanji,
        other_address_kanji,
        prefecture_kana,
        city_kana,
        district_kana,
        other_address_kana
    FROM
        p_join_guarantors
    WHERE
        p_application_header_id = {p_application_header_id};
    """
    result = await db.fetch_all(sql)

    return [none_to_blank(item) for item in result]


async def query_p_residents_for_ad(db: DB, p_application_header_id: int):
    sql = f"""
    SELECT
        CONVERT(id,CHAR) AS id,
        last_name_kanji,
        first_name_kanji,
        last_name_kana,
        first_name_kana,
        rel_to_applicant_a_name,
        rel_to_applicant_a,
        rel_to_applicant_a_other,
        DATE_FORMAT(birthday, '%Y/%m/%d') as birthday,
        gender,
        one_roof,
        loan_from_japan_house_finance_agency,
        contact_phone,
        postal_code,
        prefecture_kanji,
        city_kanji,
        district_kanji,
        other_address_kanji,
        prefecture_kana,
        city_kana,
        district_kana,
        nationality
    FROM
        p_residents
    WHERE
        p_application_header_id = {p_application_header_id};
    """
    result = await db.fetch_all(sql)

    return [none_to_blank(item) for item in result]


async def query_p_borrowings_for_ad(db: DB, p_application_header_id: int):
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
        estate_setting,
        include_in_examination
    FROM
        p_borrowings
    WHERE
        p_application_header_id = {p_application_header_id};
    """
    basic_p_borrowings = await db.fetch_all(sql)
    p_borrowings_with_files = []

    for basic_p_borrowing in basic_p_borrowings:
        sql = f"""
        SELECT
            CONVERT(p_uploaded_files.id,CHAR) AS id,
            p_uploaded_files.file_name,
            p_uploaded_files.owner_type
        FROM
            p_uploaded_files
        WHERE
            p_uploaded_files.p_application_header_id = {p_application_header_id}
            AND
            p_uploaded_files.file_name LIKE '%{p_application_header_id}/p_borrowings__I/{basic_p_borrowing["id"]}%';
        """
        p_borrowing_files_info = await db.fetch_all(sql)
        if len(p_borrowing_files_info) == 0:
            p_borrowings_with_files.append(none_to_blank({**basic_p_borrowing, "p_borrowings__I": []}))
        else:
            files = []
            for file in p_borrowing_files_info:
                files.append(
                    {**download_from_s3(file["file_name"]), "id": file["id"], "owner_type": f'{file["owner_type"]}'}
                )
            p_borrowings_with_files.append(none_to_blank({**basic_p_borrowing, "p_borrowings__I": files}))
    return p_borrowings_with_files


async def query_p_uploaded_files_for_ad(db: DB, p_application_header_id: int):
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
        "R": [],
    }

    for file_key in temp_files.keys():
        sql = f"""
        SELECT
            CONVERT(p_uploaded_files.id,CHAR) AS id,
            p_uploaded_files.file_name,
            p_uploaded_files.owner_type
        FROM
            p_uploaded_files
        WHERE
            p_uploaded_files.p_application_header_id = {p_application_header_id}
            AND
            p_uploaded_files.s3_key = '{p_application_header_id}/{file_key}';
        """
        files_info = await db.fetch_all(sql)
        if len(files_info) > 0:
            files = []
            for file in files_info:
                files.append(
                    {**download_from_s3(file["file_name"]), "id": file["id"], "owner_type": f'{file["owner_type"]}'}
                )
            temp_files[file_key] = files

    return temp_files


async def diff_update_p_application_headers_for_ad(db: DB, data_: dict, p_application_header_id, role_type, role_id):
    JOBS = []
    data = deepcopy(data_)
    if data_.get("loan_type") != "2":
        data["pair_loan_last_name"] = ""
        data["pair_loan_first_name"] = ""
        data["pair_loan_rel_name"] = ""
    old_p_application_headers = await query_p_application_headers_for_ad(db, p_application_header_id)

    for key, value in data.items():
        if key == "created_at":
            continue
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
            operate_type = 9
        if value and not old_value:
            operate_type = 2
        content = value
        if key in JSON_FIELD_KEYS:
            content = json.dumps(value, ensure_ascii=False)
        content = f"'{content}'" if content else "null"
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


async def diff_update_p_applicant_persons_for_ad(db: DB, data: dict, p_application_header_id, type, role_type, role_id):
    JOBS = []
    p_applicant_persons_basic = await db.fetch_one(
        f"SELECT id FROM p_applicant_persons WHERE p_application_header_id = {p_application_header_id} AND type = {type}"
    )
    if p_applicant_persons_basic is None:
        data_ = blank_to_none(data)
        await crud.insert_p_applicant_persons(db, data_, p_application_header_id, type, role_type, role_id)
        return None
    p_applicant_persons_id = p_applicant_persons_basic["id"]
    old_p_applicant_persons = await query_p_applicant_persons_for_ad(db, p_application_header_id, type)

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
            operate_type = 9
        if value and not old_value:
            operate_type = 2

        content = value
        if key in JSON_FIELD_KEYS:
            content = json.dumps(value, ensure_ascii=False)

        content = f"'{content}'" if content else "null"

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


async def diff_update_p_borrowing_details_for_ad(
    db: DB, data: dict, p_application_header_id, time_type, role_type, role_id
):
    JOBS = []
    p_borrowing_details_basic = await db.fetch_one(
        f"SELECT id FROM p_borrowing_details WHERE p_application_header_id = {p_application_header_id} AND time_type = {time_type}"
    )
    if p_borrowing_details_basic is None:
        data_ = blank_to_none(data)
        await crud.insert_p_borrowing_details(db, data_, p_application_header_id, time_type, role_type, role_id)
        return None
    p_borrowing_details_id = p_borrowing_details_basic["id"]
    old_p_borrowing_details = await query_p_borrowing_details_for_ad(db, p_application_header_id, time_type)

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
            operate_type = 9
        if value and not old_value:
            operate_type = 2

        content = value
        if key in JSON_FIELD_KEYS:
            content = json.dumps(value, ensure_ascii=False)

        content = f"'{content}'" if content else "null"

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


async def diff_update_p_application_banks_for_ad(db: DB, data: list, p_application_header_id, role_type, role_id):
    JOBS = []
    old_p_application_banks = await query_p_application_banks_for_ad(db, p_application_header_id)
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


async def diff_update_p_join_guarantors_for_ad(
    db: DB, data: typing.List[dict], p_application_header_id, role_type, role_id
):
    JOBS = []
    old_p_join_guarantors = await query_p_join_guarantors_for_ad(db, p_application_header_id)

    for p_join_guarantor in data:
        filter = [item for item in old_p_join_guarantors if item["id"] == p_join_guarantor["id"]]
        if len(filter) == 0:
            data_ = blank_to_none(p_join_guarantor)
            await crud.insert_p_join_guarantors(db, [data_], p_application_header_id)
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
                operate_type = 9
            if value and not old_value:
                operate_type = 2

            content = value
            if key in JSON_FIELD_KEYS:
                content = json.dumps(value, ensure_ascii=False)

            content = f"'{content}'" if content else "null"

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


async def diff_update_p_residents_for_ad(db: DB, data: typing.List[dict], p_application_header_id, role_type, role_id):
    JOBS = []
    old_p_residents = await query_p_residents_for_ad(db, p_application_header_id)

    for p_resident in data:
        filter = [item for item in old_p_residents if item["id"] == p_resident["id"]]
        if len(filter) == 0:
            data_ = blank_to_none(p_resident)
            await crud.insert_p_residents(db, [data_], p_application_header_id, role_type, role_id)
            return None
        [old_p_resident] = filter

        for key, value in p_resident.items():

            old_value = old_p_resident.get(key, "")

            if value == old_value:
                continue
            if key in JSON_FIELD_KEYS:
                temp = json.dumps(value, ensure_ascii=False)
                if temp == old_value:
                    continue

            operate_type = 1
            if not value and old_value:
                operate_type = 9
            if value and not old_value:
                operate_type = 2

            content = value
            if key in JSON_FIELD_KEYS:
                content = json.dumps(value, ensure_ascii=False)

            content = f"'{content}'" if content else "null"

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


async def diff_update_p_borrowings_for_ad(db: DB, data: typing.List[dict], p_application_header_id, role_type, role_id):
    JOBS = []

    old_p_borrowings = await query_p_borrowings_for_ad(db, p_application_header_id)

    for p_borrowing in data:
        filter = [item for item in old_p_borrowings if item["id"] == p_borrowing["id"]]
        if len(filter) == 0:
            data_ = blank_to_none(p_borrowing)
            await crud.insert_p_borrowings(db, [data_], p_application_header_id, role_type, role_id)
            return None
        [old_p_borrowing] = filter
        for key, value in p_borrowing.items():
            old_value = old_p_borrowing.get(key, [])

            if value == old_value:
                continue
            if key in JSON_FIELD_KEYS:
                temp = json.dumps(value, ensure_ascii=False)
                if temp == old_value:
                    continue

            operate_type = 1
            if not value and old_value:
                operate_type = 9
            if value and not old_value:
                operate_type = 2

            content = value
            if key in JSON_FIELD_KEYS:
                content = json.dumps(value, ensure_ascii=False)

            content = f"'{content}'" if content else "null"

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


async def diff_update_p_borrowings_files_for_ad(
    db: DB, data: typing.List[dict], p_application_header_id, role_type, role_id
):
    for p_borrowing in data:
        sql = f"""
        SELECT
            CONVERT(id,CHAR) AS id,
            file_name
        FROM
            p_uploaded_files
        WHERE
            p_application_header_id = {p_application_header_id}
            AND
            file_name LIKE '%{p_application_header_id}/p_borrowings__I/{p_borrowing["id"]}%';
        """
        old_files = await db.fetch_all(sql)
        old_files_id = [item["id"] for item in old_files]
        un_update_files_id = []

        for update_file in p_borrowing["p_borrowings__I"]:
            if update_file["id"] in old_files_id:
                un_update_files_id.append(update_file["id"])
                continue
            # new add
            id = await db.uuid_short()
            fields = ["id", "p_application_header_id", "owner_type", "owner_id"]
            values = [f"{id}", f"{p_application_header_id}", f"{role_type}", f"{role_id}"]
            s3_key = f"{p_application_header_id}/p_borrowings__I/{p_borrowing['id']}"
            file_name = f"{s3_key}/{update_file['name']}"
            file_content = base64.b64decode(update_file["src"].split(",")[1])

            upload_to_s3(file_name, file_content)

            fields.append("s3_key")
            fields.append("file_name")

            values.append(f"'{s3_key}'")
            values.append(f"'{file_name}'")

            sql = f"INSERT INTO p_uploaded_files ({', '.join(fields)}) VALUES ({', '.join(values)});"
            await db.execute(sql)
            p_activities_id = await db.uuid_short()
            sql = f"""
            INSERT INTO p_activities (id, p_application_header_id, operator_type, operator_id, table_name, field_name, table_id, content, operate_type)
            VALUES ({p_activities_id}, {p_application_header_id}, {role_type}, {role_id}, 'p_borrowings', 'p_borrowings__I', {p_borrowing["id"]}, '{update_file["name"]}', 2);
            """
            await db.execute(sql)

        delete_files_id = list(set(old_files_id) - set(un_update_files_id))
        for old_file in old_files:
            if old_file["id"] in delete_files_id:
                delete_from_s3(old_file["file_name"])
                sql = f"DELETE FROM p_uploaded_files WHERE id = '{old_file['id']}';"
                await db.execute(sql)
                p_activities_id = await db.uuid_short()
                sql = f"""
                INSERT INTO p_activities (id, p_application_header_id, operator_type, operator_id, table_name, field_name, table_id, content, operate_type)
                VALUES ({p_activities_id}, {p_application_header_id}, {role_type}, {role_id}, 'p_borrowings', 'p_borrowings__I', {p_borrowing["id"]}, '{old_file["file_name"].split("/")[-1]}', 9);
                """
                db.execute(sql)


async def diff_p_uploaded_files_for_ad(db: DB, data: dict, p_application_header_id, role_type, role_id):
    JOBS = []

    for key, value in data.items():
        sql = f"""
        SELECT
            CONVERT(id,CHAR) AS id,
            file_name
        FROM
            p_uploaded_files
        WHERE
            p_application_header_id = {p_application_header_id}
            AND
            s3_key = '{p_application_header_id}/{key}';
        """
        old_files = await db.fetch_all(sql)
        old_files_id = [item["id"] for item in old_files]
        un_update_files_id = []
        for update_file in value:
            if update_file["id"] in old_files_id:
                un_update_files_id.append(update_file["id"])
                continue
            # new add
            id = await db.uuid_short()
            fields = ["id", "p_application_header_id", "owner_type", "owner_id"]
            values = [f"{id}", f"{p_application_header_id}", f"{role_type}", f"{role_id}"]
            s3_key = f"{p_application_header_id}/{key}"
            file_name = f"{s3_key}/{update_file['name']}"
            file_content = base64.b64decode(update_file["src"].split(",")[1])

            upload_to_s3(file_name, file_content)

            fields.append("s3_key")
            fields.append("file_name")

            values.append(f"'{s3_key}'")
            values.append(f"'{file_name}'")

            sql = f"INSERT INTO p_uploaded_files ({', '.join(fields)}) VALUES ({', '.join(values)});"
            await db.execute(sql)
            p_activities_id = await db.uuid_short()
            sql = f"""
            INSERT INTO p_activities (id, p_application_header_id, operator_type, operator_id, table_name, field_name, table_id, content, operate_type)
            VALUES ({p_activities_id}, {p_application_header_id}, {role_type}, {role_id}, 'p_uploaded_files', '{key}', null, '{update_file["name"]}', 2);
            """
            JOBS.append(db.execute(sql))
        # delete file
        delete_files_id = list(set(old_files_id) - set(un_update_files_id))
        for old_file in old_files:
            if old_file["id"] in delete_files_id:
                delete_from_s3(old_file["file_name"])
                sql = f"DELETE FROM p_uploaded_files WHERE id = '{old_file['id']}';"
                await db.execute(sql)

                p_activities_id = await db.uuid_short()
                sql = f"""
                INSERT INTO p_activities (id, p_application_header_id, operator_type, operator_id, table_name, field_name, table_id, content, operate_type)
                VALUES ({p_activities_id}, {p_application_header_id}, {role_type}, {role_id}, 'p_uploaded_files', '{key}', null, '{old_file["file_name"].split("/")[-1]}', 9);
                """
                JOBS.append(db.execute(sql))

    if JOBS:
        await asyncio.wait(JOBS)


async def delete_p_borrowings_for_ad(db: DB, p_application_header_id):
    old_p_borrowings = await query_p_borrowings_for_ad(db, p_application_header_id)
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


async def delete_p_applicant_persons__1_for_ad(db: DB, p_application_header_id):
    p_applicant_persons = await db.fetch_one(
        f"SELECT id FROM p_applicant_persons WHERE p_application_header_id={p_application_header_id} AND type = 1;"
    )
    if p_applicant_persons is None:
        return
    p_applicant_persons_id = p_applicant_persons["id"]
    sql = f"DELETE FROM p_applicant_persons WHERE id = {p_applicant_persons_id};"
    await db.execute(sql)


async def delete_p_borrowing_details__2_for_ad(db: DB, p_application_header_id):
    sql = (
        f"DELETE FROM p_borrowing_details WHERE p_application_header_id = {p_application_header_id} AND time_type = 2;"
    )
    await db.execute(sql)


async def delete_p_join_guarantors(db: DB, p_application_header_id):
    sql = f"DELETE FROM p_join_guarantors WHERE p_application_header_id = {p_application_header_id};"
    await db.execute(sql)


async def query_p_activities_for_ad(db: DB, p_application_header_id):
    sql = f"""
    SELECT DISTINCT
        CONCAT(table_name, '.', field_name, '.', table_id) as update_history_key
    FROM
        p_activities
    WHERE
        p_application_header_id = {p_application_header_id}
        AND
        table_name IS NOT NULL
        AND
        field_name IS NOT NULL
        AND
        operate_type != 0;
    """
    result = await db.fetch_all(sql)

    return [item["update_history_key"] for item in result]


async def query_files_p_activities_for_ad(db: DB, p_application_header_id):
    sql = f"""
    SELECT DISTINCT
        CONCAT(table_name, '.', field_name) as update_history_key
    FROM
        p_activities
    WHERE
        p_application_header_id = {p_application_header_id}
        AND
        table_name IS NOT NULL
        AND
        field_name IS NOT NULL
        AND
        operate_type != 0;
    """
    result = await db.fetch_all(sql)

    return [item["update_history_key"] for item in result]


async def query_field_uodate_histories_for_ad(db: DB, p_application_header_id: int, update_history_key: str):
    [table_name, field_name, table_id] = update_history_key.split(".")
    sql = f"""
    SELECT
        DATE_FORMAT(p_activities.created_at, '%Y/%m/%d %H:%i') as created_at,
        p_activities.operator_type,
        p_activities.operate_type,
        p_activities.content,
        CONCAT(p_applicant_persons.last_name_kanji, ' ', p_applicant_persons.first_name_kanji) as p_applicant_person_name,
        s_sales_persons.name_kanji as s_sales_person_name,
        s_managers.name_kanji as s_manager_name
    FROM
        p_activities
    JOIN
        p_application_headers
        ON
        p_application_headers.id = p_activities.p_application_header_id
    LEFT JOIN
        p_applicant_persons
        ON
        p_applicant_persons.p_application_header_id = p_application_headers.id
        AND
        p_applicant_persons.type = 0
    LEFT JOIN
        s_sales_persons
        ON
        s_sales_persons.id = p_activities.operator_id
    LEFT JOIN
        s_managers
        ON
        s_managers.id = p_activities.operator_id
    WHERE
        p_activities.p_application_header_id = {p_application_header_id}
        AND
        p_activities.table_name = '{table_name}'
        AND
        p_activities.field_name = '{field_name}'
        AND
        p_activities.table_id = '{table_id}'
    """

    return await db.fetch_all(sql)


async def query_files_field_uodate_histories_for_ad(db: DB, p_application_header_id: int, update_history_key: str):
    [table_name, field_name] = update_history_key.split(".")
    sql = f"""
    SELECT
        DATE_FORMAT(p_activities.created_at, '%Y/%m/%d %H:%i') as created_at,
        p_activities.operator_type,
        p_activities.operate_type,
        p_activities.content,
        CONCAT(p_applicant_persons.last_name_kanji, ' ', p_applicant_persons.first_name_kanji) as p_applicant_person_name,
        s_sales_persons.name_kanji as s_sales_person_name,
        s_managers.name_kanji as s_manager_name
    FROM
        p_activities
    JOIN
        p_application_headers
        ON
        p_application_headers.id = p_activities.p_application_header_id
    LEFT JOIN
        p_applicant_persons
        ON
        p_applicant_persons.p_application_header_id = p_application_headers.id
        AND
        p_applicant_persons.type = 0
    LEFT JOIN
        s_sales_persons
        ON
        s_sales_persons.id = p_activities.operator_id
    LEFT JOIN
        s_managers
        ON
        s_managers.id = p_activities.operator_id
    WHERE
        p_activities.p_application_header_id = {p_application_header_id}
        AND
        p_activities.table_name = '{table_name}'
        AND
        p_activities.field_name = '{field_name}'
    """

    return await db.fetch_all(sql)


async def query_p_borrowings_for_ad_view(db: DB, p_application_header_id: int):
    sql = f"""
    SELECT
        CONVERT(id,CHAR) AS id
    FROM
        p_borrowings
    WHERE
        p_application_header_id = {p_application_header_id};
    """
    basic_p_borrowings = await db.fetch_all(sql)
    p_borrowings_with_files = []

    for basic_p_borrowing in basic_p_borrowings:
        sql = f"""
        SELECT
            CONVERT(p_uploaded_files.id,CHAR) AS id,
            p_uploaded_files.file_name,
            p_uploaded_files.owner_type,
            DATE_FORMAT(p_uploaded_files.created_at, '%Y/%m/%d %H:%i') as created_at,
            p_uploaded_files.owner_type,
            CONCAT(p_applicant_persons.last_name_kanji, ' ', p_applicant_persons.first_name_kanji) as p_applicant_person_name,
            s_sales_persons.name_kanji as s_sales_person_name,
            s_managers.name_kanji as s_manager_name
        FROM
            p_uploaded_files
        JOIN
            p_application_headers
            ON
            p_application_headers.id = p_uploaded_files.p_application_header_id
        LEFT JOIN
            p_applicant_persons
            ON
            p_applicant_persons.p_application_header_id = p_application_headers.id
            AND
            p_applicant_persons.type = 0
        LEFT JOIN
            s_sales_persons
            ON
            s_sales_persons.id = p_uploaded_files.owner_id
        LEFT JOIN
            s_managers
            ON
            s_managers.id = p_uploaded_files.owner_id
        WHERE
            p_uploaded_files.p_application_header_id = {p_application_header_id}
            AND
            p_uploaded_files.file_name LIKE '%{p_application_header_id}/p_borrowings__I/{basic_p_borrowing["id"]}%';
        """
        p_borrowing_files_info = await db.fetch_all(sql)
        if len(p_borrowing_files_info) == 0:
            p_borrowings_with_files.append(none_to_blank({**basic_p_borrowing, "p_borrowings__I": []}))
        else:
            files = []
            for file in p_borrowing_files_info:
                files.append({**download_from_s3(file["file_name"]), **file})
            p_borrowings_with_files.append(none_to_blank({**basic_p_borrowing, "p_borrowings__I": files}))
    return p_borrowings_with_files


async def query_p_uploaded_files_for_ad_view(db: DB, p_application_header_id: int, category: str):
    temp_files = {}
    sql = f"""
    SELECT
        CONVERT(p_uploaded_files.id,CHAR) AS id,
        p_uploaded_files.file_name,
        p_uploaded_files.s3_key,
        p_uploaded_files.owner_type,
        DATE_FORMAT(p_uploaded_files.created_at, '%Y/%m/%d %H:%i') as created_at,
        p_uploaded_files.owner_type,
        CONCAT(p_applicant_persons.last_name_kanji, ' ', p_applicant_persons.first_name_kanji) as p_applicant_person_name,
        s_sales_persons.name_kanji as s_sales_person_name,
        s_managers.name_kanji as s_manager_name
    FROM
        p_uploaded_files
    JOIN
        p_application_headers
        ON
        p_application_headers.id = p_uploaded_files.p_application_header_id
    LEFT JOIN
        p_applicant_persons
        ON
        p_applicant_persons.p_application_header_id = p_application_headers.id
        AND
        p_applicant_persons.type = 0
    LEFT JOIN
        s_sales_persons
        ON
        s_sales_persons.id = p_uploaded_files.owner_id
    LEFT JOIN
        s_managers
        ON
        s_managers.id = p_uploaded_files.owner_id
    WHERE
        p_uploaded_files.p_application_header_id = {p_application_header_id}
        AND
        p_uploaded_files.s3_key LIKE '%{category}%';
    """
    files_info = await db.fetch_all(sql)
    print(files_info)
    if len(files_info) > 0:
        files = []
        for file in files_info:
            files.append({**download_from_s3(file["file_name"]), **file})
        temp_files[file["s3_key"].split("/")[-1]] = files
    return temp_files


async def query_p_result(db: DB, p_application_header_id: int):
    sbi = await db.fetch_one("SELECT id, name FROM s_banks WHERE code = '0038';")
    sbi_id = sbi["id"]
    sql = f"""
    SELECT
        CONVERT(p_application_banks.s_bank_id,CHAR) AS s_bank_id,
        p_application_headers.pre_examination_status,
        p_application_banks.provisional_status,
        p_application_banks.provisional_result,
        p_application_banks.provisional_after_result,
        p_application_headers.approver_confirmation
    FROM
        p_application_headers
    LEFT JOIN
        p_application_banks
        ON
        p_application_banks.p_application_header_id = p_application_headers.id
        AND
        p_application_banks.s_bank_id = {sbi_id}
    WHERE
        p_application_headers.id = {p_application_header_id}
    """
    result = await db.fetch_one(sql)

    return none_to_blank(result)
