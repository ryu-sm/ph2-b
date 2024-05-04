import json
from constant import OPERATE_TYPE
from core.database import DB
import yaml
from datetime import date
import utils
from .db_filed_maps import p_borrowing_details_parameters


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


async def translate_p_activities_p_borrowing_details(db: DB, p_borrowing_detail_id):
    # translate_p_activities_p_borrowing_details
    sql = f"""
    SELECT
        p.id as p_borrowing_detail_id,
        p.p_application_header_id as p_application_header_id,
        a.owner_type,
        a.owner_id,
        a.key,
        a.parameters,
        DATE_FORMAT(a.created_at, '%Y-%m-%d %H:%i:%S') as old_created_at,
        DATE_FORMAT(a.updated_at, '%Y-%m-%d %H:%i:%S') as old_updated_at
    FROM
        mortgage_staging_v1.p_borrowing_details as p
    LEFT JOIN
        mortgage_loan_tool_be_production.activities as a
        ON
        a.trackable_id = p.old_id
    WHERE
        p.id = {p_borrowing_detail_id}
        AND
        a.trackable_type='PBorrowingDetail'
        
    """

    PBorrowingDetailsCreateData = [
        {**item, "parameters": yaml.safe_load(item["parameters"])}
        for item in await db.fetch_all(sql + "AND a.key = 'p_borrowing_detail.create'")
    ]
    PBorrowingDetailsUpdateData = [
        {**item, "parameters": yaml.safe_load(item["parameters"])}
        for item in await db.fetch_all(sql + "AND a.key = 'p_borrowing_detail.update'")
    ]

    new_data = {}

    for old_key, new_key in p_borrowing_details_parameters.items():
        create = []
        update = []
        for PBorrowingDetailCreateData in PBorrowingDetailsCreateData:
            parameters = PBorrowingDetailCreateData["parameters"]
            if "loan_desired_borrowing_date" in parameters and parameters["loan_desired_borrowing_date"]:
                if isinstance(parameters["loan_desired_borrowing_date"], date):
                    parameters["loan_desired_borrowing_date"] = parameters["loan_desired_borrowing_date"].strftime(
                        "%Y/%m/%d"
                    )
            if (
                "borrowing_detail_type" in parameters
                and parameters["borrowing_detail_type"] == "first_borrowing_detail"
            ):
                parameters["borrowing_detail_type"] = 1
            if (
                "borrowing_detail_type" in parameters
                and parameters["borrowing_detail_type"] == "second_borrowing_detail"
            ):
                parameters["borrowing_detail_type"] = 2

            operator_type = owner_type_maps[PBorrowingDetailCreateData["owner_type"]]
            operator_id = 0

            if operator_type == 1:
                user = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v1.c_users WHERE old_id = {PBorrowingDetailCreateData['owner_id']};"
                )
                if user:
                    operator_id = user["id"]
            if operator_type == 2:
                sales_person = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v1.s_sales_persons WHERE old_id = {PBorrowingDetailCreateData['owner_id']};"
                )
                if sales_person:
                    operator_id = sales_person["id"]
            if operator_type == 3:
                manager = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v1.s_managers WHERE old_id = {PBorrowingDetailCreateData['owner_id']};"
                )
                if manager:
                    operator_id = manager["id"]
            create.append(
                {
                    "p_application_header_id": PBorrowingDetailCreateData["p_application_header_id"],
                    "operator_type": operator_type,
                    "operator_id": operator_id,
                    "table_name": "p_borrowing_details",
                    "field_name": new_key,
                    "table_id": PBorrowingDetailCreateData["p_borrowing_detail_id"],
                    "content": parameters[old_key],
                    "operate_type": OPERATE_TYPE.APPLY.value,
                }
            )
        for PBorrowingDetailUpdateData in PBorrowingDetailsUpdateData:
            parameters = PBorrowingDetailUpdateData["parameters"]
            if "loan_desired_borrowing_date" in parameters and parameters["loan_desired_borrowing_date"]:
                if isinstance(parameters["loan_desired_borrowing_date"], date):
                    parameters["loan_desired_borrowing_date"] = parameters["loan_desired_borrowing_date"].strftime(
                        "%Y/%m/%d"
                    )

            if (
                "borrowing_detail_type" in parameters
                and parameters["borrowing_detail_type"] == "first_borrowing_detail"
            ):
                parameters["borrowing_detail_type"] = 1
            if (
                "borrowing_detail_type" in parameters
                and parameters["borrowing_detail_type"] == "second_borrowing_detail"
            ):
                parameters["borrowing_detail_type"] = 2
            operator_type = owner_type_maps[PBorrowingDetailUpdateData["owner_type"]]
            operator_id = 0

            if operator_type == 1:
                user = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v1.c_users WHERE old_id = {PBorrowingDetailUpdateData['owner_id']};"
                )
                if user:
                    operator_id = user["id"]
            if operator_type == 2:
                sales_person = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v1.s_sales_persons WHERE old_id = {PBorrowingDetailUpdateData['owner_id']};"
                )
                if sales_person:
                    operator_id = sales_person["id"]
            if operator_type == 3:
                manager = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v1.s_managers WHERE old_id = {PBorrowingDetailUpdateData['owner_id']};"
                )
                if manager:
                    operator_id = manager["id"]

            if old_key in parameters:
                update.append(
                    {
                        "p_application_header_id": PBorrowingDetailUpdateData["p_application_header_id"],
                        "operator_type": operator_type,
                        "operator_id": operator_id,
                        "table_name": "p_borrowing_details",
                        "field_name": new_key,
                        "table_id": PBorrowingDetailUpdateData["p_borrowing_detail_id"],
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
