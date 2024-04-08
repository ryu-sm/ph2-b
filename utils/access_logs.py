import base64

import magic
import pytz
from datetime import datetime
from core.database import DB
import json
import pandas as pd
from io import BytesIO
import crud

ENDPIONT_MAP = {
    "/user/token&POST": "ログイン",
    "/user/token&DELETE": "ログアウト",
    # "/user/password&PUT": "パスワード変更",
    # "/user/email&PUT": "メールアドレス変更",
    # "/user&DELETE": "退会",
    # "/manager/password&PUT": "パスワード変更",
    "/manager/token&POST": "ログイン",
    "/manager/token&DELETE": "ログアウト",
    # "/sales-person/password&PUT": "パスワード変更",
    "/sales-person/token&POST": "ログイン",
    "/sales-person/token&DELETE": "ログアウト",
    "/manager/pre_examination_status&PUT": "更新",
    # "/manager/provisional_result&PUT": "審査結果更新",
    # "/manager/provisional_result&POST": "審査結果削除",
    "/row_data/{p_application_header_id}&GET": "ダウンロード",
    "/manager/un-pair-loan&PUT": "更新",
    "/manager/set-pair-loan&PUT": "更新",
}


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


async def access_logs_output(start: str, end: str):
    json_data = [
        {
            "apply_no": "申込の受付番号",
            "role_type": "会社",
            "role_name": "担当者名",
            "created_at": "日時",
            "operate_type": "操作",
            "content": "操作内容",
        }
    ]
    db = DB()

    sql = f"""
    SELECT
        account_id,
        endpoint,
        method,
        params,
        DATE_FORMAT(created_at, '%Y/%m/%d %H:%i:%S') as created_at
    FROM
        c_access_logs
    """
    jp_tz = pytz.timezone("Asia/Tokyo")
    where = ""
    if start and end:
        where += f"""WHERE created_at  >= '{start.replace("/","-")} 00:00:00' AND created_at  <= '{end.replace("/","-")} 11:59:59'"""
    if start and not end:
        where += f"""WHERE created_at  >= '{start.replace("/","-")} 00:00:00'"""
    if not start and end:
        where += f"""WHERE created_at  <= '{end.replace("/","-")} 11:59:59'"""
    print(sql + where)
    access_logs = await db.fetch_all(sql + where)
    if len(access_logs) == 0:
        return {"src": None}
    for access_log in access_logs:
        key = f'{access_log["endpoint"]}&{access_log["method"]}'
        if key == "/user/token&POST":
            params_data = json.loads(access_log["params"])
            json_data.append(
                {
                    "apply_no": "",
                    "role_type": "申込人",
                    "role_name": params_data["body"]["email"],
                    "created_at": access_log["created_at"],
                    "operate_type": ENDPIONT_MAP[key],
                    "content": "",
                }
            )
        if key == "/user/token&DELETE":
            params_data = json.loads(access_log["params"])
            json_data.append(
                {
                    "apply_no": "",
                    "role_type": "申込人",
                    "role_name": params_data["query"]["email"],
                    "created_at": access_log["created_at"],
                    "operate_type": ENDPIONT_MAP[key],
                    "content": "",
                }
            )
        if key == "/manager/token&POST":
            params_data = json.loads(access_log["params"])
            json_data.append(
                {
                    "apply_no": "",
                    "role_type": "銀行代理",
                    "role_name": params_data["body"]["email"],
                    "created_at": access_log["created_at"],
                    "operate_type": ENDPIONT_MAP[key],
                    "content": "",
                }
            )
        if key == "/manager/token&DELETE":
            params_data = json.loads(access_log["params"])
            json_data.append(
                {
                    "apply_no": "",
                    "role_type": "銀行代理",
                    "role_name": params_data["query"]["email"],
                    "created_at": access_log["created_at"],
                    "operate_type": ENDPIONT_MAP[key],
                    "content": "",
                }
            )
        if key == "/sales-person/token&POST":
            params_data = json.loads(access_log["params"])
            json_data.append(
                {
                    "apply_no": "",
                    "role_type": "不動産業者",
                    "role_name": params_data["body"]["email"],
                    "created_at": access_log["created_at"],
                    "operate_type": ENDPIONT_MAP[key],
                    "content": "",
                }
            )
        if key == "/sales-person/token&DELETE":
            params_data = json.loads(access_log["params"])
            json_data.append(
                {
                    "apply_no": "",
                    "role_type": "不動産業者",
                    "role_name": params_data["query"]["email"],
                    "created_at": access_log["created_at"],
                    "operate_type": ENDPIONT_MAP[key],
                    "content": "",
                }
            )
        if key == "/manager/pre_examination_status&PUT":
            params_data = json.loads(access_log["params"])
            apply_no = await crud.query_p_application_header_apply_no(
                db, params_data["body"]["p_application_header_id"]
            )
            code_maps = {
                0: "仮審査の操作状態: 書類確認;",
                1: "仮審査の操作状態: 書類不備対応中",
                2: "仮審査の操作状態: 内容確認;",
                3: "仮審査の操作状態: 承認",
                4: "仮審査の操作状態: 銀行へデータ連携",
                5: "仮審査の操作状態: 提携会社へ審査結果公開",
                6: "仮審査の操作状態: 申込人へ審査結果公開",
                9: "仮審査の操作状態: 承認解除",
            }
            code = 9 if params_data["body"]["is_cancel_confirm"] else params_data["body"]["pre_examination_status"]
            role_name = await get_manager_name(db, access_log["account_id"])
            json_data.append(
                {
                    "apply_no": apply_no,
                    "role_type": "銀行代理",
                    "role_name": role_name,
                    "created_at": access_log["created_at"],
                    "operate_type": ENDPIONT_MAP[key],
                    "content": code_maps[code],
                }
            )
        if key == "/row_data/{p_application_header_id}&GET":
            params_data = json.loads(access_log["params"])
            manager_name = await get_manager_name(db, access_log["account_id"])
            sales_person_name = await get_sales_person_name(db, access_log["account_id"])
            apply_no = await crud.query_p_application_header_apply_no(
                db, params_data["path"]["p_application_header_id"]
            )
            json_data.append(
                {
                    "apply_no": apply_no,
                    "role_type": "不動産業者" if manager_name == "" else "銀行代理",
                    "role_name": manager_name or sales_person_name,
                    "created_at": access_log["created_at"],
                    "operate_type": ENDPIONT_MAP[key],
                    "content": "ローデータダウンロード: ダウンロードした",
                }
            )
        if key == "/manager/un-pair-loan&PUT":
            params_data = json.loads(access_log["params"])
            manager_name = await get_manager_name(db, access_log["account_id"])
            apply_no_a = await crud.query_p_application_header_apply_no(db, params_data["body"]["id"])
            apply_no_b = await crud.query_p_application_header_apply_no(db, params_data["body"]["pair_loan_id"])

            json_data.append(
                {
                    "apply_no": apply_no_a,
                    "role_type": "銀行代理",
                    "role_name": manager_name,
                    "created_at": access_log["created_at"],
                    "operate_type": ENDPIONT_MAP[key],
                    "content": f"ペアローン紐付・解除: {apply_no_a}と{apply_no_b}解除",
                }
            )
        if key == "/manager/set-pair-loan&PUT":
            params_data = json.loads(access_log["params"])
            manager_name = await get_manager_name(db, access_log["account_id"])
            apply_no_a = await crud.query_p_application_header_apply_no(db, params_data["body"]["id"])
            apply_no_b = await crud.query_p_application_header_apply_no(db, params_data["body"]["pair_loan_id"])

            json_data.append(
                {
                    "apply_no": apply_no_a,
                    "role_type": "銀行代理",
                    "role_name": manager_name,
                    "created_at": access_log["created_at"],
                    "operate_type": ENDPIONT_MAP[key],
                    "content": f"ペアローン紐付・解除: {apply_no_a}と{apply_no_b}紐付",
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

    return {"src": src}
