import pandas as pd

import utils
from utils.gen_row_data_configs import CODE_CONFIGS
from utils.ja_date import format_js_date_ym, format_js_date_ymd, gen_ja_apply_datetime
from utils.ja_numeric import format_ja_numeric


def gen_row_data(data: dict):
    json_data = [
        {"step": "STEP", "big_class": "大項目", "class": "小項目", "field_name": "項目名", "filed_value": "項目値"},
    ]

    # step10
    if data["p_application_headers"]["loan_type"] in ["3", "4"]:
        json_data.append(
            {
                "step": "STEP 10：書類添付",
                "big_class": "本人確認書類",
                "class": "",
                "field_name": "本人確認書類",
                "filed_value": CODE_CONFIGS["p_applicant_persons__1.identity_verification_type"].get(
                    data["p_applicant_persons__1"]["identity_verification_type"], ""
                ),
            }
        )

        if data["p_uploaded_files"]["p_applicant_persons__1__A__01__a"]:
            json_data.append(
                {
                    "step": "STEP 10：書類添付",
                    "big_class": "運転免許証〈表面〉",
                    "class": "",
                    "field_name": "運転免許証〈表面〉",
                    "filed_value": ", ".join(
                        [item["name"] for item in data["p_uploaded_files"]["p_applicant_persons__1__A__01__a"]]
                    ),
                }
            )
        if data["p_uploaded_files"]["p_applicant_persons__1__A__01__b"]:
            json_data.append(
                {
                    "step": "STEP 10：書類添付",
                    "big_class": "運転免許証〈裏面〉",
                    "class": "",
                    "field_name": "運転免許証〈裏面〉",
                    "filed_value": ", ".join(
                        [item["name"] for item in data["p_uploaded_files"]["p_applicant_persons__1__A__01__b"]]
                    ),
                }
            )
        if data["p_uploaded_files"]["p_applicant_persons__1__A__02"]:
            json_data.append(
                {
                    "step": "STEP 10：書類添付",
                    "big_class": "マイナンバーカード",
                    "class": "",
                    "field_name": "マイナンバーカード",
                    "filed_value": ", ".join(
                        [item["name"] for item in data["p_uploaded_files"]["p_applicant_persons__1__A__02"]]
                    ),
                }
            )
        if data["p_uploaded_files"]["p_applicant_persons__1__A__03__a"]:
            json_data.append(
                {
                    "step": "STEP 10：書類添付",
                    "big_class": "住民基本台帳カード（顔写真付き）〈表面〉",
                    "class": "",
                    "field_name": "住民基本台帳カード（顔写真付き）〈表面〉",
                    "filed_value": ", ".join(
                        [item["name"] for item in data["p_uploaded_files"]["p_applicant_persons__1__A__03__a"]]
                    ),
                }
            )
        if data["p_uploaded_files"]["p_applicant_persons__1__A__03__b"]:
            json_data.append(
                {
                    "step": "STEP 10：書類添付",
                    "big_class": "住民基本台帳カード（顔写真付き）〈裏面〉",
                    "class": "",
                    "field_name": "住民基本台帳カード（顔写真付き）〈裏面〉",
                    "filed_value": ", ".join(
                        [item["name"] for item in data["p_uploaded_files"]["p_applicant_persons__1__A__03__b"]]
                    ),
                }
            )
        if data["p_uploaded_files"]["p_applicant_persons__1__B__a"]:
            json_data.append(
                {
                    "step": "STEP 10：書類添付",
                    "big_class": "健康保険証〈表面〉",
                    "class": "",
                    "field_name": "健康保険証〈表面〉",
                    "filed_value": ", ".join(
                        [item["name"] for item in data["p_uploaded_files"]["p_applicant_persons__1__B__a"]]
                    ),
                }
            )
        if data["p_uploaded_files"]["p_applicant_persons__1__B__b"]:
            json_data.append(
                {
                    "step": "STEP 10：書類添付",
                    "big_class": "健康保険証〈裏面〉",
                    "class": "",
                    "field_name": "健康保険証〈裏面〉",
                    "filed_value": ", ".join(
                        [item["name"] for item in data["p_uploaded_files"]["p_applicant_persons__1__B__b"]]
                    ),
                }
            )
        if data["p_uploaded_files"]["p_applicant_persons__1__C__01"]:
            json_data.append(
                {
                    "step": "STEP 10：書類添付",
                    "big_class": "収入に関する書類",
                    "class": "",
                    "field_name": "源泉徴収票（前年度分）",
                    "filed_value": ", ".join(
                        [item["name"] for item in data["p_uploaded_files"]["p_applicant_persons__1__C__01"]]
                    ),
                }
            )
        if data["p_uploaded_files"]["p_applicant_persons__1__C__02"]:
            json_data.append(
                {
                    "step": "STEP 10：書類添付",
                    "big_class": "",
                    "class": "",
                    "field_name": "源泉徴収票（前々年度分）",
                    "filed_value": ", ".join(
                        [item["name"] for item in data["p_uploaded_files"]["p_applicant_persons__1__C__02"]]
                    ),
                }
            )
        if data["p_uploaded_files"]["p_applicant_persons__1__C__03"]:
            json_data.append(
                {
                    "step": "STEP 10：書類添付",
                    "big_class": "",
                    "class": "",
                    "field_name": "確定申告書（1期前）",
                    "filed_value": ", ".join(
                        [item["name"] for item in data["p_uploaded_files"]["p_applicant_persons__1__C__03"]]
                    ),
                }
            )
        if data["p_uploaded_files"]["p_applicant_persons__1__C__04"]:
            json_data.append(
                {
                    "step": "STEP 10：書類添付",
                    "big_class": "",
                    "class": "",
                    "field_name": "確定申告書（2期前）",
                    "filed_value": ", ".join(
                        [item["name"] for item in data["p_uploaded_files"]["p_applicant_persons__1__C__04"]]
                    ),
                }
            )
        if data["p_uploaded_files"]["p_applicant_persons__1__C__05"]:
            json_data.append(
                {
                    "step": "STEP 10：書類添付",
                    "big_class": "",
                    "class": "",
                    "field_name": "確定申告書（3期前）",
                    "filed_value": ", ".join(
                        [item["name"] for item in data["p_uploaded_files"]["p_applicant_persons__1__C__05"]]
                    ),
                }
            )
        if data["p_uploaded_files"]["p_applicant_persons__1__D__01"]:
            json_data.append(
                {
                    "step": "STEP 10：書類添付",
                    "big_class": "非上場企業の役員の方は下記の書類も添付してください。",
                    "class": "",
                    "field_name": "会社の決算報告書（1期前）",
                    "filed_value": ", ".join(
                        [item["name"] for item in data["p_uploaded_files"]["p_applicant_persons__1__D__01"]]
                    ),
                }
            )
        if data["p_uploaded_files"]["p_applicant_persons__1__D__02"]:
            json_data.append(
                {
                    "step": "STEP 10：書類添付",
                    "big_class": "",
                    "class": "",
                    "field_name": "会社の決算報告書（2期前）",
                    "filed_value": ", ".join(
                        [item["name"] for item in data["p_uploaded_files"]["p_applicant_persons__1__D__02"]]
                    ),
                }
            )
        if data["p_uploaded_files"]["p_applicant_persons__1__D__03"]:
            json_data.append(
                {
                    "step": "STEP 10：書類添付",
                    "big_class": "",
                    "class": "",
                    "field_name": "会社の決算報告書（3期前）",
                    "filed_value": ", ".join(
                        [item["name"] for item in data["p_uploaded_files"]["p_applicant_persons__1__D__03"]]
                    ),
                }
            )
        if data["p_uploaded_files"]["p_applicant_persons__1__E"]:
            json_data.append(
                {
                    "step": "STEP 10：書類添付",
                    "big_class": "雇用契約に関する書類",
                    "class": "",
                    "field_name": "雇用契約書",
                    "filed_value": ", ".join(
                        [item["name"] for item in data["p_uploaded_files"]["p_applicant_persons__1__E"]]
                    ),
                }
            )
        if data["p_uploaded_files"]["p_applicant_persons__1__F__01"]:
            json_data.append(
                {
                    "step": "STEP 10：書類添付",
                    "big_class": "親族経営の会社等にご勤務の方は下記の書類も添付してください。",
                    "class": "",
                    "field_name": "会社の決算報告書または経営する親族の確定申告書（1期前）",
                    "filed_value": ", ".join(
                        [item["name"] for item in data["p_uploaded_files"]["p_applicant_persons__1__F__01"]]
                    ),
                }
            )
        if data["p_uploaded_files"]["p_applicant_persons__1__F__02"]:
            json_data.append(
                {
                    "step": "STEP 10：書類添付",
                    "big_class": "",
                    "class": "",
                    "field_name": "会社の決算報告書または経営する親族の確定申告書（2期前）",
                    "filed_value": ", ".join(
                        [item["name"] for item in data["p_uploaded_files"]["p_applicant_persons__1__F__02"]]
                    ),
                }
            )
        if data["p_uploaded_files"]["p_applicant_persons__1__F__03"]:
            json_data.append(
                {
                    "step": "STEP 10：書類添付",
                    "big_class": "",
                    "class": "",
                    "field_name": "会社の決算報告書または経営する親族の確定申告書（3期前）",
                    "filed_value": ", ".join(
                        [item["name"] for item in data["p_uploaded_files"]["p_applicant_persons__1__F__03"]]
                    ),
                }
            )
        if data["p_uploaded_files"]["p_applicant_persons__1__K"]:
            json_data.append(
                {
                    "step": "STEP 10：書類添付",
                    "big_class": "その他の書類",
                    "class": "",
                    "field_name": "その他の書類",
                    "filed_value": ", ".join(
                        [item["name"] for item in data["p_uploaded_files"]["p_applicant_persons__1__K"]]
                    ),
                }
            )

    df = pd.DataFrame(
        json_data,
    )

    excel_file_path = "data.xlsx"

    df.to_excel(excel_file_path, header=False, index=False)
