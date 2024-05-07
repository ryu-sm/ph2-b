from constant import OPERATE_TYPE
from core.database import DB
import utils
import yaml


async def translate_set_pair_loan(db: DB):
    p_application_headers = await db.fetch_all(
        "SELECT id, pair_loan_id FROM mortgage_staging_v3.p_application_headers WHERE pair_loan_id IS NOT NULL;"
    )
    for p_application_header in p_application_headers:
        pair_loan = await db.fetch_one(
            f"SELECT id FROM mortgage_staging_v3.p_application_headers WHERE old_id = {p_application_header['pair_loan_id']};"
        )
        await db.execute(
            f"UPDATE mortgage_staging_v3.p_application_headers SET pair_loan_id = {pair_loan['id']} WHERE id = {p_application_header['id']}"
        )

    p_application_headers = await db.fetch_all(
        "SELECT id, pair_loan_id FROM mortgage_staging_v3.p_application_headers WHERE pair_loan_id IS NOT NULL;"
    )
    for p_application_header in p_application_headers:

        await db.execute(
            f"UPDATE mortgage_staging_v3.p_application_headers SET pair_loan_id = {p_application_header['id']} WHERE id = {p_application_header['pair_loan_id']}"
        )
