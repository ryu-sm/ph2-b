from core.database import DB


async def query_bank_options(db: DB):
    sql = "SELECT id as value, code as code, name as label FROM s_banks;"
    return await db.fetch_all(sql)
