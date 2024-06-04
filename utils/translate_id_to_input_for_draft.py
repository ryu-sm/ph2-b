import json
from core.database import DB


async def translate_id_to_input_for_draft(db: DB):
    sql = """SELECT * FROM p_drafts"""
    for p_draft in await db.fetch_all(sql):
        data = json.loads(p_draft.get("data", "{}"))

        p_application_header = data.get("p_application_headers")
        if p_application_header:
            new_p_application_header = {**p_application_header}
            if p_application_header.get("sales_company_id"):
                org = await db.fetch_one(
                    f"""SELECT name FROM s_sales_company_orgs WHERE id = {p_application_header.get("sales_company_id")}"""
                )
                if org:
                    new_p_application_header["sales_company"] = org["name"]
                else:
                    new_p_application_header["sales_company"] = ""
            else:
                new_p_application_header["sales_company"] = ""

            if p_application_header.get("sales_area_id"):
                org = await db.fetch_one(
                    f"""SELECT name FROM s_sales_company_orgs WHERE id = {p_application_header.get("sales_area_id")}"""
                )
                if org:
                    new_p_application_header["sales_area"] = org["name"]
                else:
                    new_p_application_header["sales_area"] = ""
            else:
                new_p_application_header["sales_area"] = ""

            if p_application_header.get("sales_exhibition_hall_id"):
                org = await db.fetch_one(
                    f"""SELECT name FROM s_sales_company_orgs WHERE id = {p_application_header.get("sales_exhibition_hall_id")}"""
                )
                if org:
                    new_p_application_header["sales_exhibition_hall"] = org["name"]
                else:
                    new_p_application_header["sales_exhibition_hall"] = ""
            else:
                new_p_application_header["sales_exhibition_hall"] = ""

        await db.execute(
            f"""UPDATE p_drafts SET data = '{json.dumps({**data,"p_application_headers":new_p_application_header},ensure_ascii=False)}' WHERE id = {p_draft["id"]}"""
        )
