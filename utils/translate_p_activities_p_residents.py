from constant import OPERATE_TYPE
from core.database import DB
import yaml

import utils
from .db_filed_maps import p_residents_parameters


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


async def translate_p_activities_p_residents(db: DB, p_application_header_id):
    # p_residents
    sql = f"""
    SELECT
        p.id as p_resident_id,
        p.p_application_header_id as p_application_header_id,
        a.owner_type,
        a.owner_id,
        a.key,
        a.parameters,
        DATE_FORMAT(a.created_at, '%Y-%m-%d %H:%i:%S') as old_created_at,
        DATE_FORMAT(a.updated_at, '%Y-%m-%d %H:%i:%S') as old_updated_at
    FROM
        mortgage_staging_v1.p_residents as p
    LEFT JOIN
        mortgage_loan_tool_be_production.activities as a
        ON
        a.trackable_id = p.old_id
    WHERE
        p.p_application_header_id = {p_application_header_id}
        AND
        a.trackable_type='PResident'
        
    """

    PResidentsCreateData = [
        {**item, "parameters": yaml.safe_load(item["parameters"])}
        for item in await db.fetch_all(sql + "AND a.key = 'p_resident.create'")
    ]
    PResidentsUpdateData = [
        {**item, "parameters": yaml.safe_load(item["parameters"])}
        for item in await db.fetch_all(sql + "AND a.key = 'p_resident.update'")
    ]

    new_data = {}

    for old_key, new_key in p_residents_parameters.items():
        create = []
        update = []
        for PResidentCreateData in PResidentsCreateData:
            parameters = PResidentCreateData["parameters"]
            operator_type = owner_type_maps[PResidentCreateData["owner_type"]]
            operator_id = 0

            if operator_type == 1:
                user = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v1.c_users WHERE old_id = {PResidentCreateData['owner_id']};"
                )
                if user:
                    operator_id = user["id"]
            if operator_type == 2:
                sales_person = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v1.s_sales_persons WHERE old_id = {PResidentCreateData['owner_id']};"
                )
                if sales_person:
                    operator_id = sales_person["id"]
            if operator_type == 3:
                manager = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v1.s_managers WHERE old_id = {PResidentCreateData['owner_id']};"
                )
                if manager:
                    operator_id = manager["id"]
            create.append(
                {
                    "p_application_header_id": PResidentCreateData["p_application_header_id"],
                    "operator_type": operator_type,
                    "operator_id": operator_id,
                    "table_name": "p_residents",
                    "field_name": new_key,
                    "table_id": PResidentCreateData["p_resident_id"],
                    "content": parameters[old_key],
                    "operate_type": OPERATE_TYPE.APPLY.value,
                }
            )
        for PResidentUpdateData in PResidentsUpdateData:
            parameters = PResidentUpdateData["parameters"]
            operator_type = owner_type_maps[PResidentUpdateData["owner_type"]]
            operator_id = 0

            if operator_type == 1:
                user = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v1.c_users WHERE old_id = {PResidentUpdateData['owner_id']};"
                )
                if user:
                    operator_id = user["id"]
            if operator_type == 2:
                sales_person = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v1.s_sales_persons WHERE old_id = {PResidentUpdateData['owner_id']};"
                )
                if sales_person:
                    operator_id = sales_person["id"]
            if operator_type == 3:
                manager = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v1.s_managers WHERE old_id = {PResidentUpdateData['owner_id']};"
                )
                if manager:
                    operator_id = manager["id"]

            if old_key in parameters:
                update.append(
                    {
                        "p_application_header_id": PResidentUpdateData["p_application_header_id"],
                        "operator_type": operator_type,
                        "operator_id": operator_id,
                        "table_name": "p_residents",
                        "field_name": new_key,
                        "table_id": PResidentUpdateData["p_resident_id"],
                        "content": parameters[old_key],
                        "operate_type": OPERATE_TYPE.UPDATE.value,
                    }
                )
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
