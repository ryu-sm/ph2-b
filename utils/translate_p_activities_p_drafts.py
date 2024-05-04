import json
from constant import OPERATE_TYPE
from core.database import DB
import yaml
from datetime import date
import utils
from .db_filed_maps import (
    p_drafts_p_application_headers_sub_main,
    p_drafts_p_application_headers_sub_person,
    p_drafts_p_application_headers_sub_file,
    p_drafts_p_applicant_persons_0_sub_main,
    p_drafts_p_applicant_persons_1_sub_main,
    p_drafts_p_applicant_persons_sub_file,
    p_drafts_p_borrowing_details__1,
    p_drafts_p_borrowing_details__2,
    p_drafts_p_borrowings_sub_main,
    p_drafts_p_borrowings_sub_file,
    p_drafts_p_join_guarantors,
    p_drafts_p_residents,
    p_drafts_p_application_headers_sub_p_referral_agency,
)


def construct_ruby_bigdecimal(loader, node):
    value = loader.construct_scalar(node)
    f_str = value.split(":")[1]
    return "{:.2f}".format(float(f_str))


yaml.SafeLoader.add_constructor("!ruby/object:BigDecimal", construct_ruby_bigdecimal)


owner_type_maps = {
    "User": 1,
    "SSalePerson": 2,
    "Manager": 3,
}


async def translate_p_activities_p_drafts(db: DB, old_draft_id=61):
    # p_drafts
    sql = f"""
    SELECT
        *
    FROM
        mortgage_loan_tool_be_production.drafts as d
    WHERE
        d.id = {old_draft_id};
    """

    p_draft = await db.fetch_one(sql)

    new_p_draft = {
        "p_applicant_persons_a_agreement": True,
        "p_applicant_persons_b_agreement": False,
    }
    p_application_header = yaml.safe_load(
        p_draft["p_application_header"].replace("!ruby/hash:ActiveSupport::HashWithIndifferentAccess", "")
    )
    p_applicant_people = yaml.safe_load(
        p_draft["p_applicant_people"].replace("!ruby/hash:ActiveSupport::HashWithIndifferentAccess", "")
    )
    p_borrowing_details = json.loads(yaml.safe_load(p_draft["p_borrowing_details"]))

    p_borrowings_ = yaml.safe_load(
        p_draft["p_borrowings"].replace("!ruby/hash:ActiveSupport::HashWithIndifferentAccess", "")
    )

    p_join_guarantors_ = json.loads(yaml.safe_load(p_draft["p_join_guarantors"]))

    p_residents_ = json.loads(yaml.safe_load(p_draft["p_residents"]))

    p_referral_agency = yaml.safe_load(
        p_draft["p_referral_agency"].replace("!ruby/hash:ActiveSupport::HashWithIndifferentAccess", "")
    )

    p_application_headers = {}
    # 常规转换
    for new_key, old_key in p_drafts_p_application_headers_sub_main.items():
        if old_key in p_application_header:
            if new_key in ["property_business_type", "refund_source_type"]:
                p_application_headers[new_key] = p_application_header[old_key] if p_application_header[old_key] else []
                continue
            if new_key == "loan_plus":
                p_application_headers[new_key] = "1" if p_application_header[old_key] == "true" else "0"
                continue

            p_application_headers[new_key] = p_application_header[old_key]

    for new_key, old_key in p_drafts_p_application_headers_sub_p_referral_agency.items():
        if old_key in p_referral_agency:
            if old_key in ["sale_agent_id", "store_id", "exhibition_id"]:
                org = await db.fetch_one(
                    f"SELECT id FROM s_sales_company_orgs WHERE code = '{p_referral_agency[old_key]}';"
                )
                p_application_headers[new_key] = str(org["id"]) if org else ""
                continue
            p_application_headers[new_key] = p_referral_agency[old_key]
    # 文件转换
    for new_key, old_key in p_drafts_p_application_headers_sub_file.items():
        sql = f"""
        SELECT
            b.key,
            b.filename
        FROM
            mortgage_loan_tool_be_production.active_storage_attachments as a
        JOIN
            mortgage_loan_tool_be_production.active_storage_blobs as b
            ON
            b.id = a.blob_id
        WHERE
            a.name = '{old_key}'
            AND
            a.record_type = 'Draft'
            AND
            a.record_id = {old_draft_id};
        """
        files = await db.fetch_all(sql)
        temp = []
        for file in files:
            base64_encoded_data = utils.download_from_s3(file["key"])
            temp.append({"name": file["filename"], "src": base64_encoded_data})
        p_application_headers[new_key] = temp

    p_applicant_persons_type_0 = p_applicant_people[0]
    for new_key, old_key in p_drafts_p_application_headers_sub_person.items():
        if old_key in p_applicant_persons_type_0:
            if old_key == "lived_length_year_num" or old_key == "lived_length_month_num":
                p_application_headers[new_key] = (
                    str(int(p_applicant_persons_type_0[old_key])) if p_applicant_persons_type_0[old_key] else ""
                )
                continue
            if old_key == "expected_house_selling_price":
                p_application_headers[new_key] = (
                    str(int(p_applicant_persons_type_0[old_key]) * 10000) if p_applicant_persons_type_0[old_key] else ""
                )
                continue
            p_application_headers[new_key] = p_applicant_persons_type_0[old_key]

    # 逻辑转换
    if "planned_cohabitant" in p_application_header:
        planned_cohabitant = p_application_header.get("planned_cohabitant", [])
        children_number = p_application_header.get("children_number")
        siblings_number = p_application_header.get("siblings_number")
        other_relationship = p_application_header.get("other_relationship")
        other_people_number = p_application_header.get("other_people_number")
        parse_data = {
            "spouse": "1" if "1" in planned_cohabitant else "",
            "children": str(children_number) if "2" in planned_cohabitant else "",
            "father": "1" if "3" in planned_cohabitant else "",
            "mother": "1" if "4" in planned_cohabitant else "",
            "brothers_sisters": str(siblings_number) if "5" in planned_cohabitant else "",
            "fiance": "1" if "6" in planned_cohabitant else "",
            "others": str(other_people_number) if "99" in planned_cohabitant else "",
            "others_rel": other_relationship if other_relationship else "",
            "spouse_umu": True if "1" in planned_cohabitant else False,
            "children_umu": True if "2" in planned_cohabitant else False,
            "father_umu": True if "3" in planned_cohabitant else False,
            "mother_umu": True if "4" in planned_cohabitant else False,
            "brothers_sisters_umu": True if "5" in planned_cohabitant else False,
            "fiance_umu": True if "6" in planned_cohabitant else False,
            "others_umu": True if "99" in planned_cohabitant else False,
        }
        p_application_headers["new_house_planned_resident_overview"] = parse_data
    else:
        default = {
            "spouse": "",
            "children": "",
            "father": "",
            "mother": "",
            "brothers_sisters": "",
            "fiance": "",
            "others": "",
            "others_rel": "",
            "spouse_umu": False,
            "children_umu": False,
            "father_umu": False,
            "mother_umu": False,
            "brothers_sisters_umu": False,
            "fiance_umu": False,
            "others_umu": False,
        }
        p_application_headers["new_house_planned_resident_overview"] = default
    # 主逻辑
    if "general_income_confirmation" in p_application_header:
        new_p_draft["p_applicant_persons_b_agreement"] = (
            True if p_application_header["general_income_confirmation"] == "1" else False
        )
    new_p_draft["apCurrStepId"] = int(p_draft["current_step"])
    new_p_draft["p_application_headers"] = utils.to_mann(p_application_headers)

    p_application_banks = []
    if "master_bank_ids" in p_application_header:
        bank_maps = {"1": "0038", "2": "6670"}

        for bank_id in p_application_header["master_bank_ids"]:
            bank_code = bank_maps[bank_id]
            new_bank = await db.fetch_one(f"SELECT id FROM mortgage_staging_v1.s_banks WHERE code = '{bank_code}';")
            p_application_banks.append(str(new_bank["id"]))

    new_p_draft["isMCJ"] = True if len(p_application_banks) > 1 else False
    new_p_draft["p_application_banks"] = p_application_banks

    p_applicant_persons__0 = {}
    p_applicant_persons__1 = {}

    for new_key, old_key in p_drafts_p_applicant_persons_0_sub_main.items():
        if old_key in p_applicant_persons_type_0:
            if new_key in ["income_sources", "tax_return_reasons"]:
                p_applicant_persons__0[new_key] = (
                    p_applicant_persons_type_0[old_key] if p_applicant_persons_type_0[old_key] else []
                )
                continue

            if old_key == "identity_verification":
                p_applicant_persons__0[new_key] = (
                    str(int(p_applicant_persons_type_0[old_key]) + 1) if p_applicant_persons_type_0[old_key] else ""
                )
                continue

            p_applicant_persons__0[new_key] = p_applicant_persons_type_0[old_key]

    # 文件转换
    for new_key, old_key in p_drafts_p_applicant_persons_sub_file.items():
        sql = f"""
        SELECT
            b.key,
            b.filename
        FROM
            mortgage_loan_tool_be_production.active_storage_attachments as a
        JOIN
            mortgage_loan_tool_be_production.active_storage_blobs as b
            ON
            b.id = a.blob_id
        WHERE
            a.name = '{old_key}'
            AND
            a.record_type = 'Draft'
            AND
            a.record_id = {old_draft_id}
            AND
            b.filename LIKE '<0>%';
        """
        files = await db.fetch_all(sql)
        temp = []
        for file in files:
            base64_encoded_data = utils.download_from_s3(file["key"])
            temp.append({"name": file["filename"].replace(f"<0>", ""), "src": base64_encoded_data})
        p_applicant_persons__0[new_key] = temp

    new_p_draft["p_applicant_persons__0"] = utils.to_mann(p_applicant_persons__0)

    if p_application_header["loan_type"] in ["3", "4"]:
        p_applicant_persons_type_1 = p_applicant_people[1]
        for new_key, old_key in p_drafts_p_applicant_persons_1_sub_main.items():
            if old_key in p_applicant_persons_type_1:
                if new_key in ["income_sources", "tax_return_reasons"]:
                    p_applicant_persons__1[new_key] = (
                        p_applicant_persons_type_1[old_key] if p_applicant_persons_type_1[old_key] else []
                    )
                    continue
                if old_key == "identity_verification":
                    p_applicant_persons__1[new_key] = (
                        str(int(p_applicant_persons_type_1[old_key]) + 1) if p_applicant_persons_type_1[old_key] else ""
                    )
                    continue
                p_applicant_persons__1[new_key] = p_applicant_persons_type_1[old_key]

        # 文件转换
        for new_key, old_key in p_drafts_p_applicant_persons_sub_file.items():
            sql = f"""
            SELECT
                b.key,
                b.filename
            FROM
                mortgage_loan_tool_be_production.active_storage_attachments as a
            JOIN
                mortgage_loan_tool_be_production.active_storage_blobs as b
                ON
                b.id = a.blob_id
            WHERE
                a.name = '{old_key}'
                AND
                a.record_type = 'Draft'
                AND
                a.record_id = {old_draft_id}
                AND
                b.filename LIKE '<1>%';
            """
            files = await db.fetch_all(sql)
            temp = []
            for file in files:
                base64_encoded_data = utils.download_from_s3(file["key"])
                temp.append({"name": file["filename"].replace(f"<1>", ""), "src": base64_encoded_data})
            p_applicant_persons__1[new_key] = temp

        new_p_draft["p_applicant_persons__1"] = utils.to_mann(p_applicant_persons__1)

    p_borrowing_details_time_1 = p_borrowing_details[0]

    p_borrowing_details__1 = {}
    p_borrowing_details__2 = {}

    for new_key, old_key in p_drafts_p_borrowing_details__1.items():
        if old_key in p_borrowing_details_time_1:
            p_borrowing_details__1[new_key] = p_borrowing_details_time_1[old_key]

    new_p_draft["p_borrowing_details__1"] = utils.to_mann(p_borrowing_details__1)

    if "has_land_advance_plan" in p_application_header and p_application_header["has_land_advance_plan"] == "1":
        p_borrowing_details_time_2 = p_borrowing_details[1]
        for new_key, old_key in p_drafts_p_borrowing_details__2.items():
            if old_key in p_borrowing_details_time_2:
                p_borrowing_details__2[new_key] = p_borrowing_details_time_2[old_key]
        new_p_draft["p_borrowing_details__2"] = utils.to_mann(p_borrowing_details__2)

    p_borrowings = []
    for index, p_borrowing_ in enumerate(p_borrowings_):
        p_borrowing = {
            "id": "",
            "self_input": "",
            "borrower": "",
            "type": "",
            "lender": "",
            "borrowing_from_house_finance_agency": "",
            "loan_start_date": "",
            "loan_amount": "",
            "curr_loan_balance_amount": "",
            "annual_repayment_amount": "",
            "loan_end_date": "",
            "scheduled_loan_payoff": "",
            "scheduled_loan_payoff_date": "",
            "loan_business_target": "",
            "loan_business_target_other": "",
            "loan_purpose": "",
            "loan_purpose_other": "",
            "category": "",
            "card_expiry_date": "",
            "rental_room_num": "",
            "common_housing": "",
            "estate_setting": "",
            "I": "",
        }
        for new_key, old_key in p_drafts_p_borrowings_sub_main.items():
            if old_key in p_borrowing_:
                if old_key == "self_input":
                    p_borrowing[new_key] = "1" if p_borrowing_[old_key] == "true" else "0"
                    continue
                p_borrowing[new_key] = p_borrowing_[old_key]
        for new_key, old_key in p_drafts_p_borrowings_sub_file.items():
            sql = f"""
            SELECT
                b.key,
                b.filename
            FROM
                mortgage_loan_tool_be_production.active_storage_attachments as a
            JOIN
                mortgage_loan_tool_be_production.active_storage_blobs as b
                ON
                b.id = a.blob_id
            WHERE
                a.name = '{old_key}'
                AND
                a.record_type = 'Draft'
                AND
                a.record_id = {old_draft_id}
                AND
                b.filename LIKE '<{index}>%';
            """
            files = await db.fetch_all(sql)
            temp = []
            for file in files:
                base64_encoded_data = utils.download_from_s3(file["key"])
                temp.append({"name": file["filename"].replace(f"<{index}>", ""), "src": base64_encoded_data})
            p_borrowing[new_key] = temp
        p_borrowings.append(utils.to_mann(p_borrowing))

    if p_borrowings:
        new_p_draft["p_borrowings"] = p_borrowings

    p_join_guarantors = []
    for p_join_guarantor_ in p_join_guarantors_:
        p_join_guarantor = {
            "id": "",
            "last_name_kanji": "",
            "first_name_kanji": "",
            "last_name_kana": "",
            "first_name_kana": "",
            "gender": "",
            "rel_to_applicant_a_name": "",
            "birthday": "",
            "mobile_phone": "",
            "home_phone": "",
            "postal_code": "",
            "prefecture_kanji": "",
            "city_kanji": "",
            "district_kanji": "",
            "other_address_kanji": "",
            "prefecture_kana": "",
            "city_kana": "",
            "district_kana": "",
        }
        for new_key, old_key in p_drafts_p_join_guarantors.items():
            if old_key in p_join_guarantor_:
                p_join_guarantor[new_key] = p_join_guarantor_[old_key]
        p_join_guarantors.append(utils.to_mann(p_join_guarantor))

    if p_join_guarantors:
        new_p_draft["p_join_guarantors"] = p_join_guarantors

    p_residents = []
    for p_resident_ in p_residents_:
        p_resident = {
            "id": "",
            "resident_type": "",
            "last_name_kanji": "",
            "first_name_kanji": "",
            "last_name_kana": "",
            "first_name_kana": "",
            "rel_to_applicant_a_name": "",
            "nationality": "",
            "birthday": "",
            "loan_from_japan_house_finance_agency": "",
            "contact_phone": "",
            "postal_code": "",
            "prefecture_kanji": "",
            "city_kanji": "",
            "district_kanji": "",
            "other_address_kanji": "",
            "prefecture_kana": "",
            "city_kana": "",
            "district_kana": "",
        }
        for new_key, old_key in p_drafts_p_residents.items():
            if old_key in p_resident_:
                p_resident[new_key] = p_resident_[old_key]
        p_residents.append(utils.to_mann(p_resident))

    if p_residents:
        new_p_draft["p_residents"] = p_residents
    new_user = await db.fetch_one(
        f"""SELECT id FROM mortgage_staging_v1.c_users as u WHERE u.old_id = {p_draft["user_id"]};"""
    )
    new_p_draft_json = json.dumps(new_p_draft, ensure_ascii=False)
    id = await db.uuid_short()
    sql = f"""INSERT INTO mortgage_staging_v1.p_drafts (id, c_user_id, data)
    VALUES ({id}, {new_user["id"]}, '{new_p_draft_json}')
    """
    await db.execute(sql)

    with open("data.json", "w") as json_file:
        json.dump(new_p_draft, json_file, ensure_ascii=False)
    # print(json.dumps(p_borrowings, ensure_ascii=False, indent=4))
