import base64
from datetime import datetime
import magic
import pytz
from core.database import DB
import pandas as pd
from io import BytesIO

import utils


async def preliminaries_output(data: list):
    json_data = [
        {
            "apply_no": "受付番号",
            "bank_name": "申込銀行",
            "name_kanji": "申込人",
            "created_at": "申込日時",
            "desired_borrowing_date": "実行予定日",
            "desired_loan_amount": "申込金額（万円）",
            "pre_examination_status": "進捗状況",
            "provisional_result": "仮審査結果",
            "sales_area_id": "エリア",
            "sales_exhibition_hall_id": "展示場",
            "s_sales_person_id": "営業担当",
            "s_manager_id": "銀代担当",
        }
    ]
    db = DB()

    orgs_op = await db.fetch_all(f"SELECT CONVERT(id,CHAR) AS id, name FROM s_sales_company_orgs")
    managers_op = await db.fetch_all(f"SELECT CONVERT(id,CHAR) AS id, name_kanji FROM s_managers")
    sales_persons_op = await db.fetch_all(f"SELECT CONVERT(id,CHAR) AS id, name_kanji FROM s_sales_persons")

    orgs_map = {}
    for op in orgs_op:
        orgs_map[op["id"]] = op["name"]
    managers_map = {}
    for op in managers_op:
        managers_map[op["id"]] = op["name_kanji"]
    sales_persons_map = {}
    for op in sales_persons_op:
        sales_persons_map[op["id"]] = op["name_kanji"]
    status_map = {
        "0": "書類確認",
        "1": "書類不備対応中",
        "2": "内容確認",
        "3": "承認",
        "4": "銀行へデータ連携",
        "5": "提携会社へ審査結果公開",
        "6": "申込人へ審査結果公開",
    }
    result_map = {
        "0": "承認",
        "1": "条件付承認",
        "2": "否決",
    }
    for item in data:
        json_data.append(
            {
                "apply_no": item["apply_no"],
                "bank_name": item["bank_name"],
                "name_kanji": item["name_kanji"],
                "created_at": item["created_at"].split(" ")[0],
                "desired_borrowing_date": item["desired_borrowing_date"],
                "desired_loan_amount": utils.format_ja_numeric(item["desired_loan_amount"], ""),
                "pre_examination_status": status_map.get(item["pre_examination_status"], ""),
                "provisional_result": result_map.get(item["provisional_result"], ""),
                "sales_area_id": orgs_map.get(item["sales_area_id"], ""),
                "sales_exhibition_hall_id": orgs_map.get(item["sales_exhibition_hall_id"], ""),
                "s_sales_person_id": sales_persons_map.get(item["s_sales_person_id"], ""),
                "s_manager_id": managers_map.get(item["s_manager_id"], ""),
            }
        )

    df = pd.DataFrame(json_data)
    excel_buffer = BytesIO()

    df.to_excel(excel_buffer, header=False, index=False)
    excel_buffer.seek(0)
    file_content = excel_buffer.getvalue()
    mime_type = magic.from_buffer(file_content, mime=True)
    base64_encoded_data = base64.b64encode(file_content).decode("utf-8")
    src = f"data:{mime_type};base64,{base64_encoded_data}"
    date_str = datetime.now().strftime("%Y%m%d%H%M%S")
    return {"src": src, "name": f"{date_str}_管理画面をエクスポート.xlsx"}
