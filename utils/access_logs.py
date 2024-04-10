import base64

import magic
import pytz
from datetime import datetime
from core.database import DB
import json
import pandas as pd
from io import BytesIO
import crud


async def get_manager_name(db: DB, id):
    result = await db.fetch_one(f"SELECT name_kanji FROM s_managers WHERE id={id};")
    if result:
        return result["name_kanji"]
    else:
        return ""


async def get_sales_person_name(db: DB, id):
    result = await db.fetch_one(f"SELECT name_kanji FROM s_sales_persons WHERE id={id};")
    if result:
        return result["name_kanji"]
    else:
        return ""


async def get_user_email(db: DB, id):
    result = await db.fetch_one(f"SELECT email FROM c_users WHERE id={id};")
    if result:
        return result["email"]
    else:
        return ""


async def access_logs_output(start: str, end: str):
    json_data = [
        {
            "apply_no": "申込の受付番号",
            "account_type": "担当者区分",
            "account_name": "担当者名",
            "created_at": "日時",
            "operation": "操作",
            "operation_content": "操作内容",
        }
    ]
    db = DB()

    sql = f"""
    SELECT
        apply_no,
        account_id,
        account_type,
        operation,
        operation_content,
        DATE_FORMAT(created_at, '%Y/%m/%d %H:%i:%S') as created_at
    FROM
        c_access_logs
    """
    jp_tz = pytz.timezone("Asia/Tokyo")
    where = ""
    file_name = f"監視ログ"
    if start and end:
        where += f"""WHERE created_at  >= '{start.replace("/","-")} 00:00:00' AND created_at  <= '{end.replace("/","-")} 11:59:59'"""
        file_name = f"""監視ログ_{start.replace("/","")}~{end.replace("/","")}"""
    if start and not end:
        where += f"""WHERE created_at  >= '{start.replace("/","-")} 00:00:00'"""
        file_name = f"""監視ログ_{start.replace("/","")}~"""
    if not start and end:
        where += f"""WHERE created_at  <= '{end.replace("/","-")} 11:59:59'"""
        file_name = f"""監視ログ_~{end.replace("/","")}"""
    access_logs = await db.fetch_all(sql + where)
    if len(access_logs) == 0:
        return {"src": None}

    for access_log in access_logs:
        user_name = await get_user_email(db, access_log["account_id"])
        sales_person_name = await get_sales_person_name(db, access_log["account_id"])
        manager_name = await get_manager_name(db, access_log["account_id"])
        account_type_maps = {
            1: "申込人",
            2: "不動産業者",
            3: "銀行代理",
        }
        json_data.append(
            {
                "apply_no": access_log["apply_no"],
                "account_type": account_type_maps[access_log["account_type"]],
                "account_name": user_name or sales_person_name or manager_name,
                "created_at": access_log["created_at"],
                "operation": access_log["operation"],
                "operation_content": access_log["operation_content"],
            }
        )
    df = pd.DataFrame(
        json_data,
    )
    excel_buffer = BytesIO()

    df.to_excel(excel_buffer, header=False, index=False)
    excel_buffer.seek(0)
    file_content = excel_buffer.getvalue()
    mime_type = magic.from_buffer(file_content, mime=True)
    base64_encoded_data = base64.b64encode(file_content).decode("utf-8")
    src = f"data:{mime_type};base64,{base64_encoded_data}"

    return {"src": src, "name": file_name}
