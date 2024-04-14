from constant import OPERATE_TYPE
from core.database import DB
import utils
import yaml
from .db_filed_maps import p_application_header_parameters


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
                f"SELECT id FROM mortgage_staging.c_users WHERE old_id = {old_file_info['role_id']};"
            )
            if user:
                owner_id = user["id"]
        if owner_type == 2:
            sales_person = await db.fetch_one(
                f"SELECT id FROM mortgage_staging.s_sales_persons WHERE old_id = {old_file_info['role_id']};"
            )
            if sales_person:
                owner_id = sales_person["id"]
        if owner_type == 3:
            manager = await db.fetch_one(
                f"SELECT id FROM mortgage_staging.s_managers WHERE old_id = {old_file_info['role_id']};"
            )
            if manager:
                owner_id = manager["id"]
        p_application_header_id = None
        p_application_header = await db.fetch_one(
            f"SELECT id FROM mortgage_staging.p_application_headers WHERE old_id = {old_file_info['old_record_id']};"
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
                f"SELECT id FROM mortgage_staging.c_users WHERE old_id = {old_file_info['role_id']};"
            )
            if user:
                owner_id = user["id"]
        if owner_type == 2:
            sales_person = await db.fetch_one(
                f"SELECT id FROM mortgage_staging.s_sales_persons WHERE old_id = {old_file_info['role_id']};"
            )
            if sales_person:
                owner_id = sales_person["id"]
        if owner_type == 3:
            manager = await db.fetch_one(
                f"SELECT id FROM mortgage_staging.s_managers WHERE old_id = {old_file_info['role_id']};"
            )
            if manager:
                owner_id = manager["id"]
        p_applicant_persons = await db.fetch_one(
            f"SELECT id, p_application_header_id, type FROM mortgage_staging.p_applicant_persons WHERE old_id = {old_file_info['old_record_id']};"
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
                f"SELECT id FROM mortgage_staging.c_users WHERE old_id = {old_file_info['role_id']};"
            )
            if user:
                owner_id = user["id"]
        if owner_type == 2:
            sales_person = await db.fetch_one(
                f"SELECT id FROM mortgage_staging.s_sales_persons WHERE old_id = {old_file_info['role_id']};"
            )
            if sales_person:
                owner_id = sales_person["id"]
        if owner_type == 3:
            manager = await db.fetch_one(
                f"SELECT id FROM mortgage_staging.s_managers WHERE old_id = {old_file_info['role_id']};"
            )
            if manager:
                owner_id = manager["id"]

        p_borrowing = await db.fetch_one(
            f"SELECT id, p_application_header_id FROM mortgage_staging.p_borrowings WHERE old_id = {old_file_info['old_record_id']};"
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

    for data in new_data:
        await db.execute(utils.gen_insert_sql("mortgage_staging.p_uploaded_files", data))


async def translate_p_archive_files(db: DB):
    sql = """
    SELECT
        UUID_SHORT() as id,
        af.id as old_id,
        sp.id as s_sales_person_id,
        af.note as note,
        DATE_FORMAT(af.created_at, '%Y-%m-%d %H:%i:%S') as created_at,
        DATE_FORMAT(af.updated_at, '%Y-%m-%d %H:%i:%S') as updated_at
    FROM
        mortgage_loan_tool_be_production.archive_files as af
    INNER JOIN
        mortgage_staging.s_sales_persons as sp
        ON
        sp.old_id = af.s_sale_person_id;
    """
    old_basic_info = await db.fetch_all(sql)

    basic_info = []

    for item in old_basic_info:

        sql = f"SELECT CONVERT(sor.s_sales_company_org_id,CHAR) AS s_sales_company_org_id, sor.role FROM mortgage_staging.s_sales_person_s_sales_company_org_rels as sor WHERE sor.s_sales_person_id = {item['s_sales_person_id']};"
        orgs = await db.fetch_one(sql)
        sql = f"""
        WITH RECURSIVE child AS (
        SELECT id, pid, category FROM mortgage_staging.s_sales_company_orgs WHERE id = {orgs['s_sales_company_org_id']}
        union
        SELECT parents.id, parents.pid, parents.category FROM mortgage_staging.s_sales_company_orgs as parents INNER JOIN child ON parents.id = child.pid
        )
        SELECT
            child.id AS root_id
        FROM
            child
        WHERE
            child.category = "C";
        """
        parents = await db.fetch_one(sql)

        basic_info.append({**item, "s_sales_company_org_id": parents["root_id"]})

        await db.execute(
            utils.gen_insert_sql(
                "mortgage_staging.c_archive_files", {**item, "s_sales_company_org_id": parents["root_id"]}
            )
        )

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
        aa.record_type = 'ArchiveFile';
    """

    old_files_info = await db.fetch_all(sql)
    new_data = []
    for old_file_info in old_files_info:
        id = await db.uuid_short()
        c_archive_file = await db.fetch_one(
            f"SELECT * FROM mortgage_staging.c_archive_files WHERE old_id = {old_file_info['old_record_id']};"
        )
        owner_id = None
        if c_archive_file:
            owner_id = c_archive_file["s_sales_person_id"]

        s3_key = f"{c_archive_file['s_sales_company_org_id']}/{owner_id}/{id}"
        new_data.append(
            {
                "id": id,
                "owner_id": owner_id,
                "record_id": c_archive_file["id"],
                "s3_key": s3_key,
                "file_name": old_file_info["old_filename"],
                "created_at": old_file_info["old_created_at"],
            }
        )

    for data in new_data:
        await db.execute(utils.gen_insert_sql("mortgage_staging.c_archive_uploaded_files", data))


async def translate_c_access_logs(db: DB):
    data = []
    sql = """
    SELECT
        a.key,
        a.parameters
    FROM
        mortgage_loan_tool_be_production.activities as a
    WHERE 
        a.trackable_type='PApplicationHeader'
        AND a.log_export = 1
        AND a.key != 'p_application_header.create';
    """
    PApplicationHeaders = await db.fetch_all(sql)

    for item in PApplicationHeaders:

        data.append({"key": item["key"], "parameters": yaml.safe_load(item["parameters"])})

    return data


async def translate_p_activities(db: DB):
    # p_application_headers
    sql = f"""
    SELECT
        h.id as p_application_header_id,
        a.owner_type,
        a.owner_id,
        a.key,
        a.parameters,
        DATE_FORMAT(a.created_at, '%Y-%m-%d %H:%i:%S') as old_created_at,
        DATE_FORMAT(a.updated_at, '%Y-%m-%d %H:%i:%S') as old_updated_at
    FROM
        mortgage_staging.p_application_headers as h
    LEFT JOIN
        mortgage_loan_tool_be_production.activities as a
        ON
        a.trackable_id = h.old_id
    WHERE
        h.id = 100791550216251933
        AND
        a.trackable_type='PApplicationHeader'
        
    """

    PApplicationHeadersCreateData = [
        {**item, "parameters": yaml.safe_load(item["parameters"])}
        for item in await db.fetch_all(sql + "AND a.key = 'p_application_header.create'")
    ]
    PApplicationHeadersUpdateData = [
        {**item, "parameters": yaml.safe_load(item["parameters"])}
        for item in await db.fetch_all(sql + "AND a.key = 'p_application_header.update'")
    ]

    new_data = {}

    new_house_planned_resident_overview_create = []
    new_house_planned_resident_overview_update = []
    new_house_planned_resident_overview_values = []

    for PApplicationHeaderCreateData in PApplicationHeadersCreateData:
        parameters = PApplicationHeaderCreateData["parameters"]
        if "planned_cohabitant" in parameters:

            operator_type = owner_type_maps[PApplicationHeaderCreateData["owner_type"]]
            operator_id = 0

            if operator_type == 1:
                user = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging.c_users WHERE old_id = {PApplicationHeaderCreateData['owner_id']};"
                )
                if user:
                    operator_id = user["id"]
            if operator_type == 2:
                sales_person = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging.s_sales_persons WHERE old_id = {PApplicationHeaderCreateData['owner_id']};"
                )
                if sales_person:
                    operator_id = sales_person["id"]
            if operator_type == 3:
                manager = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging.s_managers WHERE old_id = {PApplicationHeaderCreateData['owner_id']};"
                )
                if manager:
                    operator_id = manager["id"]
            planned_cohabitant = parameters.get("planned_cohabitant", [])
            children_number = parameters.get("children_number")
            siblings_number = parameters.get("siblings_number")
            other_relationship = parameters.get("other_relationship")
            other_people_number = parameters.get("other_people_number")
            # 1 => '配偶者', 2 => '子ども', 3 => '父', 4 => '母', 5 => '兄弟姉妹', 6 => '婚約者', 99 => 'その他'

            if planned_cohabitant:
                temp = {
                    "father": "1" if "3" in planned_cohabitant else None,
                    "fiance": "1" if "6" in planned_cohabitant else None,
                    "mother": "1" if "4" in planned_cohabitant else None,
                    "others": str(other_people_number) if "99" in planned_cohabitant else None,
                    "spouse": "1" if "1" in planned_cohabitant else None,
                    "children": str(children_number) if "2" in planned_cohabitant else None,
                    "father_umu": True if "3" in planned_cohabitant else False,
                    "fiance_umu": True if "6" in planned_cohabitant else False,
                    "mother_umu": True if "4" in planned_cohabitant else False,
                    "others_rel": other_relationship,
                    "others_umu": True if "99" in planned_cohabitant else False,
                    "spouse_umu": True if "1" in planned_cohabitant else False,
                    "children_umu": True if "2" in planned_cohabitant else False,
                    "brothers_sisters": str(siblings_number) if "5" in planned_cohabitant else None,
                    "brothers_sisters_umu": True if "5" in planned_cohabitant else False,
                }
                new_house_planned_resident_overview_values.append(temp)
                new_house_planned_resident_overview_create.append(
                    {
                        "p_application_header_id": PApplicationHeaderCreateData["p_application_header_id"],
                        "operator_type": operator_type,
                        "operator_id": operator_id,
                        "table_name": "p_application_headers",
                        "field_name": "new_house_planned_resident_overview",
                        "table_id": PApplicationHeaderCreateData["p_application_header_id"],
                        "content": temp,
                        "operate_type": OPERATE_TYPE.APPLY.value,
                        "created_at": PApplicationHeaderCreateData["old_created_at"],
                        "updated_at": PApplicationHeaderCreateData["old_updated_at"],
                    }
                )
            else:
                new_house_planned_resident_overview_values.append(None)
                new_house_planned_resident_overview_create.append(
                    {
                        "p_application_header_id": PApplicationHeaderCreateData["p_application_header_id"],
                        "operator_type": operator_type,
                        "operator_id": operator_id,
                        "table_name": "p_application_headers",
                        "field_name": "new_house_planned_resident_overview",
                        "table_id": PApplicationHeaderCreateData["p_application_header_id"],
                        "content": None,
                        "operate_type": OPERATE_TYPE.APPLY.value,
                        "created_at": PApplicationHeaderCreateData["old_created_at"],
                        "updated_at": PApplicationHeaderCreateData["old_updated_at"],
                    }
                )
        else:
            continue

    for PApplicationHeaderUpdateData in PApplicationHeadersUpdateData:
        parameters = PApplicationHeaderUpdateData["parameters"]
        if "planned_cohabitant" in parameters:
            operator_type = owner_type_maps[PApplicationHeaderUpdateData["owner_type"]]
            operator_id = 0
            if operator_type == 1:
                user = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging.c_users WHERE old_id = {PApplicationHeaderUpdateData['owner_id']};"
                )
                if user:
                    operator_id = user["id"]
            if operator_type == 2:
                sales_person = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging.s_sales_persons WHERE old_id = {PApplicationHeaderUpdateData['owner_id']};"
                )
                if sales_person:
                    operator_id = sales_person["id"]
            if operator_type == 3:
                manager = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging.s_managers WHERE old_id = {PApplicationHeaderUpdateData['owner_id']};"
                )
                if manager:
                    operator_id = manager["id"]
            planned_cohabitant = parameters.get("planned_cohabitant", [])
            children_number = parameters.get("children_number")
            siblings_number = parameters.get("siblings_number")
            other_relationship = parameters.get("other_relationship")
            other_people_number = parameters.get("other_people_number")
            # 1 => '配偶者', 2 => '子ども', 3 => '父', 4 => '母', 5 => '兄弟姉妹', 6 => '婚約者', 99 => 'その他'

            if planned_cohabitant and new_house_planned_resident_overview_values[-1] is None:
                temp = {
                    "father": "1" if "3" in planned_cohabitant else None,
                    "fiance": "1" if "6" in planned_cohabitant else None,
                    "mother": "1" if "4" in planned_cohabitant else None,
                    "others": str(other_people_number) if "99" in planned_cohabitant else None,
                    "spouse": "1" if "1" in planned_cohabitant else None,
                    "children": str(children_number) if "2" in planned_cohabitant else None,
                    "father_umu": True if "3" in planned_cohabitant else False,
                    "fiance_umu": True if "6" in planned_cohabitant else False,
                    "mother_umu": True if "4" in planned_cohabitant else False,
                    "others_rel": other_relationship,
                    "others_umu": True if "99" in planned_cohabitant else False,
                    "spouse_umu": True if "1" in planned_cohabitant else False,
                    "children_umu": True if "2" in planned_cohabitant else False,
                    "brothers_sisters": str(siblings_number) if "5" in planned_cohabitant else None,
                    "brothers_sisters_umu": True if "5" in planned_cohabitant else False,
                }
                new_house_planned_resident_overview_values.append(temp)
                new_house_planned_resident_overview_update.append(
                    {
                        "p_application_header_id": PApplicationHeaderUpdateData["p_application_header_id"],
                        "operator_type": operator_type,
                        "operator_id": operator_id,
                        "table_name": "p_application_headers",
                        "field_name": "new_house_planned_resident_overview",
                        "table_id": PApplicationHeaderUpdateData["p_application_header_id"],
                        "content": temp,
                        "operate_type": OPERATE_TYPE.UPDATE.value,
                        "created_at": PApplicationHeaderUpdateData["old_created_at"],
                        "updated_at": PApplicationHeaderUpdateData["old_updated_at"],
                    }
                )
            else:
                temp = {
                    "father": "1" if "3" in planned_cohabitant else None,
                    "fiance": "1" if "6" in planned_cohabitant else None,
                    "mother": "1" if "4" in planned_cohabitant else None,
                    "others": (
                        str(other_people_number)
                        if other_people_number
                        else new_house_planned_resident_overview_values[-1].get("others")
                    ),
                    "spouse": "1" if "1" in planned_cohabitant else None,
                    "children": (
                        str(children_number)
                        if children_number
                        else new_house_planned_resident_overview_values[-1].get("children")
                    ),
                    "father_umu": True if "3" in planned_cohabitant else False,
                    "fiance_umu": True if "6" in planned_cohabitant else False,
                    "mother_umu": True if "4" in planned_cohabitant else False,
                    "others_rel": (
                        other_relationship
                        if other_relationship
                        else new_house_planned_resident_overview_values[-1].get("others_rel")
                    ),
                    "others_umu": True if "99" in planned_cohabitant else False,
                    "spouse_umu": True if "1" in planned_cohabitant else False,
                    "children_umu": True if "2" in planned_cohabitant else False,
                    "brothers_sisters": (
                        str(siblings_number)
                        if siblings_number
                        else new_house_planned_resident_overview_values[-1].get("brothers_sisters")
                    ),
                    "brothers_sisters_umu": True if "5" in planned_cohabitant else False,
                }
                new_house_planned_resident_overview_values.append(temp)
                new_house_planned_resident_overview_update.append(
                    {
                        "p_application_header_id": PApplicationHeaderUpdateData["p_application_header_id"],
                        "operator_type": operator_type,
                        "operator_id": operator_id,
                        "table_name": "p_application_headers",
                        "field_name": "new_house_planned_resident_overview",
                        "table_id": PApplicationHeaderUpdateData["p_application_header_id"],
                        "content": temp,
                        "operate_type": OPERATE_TYPE.UPDATE.value,
                        "created_at": PApplicationHeaderUpdateData["old_created_at"],
                        "updated_at": PApplicationHeaderUpdateData["old_updated_at"],
                    }
                )

        if "planned_cohabitant" not in parameters and (
            "children_number" in parameters
            or "siblings_number" in parameters
            or "other_people_number" in parameters
            or "other_relationship" in parameters
        ):
            operator_type = owner_type_maps[PApplicationHeaderUpdateData["owner_type"]]
            operator_id = 0
            if operator_type == 1:
                user = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging.c_users WHERE old_id = {PApplicationHeaderUpdateData['owner_id']};"
                )
                if user:
                    operator_id = user["id"]
            if operator_type == 2:
                sales_person = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging.s_sales_persons WHERE old_id = {PApplicationHeaderUpdateData['owner_id']};"
                )
                if sales_person:
                    operator_id = sales_person["id"]
            if operator_type == 3:
                manager = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging.s_managers WHERE old_id = {PApplicationHeaderUpdateData['owner_id']};"
                )
                if manager:
                    operator_id = manager["id"]
            planned_cohabitant = parameters.get("planned_cohabitant", [])
            children_number = parameters.get("children_number")
            siblings_number = parameters.get("siblings_number")
            other_relationship = parameters.get("other_relationship")
            other_people_number = parameters.get("other_people_number")
            # 1 => '配偶者', 2 => '子ども', 3 => '父', 4 => '母', 5 => '兄弟姉妹', 6 => '婚約者', 99 => 'その他'

            temp = {**new_house_planned_resident_overview_values[-1]}
            if "children_number" in parameters:
                temp["children"] = str(children_number)
            if "siblings_number" in parameters:
                temp["brothers_sisters"] = str(siblings_number)
            if "other_people_number" in parameters:
                temp["others"] = str(other_people_number)
            if "other_relationship" in parameters:
                temp["others_rel"] = str(other_relationship)
            new_house_planned_resident_overview_values.append(temp)
            new_house_planned_resident_overview_update.append(
                {
                    "p_application_header_id": PApplicationHeaderUpdateData["p_application_header_id"],
                    "operator_type": operator_type,
                    "operator_id": operator_id,
                    "table_name": "p_application_headers",
                    "field_name": "new_house_planned_resident_overview",
                    "table_id": PApplicationHeaderUpdateData["p_application_header_id"],
                    "content": temp,
                    "operate_type": OPERATE_TYPE.UPDATE.value,
                    "created_at": PApplicationHeaderUpdateData["old_created_at"],
                    "updated_at": PApplicationHeaderUpdateData["old_updated_at"],
                }
            )

    if len(new_house_planned_resident_overview_update) == 0:
        pass
    else:
        new_data["new_house_planned_resident_overview"] = {
            "create": new_house_planned_resident_overview_create,
            "update": new_house_planned_resident_overview_update,
        }

    for old_key in ["p_referral_agency_id"]:
        if old_key == "p_referral_agency_id":
            sales_company_id_create = []
            sales_company_id_update = []
            sales_company_id_values = []

            sales_area_id_create = []
            sales_area_id_update = []
            sales_area_id_values = []

            sales_exhibition_hall_id_create = []
            sales_exhibition_hall_id_update = []
            sales_exhibition_hall_id_values = []
            for PApplicationHeaderCreateData in PApplicationHeadersCreateData:
                parameters = PApplicationHeaderCreateData["parameters"]
                if "p_referral_agency_id" in parameters:
                    operator_type = owner_type_maps[PApplicationHeaderCreateData["owner_type"]]
                    operator_id = 0

                    if operator_type == 1:
                        user = await db.fetch_one(
                            f"SELECT id FROM mortgage_staging.c_users WHERE old_id = {PApplicationHeaderCreateData['owner_id']};"
                        )
                        if user:
                            operator_id = user["id"]
                    if operator_type == 2:
                        sales_person = await db.fetch_one(
                            f"SELECT id FROM mortgage_staging.s_sales_persons WHERE old_id = {PApplicationHeaderCreateData['owner_id']};"
                        )
                        if sales_person:
                            operator_id = sales_person["id"]
                    if operator_type == 3:
                        manager = await db.fetch_one(
                            f"SELECT id FROM mortgage_staging.s_managers WHERE old_id = {PApplicationHeaderCreateData['owner_id']};"
                        )
                        if manager:
                            operator_id = manager["id"]

                    p_referral_agencies = None
                    if parameters["p_referral_agency_id"]:
                        p_referral_agencies = await db.fetch_one(
                            f"SELECT sale_agent_id, store_id, exhibition_id FROM mortgage_loan_tool_be_production.p_referral_agencies WHERE id = {parameters['p_referral_agency_id']}"
                        )
                    sales_company_id = None
                    sales_area_id = None
                    sales_exhibition_hall_id = None

                    if p_referral_agencies:
                        if p_referral_agencies["sale_agent_id"]:
                            org_c = await db.fetch_one(
                                f"""SELECT id FROM mortgage_staging.s_sales_company_orgs WHERE code = '{p_referral_agencies["sale_agent_id"]}';"""
                            )

                            if org_c:
                                sales_company_id = org_c["id"]
                        if p_referral_agencies["store_id"]:
                            org_b = await db.fetch_one(
                                f"""SELECT id FROM mortgage_staging.s_sales_company_orgs WHERE code = '{p_referral_agencies["store_id"]}';"""
                            )

                            if org_b:
                                sales_area_id = org_b["id"]
                        if p_referral_agencies["exhibition_id"]:
                            org_e = await db.fetch_one(
                                f"""SELECT id FROM mortgage_staging.s_sales_company_orgs WHERE code = '{p_referral_agencies["exhibition_id"]}';"""
                            )

                            if org_e:
                                sales_exhibition_hall_id = org_e["id"]
                    sales_company_id_values.append(sales_company_id)
                    sales_company_id_create.append(
                        {
                            "p_application_header_id": PApplicationHeaderCreateData["p_application_header_id"],
                            "operator_type": operator_type,
                            "operator_id": operator_id,
                            "table_name": "p_application_headers",
                            "field_name": "sales_company_id",
                            "table_id": PApplicationHeaderCreateData["p_application_header_id"],
                            "content": sales_company_id,
                            "operate_type": OPERATE_TYPE.APPLY.value,
                        }
                    )
                    sales_area_id_values.append(sales_area_id)
                    sales_area_id_create.append(
                        {
                            "p_application_header_id": PApplicationHeaderCreateData["p_application_header_id"],
                            "operator_type": operator_type,
                            "operator_id": operator_id,
                            "table_name": "p_application_headers",
                            "field_name": "sales_area_id",
                            "table_id": PApplicationHeaderCreateData["p_application_header_id"],
                            "content": sales_area_id,
                            "operate_type": OPERATE_TYPE.APPLY.value,
                        }
                    )
                    sales_exhibition_hall_id_values.append(sales_exhibition_hall_id)
                    sales_exhibition_hall_id_create.append(
                        {
                            "p_application_header_id": PApplicationHeaderCreateData["p_application_header_id"],
                            "operator_type": operator_type,
                            "operator_id": operator_id,
                            "table_name": "p_application_headers",
                            "field_name": "sales_exhibition_hall_id",
                            "table_id": PApplicationHeaderCreateData["p_application_header_id"],
                            "content": sales_exhibition_hall_id,
                            "operate_type": OPERATE_TYPE.APPLY.value,
                        }
                    )
                else:
                    continue

            for PApplicationHeaderUpdateData in PApplicationHeadersUpdateData:
                parameters = PApplicationHeaderUpdateData["parameters"]
                if "p_referral_agency_id" in parameters:
                    operator_type = owner_type_maps[PApplicationHeaderUpdateData["owner_type"]]
                    operator_id = 0

                    if operator_type == 1:
                        user = await db.fetch_one(
                            f"SELECT id FROM mortgage_staging.c_users WHERE old_id = {PApplicationHeaderUpdateData['owner_id']};"
                        )
                        if user:
                            operator_id = user["id"]
                    if operator_type == 2:
                        sales_person = await db.fetch_one(
                            f"SELECT id FROM mortgage_staging.s_sales_persons WHERE old_id = {PApplicationHeaderUpdateData['owner_id']};"
                        )
                        if sales_person:
                            operator_id = sales_person["id"]
                    if operator_type == 3:
                        manager = await db.fetch_one(
                            f"SELECT id FROM mortgage_staging.s_managers WHERE old_id = {PApplicationHeaderUpdateData['owner_id']};"
                        )
                        if manager:
                            operator_id = manager["id"]
                    p_referral_agencies = None
                    if parameters["p_referral_agency_id"]:
                        p_referral_agencies = await db.fetch_one(
                            f"SELECT sale_agent_id, store_id, exhibition_id FROM mortgage_loan_tool_be_production.p_referral_agencies WHERE id = {parameters['p_referral_agency_id']}"
                        )
                    sales_company_id = None
                    sales_area_id = None
                    sales_exhibition_hall_id = None

                    if p_referral_agencies:
                        if p_referral_agencies["sale_agent_id"]:
                            org_c = await db.fetch_one(
                                f"""SELECT id FROM mortgage_staging.s_sales_company_orgs WHERE code = '{p_referral_agencies["sale_agent_id"]}';"""
                            )

                            if org_c:
                                sales_company_id = org_c["id"]
                        if p_referral_agencies["store_id"]:
                            org_b = await db.fetch_one(
                                f"""SELECT id FROM mortgage_staging.s_sales_company_orgs WHERE code = '{p_referral_agencies["store_id"]}';"""
                            )

                            if org_b:
                                sales_area_id = org_b["id"]
                        if p_referral_agencies["exhibition_id"]:
                            org_e = await db.fetch_one(
                                f"""SELECT id FROM mortgage_staging.s_sales_company_orgs WHERE code = '{p_referral_agencies["exhibition_id"]}';"""
                            )

                            if org_e:
                                sales_exhibition_hall_id = org_e["id"]
                    if sales_company_id != sales_company_id_values[-1]:
                        sales_company_id_update.append(
                            {
                                "p_application_header_id": PApplicationHeaderUpdateData["p_application_header_id"],
                                "operator_type": operator_type,
                                "operator_id": operator_id,
                                "table_name": "p_application_headers",
                                "field_name": "sales_company_id",
                                "table_id": PApplicationHeaderUpdateData["p_application_header_id"],
                                "content": sales_company_id,
                                "operate_type": OPERATE_TYPE.UPDATE.value,
                            }
                        )
                    if sales_area_id != sales_area_id_values[-1]:
                        sales_area_id_update.append(
                            {
                                "p_application_header_id": PApplicationHeaderCreateData["p_application_header_id"],
                                "operator_type": operator_type,
                                "operator_id": operator_id,
                                "table_name": "p_application_headers",
                                "field_name": "sales_area_id",
                                "table_id": PApplicationHeaderCreateData["p_application_header_id"],
                                "content": sales_area_id,
                                "operate_type": OPERATE_TYPE.UPDATE.value,
                            }
                        )
                    if sales_exhibition_hall_id != sales_exhibition_hall_id_values[-1]:
                        sales_exhibition_hall_id_update.append(
                            {
                                "p_application_header_id": PApplicationHeaderCreateData["p_application_header_id"],
                                "operator_type": operator_type,
                                "operator_id": operator_id,
                                "table_name": "p_application_headers",
                                "field_name": "sales_exhibition_hall_id",
                                "table_id": PApplicationHeaderCreateData["p_application_header_id"],
                                "content": sales_exhibition_hall_id,
                                "operate_type": OPERATE_TYPE.UPDATE.value,
                            }
                        )
                else:
                    continue

            if len(sales_company_id_update) == 0:
                pass
            else:
                new_data["sales_company_id"] = {"create": sales_company_id_create, "update": sales_company_id_update}
            if len(sales_area_id_update) == 0:
                pass
            else:
                new_data["sales_area_id"] = {"create": sales_area_id_create, "update": sales_area_id_update}
            if len(sales_exhibition_hall_id_update) == 0:
                pass
            else:
                new_data["sales_exhibition_hall_id"] = {
                    "create": sales_exhibition_hall_id_create,
                    "update": sales_exhibition_hall_id_update,
                }

    for old_key, new_key in p_application_header_parameters.items():
        create = []
        update = []
        for PApplicationHeaderCreateData in PApplicationHeadersCreateData:
            parameters = PApplicationHeaderCreateData["parameters"]
            operator_type = owner_type_maps[PApplicationHeaderCreateData["owner_type"]]
            operator_id = 0

            if operator_type == 1:
                user = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging.c_users WHERE old_id = {PApplicationHeaderCreateData['owner_id']};"
                )
                if user:
                    operator_id = user["id"]
            if operator_type == 2:
                sales_person = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging.s_sales_persons WHERE old_id = {PApplicationHeaderCreateData['owner_id']};"
                )
                if sales_person:
                    operator_id = sales_person["id"]
            if operator_type == 3:
                manager = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging.s_managers WHERE old_id = {PApplicationHeaderCreateData['owner_id']};"
                )
                if manager:
                    operator_id = manager["id"]

            create.append(
                {
                    "p_application_header_id": PApplicationHeaderCreateData["p_application_header_id"],
                    "operator_type": operator_type,
                    "operator_id": operator_id,
                    "table_name": "p_application_headers",
                    "field_name": new_key,
                    "table_id": PApplicationHeaderCreateData["p_application_header_id"],
                    "content": int(parameters[old_key]) if type(parameters[old_key]) is bool else parameters[old_key],
                    "operate_type": OPERATE_TYPE.APPLY.value,
                }
            )
        for PApplicationHeaderUpdateData in PApplicationHeadersUpdateData:
            parameters = PApplicationHeaderUpdateData["parameters"]
            operator_type = owner_type_maps[PApplicationHeaderUpdateData["owner_type"]]
            operator_id = 0

            if operator_type == 1:
                user = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging.c_users WHERE old_id = {PApplicationHeaderUpdateData['owner_id']};"
                )
                if user:
                    operator_id = user["id"]
            if operator_type == 2:
                sales_person = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging.s_sales_persons WHERE old_id = {PApplicationHeaderUpdateData['owner_id']};"
                )
                if sales_person:
                    operator_id = sales_person["id"]
            if operator_type == 3:
                manager = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging.s_managers WHERE old_id = {PApplicationHeaderUpdateData['owner_id']};"
                )
                if manager:
                    operator_id = manager["id"]

            if old_key in parameters:
                update.append(
                    {
                        "p_application_header_id": PApplicationHeaderUpdateData["p_application_header_id"],
                        "operator_type": operator_type,
                        "operator_id": operator_id,
                        "table_name": "p_application_headers",
                        "field_name": new_key,
                        "table_id": PApplicationHeaderUpdateData["p_application_header_id"],
                        "content": (
                            int(parameters[old_key]) if type(parameters[old_key]) is bool else parameters[old_key]
                        ),
                        "operate_type": OPERATE_TYPE.UPDATE.value,
                    }
                )
            else:
                continue
        if len(update) == 0:
            pass
        else:
            new_data[new_key] = {"create": create, "update": update}

    return new_data
    return PApplicationHeadersCreateData + PApplicationHeadersUpdateData
    # return PApplicationHeadersUpdateData + PApplicationHeadersUpdateData
