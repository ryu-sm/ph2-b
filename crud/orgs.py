from core.database import DB


async def query_s_sales_company_orgs_root_id(db: DB, child_id: int):
    sql = f"""
    WITH RECURSIVE child AS (
     SELECT id, pid, category FROM s_sales_company_orgs WHERE id = {child_id}
     union
     SELECT parents.id, parents.pid, parents.category FROM s_sales_company_orgs as parents INNER JOIN child ON parents.id = child.pid
    )
    SELECT
        child.id AS root_id
    FROM
        child
    WHERE
        child.category = "C";
    """
    result = await db.fetch_one(sql)
    return result["root_id"]


async def query_s_sales_company_orgs(db: DB, s_sales_company_org_id: int):

    if s_sales_company_org_id:
        root_id = await query_s_sales_company_orgs_root_id(db, s_sales_company_org_id)

        sql = f"""
        WITH RECURSIVE parents AS (
        SELECT id, pid, category, name FROM s_sales_company_orgs WHERE id = {root_id}
        union
        SELECT child.id, child.pid, child.category, child.name FROM s_sales_company_orgs as child INNER JOIN parents ON parents.id = child.pid
        )
        SELECT
            CONVERT(parents.id,CHAR) as id,
            CONVERT(parents.pid,CHAR) as pid,
            parents.category,
            parents.name
        FROM
            parents
        WHERE
            parents.pid is NOT NULL;
        """
        return await db.fetch_all(sql)
    else:
        sql = """
        SELECT
            CONVERT(id,CHAR) as id,
            CONVERT(pid,CHAR) as pid,
            category,
            name
        FROM
            s_sales_company_orgs
        WHERE
            pid is NOT NULL;
        """
        return await db.fetch_all(sql)


async def query_child_s_sales_company_orgs(db: DB, parent_id: int):
    sql = f"""
    WITH RECURSIVE parents AS (
     SELECT id, pid, category, name FROM s_sales_company_orgs WHERE id = {parent_id}
     union
     SELECT child.id, child.pid, child.category, child.name FROM s_sales_company_orgs as child INNER JOIN parents ON parents.id = child.pid
    )
    SELECT
        CONVERT(parents.id,CHAR) as id,
        CONVERT(parents.pid,CHAR) as pid,
        parents.category,
        parents.name
    FROM
        parents
    WHERE
        parents.pid is NOT NULL;
    """
    return await db.fetch_all(sql)


async def query_parents_orgs_for_ap_with_id(db: DB, child_id):
    temp = {"sales_company_id": "", "sales_area_id": "", "sales_exhibition_hall_id": ""}
    if child_id is None:
        return temp

    sql = f"""
    WITH RECURSIVE child AS (
     SELECT id, pid, category, name FROM s_sales_company_orgs WHERE id = {child_id}
     union
     SELECT parents.id, parents.pid, parents.category, parents.name FROM s_sales_company_orgs as parents INNER JOIN child ON parents.id = child.pid
    )
    SELECT
        *
    FROM
        child
    WHERE
        child.pid IS NOT NULL; 
    """
    orgs = await db.fetch_all(sql)

    for org in orgs:
        if org["category"] == "E":
            temp["sales_exhibition_hall_id"] = str(org["id"])
        if org["category"] == "B":
            temp["sales_area_id"] = str(org["id"])
        if org["category"] == "C":
            temp["sales_company_id"] = str(org["id"])
            temp["sales_company_name"] = str(org["name"])

    return temp


async def query_parents_orgs_for_ad_with_sales_person_id(db: DB, sales_person_id):
    sql = f"""
    SELECT
        s_sales_company_org_id
    FROM
        s_sales_person_s_sales_company_org_rels
    WHERE
        s_sales_person_id = {sales_person_id}
    """
    orgs = []
    for child in await db.fetch_all(sql):
        sql = f"""
        WITH RECURSIVE child AS (
        SELECT id, pid, category, name FROM s_sales_company_orgs WHERE id = {child["s_sales_company_org_id"]}
        union
        SELECT parents.id, parents.pid, parents.category, parents.name FROM s_sales_company_orgs as parents INNER JOIN child ON parents.id = child.pid
        )
        SELECT
            CONVERT(child.id,CHAR) as id,
            child.category,
            child.name
        FROM
            child
        WHERE
            child.pid IS NOT NULL;
        """
        for org in await db.fetch_all(sql):
            orgs.append(org)
    return orgs


async def query_s_sales_company_orgs_with_categories(db: DB, categories: str):
    categories_ = [f"'{item}'" for item in categories.split(",")]

    sql = f"SELECT CONVERT(id,CHAR) as value, name as label FROM s_sales_company_orgs WHERE category IN ({', '.join(categories_)});"
    return await db.fetch_all(sql)


async def query_s_sales_company_orgs_with_categories_for_azure(db: DB, categories: str):
    categories_ = [f"'{item}'" for item in categories.split(",")]

    sql = f"SELECT CONVERT(id,CHAR) as value, name as label FROM s_sales_company_orgs WHERE azure_register = 1 AND category IN ({', '.join(categories_)});"
    return await db.fetch_all(sql)


async def query_children_s_sales_company_orgs_with_category(db: DB, parent_id: int, category: str):
    sql = f"""
    WITH RECURSIVE parents AS (
     SELECT id, pid, category, name FROM s_sales_company_orgs WHERE id = {parent_id}
     union
     SELECT child.id, child.pid, child.category, child.name FROM s_sales_company_orgs as child INNER JOIN parents ON parents.id = child.pid
    )
    SELECT
        CONVERT(parents.id,CHAR) as value,
        parents.category as category,
        parents.name as label
    FROM
        parents
    WHERE
        parents.category = '{category}';
    """
    return await db.fetch_all(sql)


async def query_children_s_sales_company_orgs(db: DB, parent_id: int):
    sql = f"""
    WITH RECURSIVE parents AS (
     SELECT id, pid, category, name FROM s_sales_company_orgs WHERE id = {parent_id}
     union
     SELECT child.id, child.pid, child.category, child.name FROM s_sales_company_orgs as child INNER JOIN parents ON parents.id = child.pid
    )
    SELECT
        CONVERT(parents.id,CHAR) as value,
        parents.name as label
    FROM
        parents;
    """
    return await db.fetch_all(sql)


async def query_orgs_access_s_sales_persons(db: DB, orgs_id: int):
    sql = f"""
    WITH RECURSIVE parents AS (
     SELECT id, pid, category, name FROM s_sales_company_orgs WHERE id = {orgs_id}
     union
     SELECT child.id, child.pid, child.category, child.name FROM s_sales_company_orgs as child INNER JOIN parents ON parents.id = child.pid
    )
    SELECT DISTINCT
        CONVERT(s_sales_persons.id,CHAR) as value,
        s_sales_persons.name_kanji as label
    FROM
        parents
    JOIN
        s_sales_person_s_sales_company_org_rels
        ON
        s_sales_person_s_sales_company_org_rels.s_sales_company_org_id = parents.id
    JOIN
        s_sales_persons
        ON
        s_sales_persons.id = s_sales_person_s_sales_company_org_rels.s_sales_person_id
    """

    return await db.fetch_all(sql)


async def query_azure_register_org(db: DB, tenant_id):
    org = await db.fetch_one(
        f"SELECT CONVERT(id,CHAR) as id FROM s_sales_company_orgs WHERE tenant_id = '{tenant_id}';"
    )
    if org:
        return org["id"]
    else:
        return None


async def query_org_category_c_with_id(db: DB, id):
    sql = f"""
    WITH RECURSIVE parents AS (
     SELECT id, pid, category, name FROM s_sales_company_orgs WHERE id = {id}
     union
     SELECT child.id, child.pid, child.category, child.name FROM s_sales_company_orgs as child INNER JOIN parents ON parents.id = child.pid
    )
    SELECT
        CONVERT(parents.id,CHAR) as value,
        CONVERT(parents.pid,CHAR) as pid,
        parents.name as label,
        parents.category
    FROM
        parents;
    """
    return await db.fetch_all(sql)


async def query_translate_org_root_id(db: DB, code: str):
    sql = f"""
    WITH RECURSIVE child AS (
     SELECT id, pid, category FROM s_sales_company_orgs WHERE code = '{code}'
     union
     SELECT parents.id, parents.pid, parents.category FROM s_sales_company_orgs as parents INNER JOIN child ON parents.id = child.pid
    )
    SELECT
        CONVERT(child.id,CHAR) AS s_sales_company_org_id
    FROM
        child
    WHERE
        child.category = "H";
    """
    return await db.fetch_one(sql)
