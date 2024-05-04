from constant import OPERATE_TYPE
from core.database import DB
import utils
import yaml
from .db_filed_maps import (
    p_applicant_person_parameters_0_h,
    p_applicant_person_parameters_0,
    p_applicant_person_parameters_files,
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

owner_type_kanji_maps = {
    1: "USER",
    2: "SALES_PERSON",
    3: "MANAGER",
}


async def translate_p_activities_p_applicant_persons_0(db: DB, p_application_header_id):
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
        mortgage_staging_v1.p_applicant_persons as p
    LEFT JOIN
        mortgage_loan_tool_be_production.activities as a
        ON
        a.trackable_id = p.old_id
    WHERE
        p.p_application_header_id = {p_application_header_id}
        AND
        p.type = 0
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
    for old_key, new_key in p_applicant_person_parameters_0_h.items():
        create = []
        update = []
        for PApplicantPersonCreateData in PApplicantPersonsCreateData:
            parameters = PApplicantPersonCreateData["parameters"]
            operator_type = owner_type_maps[PApplicantPersonCreateData["owner_type"]]
            operator_id = 0

            if operator_type == 1:
                user = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v1.c_users WHERE old_id = {PApplicantPersonCreateData['owner_id']};"
                )
                if user:
                    operator_id = user["id"]
            if operator_type == 2:
                sales_person = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v1.s_sales_persons WHERE old_id = {PApplicantPersonCreateData['owner_id']};"
                )
                if sales_person:
                    operator_id = sales_person["id"]
            if operator_type == 3:
                manager = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v1.s_managers WHERE old_id = {PApplicantPersonCreateData['owner_id']};"
                )
                if manager:
                    operator_id = manager["id"]

            create.append(
                {
                    "p_application_header_id": PApplicantPersonCreateData["p_application_header_id"],
                    "operator_type": operator_type,
                    "operator_id": operator_id,
                    "table_name": "p_application_headers",
                    "field_name": new_key,
                    "table_id": PApplicantPersonCreateData["p_application_header_id"],
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
                    f"SELECT id FROM mortgage_staging_v1.c_users WHERE old_id = {PApplicantPersonUpdateData['owner_id']};"
                )
                if user:
                    operator_id = user["id"]
            if operator_type == 2:
                sales_person = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v1.s_sales_persons WHERE old_id = {PApplicantPersonUpdateData['owner_id']};"
                )
                if sales_person:
                    operator_id = sales_person["id"]
            if operator_type == 3:
                manager = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v1.s_managers WHERE old_id = {PApplicantPersonUpdateData['owner_id']};"
                )
                if manager:
                    operator_id = manager["id"]

            if old_key in parameters:
                update.append(
                    {
                        "p_application_header_id": PApplicantPersonUpdateData["p_application_header_id"],
                        "operator_type": operator_type,
                        "operator_id": operator_id,
                        "table_name": "p_application_headers",
                        "field_name": new_key,
                        "table_id": PApplicantPersonUpdateData["p_application_header_id"],
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

    for old_key, new_key in p_applicant_person_parameters_0.items():
        create = []
        update = []
        for PApplicantPersonCreateData in PApplicantPersonsCreateData:
            parameters = PApplicantPersonCreateData["parameters"]
            operator_type = owner_type_maps[PApplicantPersonCreateData["owner_type"]]
            operator_id = 0

            if operator_type == 1:
                user = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v1.c_users WHERE old_id = {PApplicantPersonCreateData['owner_id']};"
                )
                if user:
                    operator_id = user["id"]
            if operator_type == 2:
                sales_person = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v1.s_sales_persons WHERE old_id = {PApplicantPersonCreateData['owner_id']};"
                )
                if sales_person:
                    operator_id = sales_person["id"]
            if operator_type == 3:
                manager = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v1.s_managers WHERE old_id = {PApplicantPersonCreateData['owner_id']};"
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
                    f"SELECT id FROM mortgage_staging_v1.c_users WHERE old_id = {PApplicantPersonUpdateData['owner_id']};"
                )
                if user:
                    operator_id = user["id"]
            if operator_type == 2:
                sales_person = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v1.s_sales_persons WHERE old_id = {PApplicantPersonUpdateData['owner_id']};"
                )
                if sales_person:
                    operator_id = sales_person["id"]
            if operator_type == 3:
                manager = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v1.s_managers WHERE old_id = {PApplicantPersonUpdateData['owner_id']};"
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
                    f"SELECT id FROM mortgage_staging_v1.c_users WHERE old_id = {PApplicantPersonCreateData['owner_id']};"
                )
                if user:
                    operator_id = user["id"]
            if operator_type == 2:
                sales_person = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v1.s_sales_persons WHERE old_id = {PApplicantPersonCreateData['owner_id']};"
                )
                if sales_person:
                    operator_id = sales_person["id"]
            if operator_type == 3:
                manager = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v1.s_managers WHERE old_id = {PApplicantPersonCreateData['owner_id']};"
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
                    f"SELECT id FROM mortgage_staging_v1.c_users WHERE old_id = {PApplicantPersonUpdateData['owner_id']};"
                )
                if user:
                    operator_id = user["id"]
            if operator_type == 2:
                sales_person = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v1.s_sales_persons WHERE old_id = {PApplicantPersonUpdateData['owner_id']};"
                )
                if sales_person:
                    operator_id = sales_person["id"]
            if operator_type == 3:
                manager = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v1.s_managers WHERE old_id = {PApplicantPersonUpdateData['owner_id']};"
                )
                if manager:
                    operator_id = manager["id"]

            if old_key in parameters:
                pre_value = [] if len(values) == 0 else values[-1]
                old_value = [] if parameters[old_key] == "アップロードファイルを削除した" else parameters[old_key]
                for file in [item for item in old_value if item != ""]:
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
                for file in list(set(pre_value) - set([item for item in old_value if item != ""])):
                    update.append(
                        {
                            "p_application_header_id": PApplicantPersonUpdateData["p_application_header_id"],
                            "operator_type": operator_type,
                            "operator_id": operator_id,
                            "table_name": "p_applicant_persons",
                            "field_name": new_key,
                            "table_id": PApplicantPersonUpdateData["p_applicant_person_id"],
                            "content": file,
                            "operate_type": OPERATE_TYPE.DELETE.value,
                            "created_at": PApplicantPersonUpdateData["old_created_at"],
                            "updated_at": PApplicantPersonUpdateData["old_updated_at"],
                        }
                    )
                values.append([item for item in old_value if item != ""])
            else:
                continue
        if len(update) == 0:
            pass
        else:
            new_data[new_key] = {"create": create, "update": update}

    for key, value in new_data.items():
        datas = value["create"] + value["update"]
        for data in datas:
            id = await db.uuid_short()
            await db.execute(utils.gen_insert_sql("mortgage_staging_v1.p_activities", {"id": id, **data}))

    # return new_data
    # return PApplicantPersonsCreateData + PApplicantPersonsUpdateData
    # # return PApplicationHeadersUpdateData + PApplicationHeadersUpdateData
