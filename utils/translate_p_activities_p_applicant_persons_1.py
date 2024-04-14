from constant import OPERATE_TYPE
from core.database import DB
import utils
import yaml
from .db_filed_maps import (
    p_applicant_person_parameters_0_h,
    p_applicant_person_parameters_0,
    p_applicant_person_parameters_1,
    p_applicant_person_parameters_files,
)


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


async def translate_p_activities_p_applicant_persons_1(db: DB):
    # p_applicant_persons
    sql = f"""
    SELECT
        p.id as p_applicant_person_id,
        p.p_application_header_id as p_application_header_id,
        a.owner_type,
        a.owner_id,
        a.key,
        a.parameters,
        DATE_FORMAT(a.created_at, '%Y-%m-%d %H:%i:%S') as old_created_at,
        DATE_FORMAT(a.updated_at, '%Y-%m-%d %H:%i:%S') as old_updated_at
    FROM
        mortgage_staging.p_applicant_persons as p
    LEFT JOIN
        mortgage_loan_tool_be_production.activities as a
        ON
        a.trackable_id = p.old_id
    WHERE
        p.p_application_header_id = 100791550216251933
        AND
        p.type = 1
        AND
        a.trackable_type='PApplicantPerson'
        
    """

    PApplicantPersonsCreateData = [
        {**item, "parameters": yaml.safe_load(item["parameters"])}
        for item in await db.fetch_all(sql + "AND a.key = 'p_applicant_person.create'")
    ]
    PApplicantPersonsUpdateData = [
        {**item, "parameters": yaml.safe_load(item["parameters"])}
        for item in await db.fetch_all(sql + "AND a.key IN ('p_applicant_person.update', 'PApplicantPerson.update')")
    ]

    new_data = {}

    for old_key, new_key in p_applicant_person_parameters_1.items():
        create = []
        update = []
        for PApplicantPersonCreateData in PApplicantPersonsCreateData:
            parameters = PApplicantPersonCreateData["parameters"]
            operator_type = owner_type_maps[PApplicantPersonCreateData["owner_type"]]
            operator_id = 0

            if operator_type == 1:
                user = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging.c_users WHERE old_id = {PApplicantPersonCreateData['owner_id']};"
                )
                if user:
                    operator_id = user["id"]
            if operator_type == 2:
                sales_person = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging.s_sales_persons WHERE old_id = {PApplicantPersonCreateData['owner_id']};"
                )
                if sales_person:
                    operator_id = sales_person["id"]
            if operator_type == 3:
                manager = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging.s_managers WHERE old_id = {PApplicantPersonCreateData['owner_id']};"
                )
                if manager:
                    operator_id = manager["id"]

            create.append(
                {
                    "p_application_header_id": PApplicantPersonCreateData["p_application_header_id"],
                    "operator_type": operator_type,
                    "operator_id": operator_id,
                    "table_name": "p_applicant_persons",
                    "field_name": new_key,
                    "table_id": PApplicantPersonCreateData["p_applicant_person_id"],
                    "content": parameters[old_key],
                    "operate_type": OPERATE_TYPE.APPLY.value,
                    "created_at": PApplicantPersonCreateData["old_created_at"],
                    "updated_at": PApplicantPersonCreateData["old_updated_at"],
                }
            )

        for PApplicantPersonUpdateData in PApplicantPersonsUpdateData:
            parameters = PApplicantPersonUpdateData["parameters"]
            operator_type = owner_type_maps[PApplicantPersonUpdateData["owner_type"]]
            operator_id = 0

            if operator_type == 1:
                user = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging.c_users WHERE old_id = {PApplicantPersonUpdateData['owner_id']};"
                )
                if user:
                    operator_id = user["id"]
            if operator_type == 2:
                sales_person = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging.s_sales_persons WHERE old_id = {PApplicantPersonUpdateData['owner_id']};"
                )
                if sales_person:
                    operator_id = sales_person["id"]
            if operator_type == 3:
                manager = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging.s_managers WHERE old_id = {PApplicantPersonUpdateData['owner_id']};"
                )
                if manager:
                    operator_id = manager["id"]

            if old_key in parameters:
                update.append(
                    {
                        "p_application_header_id": PApplicantPersonUpdateData["p_application_header_id"],
                        "operator_type": operator_type,
                        "operator_id": operator_id,
                        "table_name": "p_applicant_persons",
                        "field_name": new_key,
                        "table_id": PApplicantPersonUpdateData["p_applicant_person_id"],
                        "content": parameters[old_key],
                        "operate_type": OPERATE_TYPE.UPDATE.value,
                        "created_at": PApplicantPersonUpdateData["old_created_at"],
                        "updated_at": PApplicantPersonUpdateData["old_updated_at"],
                    }
                )
            else:
                continue
        if len(update) == 0:
            pass
        else:
            new_data[new_key] = {"create": create, "update": update}

    for old_key, new_key in p_applicant_person_parameters_files.items():
        create = []
        update = []
        values = []
        for PApplicantPersonCreateData in PApplicantPersonsCreateData:
            parameters = PApplicantPersonCreateData["parameters"]
            operator_type = owner_type_maps[PApplicantPersonCreateData["owner_type"]]
            operator_id = 0

            if operator_type == 1:
                user = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging.c_users WHERE old_id = {PApplicantPersonCreateData['owner_id']};"
                )
                if user:
                    operator_id = user["id"]
            if operator_type == 2:
                sales_person = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging.s_sales_persons WHERE old_id = {PApplicantPersonCreateData['owner_id']};"
                )
                if sales_person:
                    operator_id = sales_person["id"]
            if operator_type == 3:
                manager = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging.s_managers WHERE old_id = {PApplicantPersonCreateData['owner_id']};"
                )
                if manager:
                    operator_id = manager["id"]
            if old_key in parameters:
                if len([item for item in parameters[old_key] if item != ""]) == 0:
                    create.append(
                        {
                            "p_application_header_id": PApplicantPersonCreateData["p_application_header_id"],
                            "operator_type": operator_type,
                            "operator_id": operator_id,
                            "table_name": "p_applicant_persons",
                            "field_name": new_key,
                            "table_id": PApplicantPersonCreateData["p_applicant_person_id"],
                            "content": None,
                            "operate_type": OPERATE_TYPE.APPLY.value,
                            "created_at": PApplicantPersonCreateData["old_created_at"],
                            "updated_at": PApplicantPersonCreateData["old_updated_at"],
                        }
                    )
                else:
                    for file in [item for item in parameters[old_key] if item != ""]:
                        create.append(
                            {
                                "p_application_header_id": PApplicantPersonCreateData["p_application_header_id"],
                                "operator_type": operator_type,
                                "operator_id": operator_id,
                                "table_name": "p_applicant_persons",
                                "field_name": new_key,
                                "table_id": PApplicantPersonCreateData["p_applicant_person_id"],
                                "content": file,
                                "operate_type": OPERATE_TYPE.APPLY.value,
                                "created_at": PApplicantPersonCreateData["old_created_at"],
                                "updated_at": PApplicantPersonCreateData["old_updated_at"],
                            }
                        )
                values.append([item for item in parameters[old_key] if item != ""])

        for PApplicantPersonUpdateData in PApplicantPersonsUpdateData:
            parameters = PApplicantPersonUpdateData["parameters"]
            operator_type = owner_type_maps[PApplicantPersonUpdateData["owner_type"]]
            operator_id = 0

            if operator_type == 1:
                user = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging.c_users WHERE old_id = {PApplicantPersonUpdateData['owner_id']};"
                )
                if user:
                    operator_id = user["id"]
            if operator_type == 2:
                sales_person = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging.s_sales_persons WHERE old_id = {PApplicantPersonUpdateData['owner_id']};"
                )
                if sales_person:
                    operator_id = sales_person["id"]
            if operator_type == 3:
                manager = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging.s_managers WHERE old_id = {PApplicantPersonUpdateData['owner_id']};"
                )
                if manager:
                    operator_id = manager["id"]

            if old_key in parameters:
                pre_value = values[-1]
                for file in [item for item in parameters[old_key] if item != ""]:
                    if file not in pre_value:
                        update.append(
                            {
                                "p_application_header_id": PApplicantPersonUpdateData["p_application_header_id"],
                                "operator_type": operator_type,
                                "operator_id": operator_id,
                                "table_name": "p_applicant_persons",
                                "field_name": new_key,
                                "table_id": PApplicantPersonUpdateData["p_applicant_person_id"],
                                "content": file,
                                "operate_type": OPERATE_TYPE.CREATE.value,
                                "created_at": PApplicantPersonUpdateData["old_created_at"],
                                "updated_at": PApplicantPersonUpdateData["old_updated_at"],
                            }
                        )
                for file in list(set(pre_value) - set([item for item in parameters[old_key] if item != ""])):
                    update.append(
                        {
                            "p_application_header_id": PApplicantPersonUpdateData["p_application_header_id"],
                            "operator_type": operator_type,
                            "operator_id": operator_id,
                            "table_name": "p_applicant_persons",
                            "field_name": new_key,
                            "table_id": PApplicantPersonUpdateData["p_applicant_person_id"],
                            "content": file,
                            "operate_type": OPERATE_TYPE.CREATE.value,
                            "created_at": PApplicantPersonUpdateData["old_created_at"],
                            "updated_at": PApplicantPersonUpdateData["old_updated_at"],
                        }
                    )
                values.append([item for item in parameters[old_key] if item != ""])
            else:
                continue
        if len(update) == 0:
            pass
        else:
            new_data[new_key] = {"create": create, "update": update}

    return new_data
    return PApplicantPersonsCreateData + PApplicantPersonsUpdateData
    # return PApplicationHeadersUpdateData + PApplicationHeadersUpdateData
