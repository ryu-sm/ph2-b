from constant import OPERATE_TYPE
from core.database import DB
import utils
import yaml
from .db_filed_maps import p_application_header_parameters
from core.config import settings


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
        mortgage_staging_v3.s_sales_persons as sp
        ON
        sp.old_id = af.s_sale_person_id;
    """
    old_basic_info = await db.fetch_all(sql)

    basic_info = []

    for item in old_basic_info:

        sql = f"SELECT CONVERT(sor.s_sales_company_org_id,CHAR) AS s_sales_company_org_id, sor.role FROM mortgage_staging_v3.s_sales_person_s_sales_company_org_rels as sor WHERE sor.s_sales_person_id = {item['s_sales_person_id']};"
        orgs = await db.fetch_one(sql)
        sql = f"""
        WITH RECURSIVE child AS (
        SELECT id, pid, category FROM mortgage_staging_v3.s_sales_company_orgs WHERE id = {orgs['s_sales_company_org_id']}
        union
        SELECT parents.id, parents.pid, parents.category FROM mortgage_staging_v3.s_sales_company_orgs as parents INNER JOIN child ON parents.id = child.pid
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
                "mortgage_staging_v3.c_archive_files", {**item, "s_sales_company_org_id": parents["root_id"]}
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
            f"SELECT * FROM mortgage_staging_v3.c_archive_files WHERE old_id = {old_file_info['old_record_id']};"
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
        base64_encoded_data = utils.download_from_s3(old_file_info["old_s3_key"])
        utils.upload_base64_file_s3(
            f"{s3_key}/{old_file_info['old_filename']}",
            base64_encoded_data,
            settings.C_ARCHIVE_UPLOADED_FILES_BUCKET_NAME,
        )

    for data in new_data:
        await db.execute(utils.gen_insert_sql("mortgage_staging_v3.c_archive_uploaded_files", data))
