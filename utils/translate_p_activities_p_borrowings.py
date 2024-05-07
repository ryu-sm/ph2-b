from constant import OPERATE_TYPE
from core.database import DB
import yaml

import utils
from .db_filed_maps import p_borrowings_parameters


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


async def translate_p_activities_p_borrowings(db: DB, p_application_header_id):
    # p_borrowings
    sql = f"""
    SELECT
        p.id as p_borrowing_id,
        p.p_application_header_id as p_application_header_id,
        a.owner_type,
        a.owner_id,
        a.key,
        a.parameters,
        DATE_FORMAT(a.created_at, '%Y-%m-%d %H:%i:%S') as old_created_at,
        DATE_FORMAT(a.updated_at, '%Y-%m-%d %H:%i:%S') as old_updated_at
    FROM
        mortgage_staging_v3.p_borrowings as p
    LEFT JOIN
        mortgage_loan_tool_be_production.activities as a
        ON
        a.trackable_id = p.old_id
    WHERE
        p.p_application_header_id = {p_application_header_id}
        AND
        a.trackable_type='PBorrowing'
        
    """

    PBorrowingsCreateData = [
        {**item, "parameters": yaml.safe_load(item["parameters"])}
        for item in await db.fetch_all(sql + "AND a.key = 'p_borrowing.create'")
    ]
    PBorrowingsUpdateData = [
        {**item, "parameters": yaml.safe_load(item["parameters"])}
        for item in await db.fetch_all(sql + "AND a.key IN ('p_borrowing.update', 'PBorrowing.update')")
    ]

    new_data = {}

    for old_key in ["repayment_schedule_image"]:
        create = []
        update = []
        values = []
        for PBorrowingCreateData in PBorrowingsCreateData:
            parameters = PBorrowingCreateData["parameters"]
            operator_type = owner_type_maps[PBorrowingCreateData["owner_type"]]
            operator_id = 0

            if operator_type == 1:
                user = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v3.c_users WHERE old_id = {PBorrowingCreateData['owner_id']};"
                )
                if user:
                    operator_id = user["id"]
            if operator_type == 2:
                sales_person = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v3.s_sales_persons WHERE old_id = {PBorrowingCreateData['owner_id']};"
                )
                if sales_person:
                    operator_id = sales_person["id"]
            if operator_type == 3:
                manager = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v3.s_managers WHERE old_id = {PBorrowingCreateData['owner_id']};"
                )
                if manager:
                    operator_id = manager["id"]

            if old_key in parameters:
                files = []
                if parameters[old_key] and parameters[old_key] != "アップロードファイルを削除した":
                    files = [item for item in parameters[old_key] if item != ""]
                    create.append(
                        {
                            "p_application_header_id": PBorrowingCreateData["p_application_header_id"],
                            "operator_type": operator_type,
                            "operator_id": operator_id,
                            "table_name": "p_borrowings",
                            "field_name": "I",
                            "table_id": PBorrowingCreateData["p_borrowing_id"],
                            "content": ", ".join(files) if files else None,
                            "operate_type": OPERATE_TYPE.APPLY.value,
                            "created_at": PBorrowingCreateData["old_created_at"],
                            "updated_at": PBorrowingCreateData["old_updated_at"],
                        }
                    )
                # if len([item for item in parameters[old_key] if item != ""]) == 0:
                #     create.append(
                #         {
                #             "p_application_header_id": PBorrowingCreateData["p_application_header_id"],
                #             "operator_type": operator_type,
                #             "operator_id": operator_id,
                #             "table_name": "p_borrowings",
                #             "field_name": "I",
                #             "table_id": PBorrowingCreateData["p_borrowing_id"],
                #             "content": None,
                #             "operate_type": OPERATE_TYPE.APPLY.value,
                #             "created_at": PBorrowingCreateData["old_created_at"],
                #             "updated_at": PBorrowingCreateData["old_updated_at"],
                #         }
                #     )
                # else:
                #     for file in [item for item in parameters[old_key] if item != ""]:
                #         create.append(
                #             {
                #                 "p_application_header_id": PBorrowingCreateData["p_application_header_id"],
                #                 "operator_type": operator_type,
                #                 "operator_id": operator_id,
                #                 "table_name": "p_borrowings",
                #                 "field_name": "I",
                #                 "table_id": PBorrowingCreateData["p_borrowing_id"],
                #                 "content": file,
                #                 "operate_type": OPERATE_TYPE.APPLY.value,
                #                 "created_at": PBorrowingCreateData["old_created_at"],
                #                 "updated_at": PBorrowingCreateData["old_updated_at"],
                #             }
                #         )
                # values.append([item for item in parameters[old_key] if item != ""])

        for PBorrowingUpdateData in PBorrowingsUpdateData:
            parameters = PBorrowingUpdateData["parameters"]
            operator_type = owner_type_maps[PBorrowingUpdateData["owner_type"]]
            operator_id = 0

            if operator_type == 1:
                user = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v3.c_users WHERE old_id = {PBorrowingUpdateData['owner_id']};"
                )
                if user:
                    operator_id = user["id"]
            if operator_type == 2:
                sales_person = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v3.s_sales_persons WHERE old_id = {PBorrowingUpdateData['owner_id']};"
                )
                if sales_person:
                    operator_id = sales_person["id"]
            if operator_type == 3:
                manager = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v3.s_managers WHERE old_id = {PBorrowingUpdateData['owner_id']};"
                )
                if manager:
                    operator_id = manager["id"]

            if old_key in parameters:
                files = []
                if parameters[old_key] and parameters[old_key] != "アップロードファイルを削除した":
                    files = [item for item in parameters[old_key] if item != ""]
                    update.append(
                        {
                            "p_application_header_id": PBorrowingCreateData["p_application_header_id"],
                            "operator_type": operator_type,
                            "operator_id": operator_id,
                            "table_name": "p_borrowings",
                            "field_name": "I",
                            "table_id": PBorrowingCreateData["p_borrowing_id"],
                            "content": ", ".join(files) if files else None,
                            "operate_type": OPERATE_TYPE.UPDATE.value,
                            "created_at": PBorrowingCreateData["old_created_at"],
                            "updated_at": PBorrowingCreateData["old_updated_at"],
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
                #                 "p_application_header_id": PBorrowingUpdateData["p_application_header_id"],
                #                 "operator_type": operator_type,
                #                 "operator_id": operator_id,
                #                 "table_name": "p_borrowings",
                #                 "field_name": "I",
                #                 "table_id": PBorrowingUpdateData["p_borrowing_id"],
                #                 "content": up_file,
                #                 "operate_type": OPERATE_TYPE.UPDATE.value,
                #                 "created_at": PBorrowingUpdateData["old_created_at"],
                #                 "updated_at": PBorrowingUpdateData["old_updated_at"],
                #             }
                #         )
                # for ol_file in ol_files:
                #     if ol_file in up_files:
                #         continue
                #     else:
                #         update.append(
                #             {
                #                 "p_application_header_id": PBorrowingUpdateData["p_application_header_id"],
                #                 "operator_type": operator_type,
                #                 "operator_id": operator_id,
                #                 "table_name": "p_borrowings",
                #                 "field_name": "I",
                #                 "table_id": PBorrowingUpdateData["p_borrowing_id"],
                #                 "content": up_file,
                #                 "operate_type": OPERATE_TYPE.DELETE.value,
                #                 "created_at": PBorrowingUpdateData["old_created_at"],
                #                 "updated_at": PBorrowingUpdateData["old_updated_at"],
                #             }
                #         )
                # values = up_files
        new_data[old_key] = {"create": create, "update": update}

    for old_key, new_key in p_borrowings_parameters.items():
        create = []
        update = []
        for PBorrowingCreateData in PBorrowingsCreateData:
            parameters = PBorrowingCreateData["parameters"]
            operator_type = owner_type_maps[PBorrowingCreateData["owner_type"]]
            operator_id = 0

            if operator_type == 1:
                user = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v3.c_users WHERE old_id = {PBorrowingCreateData['owner_id']};"
                )
                if user:
                    operator_id = user["id"]
            if operator_type == 2:
                sales_person = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v3.s_sales_persons WHERE old_id = {PBorrowingCreateData['owner_id']};"
                )
                if sales_person:
                    operator_id = sales_person["id"]
            if operator_type == 3:
                manager = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v3.s_managers WHERE old_id = {PBorrowingCreateData['owner_id']};"
                )
                if manager:
                    operator_id = manager["id"]
            create.append(
                {
                    "p_application_header_id": PBorrowingCreateData["p_application_header_id"],
                    "operator_type": operator_type,
                    "operator_id": operator_id,
                    "table_name": "p_borrowings",
                    "field_name": new_key,
                    "table_id": PBorrowingCreateData["p_borrowing_id"],
                    "content": parameters[old_key],
                    "operate_type": OPERATE_TYPE.APPLY.value,
                }
            )
        for PBorrowingUpdateData in PBorrowingsUpdateData:
            parameters = PBorrowingUpdateData["parameters"]
            operator_type = owner_type_maps[PBorrowingUpdateData["owner_type"]]
            operator_id = 0

            if operator_type == 1:
                user = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v3.c_users WHERE old_id = {PBorrowingUpdateData['owner_id']};"
                )
                if user:
                    operator_id = user["id"]
            if operator_type == 2:
                sales_person = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v3.s_sales_persons WHERE old_id = {PBorrowingUpdateData['owner_id']};"
                )
                if sales_person:
                    operator_id = sales_person["id"]
            if operator_type == 3:
                manager = await db.fetch_one(
                    f"SELECT id FROM mortgage_staging_v3.s_managers WHERE old_id = {PBorrowingUpdateData['owner_id']};"
                )
                if manager:
                    operator_id = manager["id"]

            if old_key in parameters:
                update.append(
                    {
                        "p_application_header_id": PBorrowingUpdateData["p_application_header_id"],
                        "operator_type": operator_type,
                        "operator_id": operator_id,
                        "table_name": "p_borrowings",
                        "field_name": new_key,
                        "table_id": PBorrowingUpdateData["p_borrowing_id"],
                        "content": (
                            int(parameters[old_key]) if type(parameters[old_key]) is bool else parameters[old_key]
                        ),
                        "operate_type": OPERATE_TYPE.UPDATE.value,
                    }
                )
            else:
                continue
        # if len(update) == 0:
        #     pass
        # else:
        new_data[new_key] = {"create": create, "update": update}

    for key, value in new_data.items():
        datas = value["create"] + value["update"]
        for data in datas:
            id = await db.uuid_short()
            await db.execute(utils.gen_insert_sql("mortgage_staging_v3.p_activities", {"id": id, **data}))
