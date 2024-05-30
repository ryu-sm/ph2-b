from core.database import DB


async def translate_sales_host_company_id(db: DB):
    default_id = "999999999999999999"

    sql = """SELECT id, s_sales_person_id, sales_company_id, sales_area_id, sales_exhibition_hall_id FROM p_application_headers;"""

    for ph in await db.fetch_all(sql):
        org_ids = []
        child_org_id = ph["sales_company_id"] or ph["sales_area_id"] or ph["sales_exhibition_hall_id"]

        if child_org_id:
            org_ids.append(str(child_org_id))

        if child_org_id is None and ph["s_sales_person_id"]:
            rel_orgs = await db.fetch_all(
                f"SELECT s_sales_company_org_id FROM s_sales_person_s_sales_company_org_rels WHERE s_sales_person_id = {ph['s_sales_person_id']}"
            )

            for org in rel_orgs:
                if org["s_sales_company_org_id"]:
                    org_ids.append(str(org["s_sales_company_org_id"]))

        child_id = default_id

        if org_ids:
            child_id = org_ids[0]

        sql = f"""
        WITH RECURSIVE child AS (
        SELECT id, pid, category, name FROM s_sales_company_orgs WHERE id = {child_id}
        union
        SELECT parents.id, parents.pid, parents.category, parents.name FROM s_sales_company_orgs as parents INNER JOIN child ON parents.id = child.pid
        )
        SELECT
            child.id,
            child.name
        FROM
            child
        WHERE
            child.category = "H";
        """
        host_org = await db.fetch_one(sql)
        sql = f"""UPDATE p_application_headers SET sales_host_company_id = {host_org["id"]} WHERE id = {ph["id"]}"""
        await db.execute(sql)
