from core.database import DB


async def translate_id_to_input(db: DB):
    sql = """SELECT id, sales_company_id, sales_area_id, sales_exhibition_hall_id FROM p_application_headers"""
    for p_application_header in await db.fetch_all(sql):
        if p_application_header.get("sales_company_id"):
            org = await db.fetch_one(
                f"""SELECT name FROM s_sales_company_orgs WHERE id = {p_application_header.get("sales_company_id")}"""
            )
            if org:
                await db.execute(
                    f"""UPDATE p_application_headers SET sales_company = '{org["name"]}' WHERE id = {p_application_header["id"]}"""
                )
        if p_application_header.get("sales_area_id"):
            org = await db.fetch_one(
                f"""SELECT name FROM s_sales_company_orgs WHERE id = {p_application_header.get("sales_area_id")}"""
            )
            if org:
                await db.execute(
                    f"""UPDATE p_application_headers SET sales_area = '{org["name"]}' WHERE id = {p_application_header["id"]}"""
                )
        if p_application_header.get("sales_exhibition_hall_id"):
            org = await db.fetch_one(
                f"""SELECT name FROM s_sales_company_orgs WHERE id = {p_application_header.get("sales_exhibition_hall_id")}"""
            )
            if org:
                await db.execute(
                    f"""UPDATE p_application_headers SET sales_exhibition_hall = '{org["name"]}' WHERE id = {p_application_header["id"]}"""
                )
