import json
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


async def translate_p_activities_p_application_headers(db: DB, p_application_header_id):
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
        mortgage_staging_v2.p_application_headers as h
    LEFT JOIN
        mortgage_loan_tool_be_production.activities as a
        ON
        a.trackable_id = h.old_id
    WHERE
        h.id = {p_application_header_id}
        AND
        a.trackable_type='PApplicationHeader'
        AND
        a.owner_type IS NOT NULL
        AND
        a.owner_id IS NOT NULL
    """

    PApplicationHeadersCreateData = [
        {**item, "parameters": yaml.safe_load(item["parameters"])}
        for item in await db.fetch_all(sql + "AND a.key = 'p_application_header.create'")
    ]
    PApplicationHeadersUpdateData = [
        {**item, "parameters": yaml.safe_load(item["parameters"])}
        for item in await db.fetch_all(
            sql + "AND a.key IN ('p_application_header.update', 'PApplicationHeader.update')"
        )
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
                    f"SELECT id FROM mortgage_staging_v2.c_users WHERE old_id = {PApplicationHeaderCreateData['owner_id']};"
                )
                if user:
                    operator_id = user["id"]
            if operator_type == 2:
                sales_person = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v2.s_sales_persons WHERE old_id = {PApplicationHeaderCreateData['owner_id']};"
                )
                if sales_person:
                    operator_id = sales_person["id"]
            if operator_type == 3:
                manager = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v2.s_managers WHERE old_id = {PApplicationHeaderCreateData['owner_id']};"
                )
                if manager:
                    operator_id = manager["id"]
            planned_cohabitant = parameters.get("planned_cohabitant", [])
            children_number = parameters.get("children_number")
            siblings_number = parameters.get("siblings_number")
            other_relationship = parameters.get("other_relationship")
            other_people_number = parameters.get("other_people_number")

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
                        "content": json.dumps(temp, ensure_ascii=False),
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
                    f"SELECT id FROM mortgage_staging_v2.c_users WHERE old_id = {PApplicationHeaderUpdateData['owner_id']};"
                )
                if user:
                    operator_id = user["id"]
            if operator_type == 2:
                sales_person = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v2.s_sales_persons WHERE old_id = {PApplicationHeaderUpdateData['owner_id']};"
                )
                if sales_person:
                    operator_id = sales_person["id"]
            if operator_type == 3:
                manager = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v2.s_managers WHERE old_id = {PApplicationHeaderUpdateData['owner_id']};"
                )
                if manager:
                    operator_id = manager["id"]
            planned_cohabitant = parameters.get("planned_cohabitant", [])
            children_number = parameters.get("children_number")
            siblings_number = parameters.get("siblings_number")
            other_relationship = parameters.get("other_relationship")
            other_people_number = parameters.get("other_people_number")

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
                        "content": json.dumps(temp, ensure_ascii=False),
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
                        "content": json.dumps(temp, ensure_ascii=False),
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
                    f"SELECT id FROM mortgage_staging_v2.c_users WHERE old_id = {PApplicationHeaderUpdateData['owner_id']};"
                )
                if user:
                    operator_id = user["id"]
            if operator_type == 2:
                sales_person = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v2.s_sales_persons WHERE old_id = {PApplicationHeaderUpdateData['owner_id']};"
                )
                if sales_person:
                    operator_id = sales_person["id"]
            if operator_type == 3:
                manager = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v2.s_managers WHERE old_id = {PApplicationHeaderUpdateData['owner_id']};"
                )
                if manager:
                    operator_id = manager["id"]
            planned_cohabitant = parameters.get("planned_cohabitant", [])
            children_number = parameters.get("children_number")
            siblings_number = parameters.get("siblings_number")
            other_relationship = parameters.get("other_relationship")
            other_people_number = parameters.get("other_people_number")

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
                    "content": json.dumps(temp, ensure_ascii=False),
                    "operate_type": OPERATE_TYPE.UPDATE.value,
                    "created_at": PApplicationHeaderUpdateData["old_created_at"],
                    "updated_at": PApplicationHeaderUpdateData["old_updated_at"],
                }
            )

    # if len(new_house_planned_resident_overview_update) == 0:
    #     pass
    # else:
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
                            f"SELECT id FROM mortgage_staging_v2.c_users WHERE old_id = {PApplicationHeaderCreateData['owner_id']};"
                        )
                        if user:
                            operator_id = user["id"]
                    if operator_type == 2:
                        sales_person = await db.fetch_one(
                            f"SELECT id FROM mortgage_staging_v2.s_sales_persons WHERE old_id = {PApplicationHeaderCreateData['owner_id']};"
                        )
                        if sales_person:
                            operator_id = sales_person["id"]
                    if operator_type == 3:
                        manager = await db.fetch_one(
                            f"SELECT id FROM mortgage_staging_v2.s_managers WHERE old_id = {PApplicationHeaderCreateData['owner_id']};"
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
                                f"""SELECT id FROM mortgage_staging_v2.s_sales_company_orgs WHERE code = '{p_referral_agencies["sale_agent_id"]}';"""
                            )

                            if org_c:
                                sales_company_id = org_c["id"]
                        if p_referral_agencies["store_id"]:
                            org_b = await db.fetch_one(
                                f"""SELECT id FROM mortgage_staging_v2.s_sales_company_orgs WHERE code = '{p_referral_agencies["store_id"]}';"""
                            )

                            if org_b:
                                sales_area_id = org_b["id"]
                        if p_referral_agencies["exhibition_id"]:
                            org_e = await db.fetch_one(
                                f"""SELECT id FROM mortgage_staging_v2.s_sales_company_orgs WHERE code = '{p_referral_agencies["exhibition_id"]}';"""
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
                            "created_at": PApplicationHeaderCreateData["old_created_at"],
                            "updated_at": PApplicationHeaderCreateData["old_updated_at"],
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
                            "created_at": PApplicationHeaderCreateData["old_created_at"],
                            "updated_at": PApplicationHeaderCreateData["old_updated_at"],
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
                            "created_at": PApplicationHeaderCreateData["old_created_at"],
                            "updated_at": PApplicationHeaderCreateData["old_updated_at"],
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
                            f"SELECT id FROM mortgage_staging_v2.c_users WHERE old_id = {PApplicationHeaderUpdateData['owner_id']};"
                        )
                        if user:
                            operator_id = user["id"]
                    if operator_type == 2:
                        sales_person = await db.fetch_one(
                            f"SELECT id FROM mortgage_staging_v2.s_sales_persons WHERE old_id = {PApplicationHeaderUpdateData['owner_id']};"
                        )
                        if sales_person:
                            operator_id = sales_person["id"]
                    if operator_type == 3:
                        manager = await db.fetch_one(
                            f"SELECT id FROM mortgage_staging_v2.s_managers WHERE old_id = {PApplicationHeaderUpdateData['owner_id']};"
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
                                f"""SELECT id FROM mortgage_staging_v2.s_sales_company_orgs WHERE code = '{p_referral_agencies["sale_agent_id"]}';"""
                            )

                            if org_c:
                                sales_company_id = org_c["id"]
                        if p_referral_agencies["store_id"]:
                            org_b = await db.fetch_one(
                                f"""SELECT id FROM mortgage_staging_v2.s_sales_company_orgs WHERE code = '{p_referral_agencies["store_id"]}';"""
                            )

                            if org_b:
                                sales_area_id = org_b["id"]
                        if p_referral_agencies["exhibition_id"]:
                            org_e = await db.fetch_one(
                                f"""SELECT id FROM mortgage_staging_v2.s_sales_company_orgs WHERE code = '{p_referral_agencies["exhibition_id"]}';"""
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
                                "created_at": PApplicationHeaderUpdateData["old_created_at"],
                                "updated_at": PApplicationHeaderUpdateData["old_updated_at"],
                            }
                        )
                    if sales_area_id != sales_area_id_values[-1]:
                        sales_area_id_update.append(
                            {
                                "p_application_header_id": PApplicationHeaderUpdateData["p_application_header_id"],
                                "operator_type": operator_type,
                                "operator_id": operator_id,
                                "table_name": "p_application_headers",
                                "field_name": "sales_area_id",
                                "table_id": PApplicationHeaderUpdateData["p_application_header_id"],
                                "content": sales_area_id,
                                "operate_type": OPERATE_TYPE.UPDATE.value,
                                "created_at": PApplicationHeaderUpdateData["old_created_at"],
                                "updated_at": PApplicationHeaderUpdateData["old_updated_at"],
                            }
                        )
                    if sales_exhibition_hall_id != sales_exhibition_hall_id_values[-1]:
                        sales_exhibition_hall_id_update.append(
                            {
                                "p_application_header_id": PApplicationHeaderUpdateData["p_application_header_id"],
                                "operator_type": operator_type,
                                "operator_id": operator_id,
                                "table_name": "p_application_headers",
                                "field_name": "sales_exhibition_hall_id",
                                "table_id": PApplicationHeaderUpdateData["p_application_header_id"],
                                "content": sales_exhibition_hall_id,
                                "operate_type": OPERATE_TYPE.UPDATE.value,
                                "created_at": PApplicationHeaderUpdateData["old_created_at"],
                                "updated_at": PApplicationHeaderUpdateData["old_updated_at"],
                            }
                        )
                else:
                    continue

            # if len(sales_company_id_update) == 0:
            #     pass
            # else:
            new_data["sales_company_id"] = {"create": sales_company_id_create, "update": sales_company_id_update}
            # if len(sales_area_id_update) == 0:
            #     pass
            # else:
            new_data["sales_area_id"] = {"create": sales_area_id_create, "update": sales_area_id_update}
            # if len(sales_exhibition_hall_id_update) == 0:
            #     pass
            # else:
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
                    f"SELECT id FROM mortgage_staging_v2.c_users WHERE old_id = {PApplicationHeaderCreateData['owner_id']};"
                )
                if user:
                    operator_id = user["id"]
            if operator_type == 2:
                sales_person = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v2.s_sales_persons WHERE old_id = {PApplicationHeaderCreateData['owner_id']};"
                )
                if sales_person:
                    operator_id = sales_person["id"]
            if operator_type == 3:
                manager = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v2.s_managers WHERE old_id = {PApplicationHeaderCreateData['owner_id']};"
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
                    "created_at": PApplicationHeaderCreateData["old_created_at"],
                    "updated_at": PApplicationHeaderCreateData["old_updated_at"],
                }
            )
        for PApplicationHeaderUpdateData in PApplicationHeadersUpdateData:
            parameters = PApplicationHeaderUpdateData["parameters"]
            if PApplicationHeaderUpdateData["owner_type"] is None:
                print(999999, PApplicationHeaderUpdateData)
            operator_type = owner_type_maps[PApplicationHeaderUpdateData["owner_type"]]
            operator_id = 0

            if operator_type == 1:
                user = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v2.c_users WHERE old_id = {PApplicationHeaderUpdateData['owner_id']};"
                )
                if user:
                    operator_id = user["id"]
            if operator_type == 2:
                sales_person = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v2.s_sales_persons WHERE old_id = {PApplicationHeaderUpdateData['owner_id']};"
                )
                if sales_person:
                    operator_id = sales_person["id"]
            if operator_type == 3:
                manager = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v2.s_managers WHERE old_id = {PApplicationHeaderUpdateData['owner_id']};"
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
                        "created_at": PApplicationHeaderUpdateData["old_created_at"],
                        "updated_at": PApplicationHeaderUpdateData["old_updated_at"],
                    }
                )
            else:
                continue
        # if len(update) == 0:
        #     pass
        # else:
        new_data[new_key] = {"create": create, "update": update}

    for old_key in ["business_card", "property_information_file"]:
        create = []
        update = []
        values = []
        for PApplicationHeaderCreateData in PApplicationHeadersCreateData:
            parameters = PApplicationHeaderCreateData["parameters"]
            operator_type = owner_type_maps[PApplicationHeaderCreateData["owner_type"]]
            operator_id = 0

            if operator_type == 1:
                user = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v2.c_users WHERE old_id = {PApplicationHeaderCreateData['owner_id']};"
                )
                if user:
                    operator_id = user["id"]
            if operator_type == 2:
                sales_person = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v2.s_sales_persons WHERE old_id = {PApplicationHeaderCreateData['owner_id']};"
                )
                if sales_person:
                    operator_id = sales_person["id"]
            if operator_type == 3:
                manager = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v2.s_managers WHERE old_id = {PApplicationHeaderCreateData['owner_id']};"
                )
                if manager:
                    operator_id = manager["id"]

            if old_key in parameters:
                files = []
                if parameters[old_key] and parameters[old_key] != "アップロードファイルを削除した":
                    files = [item for item in parameters[old_key] if item != ""]
                    create.append(
                        {
                            "p_application_header_id": PApplicationHeaderCreateData["p_application_header_id"],
                            "operator_type": operator_type,
                            "operator_id": operator_id,
                            "table_name": "p_application_headers",
                            "field_name": prekey_maps[old_key],
                            "table_id": PApplicationHeaderCreateData["p_application_header_id"],
                            "content": ", ".join(files) if files else None,
                            "operate_type": OPERATE_TYPE.APPLY.value,
                            "created_at": PApplicationHeaderCreateData["old_created_at"],
                            "updated_at": PApplicationHeaderCreateData["old_updated_at"],
                        }
                    )

        for PApplicationHeaderUpdateData in PApplicationHeadersUpdateData:
            parameters = PApplicationHeaderUpdateData["parameters"]
            operator_type = owner_type_maps[PApplicationHeaderUpdateData["owner_type"]]
            operator_id = 0

            if operator_type == 1:
                user = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v2.c_users WHERE old_id = {PApplicationHeaderUpdateData['owner_id']};"
                )
                if user:
                    operator_id = user["id"]
            if operator_type == 2:
                sales_person = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v2.s_sales_persons WHERE old_id = {PApplicationHeaderUpdateData['owner_id']};"
                )
                if sales_person:
                    operator_id = sales_person["id"]
            if operator_type == 3:
                manager = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v2.s_managers WHERE old_id = {PApplicationHeaderUpdateData['owner_id']};"
                )
                if manager:
                    operator_id = manager["id"]

            if old_key in parameters:
                files = []
                if parameters[old_key] and parameters[old_key] != "アップロードファイルを削除した":
                    files = [item for item in parameters[old_key] if item != ""]
                    update.append(
                        {
                            "p_application_header_id": PApplicationHeaderCreateData["p_application_header_id"],
                            "operator_type": operator_type,
                            "operator_id": operator_id,
                            "table_name": "p_application_headers",
                            "field_name": prekey_maps[old_key],
                            "table_id": PApplicationHeaderCreateData["p_application_header_id"],
                            "content": ", ".join(files) if files else None,
                            "operate_type": OPERATE_TYPE.UPDATE.value,
                            "created_at": PApplicationHeaderCreateData["old_created_at"],
                            "updated_at": PApplicationHeaderCreateData["old_updated_at"],
                        }
                    )
                # up_files = [item for item in parameters[old_key] if item != ""]
                # ol_files = values
                # for up_file in up_files:
                #     if up_file in ol_files:
                #         continue
                #     else:
                #         update.append(
                #             {
                #                 "p_application_header_id": PApplicationHeaderUpdateData["p_application_header_id"],
                #                 "operator_type": operator_type,
                #                 "operator_id": operator_id,
                #                 "table_name": "p_application_headers",
                #                 "field_name": prekey_maps[old_key],
                #                 "table_id": PApplicationHeaderUpdateData["p_application_header_id"],
                #                 "content": up_file,
                #                 "operate_type": OPERATE_TYPE.UPDATE.value,
                #                 "created_at": PApplicationHeaderUpdateData["old_created_at"],
                #                 "updated_at": PApplicationHeaderUpdateData["old_updated_at"],
                #             }
                #         )
                # for ol_file in ol_files:
                #     if ol_file in up_files:
                #         continue
                #     else:
                #         update.append(
                #             {
                #                 "p_application_header_id": PApplicationHeaderUpdateData["p_application_header_id"],
                #                 "operator_type": operator_type,
                #                 "operator_id": operator_id,
                #                 "table_name": "p_application_headers",
                #                 "field_name": prekey_maps[old_key],
                #                 "table_id": PApplicationHeaderUpdateData["p_application_header_id"],
                #                 "content": up_file,
                #                 "operate_type": OPERATE_TYPE.DELETE.value,
                #                 "created_at": PApplicationHeaderUpdateData["old_created_at"],
                #                 "updated_at": PApplicationHeaderUpdateData["old_updated_at"],
                #             }
                #         )
                # values = up_files
        new_data[old_key] = {"create": create, "update": update}

    for key, value in new_data.items():
        datas = value["create"] + value["update"]
        for data in datas:
            id = await db.uuid_short()
            await db.execute(utils.gen_insert_sql("mortgage_staging_v2.p_activities", {"id": id, **data}))
