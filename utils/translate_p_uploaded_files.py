from core.database import DB
import utils
import yaml


def construct_ruby_bigdecimal(loader, node):
    value = loader.construct_scalar(node)
    f_str = value.split(":")[1]
    return "{:.2f}".format(float(f_str))


yaml.SafeLoader.add_constructor("!ruby/object:BigDecimal", construct_ruby_bigdecimal)


prekey_maps = {
    "driver_license_back_image": "A__01__a",
    "driver_license_front_image": "A__01__b",
    "card_number_front_image": "A__02",
    "resident_register_back_image": "A__03__a",
    "resident_register_front_image": "A__03__b",
    "insurance_file": "B__a",
    "insurance_file_back_image": "B__b",
    "first_withholding_slip_file": "C__01",
    "second_withholding_slip_file": "C__02",
    "first_income_file": "C__03",
    "second_income_file": "C__04",
    "third_income_file": "C__05",
    "financial_statement_1_file": "D__01",
    "financial_statement_2_file": "D__02",
    "financial_statement_3_file": "D__03",
    "employment_agreement_file": "E",
    "business_tax_return_1_file": "F__01",
    "business_tax_return_2_file": "F__02",
    "business_tax_return_3_file": "F__03",
    "property_information_file": "G",
    "residence_file": "H__a",
    "residence_file_back_image": "H__b",
    "repayment_schedule_image": "I",
    "business_card": "J",
    "other_document_file": "K",
    "examination_file": "R",
}

owner_type_maps = {
    "User": 1,
    "SSalePerson": 2,
    "Manager": 3,
}

owner_type_kanji_maps = {
    1: "USER",
    2: "SALES_PERSON",
    3: "MANAGER",
}


async def translate_p_uploaded_files(db: DB):
    new_data = []
    sql = """
    SELECT
        aa.name as old_prekey,
        aa.record_id as old_record_id,
        aa.created_at as created_at,
        aa.role_type as role_type,
        aa.role_id as role_id,
        ab.key as old_s3_key,
        ab.filename as old_filename,
        DATE_FORMAT(aa.created_at, '%Y-%m-%d %H:%i:%S') as old_created_at
    FROM
        mortgage_loan_tool_be_production.active_storage_attachments as aa
    INNER JOIN
        mortgage_loan_tool_be_production.active_storage_blobs as ab
        ON
        aa.blob_id = ab.id
    WHERE
        aa.record_type = 'PApplicationHeader';
    """

    old_files_info = await db.fetch_all(sql)

    for old_file_info in old_files_info:
        id = await db.uuid_short()
        owner_type = owner_type_maps.get(old_file_info["role_type"])
        owner_id = 0
        if owner_type == 1:
            user = await db.fetch_one(
                f"SELECT id FROM mortgage_staging_v1.c_users WHERE old_id = {old_file_info['role_id']};"
            )
            if user:
                owner_id = user["id"]
        if owner_type == 2:
            sales_person = await db.fetch_one(
                f"SELECT id FROM mortgage_staging_v1.s_sales_persons WHERE old_id = {old_file_info['role_id']};"
            )
            if sales_person:
                owner_id = sales_person["id"]
        if owner_type == 3:
            manager = await db.fetch_one(
                f"SELECT id FROM mortgage_staging_v1.s_managers WHERE old_id = {old_file_info['role_id']};"
            )
            if manager:
                owner_id = manager["id"]
        p_application_header_id = None
        p_application_header = await db.fetch_one(
            f"SELECT id FROM mortgage_staging_v1.p_application_headers WHERE old_id = {old_file_info['old_record_id']};"
        )
        if p_application_header:
            p_application_header_id = p_application_header["id"]

        s3_key = f"{p_application_header_id}/{owner_id}_{owner_type_kanji_maps[owner_type]}/{prekey_maps[old_file_info['old_prekey']]}/{id}"
        new_data.append(
            {
                "id": id,
                "owner_type": owner_type,
                "owner_id": owner_id,
                "p_application_header_id": p_application_header_id,
                "record_id": p_application_header_id,
                "type": 0,
                "s3_key": s3_key,
                "file_name": old_file_info["old_filename"],
                "created_at": old_file_info["old_created_at"],
            }
        )
        base64_encoded_data = utils.download_from_s3(old_file_info["old_s3_key"])
        utils.upload_base64_file_s3(f"{s3_key}/{old_file_info['old_filename']}", base64_encoded_data)

    sql = """
    SELECT
        aa.name as old_prekey,
        aa.record_id as old_record_id,
        aa.created_at as created_at,
        aa.role_type as role_type,
        aa.role_id as role_id,
        ab.key as old_s3_key,
        ab.filename as old_filename,
        DATE_FORMAT(aa.created_at, '%Y-%m-%d %H:%i:%S') as old_created_at
    FROM
        mortgage_loan_tool_be_production.active_storage_attachments as aa
    INNER JOIN
        mortgage_loan_tool_be_production.active_storage_blobs as ab
        ON
        aa.blob_id = ab.id
    WHERE
        aa.record_type = 'PApplicantPerson';
    """

    old_files_info = await db.fetch_all(sql)

    for old_file_info in old_files_info:
        id = await db.uuid_short()
        owner_type = owner_type_maps.get(old_file_info["role_type"])
        owner_id = 0
        if owner_type == 1:
            user = await db.fetch_one(
                f"SELECT id FROM mortgage_staging_v1.c_users WHERE old_id = {old_file_info['role_id']};"
            )
            if user:
                owner_id = user["id"]
        if owner_type == 2:
            sales_person = await db.fetch_one(
                f"SELECT id FROM mortgage_staging_v1.s_sales_persons WHERE old_id = {old_file_info['role_id']};"
            )
            if sales_person:
                owner_id = sales_person["id"]
        if owner_type == 3:
            manager = await db.fetch_one(
                f"SELECT id FROM mortgage_staging_v1.s_managers WHERE old_id = {old_file_info['role_id']};"
            )
            if manager:
                owner_id = manager["id"]
        p_applicant_persons = await db.fetch_one(
            f"SELECT id, p_application_header_id, type FROM mortgage_staging_v1.p_applicant_persons WHERE old_id = {old_file_info['old_record_id']};"
        )

        s3_key = f"{p_applicant_persons['p_application_header_id']}/{owner_id}_{owner_type_kanji_maps[owner_type]}/{prekey_maps[old_file_info['old_prekey']]}/{id}"
        new_data.append(
            {
                "id": id,
                "owner_type": owner_type,
                "owner_id": owner_id,
                "p_application_header_id": p_applicant_persons["p_application_header_id"],
                "record_id": p_applicant_persons["id"],
                "type": p_applicant_persons["type"],
                "s3_key": s3_key,
                "file_name": old_file_info["old_filename"],
                "created_at": old_file_info["old_created_at"],
            }
        )
        base64_encoded_data = utils.download_from_s3(old_file_info["old_s3_key"])
        utils.upload_base64_file_s3(f"{s3_key}/{old_file_info['old_filename']}", base64_encoded_data)

    sql = """
    SELECT
        aa.name as old_prekey,
        aa.record_id as old_record_id,
        aa.created_at as created_at,
        aa.role_type as role_type,
        aa.role_id as role_id,
        ab.key as old_s3_key,
        ab.filename as old_filename,
        DATE_FORMAT(aa.created_at, '%Y-%m-%d %H:%i:%S') as old_created_at
    FROM
        mortgage_loan_tool_be_production.active_storage_attachments as aa
    INNER JOIN
        mortgage_loan_tool_be_production.active_storage_blobs as ab
        ON
        aa.blob_id = ab.id
    WHERE
        aa.record_type = 'PBorrowing';
    """

    old_files_info = await db.fetch_all(sql)

    for old_file_info in old_files_info:
        id = await db.uuid_short()
        owner_type = owner_type_maps.get(old_file_info["role_type"])
        owner_id = 0
        if owner_type == 1:
            user = await db.fetch_one(
                f"SELECT id FROM mortgage_staging_v1.c_users WHERE old_id = {old_file_info['role_id']};"
            )
            if user:
                owner_id = user["id"]
        if owner_type == 2:
            sales_person = await db.fetch_one(
                f"SELECT id FROM mortgage_staging_v1.s_sales_persons WHERE old_id = {old_file_info['role_id']};"
            )
            if sales_person:
                owner_id = sales_person["id"]
        if owner_type == 3:
            manager = await db.fetch_one(
                f"SELECT id FROM mortgage_staging_v1.s_managers WHERE old_id = {old_file_info['role_id']};"
            )
            if manager:
                owner_id = manager["id"]

        p_borrowing = await db.fetch_one(
            f"SELECT id, p_application_header_id FROM mortgage_staging_v1.p_borrowings WHERE old_id = {old_file_info['old_record_id']};"
        )

        s3_key = f"{p_borrowing['p_application_header_id']}/{owner_id}_{owner_type_kanji_maps[owner_type]}/{prekey_maps[old_file_info['old_prekey']]}/{id}"
        new_data.append(
            {
                "id": id,
                "owner_type": owner_type,
                "owner_id": owner_id,
                "p_application_header_id": p_borrowing["p_application_header_id"],
                "record_id": p_borrowing["id"],
                "type": 0,
                "s3_key": s3_key,
                "file_name": old_file_info["old_filename"],
                "created_at": old_file_info["old_created_at"],
            }
        )
        base64_encoded_data = utils.download_from_s3(old_file_info["old_s3_key"])
        utils.upload_base64_file_s3(f"{s3_key}/{old_file_info['old_filename']}", base64_encoded_data)

    for data in new_data:
        await db.execute(utils.gen_insert_sql("mortgage_staging_v1.p_uploaded_files", data))
