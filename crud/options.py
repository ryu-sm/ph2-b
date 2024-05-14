from core.database import DB


async def query_bank_options(db: DB):
    return await db.fetch_all("SELECT CONVERT(id,CHAR) as value, code as code, name as label FROM s_banks;")


async def query_child_area_options(db: DB, parent_id):
    if parent_id is None:
        sql = f"""
        SELECT
            CONVERT(s_sales_company_orgs.id,CHAR) as value,
            s_sales_company_orgs.name as label
        FROM
            s_sales_company_orgs
        WHERE
            s_sales_company_orgs.category = 'B'
            AND
            s_sales_company_orgs.pid is NOT NULL;
        """
        return await db.fetch_all(sql)

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
        parents
    WHERE
        parents.category = 'B'
        AND
        parents.pid is NOT NULL;
    """
    return await db.fetch_all(sql)


async def query_child_exhibition_hall_options(db, parent_id):
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
        parents
    WHERE
        parents.category = 'E'
        AND
        parents.pid is NOT NULL;
    """
    return await db.fetch_all(sql)


async def query_manager_options(db: DB):
    return await db.fetch_all("SELECT CONVERT(id,CHAR) as value, name_kanji as label FROM s_managers;")


async def query_sales_person_options(db: DB, parent_id):
    sql = f"""
    WITH RECURSIVE parents AS (
     SELECT id, pid, category, name FROM s_sales_company_orgs WHERE id = {parent_id}
     union
     SELECT child.id, child.pid, child.category, child.name FROM s_sales_company_orgs as child INNER JOIN parents ON parents.id = child.pid
    )
    SELECT DISTINCT
        CONVERT(s_sales_persons.id,CHAR) as value,
        s_sales_persons.name_kanji as label,
        s_sales_persons.mobile_phone as mobile_phone,
        s_sales_persons.email as email
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
    WHERE
        parents.pid is NOT NULL;
    """
    return await db.fetch_all(sql)


async def query_pair_loan_options(db: DB, p_application_header_id, is_seted):
    sbi = await db.fetch_one("SELECT id, name FROM s_banks WHERE code = '0038';")
    sbi_id = sbi["id"]
    if is_seted == 1:
        sql = f"""
        SELECT
            CONVERT(p_application_headers.id,CHAR) AS value,
            p_application_headers.apply_no as label
        FROM
            p_application_headers
        JOIN
            p_application_banks
            ON
            p_application_banks.p_application_header_id = p_application_headers.id
            AND
            p_application_banks.s_bank_id = {sbi_id}
        WHERE
            p_application_headers.unsubcribed is NULL
            AND
            p_application_headers.pair_loan_id is NOT NULL
            AND
            p_application_headers.loan_type = 2
            AND
            p_application_banks.provisional_after_result is NULL
            AND
            p_application_headers.id != {p_application_header_id}
        ORDER BY p_application_headers.id DESC;
        """

        return await db.fetch_all(sql)
    sql = f"""
    SELECT
        CONVERT(p_application_headers.id,CHAR) AS value,
        p_application_headers.apply_no as label
    FROM
        p_application_headers
    JOIN
        p_application_banks
        ON
        p_application_banks.p_application_header_id = p_application_headers.id
        AND
        p_application_banks.s_bank_id = {sbi_id}
    WHERE
        p_application_headers.unsubcribed is NULL
        AND
        p_application_headers.pair_loan_id is NULL
        AND
        p_application_headers.loan_type = 2
        AND
        p_application_banks.provisional_after_result is NULL
        AND
        p_application_headers.id != {p_application_header_id}
    ORDER BY p_application_headers.id DESC;
    """

    return await db.fetch_all(sql)


async def query_s_sales_company_id_for_category(db: DB, category):
    sql = f"""
    SELECT
        CONVERT(id,CHAR) as value,
        name as label
    FROM
        s_sales_company_orgs
    WHERE
        category = '{category}';
    """
    return await db.fetch_all(sql)


async def query_all_sales_person_options(db: DB):
    return await db.fetch_all(
        "SELECT CONVERT(id,CHAR) as value, name_kanji as label, mobile_phone, email FROM s_sales_persons;"
    )
