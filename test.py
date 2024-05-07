import asyncio
from utils.translate_p_uploaded_files import translate_p_uploaded_files
from utils.translate_p_archive_files import translate_p_archive_files
from utils.translate_p_activities_p_application_headers import translate_p_activities_p_application_headers
from utils.translate_p_activities_p_borrowings import translate_p_activities_p_borrowings
from utils.translate_p_activities_p_applicant_persons_0 import translate_p_activities_p_applicant_persons_0
from utils.translate_p_activities_p_applicant_persons_1 import translate_p_activities_p_applicant_persons_1
from utils.translate_p_activities_p_borrowing_details import translate_p_activities_p_borrowing_details
from utils.translate_p_activities_p_join_guarantors import translate_p_activities_p_join_guarantors
from utils.translate_p_activities_p_residents import translate_p_activities_p_residents
from utils.translate_p_activities_p_drafts import translate_p_activities_p_drafts
from utils.translate_set_pair_loan import translate_set_pair_loan
from utils.translate_c_messages import translate_c_messages
from core.database import DB


async def main():
    db = DB()
    await translate_c_messages(db)
    # await translate_set_pair_loan(db)
    # p_drafts = await db.fetch_all(
    #     "SELECT id FROM mortgage_loan_tool_be_production.drafts WHERE user_id IS NOT NULL AND first_submit IS NULL AND p_application_header_id IS NULL;"
    # )
    # for p_draft in p_drafts:
    #     await translate_p_activities_p_drafts(db, p_draft["id"])
    # await translate_p_uploaded_files(db)
    # await translate_p_archive_files(db)
    # p_application_headers = await db.fetch_all("SELECT id FROM mortgage_staging_v3.p_application_headers;")
    # for p_application_header in p_application_headers:
    #     await translate_p_activities_p_application_headers(db, p_application_header["id"])
    #     await translate_p_activities_p_borrowings(db, p_application_header["id"])
    #     await translate_p_activities_p_applicant_persons_0(db, p_application_header["id"])
    #     await translate_p_activities_p_applicant_persons_1(db, p_application_header["id"])
    #     await translate_p_activities_p_join_guarantors(db, p_application_header["id"])
    #     await translate_p_activities_p_residents(db, p_application_header["id"])
    #     pass
    # p_borrowing_details = await db.fetch_all(
    #     "SELECT id, p_application_header_id FROM mortgage_staging_v3.p_borrowing_details;"
    # )
    # for p_borrowing_detail in p_borrowing_details:
    #     await translate_p_activities_p_borrowing_details(db, p_borrowing_detail["id"])

    # p_date_translate = await db.fetch_all(
    #     "SELECT  id, content FROM p_activities WHERE field_name IN ('birthday', 'desired_borrowing_date') AND content IS NOT NULL;"
    # )
    # for item in p_date_translate:
    #     if "-" in item["content"]:
    #         await db.execute(
    #             f"""UPDATE p_activities SET content = '{item["content"].replace("-", "/")}' WHERE id = {item["id"]}"""
    #         )

    # for item in await db.fetch_all("SELECT DISTINCT p_application_header_id FROM p_residents;"):
    #     pr_ids = [
    #         str(i["id"])
    #         for i in await db.fetch_all(
    #             f"""SELECT id FROM p_residents WHERE p_application_header_id = {item["p_application_header_id"]}"""
    #         )
    #     ]

    #     if len(pr_ids) == 1:
    #         await db.execute(f"""UPDATE p_residents SET resident_type = 0 WHERE id IN ({", ".join(pr_ids)});""")
    #     else:
    #         await db.execute(f"""UPDATE p_residents SET resident_type = 0 WHERE id IN ({", ".join(pr_ids[0:1])});""")
    #         await db.execute(f"""UPDATE p_residents SET resident_type = 1 WHERE id IN ({", ".join(pr_ids[1:])});""")


asyncio.run(main())
