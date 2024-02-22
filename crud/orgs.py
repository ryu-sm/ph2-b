from core.database import DB


async def query_s_sales_company_orgs_root_id(db: DB, child_id: int):
    sql = f"""
    WITH RECURSIVE child AS (
     SELECT id, pid FROM s_sales_company_orgs WHERE id = {child_id}
     union
     SELECT parents.id, parents.pid FROM s_sales_company_orgs as parents INNER JOIN child ON parents.id = child.pid
    )
    SELECT
        child.id AS root_id
    FROM
        child
    WHERE
        child.pid is NULL;
    """
    result = await db.fetch_one(sql)
    return result["root_id"]


async def query_s_sales_company_orgs(db: DB, s_sales_company_org_id: int):
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
        CONVERT(parents.category,CHAR) as category,
        parents.name
    FROM
        parents
    WHERE
        parents.pid is NOT NULL;
    """
    return await db.fetch_all(sql)
