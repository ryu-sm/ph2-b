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


async def query_s_sales_company_id_for_c(db: DB, id: int):
    pass
