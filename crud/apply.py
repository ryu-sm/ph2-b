import json
import typing
import base64
import asyncio
import pytz
from datetime import datetime
from core.database import DB
from constant import (
    JSON_FIELD_KEYS,
    FILE_FIELF_KEYS,
    P_APPLICATION_HEADERS_FILE_FIELF_KEYS,
    P_APPLICANT_PERSONS_FILE_FIELF_KEYS,
    P_BORROWINGS_FILE_FIELF_KEYS,
    JSON_DICT_FIELD_KEYS,
    JSON_LIST_FIELD_KEYS,
    INIT_NEW_HOUSE_PLANNED_RESIDENT_OVERVIEW,
    OWNER_TYPE_EN_MAPS,
)
from constant import (
    P_UPLOAD_FILE_TYPE,
    TOKEN_ROLE_TYPE,
    P_APPLICANT_PERSONS_TYPE,
    P_BORROWING_DETAILS_TIME_TYPE,
    LOAN_TYPE,
    LAND_ADVANCE_PLAN,
    JOIN_GUARANTOR_UMU,
    CURR_BORROWING_STATUS,
    OPERATE_TYPE,
)
from utils import upload_to_s3, none_to_blank
import utils
import crud


async def insert_p_application_headers(db: DB, data: dict, role_type, role_id, c_user_id=None, s_sales_person_id=None):
    jp_tz = pytz.timezone("Asia/Tokyo")
    sql = f"SELECT MAX(apply_no) no FROM p_application_headers WHERE created_at  >= '{datetime.strftime(datetime.now(jp_tz),'%Y-%m-%d')} 00:00:00'"
    last_apply = await db.fetch_one(sql)
    new_apply_no = None
    if last_apply["no"] is None:
        new_apply_no = f"SET{datetime.strftime(datetime.now(),'%Y%m%d')}001"
    else:
        new_no = str(int(last_apply["no"][-3:]) + 1).zfill(3)
        new_apply_no = f"SET{datetime.strftime(datetime.now(),'%Y%m%d')}{new_no}"

    p_application_header_id = await db.uuid_short()
    basuc_p_application_header_sql_params = {
        "id": p_application_header_id,
        "c_user_id": c_user_id,
        "s_sales_person_id": s_sales_person_id,
        "apply_no": new_apply_no,
    }
    await db.execute(utils.gen_insert_sql("p_application_headers", {**data, **basuc_p_application_header_sql_params}))
    for file_field_key in P_APPLICATION_HEADERS_FILE_FIELF_KEYS:
        files = data.get(file_field_key, [])
        for file in files:
            p_upload_file_id = await db.uuid_short()
            p_upload_file_sql_params = {
                "id": p_upload_file_id,
                "p_application_header_id": p_application_header_id,
                "owner_type": role_type,
                "owner_id": role_id,
                "record_id": p_application_header_id,
                "type": P_UPLOAD_FILE_TYPE.APPLICANT.value,
                # "s3_key": f"{p_application_header_id}/{p_upload_file_id}/{file_field_key}",
                "s3_key": f"{p_application_header_id}/{role_id}_{OWNER_TYPE_EN_MAPS[role_type]}/{file_field_key}/{p_upload_file_id}",
                "file_name": file["name"],
            }
            utils.upload_base64_file_s3(
                f"{p_upload_file_sql_params.get('s3_key')}/{p_upload_file_sql_params.get('file_name')}",
                file["src"],
            )
            await db.execute(utils.gen_insert_sql("p_uploaded_files", p_upload_file_sql_params))
    return p_application_header_id


async def insert_p_applicant_persons(
    db: DB, data: dict, p_application_header_id: int, type: int, role_type: int, role_id: int
):
    p_applicant_person_id = await db.uuid_short()
    basic_p_applicant_person_sql_params = {
        "id": p_applicant_person_id,
        "p_application_header_id": p_application_header_id,
        "type": type,
    }
    await db.execute(utils.gen_insert_sql("p_applicant_persons", {**data, **basic_p_applicant_person_sql_params}))

    for file_field_key in P_APPLICANT_PERSONS_FILE_FIELF_KEYS:
        files = data.get(file_field_key, [])
        for file in files:
            p_upload_file_id = await db.uuid_short()
            p_upload_file_sql_params = {
                "id": p_upload_file_id,
                "p_application_header_id": p_application_header_id,
                "owner_type": role_type,
                "owner_id": role_id,
                "record_id": p_applicant_person_id,
                "type": type,
                # "s3_key": f"{p_application_header_id}/{p_upload_file_id}/{file_field_key}",
                "s3_key": f"{p_application_header_id}/{role_id}_{OWNER_TYPE_EN_MAPS[role_type]}/{file_field_key}/{p_upload_file_id}",
                "file_name": file["name"],
            }
            utils.upload_base64_file_s3(
                f"{p_upload_file_sql_params.get('s3_key')}/{p_upload_file_sql_params.get('file_name')}",
                file["src"],
            )
            await db.execute(utils.gen_insert_sql("p_uploaded_files", p_upload_file_sql_params))


async def insert_p_borrowing_details(db: DB, data: dict, p_application_header_id: int, time_type: int):
    p_borrowing_detail_id = await db.uuid_short()
    basic_p_borrowing_detail_sql_params = {
        "id": p_borrowing_detail_id,
        "p_application_header_id": p_application_header_id,
        "time_type": time_type,
    }
    await db.execute(utils.gen_insert_sql("p_borrowing_details", {**data, **basic_p_borrowing_detail_sql_params}))


async def instert_p_application_banks(db: DB, data: list, p_application_header_id: int):
    for s_bank_id in data:
        p_application_banks_id = await db.uuid_short()
        p_application_banks_sql_params = {
            "id": p_application_banks_id,
            "p_application_header_id": p_application_header_id,
            "s_bank_id": s_bank_id,
        }
        await db.execute(utils.gen_insert_sql("p_application_banks", p_application_banks_sql_params))


async def insert_p_join_guarantors(db: DB, data: typing.List[dict], p_application_header_id: int):
    for join_guarantor in data:
        p_join_guarantor_id = await db.uuid_short()
        basic_p_join_guarantor_sql_params = {
            "id": p_join_guarantor_id,
            "p_application_header_id": p_application_header_id,
        }
        await db.execute(
            utils.gen_insert_sql("p_join_guarantors", {**join_guarantor, **basic_p_join_guarantor_sql_params})
        )


async def insert_p_borrowings(db: DB, data: typing.List[dict], p_application_header_id: int, role_type, role_id):
    for borrowing in data:
        p_borrowing_id = await db.uuid_short()
        basic_p_borrowing_sql_params = {"id": p_borrowing_id, "p_application_header_id": p_application_header_id}
        await db.execute(utils.gen_insert_sql("p_borrowings", {**borrowing, **basic_p_borrowing_sql_params}))

        for file_field_key in P_BORROWINGS_FILE_FIELF_KEYS:
            files = borrowing.get(file_field_key, [])
            for file in files:
                p_upload_file_id = await db.uuid_short()
                p_upload_file_sql_params = {
                    "id": p_upload_file_id,
                    "p_application_header_id": p_application_header_id,
                    "owner_type": role_type,
                    "owner_id": role_id,
                    "record_id": p_borrowing_id,
                    "type": P_UPLOAD_FILE_TYPE.APPLICANT.value,
                    # "s3_key": f"{p_application_header_id}/{p_upload_file_id}/{file_field_key}",
                    "s3_key": f"{p_application_header_id}/{role_id}_{OWNER_TYPE_EN_MAPS[role_type]}/{file_field_key}/{p_upload_file_id}",
                    "file_name": file["name"],
                }
                utils.upload_base64_file_s3(
                    f"{p_upload_file_sql_params.get('s3_key')}/{p_upload_file_sql_params.get('file_name')}",
                    file["src"],
                )
                await db.execute(utils.gen_insert_sql("p_uploaded_files", p_upload_file_sql_params))


async def insert_p_residents(db: DB, data: typing.List[dict], p_application_header_id: int):
    for resident in data:
        p_resident_id = await db.uuid_short()
        basic_p_resident_sql_params = {"id": p_resident_id, "p_application_header_id": p_application_header_id}
        await db.execute(utils.gen_insert_sql("p_residents", {**resident, **basic_p_resident_sql_params}))


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
        curr_house_shell_scheduled_date,
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
        funding_self_amount,
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
        vendor_phone,
        vendor_business_card
    FROM
        p_application_headers
    WHERE
        id = {p_application_header_id};
    """

    p_application_headers = await db.fetch_one(sql)

    file_keys = ["G", "J", "R"]
    files = {"G": [], "J": [], "R": []}
    for key in file_keys:
        sql = f"""
        SELECT
            CONVERT(id,CHAR) AS id,
            s3_key,
            file_name
        FROM
            p_uploaded_files
        WHERE
            p_application_header_id = {p_application_header_id}
            AND
            owner_type = 1
            AND
            type = 0
            AND
            deleted IS NULL
            AND
            s3_key LIKE '%/{key}%';
        """
        files_info = await db.fetch_all(sql)

        temp_files = []
        for file_info in files_info:
            src = utils.generate_presigned_url(f"{file_info['s3_key']}/{file_info['file_name']}")
            temp_files.append({"id": file_info["id"], "name": file_info["file_name"], "src": src})
        files[key] = temp_files

    return none_to_blank({**p_application_headers, **files})


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
    if time_type == P_BORROWING_DETAILS_TIME_TYPE.ONE_TIME.value:
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
    p_application_banks = await db.fetch_all(sql)
    return [p_application_bank["s_bank_id"] for p_application_bank in p_application_banks]


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
        identity_verification_type,
        before_last_year_income
    FROM
        p_applicant_persons
    WHERE
        p_application_header_id = {p_application_header_id}
        AND
        type = {type};
    """
    p_applicant_persons = await db.fetch_one(sql)
    file_keys = [
        "H__a",
        "H__b",
        "A__01__a",
        "A__01__b",
        "A__02",
        "A__03__a",
        "A__03__b",
        "B__a",
        "B__b",
        "C__01",
        "C__02",
        "C__03",
        "C__04",
        "C__05",
        "D__01",
        "D__02",
        "D__03",
        "E",
        "F__01",
        "F__02",
        "F__03",
        "K",
    ]
    files = {
        "G": [],
        "J": [],
        "H__a": [],
        "H__b": [],
        "A__01__a": [],
        "A__01__b": [],
        "A__02": [],
        "A__03__a": [],
        "A__03__b": [],
        "B__a": [],
        "B__b": [],
        "C__01": [],
        "C__02": [],
        "C__03": [],
        "C__04": [],
        "C__05": [],
        "D__01": [],
        "D__02": [],
        "D__03": [],
        "E": [],
        "F__01": [],
        "F__02": [],
        "F__03": [],
        "K": [],
    }
    if type == 0:
        file_keys.append("S")
        files["S"] = []
    for key in file_keys:
        sql = f"""
        SELECT
            CONVERT(id,CHAR) AS id,
            s3_key,
            file_name
        FROM
            p_uploaded_files
        WHERE
            p_application_header_id = {p_application_header_id}
            AND
            owner_type = 1
            AND
            type = {type}
            AND
            deleted IS NULL
            AND
            s3_key LIKE '%/{key}%';
        """
        files_info = await db.fetch_all(sql)
        temp_files = []
        for file_info in files_info:
            src = utils.generate_presigned_url(f"{file_info['s3_key']}/{file_info['file_name']}")
            temp_files.append({"id": file_info["id"], "name": file_info["file_name"], "src": src})
        files[key] = temp_files
    return none_to_blank({**p_applicant_persons, **files})


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
    p_join_guarantors = await db.fetch_all(sql)

    return [none_to_blank(p_join_guarantor) for p_join_guarantor in p_join_guarantors]


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
        DATE_FORMAT(birthday, '%Y/%m/%d') as birthday,
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
    p_residents = await db.fetch_all(sql)

    return [none_to_blank(p_resident) for p_resident in p_residents]


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
    borrowings = []
    for borrowing in result:
        file_keys = ["I"]
        files = {"I": []}
        for key in file_keys:
            sql = f"""
            SELECT
                CONVERT(id,CHAR) AS id,
                s3_key,
                file_name
            FROM
                p_uploaded_files
            WHERE
                p_application_header_id = {p_application_header_id}
                AND
                record_id = {borrowing["id"]}
                AND
                owner_type = 1
                AND
                type = 0
                AND
                deleted IS NULL
                AND
                s3_key LIKE '%/{key}%';
            """
            files_info = await db.fetch_all(sql)
            temp_files = []
            for file_info in files_info:
                src = utils.generate_presigned_url(f"{file_info['s3_key']}/{file_info['file_name']}")
                temp_files.append({"id": file_info["id"], "name": file_info["file_name"], "src": src})
            files[key] = temp_files
        borrowings.append(none_to_blank({**borrowing, **files}))
    return borrowings


async def query_p_application_header_id_with_c_user_id(db: DB, c_user_id: str):
    p_application_headers = await db.fetch_one(
        f"SELECT CONVERT(id,CHAR) as id FROM p_application_headers WHERE c_user_id={c_user_id};"
    )
    return p_application_headers["id"]


async def query_p_application_header_apply_no(db: DB, p_application_header_id: int):
    sql = f"SELECT apply_no FROM p_application_headers WHERE id = {p_application_header_id};"
    p_application_headers = await db.fetch_one(sql)
    return p_application_headers["apply_no"]


async def diff_update_p_application_headers_for_ap(db: DB, data: dict, p_application_header_id, role_type, role_id):
    JOBS = []

    old_p_application_headers = await query_p_application_headers_for_ap(db, p_application_header_id)

    # delete join_guarantor
    join_guarantor_umu = data.get("join_guarantor_umu")
    if join_guarantor_umu != JOIN_GUARANTOR_UMU.HAVE.value:
        await db.execute(f"DELETE FROM p_join_guarantors WHERE p_application_header_id = {p_application_header_id};")
    # delete p_applicant_persons__1
    loan_type = data.get("loan_type")
    if loan_type not in [LOAN_TYPE.TOTAL_INCOME_EQUITY.value, LOAN_TYPE.TOTAL_INCOME_NO_EQUITY.value]:
        await db.execute(
            f"DELETE FROM p_applicant_persons WHERE p_application_header_id = {p_application_header_id}  AND type = {P_UPLOAD_FILE_TYPE.TOTAL_INCOME.value};"
        )
        await db.execute(
            f"UPDATE p_uploaded_files SET deleted = 1 WHERE p_application_header_id = {p_application_header_id} AND type = {P_UPLOAD_FILE_TYPE.TOTAL_INCOME.value};"
        )
    # delete p_borrowing_details__2
    land_advance_plan = data.get("land_advance_plan")
    if land_advance_plan != LAND_ADVANCE_PLAN.HOPE.value:
        await db.execute(
            f"DELETE FROM p_borrowing_details WHERE p_application_header_id = {p_application_header_id} AND time_type = {P_BORROWING_DETAILS_TIME_TYPE.TWO_TIME.value};"
        )
    for key, value in data.items():
        old_value = old_p_application_headers.get(key, "")
        if key in JSON_LIST_FIELD_KEYS:
            if sorted(value) == sorted(old_value):
                continue
        if key in JSON_DICT_FIELD_KEYS:
            if INIT_NEW_HOUSE_PLANNED_RESIDENT_OVERVIEW == value and not old_value:
                continue
        if value == old_value:
            continue

        if key in FILE_FIELF_KEYS:
            sql = f"""
            SELECT
                CONVERT(id,CHAR) AS id,
                s3_key,
                file_name
            FROM
                p_uploaded_files
            WHERE
                p_application_header_id = {p_application_header_id}
                AND
                deleted IS NULL
                AND
                owner_type = 1
                AND
                type = 0
                AND
                s3_key LIKE '%/{key}%';
            """
            old_files_info = await db.fetch_all(sql)
            old_files_id = [item["id"] for item in old_files_info]
            un_update_files_id = []

            for update_file in value:
                if update_file["id"] in old_files_id:
                    un_update_files_id.append(update_file["id"])
                    continue
                # add file
                p_upload_file_id = await db.uuid_short()
                p_upload_file_sql_params = {
                    "id": p_upload_file_id,
                    "p_application_header_id": p_application_header_id,
                    "owner_type": role_type,
                    "owner_id": role_id,
                    "record_id": p_application_header_id,
                    "type": P_UPLOAD_FILE_TYPE.APPLICANT.value,
                    # "s3_key": f"{p_application_header_id}/{p_upload_file_id}/{key}",
                    "s3_key": f"{p_application_header_id}/{role_id}_{OWNER_TYPE_EN_MAPS[role_type]}/{key}/{p_upload_file_id}",
                    "file_name": update_file["name"],
                }
                utils.upload_base64_file_s3(
                    f"{p_upload_file_sql_params.get('s3_key')}/{p_upload_file_sql_params.get('file_name')}",
                    update_file["src"],
                )
                await db.execute(utils.gen_insert_sql("p_uploaded_files", p_upload_file_sql_params))

                total = await crud.query_update_history_count(
                    db, p_application_header_id, "p_application_headers", key, p_application_header_id
                )
                if total == 0 and len(old_files_info) == 0:
                    JOBS.append(
                        db.execute(
                            utils.gen_insert_sql(
                                "p_activities",
                                {
                                    "id": await db.uuid_short(),
                                    "p_application_header_id": p_application_header_id,
                                    "operator_type": role_type,
                                    "operator_id": role_id,
                                    "table_name": "p_application_headers",
                                    "field_name": key,
                                    "table_id": p_application_header_id,
                                    "content": None,
                                    "operate_type": OPERATE_TYPE.APPLY.value,
                                },
                            )
                        )
                    )
                if total == 0 and len(old_files_info) > 0:
                    for old_file in old_files_info:
                        JOBS.append(
                            db.execute(
                                utils.gen_insert_sql(
                                    "p_activities",
                                    {
                                        "id": await db.uuid_short(),
                                        "p_application_header_id": p_application_header_id,
                                        "operator_type": role_type,
                                        "operator_id": role_id,
                                        "table_name": "p_application_headers",
                                        "field_name": key,
                                        "table_id": p_application_header_id,
                                        "content": old_file["file_name"],
                                        "operate_type": OPERATE_TYPE.APPLY.value,
                                    },
                                )
                            )
                        )
                JOBS.append(
                    db.execute(
                        utils.gen_insert_sql(
                            "p_activities",
                            {
                                "id": await db.uuid_short(),
                                "p_application_header_id": p_application_header_id,
                                "operator_type": role_type,
                                "operator_id": role_id,
                                "table_name": "p_application_headers",
                                "field_name": key,
                                "table_id": p_application_header_id,
                                "content": update_file["name"],
                                "operate_type": OPERATE_TYPE.UPDATE.value,
                            },
                        )
                    )
                )
            # delete file
            delete_files_id = list(set(old_files_id) - set(un_update_files_id))
            if len(delete_files_id) == 0:
                continue
            delete_files_info = await db.fetch_all(
                f"SELECT CONVERT(id,CHAR) AS id, s3_key, file_name FROM p_uploaded_files WHERE id IN ({', '.join(delete_files_id)});"
            )

            for delete_file_info in delete_files_info:
                sql = f"UPDATE p_uploaded_files SET deleted = 1 WHERE id = {delete_file_info['id']};"
                JOBS.append(db.execute(sql))
                JOBS.append(
                    db.execute(
                        utils.gen_insert_sql(
                            "p_activities",
                            {
                                "id": await db.uuid_short(),
                                "p_application_header_id": p_application_header_id,
                                "operator_type": role_type,
                                "operator_id": role_id,
                                "table_name": "p_application_headers",
                                "field_name": key,
                                "table_id": p_application_header_id,
                                "content": delete_file_info["file_name"],
                                "operate_type": OPERATE_TYPE.DELETE.value,
                            },
                        )
                    )
                )
            continue

        # field deleted
        if not value and old_value:
            JOBS.append(
                db.execute(
                    utils.gen_insert_sql(
                        "p_activities",
                        {
                            "id": await db.uuid_short(),
                            "p_application_header_id": p_application_header_id,
                            "operator_type": role_type,
                            "operator_id": role_id,
                            "table_name": "p_application_headers",
                            "field_name": key,
                            "table_id": p_application_header_id,
                            "content": None,
                            "operate_type": OPERATE_TYPE.DELETE.value,
                        },
                    )
                )
            )
        # field update
        else:
            total = await crud.query_update_history_count(
                db, p_application_header_id, "p_application_headers", key, p_application_header_id
            )
            if total == 0:
                JOBS.append(
                    db.execute(
                        utils.gen_insert_sql(
                            "p_activities",
                            {
                                "id": await db.uuid_short(),
                                "p_application_header_id": p_application_header_id,
                                "operator_type": role_type,
                                "operator_id": role_id,
                                "table_name": "p_application_headers",
                                "field_name": key,
                                "table_id": p_application_header_id,
                                "content": old_value if old_value != "" else None,
                                "operate_type": OPERATE_TYPE.APPLY.value,
                            },
                        )
                    )
                )
            JOBS.append(
                db.execute(
                    utils.gen_insert_sql(
                        "p_activities",
                        {
                            "id": await db.uuid_short(),
                            "p_application_header_id": p_application_header_id,
                            "operator_type": role_type,
                            "operator_id": role_id,
                            "table_name": "p_application_headers",
                            "field_name": key,
                            "table_id": p_application_header_id,
                            "content": value,
                            "operate_type": OPERATE_TYPE.UPDATE.value,
                        },
                    )
                )
            )

        JOBS.append(
            db.execute(utils.gen_update_sql("p_application_headers", {key: value}, {"id": p_application_header_id}))
        )

    if JOBS:
        await asyncio.wait(JOBS)


async def diff_update_p_applicant_persons_for_ap(db: DB, data: dict, p_application_header_id, type, role_type, role_id):
    JOBS = []
    p_applicant_persons_basic = await db.fetch_one(
        f"SELECT id FROM p_applicant_persons WHERE p_application_header_id = {p_application_header_id} AND type = {type}"
    )
    if p_applicant_persons_basic is None:
        data_ = utils.blank_to_none(data)
        await insert_p_applicant_persons(db, data_, p_application_header_id, type, role_type, role_id)
        return None

    p_applicant_persons_id = p_applicant_persons_basic["id"]
    old_p_applicant_persons = await query_p_applicant_persons_for_ap(db, p_application_header_id, type)

    for key, value in data.items():
        old_value = old_p_applicant_persons.get(key, "")
        if key in JSON_LIST_FIELD_KEYS:
            if sorted(value) == sorted(old_value):
                continue
        # if key in JSON_DICT_FIELD_KEYS:
        #     if INIT_NEW_HOUSE_PLANNED_RESIDENT_OVERVIEW == value and not old_value:
        #         continue
        if value == old_value:
            continue
        if key in FILE_FIELF_KEYS:
            sql = f"""
            SELECT
                CONVERT(id,CHAR) AS id,
                s3_key,
                file_name
            FROM
                p_uploaded_files
            WHERE
                p_application_header_id = {p_application_header_id}
                AND
                deleted IS NULL
                AND
                owner_type = 1
                AND
                type = {type}
                AND
                s3_key LIKE '%/{key}%';
            """
            old_files_info = await db.fetch_all(sql)
            old_files_id = [item["id"] for item in old_files_info]
            un_update_files_id = []

            for update_file in value:
                if update_file["id"] in old_files_id:
                    un_update_files_id.append(update_file["id"])
                    continue
                # add file
                p_upload_file_id = await db.uuid_short()
                p_upload_file_sql_params = {
                    "id": p_upload_file_id,
                    "p_application_header_id": p_application_header_id,
                    "owner_type": role_type,
                    "owner_id": role_id,
                    "record_id": p_applicant_persons_id,
                    "type": P_UPLOAD_FILE_TYPE.APPLICANT.value,
                    # "s3_key": f"{p_application_header_id}/{p_upload_file_id}/{key}",
                    "s3_key": f"{p_application_header_id}/{role_id}_{OWNER_TYPE_EN_MAPS[role_type]}/{key}/{p_upload_file_id}",
                    "file_name": update_file["name"],
                }
                utils.upload_base64_file_s3(
                    f"{p_upload_file_sql_params.get('s3_key')}/{p_upload_file_sql_params.get('file_name')}",
                    update_file["src"],
                )
                await db.execute(utils.gen_insert_sql("p_uploaded_files", p_upload_file_sql_params))

                total = await crud.query_update_history_count(
                    db, p_application_header_id, "p_applicant_persons", key, p_applicant_persons_id
                )
                if total == 0 and len(old_files_info) == 0:
                    JOBS.append(
                        db.execute(
                            utils.gen_insert_sql(
                                "p_activities",
                                {
                                    "id": await db.uuid_short(),
                                    "p_application_header_id": p_application_header_id,
                                    "operator_type": role_type,
                                    "operator_id": role_id,
                                    "table_name": "p_applicant_persons",
                                    "field_name": key,
                                    "table_id": p_applicant_persons_id,
                                    "content": None,
                                    "operate_type": OPERATE_TYPE.APPLY.value,
                                },
                            )
                        )
                    )
                if total == 0 and len(old_files_info) > 0:
                    for old_file in old_files_info:
                        JOBS.append(
                            db.execute(
                                utils.gen_insert_sql(
                                    "p_activities",
                                    {
                                        "id": await db.uuid_short(),
                                        "p_application_header_id": p_application_header_id,
                                        "operator_type": role_type,
                                        "operator_id": role_id,
                                        "table_name": "p_applicant_persons",
                                        "field_name": key,
                                        "table_id": p_applicant_persons_id,
                                        "content": old_file["file_name"],
                                        "operate_type": OPERATE_TYPE.APPLY.value,
                                    },
                                )
                            )
                        )
                JOBS.append(
                    db.execute(
                        utils.gen_insert_sql(
                            "p_activities",
                            {
                                "id": await db.uuid_short(),
                                "p_application_header_id": p_application_header_id,
                                "operator_type": role_type,
                                "operator_id": role_id,
                                "table_name": "p_applicant_persons",
                                "field_name": key,
                                "table_id": p_applicant_persons_id,
                                "content": update_file["name"],
                                "operate_type": OPERATE_TYPE.UPDATE.value,
                            },
                        )
                    )
                )

            # delete file
            delete_files_id = list(set(old_files_id) - set(un_update_files_id))
            if len(delete_files_id) == 0:
                continue
            delete_files_info = await db.fetch_all(
                f"SELECT CONVERT(id,CHAR) AS id, s3_key, file_name FROM p_uploaded_files WHERE id IN ({', '.join(delete_files_id)});"
            )

            for delete_file_info in delete_files_info:
                sql = f"UPDATE p_uploaded_files SET deleted = 1 WHERE id = {delete_file_info['id']};"
                JOBS.append(db.execute(sql))
                JOBS.append(
                    db.execute(
                        utils.gen_insert_sql(
                            "p_activities",
                            {
                                "id": await db.uuid_short(),
                                "p_application_header_id": p_application_header_id,
                                "operator_type": role_type,
                                "operator_id": role_id,
                                "table_name": "p_applicant_persons",
                                "field_name": key,
                                "table_id": p_applicant_persons_id,
                                "content": delete_file_info["file_name"],
                                "operate_type": OPERATE_TYPE.DELETE.value,
                            },
                        )
                    )
                )
            continue

        # field deleted
        if not value and old_value:
            JOBS.append(
                db.execute(
                    utils.gen_insert_sql(
                        "p_activities",
                        {
                            "id": await db.uuid_short(),
                            "p_application_header_id": p_application_header_id,
                            "operator_type": role_type,
                            "operator_id": role_id,
                            "table_name": "p_applicant_persons",
                            "field_name": key,
                            "table_id": p_applicant_persons_id,
                            "content": None,
                            "operate_type": OPERATE_TYPE.DELETE.value,
                        },
                    )
                )
            )

        # field update
        else:
            total = await crud.query_update_history_count(
                db, p_application_header_id, "p_applicant_persons", key, p_applicant_persons_id
            )
            if total == 0:
                JOBS.append(
                    db.execute(
                        utils.gen_insert_sql(
                            "p_activities",
                            {
                                "id": await db.uuid_short(),
                                "p_application_header_id": p_application_header_id,
                                "operator_type": role_type,
                                "operator_id": role_id,
                                "table_name": "p_applicant_persons",
                                "field_name": key,
                                "table_id": p_applicant_persons_id,
                                "content": old_value if old_value != "" else None,
                                "operate_type": OPERATE_TYPE.APPLY.value,
                            },
                        )
                    )
                )
            JOBS.append(
                db.execute(
                    utils.gen_insert_sql(
                        "p_activities",
                        {
                            "id": await db.uuid_short(),
                            "p_application_header_id": p_application_header_id,
                            "operator_type": role_type,
                            "operator_id": role_id,
                            "table_name": "p_applicant_persons",
                            "field_name": key,
                            "table_id": p_applicant_persons_id,
                            "content": value,
                            "operate_type": OPERATE_TYPE.UPDATE.value,
                        },
                    )
                )
            )

        JOBS.append(
            db.execute(utils.gen_update_sql("p_applicant_persons", {key: value}, {"id": p_applicant_persons_id}))
        )
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
        # field deleted
        if not value and old_value:
            JOBS.append(
                db.execute(
                    utils.gen_insert_sql(
                        "p_activities",
                        {
                            "id": await db.uuid_short(),
                            "p_application_header_id": p_application_header_id,
                            "operator_type": role_type,
                            "operator_id": role_id,
                            "table_name": "p_borrowing_details",
                            "field_name": key,
                            "table_id": p_borrowing_details_id,
                            "content": None,
                            "operate_type": OPERATE_TYPE.DELETE.value,
                        },
                    )
                )
            )

        # field update
        else:
            total = await crud.query_update_history_count(
                db, p_application_header_id, "p_borrowing_details", key, p_borrowing_details_id
            )
            if total == 0:
                JOBS.append(
                    db.execute(
                        utils.gen_insert_sql(
                            "p_activities",
                            {
                                "id": await db.uuid_short(),
                                "p_application_header_id": p_application_header_id,
                                "operator_type": role_type,
                                "operator_id": role_id,
                                "table_name": "p_borrowing_details",
                                "field_name": key,
                                "table_id": p_borrowing_details_id,
                                "content": old_value if old_value != "" else None,
                                "operate_type": OPERATE_TYPE.APPLY.value,
                            },
                        )
                    )
                )
            JOBS.append(
                db.execute(
                    utils.gen_insert_sql(
                        "p_activities",
                        {
                            "id": await db.uuid_short(),
                            "p_application_header_id": p_application_header_id,
                            "operator_type": role_type,
                            "operator_id": role_id,
                            "table_name": "p_borrowing_details",
                            "field_name": key,
                            "table_id": p_borrowing_details_id,
                            "content": value,
                            "operate_type": OPERATE_TYPE.UPDATE.value,
                        },
                    )
                )
            )

        JOBS.append(
            db.execute(utils.gen_update_sql("p_borrowing_details", {key: value}, {"id": p_borrowing_details_id}))
        )
    if JOBS:
        await asyncio.wait(JOBS)


async def diff_update_p_application_banks_for_ap(db: DB, data: list, p_application_header_id, role_type, role_id):
    JOBS = []
    old_p_application_banks = await query_p_application_banks_for_ap(db, p_application_header_id)
    for s_bank_id in data:
        if s_bank_id in old_p_application_banks:
            continue

        p_application_banks_id = await db.uuid_short()
        p_application_banks_sql_params = {
            "id": p_application_banks_id,
            "p_application_header_id": p_application_header_id,
            "s_bank_id": s_bank_id,
        }
        await db.execute(utils.gen_insert_sql("p_application_banks", p_application_banks_sql_params))

        JOBS.append(
            db.execute(
                utils.gen_insert_sql(
                    "p_activities",
                    {
                        "id": await db.uuid_short(),
                        "p_application_header_id": p_application_header_id,
                        "operator_type": role_type,
                        "operator_id": role_id,
                        "table_name": "p_application_banks",
                        "field_name": "s_bank_id",
                        "table_id": p_application_banks_id,
                        "content": s_bank_id,
                        "operate_type": OPERATE_TYPE.UPDATE.value,
                    },
                )
            )
        )

    for s_bank_id in old_p_application_banks:
        if s_bank_id in data:
            continue

        p_application_banks_basic = await db.fetch_one(
            f"SELECT id FROM p_application_banks WHERE p_application_header_id = {p_application_header_id} AND s_bank_id = {s_bank_id}"
        )

        p_application_banks_id = p_application_banks_basic["id"]

        JOBS.append(
            db.execute(
                utils.gen_insert_sql(
                    "p_activities",
                    {
                        "id": await db.uuid_short(),
                        "p_application_header_id": p_application_header_id,
                        "operator_type": role_type,
                        "operator_id": role_id,
                        "table_name": "p_application_banks",
                        "field_name": "s_bank_id",
                        "table_id": p_application_banks_id,
                        "content": s_bank_id,
                        "operate_type": OPERATE_TYPE.DELETE.value,
                    },
                )
            )
        )
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
            continue
        [old_p_join_guarantor] = filter
        for key, value in p_join_guarantor.items():
            old_value = old_p_join_guarantor.get(key, "")

            if value == old_value:
                continue
            # field deleted
            if not value and old_value:
                JOBS.append(
                    db.execute(
                        utils.gen_insert_sql(
                            "p_activities",
                            {
                                "id": await db.uuid_short(),
                                "p_application_header_id": p_application_header_id,
                                "operator_type": role_type,
                                "operator_id": role_id,
                                "table_name": "p_join_guarantors",
                                "field_name": key,
                                "table_id": old_p_join_guarantor["id"],
                                "content": None,
                                "operate_type": OPERATE_TYPE.DELETE.value,
                            },
                        )
                    )
                )

            # field update
            else:
                total = await crud.query_update_history_count(
                    db, p_application_header_id, "p_join_guarantors", key, old_p_join_guarantor["id"]
                )
                if total == 0:
                    JOBS.append(
                        db.execute(
                            utils.gen_insert_sql(
                                "p_activities",
                                {
                                    "id": await db.uuid_short(),
                                    "p_application_header_id": p_application_header_id,
                                    "operator_type": role_type,
                                    "operator_id": role_id,
                                    "table_name": "p_join_guarantors",
                                    "field_name": key,
                                    "table_id": old_p_join_guarantor["id"],
                                    "content": old_value if old_value != "" else None,
                                    "operate_type": OPERATE_TYPE.APPLY.value,
                                },
                            )
                        )
                    )
                JOBS.append(
                    db.execute(
                        utils.gen_insert_sql(
                            "p_activities",
                            {
                                "id": await db.uuid_short(),
                                "p_application_header_id": p_application_header_id,
                                "operator_type": role_type,
                                "operator_id": role_id,
                                "table_name": "p_join_guarantors",
                                "field_name": key,
                                "table_id": old_p_join_guarantor["id"],
                                "content": value,
                                "operate_type": OPERATE_TYPE.UPDATE.value,
                            },
                        )
                    )
                )

            JOBS.append(
                db.execute(utils.gen_update_sql("p_join_guarantors", {key: value}, {"id": old_p_join_guarantor["id"]}))
            )

    for old_p_join_guarantor in old_p_join_guarantors:
        filter = [item for item in data if item["id"] == old_p_join_guarantor["id"]]
        if len(filter) > 0:
            continue
        JOBS.append(
            db.execute(
                utils.gen_insert_sql(
                    "p_activities",
                    {
                        "id": await db.uuid_short(),
                        "p_application_header_id": p_application_header_id,
                        "operator_type": role_type,
                        "operator_id": role_id,
                        "table_name": "p_join_guarantors",
                        "field_name": None,
                        "table_id": old_p_join_guarantor["id"],
                        "content": None,
                        "operate_type": OPERATE_TYPE.DELETE.value,
                    },
                )
            )
        )
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
            continue
        [old_p_resident] = filter
        for key, value in p_resident.items():
            old_value = old_p_resident.get(key, "")

            if value == old_value:
                continue
            # field deleted
            if not value and old_value:
                JOBS.append(
                    db.execute(
                        utils.gen_insert_sql(
                            "p_activities",
                            {
                                "id": await db.uuid_short(),
                                "p_application_header_id": p_application_header_id,
                                "operator_type": role_type,
                                "operator_id": role_id,
                                "table_name": "p_residents",
                                "field_name": key,
                                "table_id": old_p_resident["id"],
                                "content": None,
                                "operate_type": OPERATE_TYPE.DELETE.value,
                            },
                        )
                    )
                )

            # field update
            else:
                total = await crud.query_update_history_count(
                    db, p_application_header_id, "p_residents", key, old_p_resident["id"]
                )
                if total == 0:
                    JOBS.append(
                        db.execute(
                            utils.gen_insert_sql(
                                "p_activities",
                                {
                                    "id": await db.uuid_short(),
                                    "p_application_header_id": p_application_header_id,
                                    "operator_type": role_type,
                                    "operator_id": role_id,
                                    "table_name": "p_residents",
                                    "field_name": key,
                                    "table_id": old_p_resident["id"],
                                    "content": old_value if old_value != "" else None,
                                    "operate_type": OPERATE_TYPE.APPLY.value,
                                },
                            )
                        )
                    )
                JOBS.append(
                    db.execute(
                        utils.gen_insert_sql(
                            "p_activities",
                            {
                                "id": await db.uuid_short(),
                                "p_application_header_id": p_application_header_id,
                                "operator_type": role_type,
                                "operator_id": role_id,
                                "table_name": "p_residents",
                                "field_name": key,
                                "table_id": old_p_resident["id"],
                                "content": value,
                                "operate_type": OPERATE_TYPE.UPDATE.value,
                            },
                        )
                    )
                )

            JOBS.append(db.execute(utils.gen_update_sql("p_residents", {key: value}, {"id": old_p_resident["id"]})))

    for old_p_resident in old_p_residents:
        filter = [item for item in data if item["id"] == old_p_resident["id"]]
        if len(filter) > 0:
            continue
        JOBS.append(
            db.execute(
                utils.gen_insert_sql(
                    "p_activities",
                    {
                        "id": await db.uuid_short(),
                        "p_application_header_id": p_application_header_id,
                        "operator_type": role_type,
                        "operator_id": role_id,
                        "table_name": "p_residents",
                        "field_name": None,
                        "table_id": old_p_resident["id"],
                        "content": None,
                        "operate_type": OPERATE_TYPE.DELETE.value,
                    },
                )
            )
        )
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
            continue
        [old_p_borrowing] = filter
        for key, value in p_borrowing.items():
            if key in ["I"]:
                sql = f"""
                SELECT
                    CONVERT(id,CHAR) AS id,
                    s3_key,
                    file_name
                FROM
                    p_uploaded_files
                WHERE
                    p_application_header_id = {p_application_header_id}
                    AND
                    record_id = {old_p_borrowing["id"]}
                    AND
                    deleted IS NULL
                    AND
                    owner_type = 1
                    AND
                    type = 0
                    AND
                    s3_key LIKE '%/{key}%';
                """
                old_files_info = await db.fetch_all(sql)
                old_files_id = [item["id"] for item in old_files_info]
                un_update_files_id = []

                for update_file in value:
                    if update_file["id"] in old_files_id:
                        un_update_files_id.append(update_file["id"])
                        continue
                    # add file
                    p_upload_file_id = await db.uuid_short()
                    p_upload_file_sql_params = {
                        "id": p_upload_file_id,
                        "p_application_header_id": p_application_header_id,
                        "owner_type": role_type,
                        "owner_id": role_id,
                        "record_id": old_p_borrowing["id"],
                        "type": P_UPLOAD_FILE_TYPE.APPLICANT.value,
                        # "s3_key": f"{p_application_header_id}/{p_upload_file_id}/{key}",
                        "s3_key": f"{p_application_header_id}/{role_id}_{OWNER_TYPE_EN_MAPS[role_type]}/{key}/{p_upload_file_id}",
                        "file_name": update_file["name"],
                    }
                    utils.upload_base64_file_s3(
                        f"{p_upload_file_sql_params.get('s3_key')}/{p_upload_file_sql_params.get('file_name')}",
                        update_file["src"],
                    )
                    await db.execute(utils.gen_insert_sql("p_uploaded_files", p_upload_file_sql_params))

                    total = await crud.query_update_history_count(
                        db, p_application_header_id, "p_borrowings", key, old_p_borrowing["id"]
                    )
                    if total == 0 and len(old_files_info) == 0:
                        JOBS.append(
                            db.execute(
                                utils.gen_insert_sql(
                                    "p_activities",
                                    {
                                        "id": await db.uuid_short(),
                                        "p_application_header_id": p_application_header_id,
                                        "operator_type": role_type,
                                        "operator_id": role_id,
                                        "table_name": "p_borrowings",
                                        "field_name": key,
                                        "table_id": old_p_borrowing["id"],
                                        "content": None,
                                        "operate_type": OPERATE_TYPE.APPLY.value,
                                    },
                                )
                            )
                        )
                    if total == 0 and len(old_files_info) > 0:
                        for old_file in old_files_info:
                            JOBS.append(
                                db.execute(
                                    utils.gen_insert_sql(
                                        "p_activities",
                                        {
                                            "id": await db.uuid_short(),
                                            "p_application_header_id": p_application_header_id,
                                            "operator_type": role_type,
                                            "operator_id": role_id,
                                            "table_name": "p_borrowings",
                                            "field_name": key,
                                            "table_id": old_p_borrowing["id"],
                                            "content": old_file["file_name"],
                                            "operate_type": OPERATE_TYPE.APPLY.value,
                                        },
                                    )
                                )
                            )
                    JOBS.append(
                        db.execute(
                            utils.gen_insert_sql(
                                "p_activities",
                                {
                                    "id": await db.uuid_short(),
                                    "p_application_header_id": p_application_header_id,
                                    "operator_type": role_type,
                                    "operator_id": role_id,
                                    "table_name": "p_borrowings",
                                    "field_name": key,
                                    "table_id": old_p_borrowing["id"],
                                    "content": update_file["name"],
                                    "operate_type": OPERATE_TYPE.UPDATE.value,
                                },
                            )
                        )
                    )

                # delete file
                delete_files_id = list(set(old_files_id) - set(un_update_files_id))
                if len(delete_files_id) == 0:
                    continue
                delete_files_info = await db.fetch_all(
                    f"SELECT CONVERT(id,CHAR) AS id, s3_key, file_name FROM p_uploaded_files WHERE id IN ({', '.join(delete_files_id)});"
                )

                for delete_file_info in delete_files_info:
                    sql = f"UPDATE p_uploaded_files SET deleted = 1 WHERE id = {delete_file_info['id']};"
                    JOBS.append(db.execute(sql))
                    JOBS.append(
                        db.execute(
                            utils.gen_insert_sql(
                                "p_activities",
                                {
                                    "id": await db.uuid_short(),
                                    "p_application_header_id": p_application_header_id,
                                    "operator_type": role_type,
                                    "operator_id": role_id,
                                    "table_name": "p_borrowings",
                                    "field_name": key,
                                    "table_id": old_p_borrowing["id"],
                                    "content": delete_file_info["file_name"],
                                    "operate_type": OPERATE_TYPE.DELETE.value,
                                },
                            )
                        )
                    )
                continue

            old_value = old_p_borrowing.get(key, "")

            if value == old_value:
                continue
            # field deleted
            if not value and old_value:
                JOBS.append(
                    db.execute(
                        utils.gen_insert_sql(
                            "p_activities",
                            {
                                "id": await db.uuid_short(),
                                "p_application_header_id": p_application_header_id,
                                "operator_type": role_type,
                                "operator_id": role_id,
                                "table_name": "p_borrowings",
                                "field_name": key,
                                "table_id": old_p_borrowing["id"],
                                "content": None,
                                "operate_type": OPERATE_TYPE.DELETE.value,
                            },
                        )
                    )
                )

            # field update
            else:
                total = await crud.query_update_history_count(
                    db, p_application_header_id, "p_borrowings", key, old_p_borrowing["id"]
                )
                if total == 0:
                    JOBS.append(
                        db.execute(
                            utils.gen_insert_sql(
                                "p_activities",
                                {
                                    "id": await db.uuid_short(),
                                    "p_application_header_id": p_application_header_id,
                                    "operator_type": role_type,
                                    "operator_id": role_id,
                                    "table_name": "p_borrowings",
                                    "field_name": key,
                                    "table_id": old_p_borrowing["id"],
                                    "content": old_value if old_value != "" else None,
                                    "operate_type": OPERATE_TYPE.APPLY.value,
                                },
                            )
                        )
                    )
                JOBS.append(
                    db.execute(
                        utils.gen_insert_sql(
                            "p_activities",
                            {
                                "id": await db.uuid_short(),
                                "p_application_header_id": p_application_header_id,
                                "operator_type": role_type,
                                "operator_id": role_id,
                                "table_name": "p_borrowings",
                                "field_name": key,
                                "table_id": old_p_borrowing["id"],
                                "content": value,
                                "operate_type": OPERATE_TYPE.UPDATE.value,
                            },
                        )
                    )
                )

            JOBS.append(db.execute(utils.gen_update_sql("p_borrowings", {key: value}, {"id": old_p_borrowing["id"]})))

    for old_p_borrowing in old_p_borrowings:
        filter = [item for item in data if item["id"] == old_p_borrowing["id"]]
        if len(filter) > 0:
            continue
        JOBS.append(
            db.execute(
                utils.gen_insert_sql(
                    "p_activities",
                    {
                        "id": await db.uuid_short(),
                        "p_application_header_id": p_application_header_id,
                        "operator_type": role_type,
                        "operator_id": role_id,
                        "table_name": "p_borrowings",
                        "field_name": None,
                        "table_id": old_p_borrowing["id"],
                        "content": None,
                        "operate_type": OPERATE_TYPE.DELETE.value,
                    },
                )
            )
        )
        sql = f"DELETE FROM p_borrowings WHERE id = {old_p_borrowing['id']};"
        JOBS.append(db.execute(sql))
        for delete_file_info in old_p_borrowing["I"]:
            sql = f"UPDATE p_uploaded_files SET deleted = 1 WHERE id = {delete_file_info['id']};"
            JOBS.append(db.execute(sql))
    if JOBS:
        await asyncio.wait(JOBS)


async def query_p_application_headers_files_for_ap(db: DB, p_application_header_id):
    file_keys = ["G", "J", "R"]
    files = {
        "G": [],
        "J": [],
        "R": [],
    }
    for key in file_keys:
        sql = f"""
        SELECT
            CONVERT(id,CHAR) AS id,
            s3_key,
            file_name
        FROM
            p_uploaded_files
        WHERE
            p_application_header_id = {p_application_header_id}
            AND
            owner_type = 1
            AND
            type = {P_UPLOAD_FILE_TYPE.APPLICANT.value}
            AND
            deleted IS NULL
            AND
            s3_key LIKE '%/{key}%';
        """
        files_info = await db.fetch_all(sql)
        temp_files = []
        for file_info in files_info:
            src = utils.generate_presigned_url(f"{file_info['s3_key']}/{file_info['file_name']}")
            temp_files.append({"id": file_info["id"], "name": file_info["file_name"], "src": src})
        files[key] = temp_files
    return files


async def query_p_applicant_persons_files_for_ap(db: DB, p_application_header_id: int, type: int):
    file_keys = [
        "H__a",
        "H__b",
        "A__01__a",
        "A__01__b",
        "A__02",
        "A__03__a",
        "A__03__b",
        "B__a",
        "B__b",
        "C__01",
        "C__02",
        "C__03",
        "C__04",
        "C__05",
        "D__01",
        "D__02",
        "D__03",
        "E",
        "F__01",
        "F__02",
        "F__03",
        "K",
    ]
    files = {
        "H__a": [],
        "H__b": [],
        "A__01__a": [],
        "A__01__b": [],
        "A__02": [],
        "A__03__a": [],
        "A__03__b": [],
        "B__a": [],
        "B__b": [],
        "C__01": [],
        "C__02": [],
        "C__03": [],
        "C__04": [],
        "C__05": [],
        "D__01": [],
        "D__02": [],
        "D__03": [],
        "E": [],
        "F__01": [],
        "F__02": [],
        "F__03": [],
        "K": [],
    }
    if type == 0:
        file_keys.append("S")
        files["S"] = []
    for key in file_keys:
        sql = f"""
        SELECT
            CONVERT(id,CHAR) AS id,
            s3_key,
            file_name
        FROM
            p_uploaded_files
        WHERE
            p_application_header_id = {p_application_header_id}
            AND
            owner_type = 1
            AND
            type = {type}
            AND
            deleted IS NULL
            AND
            s3_key LIKE '%/{key}%';
        """
        files_info = await db.fetch_all(sql)
        temp_files = []
        for file_info in files_info:
            src = utils.generate_presigned_url(f"{file_info['s3_key']}/{file_info['file_name']}")
            temp_files.append({"id": file_info["id"], "name": file_info["file_name"], "src": src})
        files[key] = temp_files
    return files


async def query_p_borrowings_files_for_ap(db: DB, p_application_header_id: int):
    sql = f"""
    SELECT
        CONVERT(id,CHAR) AS borrowing_id
    FROM
        p_borrowings
    WHERE
        p_application_header_id = {p_application_header_id};
    """
    result = await db.fetch_all(sql)
    borrowings = []
    for borrowing in result:
        file_keys = ["I"]
        files = {"I": []}
        for key in file_keys:
            sql = f"""
            SELECT
                CONVERT(id,CHAR) AS id,
                s3_key,
                file_name
            FROM
                p_uploaded_files
            WHERE
                p_application_header_id = {p_application_header_id}
                AND
                record_id = {borrowing["borrowing_id"]}
                AND
                owner_type = 1
                AND
                type = {P_UPLOAD_FILE_TYPE.APPLICANT.value}
                AND
                deleted IS NULL
                AND
                s3_key LIKE '%/{key}%';
            """
            files_info = await db.fetch_all(sql)
            temp_files = []
            for file_info in files_info:
                src = utils.generate_presigned_url(f"{file_info['s3_key']}/{file_info['file_name']}")
                temp_files.append({"id": file_info["id"], "name": file_info["file_name"], "src": src})
            files[key] = temp_files
        borrowings.append(none_to_blank({**borrowing, **files}))

    return borrowings
