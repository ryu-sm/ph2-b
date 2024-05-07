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


async def get_type_and_id(db: DB, viewed_account_id, viewed_account_type):
    if viewed_account_type == "User":
        user = await db.fetch_one(f"SELECT id FROM mortgage_staging_v2.c_users WHERE old_id = {viewed_account_id}")
        user_id = None
        if user:
            user_id = user["id"]
        return {"viewed_account_id": user_id, "viewed_account_type": 1}
    if viewed_account_type == "SSalePerson":
        user = await db.fetch_one(
            f"SELECT id FROM mortgage_staging_v2.s_sales_persons WHERE old_id = {viewed_account_id}"
        )
        user_id = None
        if user:
            user_id = user["id"]
        return {"viewed_account_id": user_id, "viewed_account_type": 2}
    if viewed_account_type == "Manager":
        user = await db.fetch_one(f"SELECT id FROM mortgage_staging_v2.s_managers WHERE old_id = {viewed_account_id}")
        user_id = None
        if user:
            user_id = user["id"]
        return {"viewed_account_id": user_id, "viewed_account_type": 3}


async def translate_c_messages(db: DB):
    # p_drafts
    sql = f"""
    SELECT
        om.viewed
    FROM
        mortgage_loan_tool_be_production.messages as om
    JOIN
        mortgage_staging_v2.c_messages as nm
        ON
        nm.old_id = om.id
    """
    for message in await db.fetch_all(sql):
        v_list = []
        old = yaml.safe_load(message["viewed"].replace("!ruby/hash:ActiveSupport::HashWithIndifferentAccess", ""))
        for item in old:
            new = await get_type_and_id(db, item["viewed_account_id"], item["viewed_account_type"])
            v_list.append(new)
        await db.execute(f"""UPDATE c_messages SET viewed = '{json.dumps(v_list, ensure_ascii=False)}' """)
