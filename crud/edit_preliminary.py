import json
import crud
from core.database import DB
from constant import JSON_FIELD_KEYS
from utils import none_to_blank
import crud


async def query_p_application_headers_for_ad(db: DB, p_application_header_id):
    sbi = await db.fetch_one("SELECT id, name FROM s_banks WHERE code = '0038';")
    sbi_id = sbi["id"]
    sql = f"""
    SELECT
        p_application_headers.apply_no,
        DATE_FORMAT(p_application_headers.created_at, '%Y/%m/%d %h:%m') as created_at,
        DATE_FORMAT(p_application_headers.apply_date, '%Y/%m/%d') as apply_date,
        p_application_headers.move_scheduled_date,
        p_application_headers.loan_target,
        p_application_headers.land_advance_plan,
        p_application_headers.loan_type,
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
        DATE_FORMAT(p_application_headers.curr_house_shell_scheduled_date, '%Y/%m/%d') as curr_house_shell_scheduled_date,
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
        property_flat_35_plan,
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
        p_application_headers.funding_other_loan_amount
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


async def query_p_application_banks_for_ad(db: DB, p_application_header_id: int):
    sql = f"SELECT CONVERT(s_bank_id,CHAR) AS s_bank_id FROM p_application_banks WHERE p_application_header_id={p_application_header_id};"
    result = await db.fetch_all(sql)
    return [item["s_bank_id"] for item in result]


async def query_p_applicant_persons_for_ad(db: DB, p_application_header_id: int, type: int):
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
        before_last_year_bonus_income
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
        rel_to_applicant_a,
        rel_to_applicant_a_other,
        birthday,
        gender,
        one_roof
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
    return await db.fetch_all(sql)
