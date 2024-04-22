import json
import pandas as pd
from io import BytesIO
from core.database import DB
from utils.gen_row_data_configs import CODE_CONFIGS
from utils.ja_date import format_js_date_ym, format_js_date_ymd, gen_ja_apply_datetime
from utils.ja_numeric import format_ja_numeric
from utils.s3 import upload_buffer_to_s3
from constant import BANK_CODE


async def gen_row_data(p_application_header_id: int, data: dict):

    def get_step_code(id):
        step_list = [
            1,
            2,
            3,
        ]
        if data["p_application_headers"]["loan_type"] in ["3", "4"]:
            step_list = [
                *step_list,
                4,
                5,
            ]
        if data["p_application_headers"]["join_guarantor_umu"] == "1":
            step_list = [
                *step_list,
                6,
            ]
        step_list = [
            *step_list,
            7,
            8,
            9,
            10,
        ]
        if data["p_application_headers"]["loan_type"] in ["3", "4"]:
            step_list = [
                *step_list,
                11,
            ]
        step_list = [
            *step_list,
            12,
        ]
        index = step_list.index(id)
        return str(index + 1).zfill(2)

    db = DB()
    banks = await db.fetch_all("SELECT CONVERT(id,CHAR) as id, name FROM s_banks;")
    orgs = await db.fetch_all("SELECT CONVERT(id,CHAR) as id, name FROM s_sales_company_orgs;")
    is_mcj = await db.fetch_one(
        f"""SELECT id FROM s_banks WHERE code = '{BANK_CODE.MCJ.value}' AND id IN ({",".join(data["p_application_banks"])})"""
    )

    json_data = [
        {"step": "STEP", "big_class": "大項目", "class": "小項目", "field_name": "項目名", "filed_value": "項目値"},
    ]

    # step01
    json_data.append(
        {
            "step": f"STEP {get_step_code(1)}：お借入のご希望",
            "big_class": "申込日時",
            "class": "",
            "field_name": "申込日時",
            "filed_value": gen_ja_apply_datetime(),
        },
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(1)}：お借入のご希望",
            "big_class": "同意日",
            "class": "",
            "field_name": "同意日",
            "filed_value": format_js_date_ymd(data["p_application_headers"]["apply_date"]),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(1)}：お借入のご希望",
            "big_class": "入居予定年月",
            "class": "",
            "field_name": "入居予定年月",
            "filed_value": format_js_date_ym(data["p_application_headers"]["move_scheduled_date"]),
        }
    )

    banks_name = []
    for id in data["p_application_banks"]:
        target = list(filter(lambda x: x["id"] == id, banks))
        banks_name.append(target[0]["name"])

    json_data.append(
        {
            "step": f"STEP {get_step_code(1)}：お借入のご希望",
            "big_class": "仮審査を申し込む金融機関を選択してください。※複数選択可",
            "class": "",
            "field_name": "申し込む金融機関",
            "filed_value": ", ".join(banks_name),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(1)}：お借入のご希望",
            "big_class": "お借入の目的",
            "class": "",
            "field_name": "お借入の目的",
            "filed_value": CODE_CONFIGS["p_application_headers.loan_target_type"].get(
                data["p_application_headers"]["loan_target_type"], ""
            ),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(1)}：お借入のご希望",
            "big_class": "資金の使いみち",
            "class": "",
            "field_name": "資金の使いみち",
            "filed_value": CODE_CONFIGS["p_application_headers.loan_target"].get(
                data["p_application_headers"]["loan_target"], ""
            ),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(1)}：お借入のご希望",
            "big_class": "土地先行プランをご希望ですか？",
            "class": "",
            "field_name": "土地先行プラン希望",
            "filed_value": CODE_CONFIGS["p_application_headers.land_advance_plan"].get(
                data["p_application_headers"]["land_advance_plan"], ""
            ),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(1)}：お借入のご希望",
            "big_class": "お借入形態",
            "class": "",
            "field_name": "お借入形態",
            "filed_value": CODE_CONFIGS["p_application_headers.loan_type"].get(
                data["p_application_headers"]["loan_type"], ""
            ),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(1)}：お借入のご希望",
            "big_class": "ペアローンのお相手について",
            "class": "お名前　姓",
            "field_name": "ペアローンの申込人名前　姓",
            "filed_value": data["p_application_headers"]["pair_loan_last_name"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(1)}：お借入のご希望",
            "big_class": "",
            "class": "お名前　名",
            "field_name": "ペアローンの申込人名前　名",
            "filed_value": data["p_application_headers"]["pair_loan_first_name"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(1)}：お借入のご希望",
            "big_class": "",
            "class": "続柄",
            "field_name": "続柄",
            "filed_value": data["p_application_headers"]["pair_loan_rel_name"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(1)}：お借入のご希望",
            "big_class": "お借入内容",
            "class": "お借入内容 1回目の融資",
            "field_name": "借入希望日",
            "filed_value": format_js_date_ymd(data["p_borrowing_details__1"]["desired_borrowing_date"]),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(1)}：お借入のご希望",
            "big_class": "",
            "class": "お借入希望額",
            "field_name": "仮入り希望金額",
            "filed_value": format_ja_numeric(data["p_borrowing_details__1"]["desired_loan_amount"], "万円"),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(1)}：お借入のご希望",
            "big_class": "",
            "class": "うち、ボーナス返済分",
            "field_name": "うち、ボーナス返済分",
            "filed_value": format_ja_numeric(data["p_borrowing_details__1"]["bonus_repayment_amount"], "万円"),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(1)}：お借入のご希望",
            "big_class": "",
            "class": "ボーナス返済月",
            "field_name": "ボーナス併用払い",
            "filed_value": CODE_CONFIGS["p_borrowing_details__1.bonus_repayment_month"].get(
                data["p_borrowing_details__1"]["bonus_repayment_month"], ""
            ),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(1)}：お借入のご希望",
            "big_class": "",
            "class": "お借入期間 年",
            "field_name": "お借入期間 年",
            "filed_value": format_ja_numeric(data["p_borrowing_details__1"]["loan_term_year"], "年"),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(1)}：お借入のご希望",
            "big_class": "",
            "class": "返済方法",
            "field_name": "返済方法",
            "filed_value": CODE_CONFIGS["p_borrowing_details__1.repayment_method"].get(
                data["p_borrowing_details__1"]["repayment_method"], ""
            ),
        }
    )

    if data["p_application_headers"]["land_advance_plan"] == "1":
        json_data.append(
            {
                "step": f"STEP {get_step_code(1)}：お借入のご希望",
                "big_class": "お借入内容",
                "class": "お借入内容 2回目の融資",
                "field_name": "借入希望日",
                "filed_value": format_js_date_ymd(data["p_borrowing_details__2"]["desired_borrowing_date"]),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(1)}：お借入のご希望",
                "big_class": "",
                "class": "お借入希望額",
                "field_name": "仮入り希望金額",
                "filed_value": format_ja_numeric(data["p_borrowing_details__2"]["desired_loan_amount"], "万円"),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(1)}：お借入のご希望",
                "big_class": "",
                "class": "うち、ボーナス返済分",
                "field_name": "うち、ボーナス返済分",
                "filed_value": format_ja_numeric(data["p_borrowing_details__2"]["bonus_repayment_amount"], "万円"),
            }
        )
    json_data.append(
        {
            "step": f"STEP {get_step_code(1)}：お借入のご希望",
            "big_class": "担保提供者がいる方のみ、チェックをつけてください。",
            "class": "",
            "field_name": "担保提供者（共有者）の有無",
            "filed_value": "いる" if data["p_application_headers"]["join_guarantor_umu"] else "いない",
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(1)}：お借入のご希望",
            "big_class": "住信SBIネット銀行の「住宅ローンプラス」を申し込みますか？",
            "class": "",
            "field_name": "住信SBIネット銀行の「住宅ローンプラス」を申し込みますか？",
            "filed_value": "申し込む" if data["p_application_headers"]["loan_plus"] else "申し込まない",
        }
    )

    # step02
    json_data.append(
        {
            "step": f"STEP {get_step_code(2)}：あなたの情報",
            "big_class": "お名前",
            "class": "姓",
            "field_name": "姓　漢字",
            "filed_value": data["p_applicant_persons__0"]["last_name_kanji"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(2)}：あなたの情報",
            "big_class": "",
            "class": "名",
            "field_name": "名　漢字",
            "filed_value": data["p_applicant_persons__0"]["first_name_kanji"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(2)}：あなたの情報",
            "big_class": "お名前（フリガナ）",
            "class": "セイ",
            "field_name": "姓　カナ",
            "filed_value": data["p_applicant_persons__0"]["last_name_kana"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(2)}：あなたの情報",
            "big_class": "",
            "class": "メイ",
            "field_name": "名　カナ",
            "filed_value": data["p_applicant_persons__0"]["first_name_kana"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(2)}：あなたの情報",
            "big_class": "性別",
            "class": "",
            "field_name": "性別",
            "filed_value": CODE_CONFIGS["p_applicant_persons__0.gender"].get(
                data["p_applicant_persons__0"]["gender"], ""
            ),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(2)}：あなたの情報",
            "big_class": "生年月日",
            "class": "",
            "field_name": "生年月日",
            "filed_value": format_js_date_ymd(data["p_applicant_persons__0"]["birthday"]),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(2)}：あなたの情報",
            "big_class": "現在の国籍",
            "class": "",
            "field_name": "国籍",
            "filed_value": CODE_CONFIGS["p_applicant_persons__0.nationality"].get(
                data["p_applicant_persons__0"]["nationality"], ""
            ),
        }
    )
    if data["p_applicant_persons__0"]["H__a"]:
        json_data.append(
            {
                "step": f"STEP {get_step_code(2)}：あなたの情報",
                "big_class": "在留カードまたは特別永住者証明書を添付してください。",
                "class": "",
                "field_name": "在留カードまたは特別永住者証明書〈表面〉",
                "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__0"]["H__a"]]),
            }
        )
    if data["p_applicant_persons__0"]["H__b"]:
        json_data.append(
            {
                "step": f"STEP {get_step_code(2)}：あなたの情報",
                "big_class": "在留カードまたは特別永住者証明書を添付してください。",
                "class": "",
                "field_name": "在留カードまたは特別永住者証明書〈表面〉",
                "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__0"]["H__b"]]),
            }
        )

    json_data.append(
        {
            "step": f"STEP {get_step_code(2)}：あなたの情報",
            "big_class": "電話番号",
            "class": "携帯",
            "field_name": "携帯電話番号",
            "filed_value": data["p_applicant_persons__0"]["mobile_phone"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(2)}：あなたの情報",
            "big_class": "",
            "class": "自宅",
            "field_name": "自宅電話番号",
            "filed_value": data["p_applicant_persons__0"]["home_phone"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(2)}：あなたの情報",
            "big_class": "現住所",
            "class": "郵便番号",
            "field_name": "現住所　郵便番号",
            "filed_value": data["p_applicant_persons__0"]["postal_code"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(2)}：あなたの情報",
            "big_class": "",
            "class": "都道府県",
            "field_name": "現住所　都道府県　漢字",
            "filed_value": data["p_applicant_persons__0"]["prefecture_kanji"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(2)}：あなたの情報",
            "big_class": "",
            "class": "市区町村郡",
            "field_name": "現住所　市区町村郡",
            "filed_value": data["p_applicant_persons__0"]["city_kanji"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(2)}：あなたの情報",
            "big_class": "",
            "class": "町村丁目",
            "field_name": "現住所　町村丁目",
            "filed_value": data["p_applicant_persons__0"]["district_kanji"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(2)}：あなたの情報",
            "big_class": "",
            "class": "丁目以下・建物名・部屋番号",
            "field_name": "現住所　丁目以下・建物名・部屋番号",
            "filed_value": data["p_applicant_persons__0"]["other_address_kanji"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(2)}：あなたの情報",
            "big_class": "現住所（フリガナ）",
            "class": "都道府県（フリガナ）",
            "field_name": "現住所　都道府県　漢字　カナ",
            "filed_value": data["p_applicant_persons__0"]["prefecture_kana"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(2)}：あなたの情報",
            "big_class": "",
            "class": "市区町村郡（フリガナ）",
            "field_name": "現住所　市区町村郡　カナ",
            "filed_value": data["p_applicant_persons__0"]["city_kana"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(2)}：あなたの情報",
            "big_class": "",
            "class": "町村丁目（フリガナ）",
            "field_name": "現住所　町村丁目　カナ",
            "filed_value": data["p_applicant_persons__0"]["district_kana"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(2)}：あなたの情報",
            "big_class": "",
            "class": "丁目以下・建物名・部屋番号（フリガナ）",
            "field_name": "現住所　丁目以下・建物名・部屋番号　カナ",
            "filed_value": "",
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(2)}：あなたの情報",
            "big_class": "ご連絡先用メールアドレス",
            "class": "",
            "field_name": "メールアドレス",
            "filed_value": data["p_applicant_persons__0"]["email"],
        }
    )

    # step03
    json_data.append(
        {
            "step": f"STEP {get_step_code(3)}：あなたのご職業",
            "big_class": "ご職業",
            "class": "",
            "field_name": "勤務先　職業",
            "filed_value": CODE_CONFIGS["p_applicant_persons__0.office_occupation"].get(
                data["p_applicant_persons__0"]["office_occupation"], ""
            ),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(3)}：あなたのご職業",
            "big_class": "",
            "class": "その他",
            "field_name": "勤務先　職業（その他）",
            "filed_value": data["p_applicant_persons__0"]["office_occupation_other"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(3)}：あなたのご職業",
            "big_class": "業種",
            "class": "",
            "field_name": "勤務先　業種",
            "filed_value": CODE_CONFIGS["p_applicant_persons__0.office_industry"].get(
                data["p_applicant_persons__0"]["office_industry"], ""
            ),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(3)}：あなたのご職業",
            "big_class": "",
            "class": "その他",
            "field_name": "勤務先　業種（その他）",
            "filed_value": data["p_applicant_persons__0"]["office_industry_other"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(3)}：あなたのご職業",
            "big_class": "職種",
            "class": "",
            "field_name": "勤務先　職種",
            "filed_value": CODE_CONFIGS["p_applicant_persons__0.office_occupation_detail"].get(
                data["p_applicant_persons__0"]["office_occupation_detail"], ""
            ),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(3)}：あなたのご職業",
            "big_class": "",
            "class": "その他",
            "field_name": "勤務先　職種（その他）",
            "filed_value": data["p_applicant_persons__0"]["office_occupation_detail_other"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(3)}：あなたのご職業",
            "big_class": "勤務先名",
            "class": "",
            "field_name": "勤務先　名　漢字",
            "filed_value": data["p_applicant_persons__0"]["office_name_kanji"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(3)}：あなたのご職業",
            "big_class": "所属部課",
            "class": "",
            "field_name": "勤務先　所属部署",
            "filed_value": data["p_applicant_persons__0"]["office_department"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(3)}：あなたのご職業",
            "big_class": "勤務先の電話番号",
            "class": "",
            "field_name": "勤務先　電話番号",
            "filed_value": data["p_applicant_persons__0"]["office_phone"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(3)}：あなたのご職業",
            "big_class": "勤務先の住所",
            "class": "郵便番号",
            "field_name": "勤務先　郵便番号",
            "filed_value": data["p_applicant_persons__0"]["office_postal_code"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(3)}：あなたのご職業",
            "big_class": "",
            "class": "都道府県",
            "field_name": "勤務先　都道府県　漢字",
            "filed_value": data["p_applicant_persons__0"]["office_prefecture_kanji"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(3)}：あなたのご職業",
            "big_class": "",
            "class": "市区町村郡",
            "field_name": "勤務先　市区町村郡　漢字",
            "filed_value": data["p_applicant_persons__0"]["office_city_kanji"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(3)}：あなたのご職業",
            "big_class": "",
            "class": "町村丁目",
            "field_name": "勤務先　町村丁目　漢字",
            "filed_value": data["p_applicant_persons__0"]["office_district_kanji"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(3)}：あなたのご職業",
            "big_class": "",
            "class": "丁目以下・建物名・部屋番号",
            "field_name": "丁目以下・建物名・部屋番号",
            "filed_value": data["p_applicant_persons__0"]["office_other_address_kanji"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(3)}：あなたのご職業",
            "big_class": "勤務先の住所（フリガナ）",
            "class": "都道府県（フリガナ）",
            "field_name": "勤務先　都道府県　カナ",
            "filed_value": data["p_applicant_persons__0"]["office_prefecture_kana"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(3)}：あなたのご職業",
            "big_class": "",
            "class": "市区町村郡（フリガナ）",
            "field_name": "勤務先　市区町村郡　カナ",
            "filed_value": data["p_applicant_persons__0"]["office_city_kana"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(3)}：あなたのご職業",
            "big_class": "",
            "class": "町村丁目（フリガナ）",
            "field_name": "勤務先　町村丁目　カナ",
            "filed_value": data["p_applicant_persons__0"]["office_district_kana"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(3)}：あなたのご職業",
            "big_class": "",
            "class": "丁目以下・建物名・部屋番号（フリガナ）",
            "field_name": "勤務先　丁目以下・建物名・部屋番号　カナ",
            "filed_value": "",
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(3)}：あなたのご職業",
            "big_class": "従業員数",
            "class": "",
            "field_name": "勤務先　従業員数",
            "filed_value": format_ja_numeric(data["p_applicant_persons__0"]["office_employee_num"], "名"),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(3)}：あなたのご職業",
            "big_class": "入社年月",
            "class": "",
            "field_name": "入社年月",
            "filed_value": format_js_date_ym(data["p_applicant_persons__0"]["office_joining_date"]),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(3)}：あなたのご職業",
            "big_class": "ご年収",
            "class": "前年度年収",
            "field_name": "ご年収　前年度年収",
            "filed_value": format_ja_numeric(data["p_applicant_persons__0"]["last_year_income"], "万円"),
        }
    )

    if is_mcj:
        json_data.append(
            {
                "step": f"STEP {get_step_code(3)}：あなたのご職業",
                "big_class": "",
                "class": "うち、ボーナス",
                "field_name": "ご年収　うち、ボーナス",
                "filed_value": format_ja_numeric(data["p_applicant_persons__0"]["last_year_bonus_income"], "万円"),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(3)}：あなたのご職業",
                "big_class": "",
                "class": "前々年度年収 （MCJ固有項目）",
                "field_name": "ご年収　前々年度年収 （MCJ固有項目）",
                "filed_value": format_ja_numeric(data["p_applicant_persons__0"]["before_last_year_income"], "万円"),
            }
        )
    json_data.append(
        {
            "step": f"STEP {get_step_code(3)}：あなたのご職業",
            "big_class": "収入源",
            "class": "",
            "field_name": "収入源",
            "filed_value": ",　".join(
                [
                    CODE_CONFIGS["p_applicant_persons__0.income_sources"].get(item, "")
                    for item in data["p_applicant_persons__0"]["income_sources"]
                ]
            ),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(3)}：あなたのご職業",
            "big_class": "確定申告をしていますか？",
            "class": "",
            "field_name": "確定申告をしていますか？",
            "filed_value": CODE_CONFIGS["p_applicant_persons__0.tax_return"].get(
                data["p_applicant_persons__0"]["tax_return"], ""
            ),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(3)}：あなたのご職業",
            "big_class": "確定申告の理由",
            "class": "",
            "field_name": "確定申告の理由",
            "filed_value": ",　".join(
                [
                    CODE_CONFIGS["p_applicant_persons__0.tax_return_reasons"].get(item, "")
                    for item in data["p_applicant_persons__0"]["tax_return_reasons"]
                ]
            ),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(3)}：あなたのご職業",
            "big_class": "確定申告の理由（その他）",
            "class": "",
            "field_name": "確定申告の理由（その他）",
            "filed_value": data["p_applicant_persons__0"]["tax_return_reason_other"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(3)}：あなたのご職業",
            "big_class": "現在、出向（派遣）していますか？",
            "class": "",
            "field_name": "出向（派遣）有無",
            "filed_value": CODE_CONFIGS["p_applicant_persons__0.transfer_office"].get(
                data["p_applicant_persons__0"]["transfer_office"], ""
            ),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(3)}：あなたのご職業",
            "big_class": "出向（派遣）勤務先名",
            "class": "",
            "field_name": "出向（派遣）先　名　漢字",
            "filed_value": data["p_applicant_persons__0"]["transfer_office_name_kanji"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(3)}：あなたのご職業",
            "big_class": "出向（派遣）勤務先名（フリガナ）",
            "class": "",
            "field_name": "出向（派遣）先　名　カナ",
            "filed_value": data["p_applicant_persons__0"]["transfer_office_name_kana"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(3)}：あなたのご職業",
            "big_class": "出向（派遣）先　電話番号",
            "class": "",
            "field_name": "出向（派遣）先　電話番号",
            "filed_value": data["p_applicant_persons__0"]["transfer_office_phone"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(3)}：あなたのご職業",
            "big_class": "出向（派遣）先　住所",
            "class": "郵便番号",
            "field_name": "出向（派遣）先　郵便番号",
            "filed_value": data["p_applicant_persons__0"]["transfer_office_postal_code"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(3)}：あなたのご職業",
            "big_class": "",
            "class": "都道府県",
            "field_name": "出向（派遣）先　都道府県　漢字",
            "filed_value": data["p_applicant_persons__0"]["transfer_office_prefecture_kanji"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(3)}：あなたのご職業",
            "big_class": "",
            "class": "市区町村郡",
            "field_name": "出向（派遣）先　市区町村郡　漢字",
            "filed_value": data["p_applicant_persons__0"]["transfer_office_city_kanji"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(3)}：あなたのご職業",
            "big_class": "",
            "class": "町村丁目",
            "field_name": "出向（派遣）先　町村丁目　漢字",
            "filed_value": data["p_applicant_persons__0"]["transfer_office_district_kanji"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(3)}：あなたのご職業",
            "big_class": "",
            "class": "丁目以下・建物名・部屋番号",
            "field_name": "出向（派遣）先　丁目以下・建物名・部屋番号",
            "filed_value": data["p_applicant_persons__0"]["transfer_office_other_address_kanji"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(3)}：あなたのご職業",
            "big_class": "産休・育休の取得状況※該当する方のみお答えください。",
            "class": "",
            "field_name": "産休・育休の取得状況",
            "filed_value": CODE_CONFIGS["p_applicant_persons__0.maternity_paternity_leave"].get(
                data["p_applicant_persons__0"]["maternity_paternity_leave"], ""
            ),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(3)}：あなたのご職業",
            "big_class": "取得開始時期",
            "class": "",
            "field_name": "産休・育休取得開始期間",
            "filed_value": format_js_date_ym(data["p_applicant_persons__0"]["maternity_paternity_leave_start_date"]),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(3)}：あなたのご職業",
            "big_class": "取得終了時期",
            "class": "",
            "field_name": "産休・育休取得終了期間",
            "filed_value": format_js_date_ym(data["p_applicant_persons__0"]["maternity_paternity_leave_end_date"]),
        }
    )
    if is_mcj:
        json_data.append(
            {
                "step": f"STEP {get_step_code(3)}：あなたのご職業",
                "big_class": "介護休暇の取得状況（MCJ固有項目）※該当する方のみお答えください。",
                "class": "",
                "field_name": "介護休取得状況",
                "filed_value": CODE_CONFIGS["p_applicant_persons__0.maternity_paternity_leave_start_date"].get(
                    data["p_applicant_persons__0"]["maternity_paternity_leave_start_date"], ""
                ),
            }
        )

    if data["p_application_headers"]["loan_type"] in ["3", "4"]:
        # step04
        json_data.append(
            {
                "step": f"STEP {get_step_code(4)}：収入合算者",
                "big_class": "お名前",
                "class": "姓",
                "field_name": "姓　漢字",
                "filed_value": data["p_applicant_persons__1"]["last_name_kanji"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(4)}：収入合算者",
                "big_class": "",
                "class": "名",
                "field_name": "名　漢字",
                "filed_value": data["p_applicant_persons__1"]["first_name_kanji"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(4)}：収入合算者",
                "big_class": "お名前（フリガナ）",
                "class": "セイ",
                "field_name": "姓　カナ",
                "filed_value": data["p_applicant_persons__1"]["last_name_kana"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(4)}：収入合算者",
                "big_class": "",
                "class": "メイ",
                "field_name": "名　カナ",
                "filed_value": data["p_applicant_persons__1"]["first_name_kana"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(4)}：収入合算者",
                "big_class": "性別",
                "class": "",
                "field_name": "性別",
                "filed_value": CODE_CONFIGS["p_applicant_persons__1.gender"].get(
                    data["p_applicant_persons__1"]["gender"], ""
                ),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(4)}：収入合算者",
                "big_class": "続柄",
                "class": "",
                "field_name": "収入合算者続柄",
                "filed_value": data["p_applicant_persons__1"]["rel_to_applicant_a_name"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(4)}：収入合算者",
                "big_class": "生年月日",
                "class": "",
                "field_name": "生年月日",
                "filed_value": format_js_date_ymd(data["p_applicant_persons__1"]["birthday"]),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(4)}：収入合算者",
                "big_class": "現在の国籍",
                "class": "",
                "field_name": "国籍",
                "filed_value": CODE_CONFIGS["p_applicant_persons__1.nationality"].get(
                    data["p_applicant_persons__1"]["nationality"], ""
                ),
            }
        )
        if data["p_applicant_persons__1"]["H__a"]:
            json_data.append(
                {
                    "step": f"STEP {get_step_code(4)}：収入合算者",
                    "big_class": "在留カードまたは特別永住者証明書を添付してください。",
                    "class": "",
                    "field_name": "在留カードまたは特別永住者証明書〈表面〉",
                    "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__1"]["H__a"]]),
                }
            )
        if data["p_applicant_persons__1"]["H__b"]:
            json_data.append(
                {
                    "step": f"STEP {get_step_code(4)}：収入合算者",
                    "big_class": "在留カードまたは特別永住者証明書を添付してください。",
                    "class": "",
                    "field_name": "在留カードまたは特別永住者証明書〈表面〉",
                    "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__1"]["H__b"]]),
                }
            )

        json_data.append(
            {
                "step": f"STEP {get_step_code(4)}：収入合算者",
                "big_class": "電話番号",
                "class": "携帯",
                "field_name": "携帯電話番号",
                "filed_value": data["p_applicant_persons__1"]["mobile_phone"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(4)}：収入合算者",
                "big_class": "",
                "class": "自宅",
                "field_name": "自宅電話番号",
                "filed_value": data["p_applicant_persons__1"]["home_phone"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(4)}：収入合算者",
                "big_class": "現住所",
                "class": "郵便番号",
                "field_name": "現住所　郵便番号",
                "filed_value": data["p_applicant_persons__1"]["postal_code"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(4)}：収入合算者",
                "big_class": "",
                "class": "都道府県",
                "field_name": "現住所　都道府県　漢字",
                "filed_value": data["p_applicant_persons__1"]["prefecture_kanji"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(4)}：収入合算者",
                "big_class": "",
                "class": "市区町村郡",
                "field_name": "現住所　市区町村郡",
                "filed_value": data["p_applicant_persons__1"]["city_kanji"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(4)}：収入合算者",
                "big_class": "",
                "class": "町村丁目",
                "field_name": "現住所　町村丁目",
                "filed_value": data["p_applicant_persons__1"]["district_kanji"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(4)}：収入合算者",
                "big_class": "",
                "class": "丁目以下・建物名・部屋番号",
                "field_name": "現住所　丁目以下・建物名・部屋番号",
                "filed_value": data["p_applicant_persons__1"]["other_address_kanji"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(4)}：収入合算者",
                "big_class": "現住所（フリガナ）",
                "class": "都道府県（フリガナ）",
                "field_name": "現住所　都道府県　漢字　カナ",
                "filed_value": data["p_applicant_persons__1"]["prefecture_kana"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(4)}：収入合算者",
                "big_class": "",
                "class": "市区町村郡（フリガナ）",
                "field_name": "現住所　市区町村郡　カナ",
                "filed_value": data["p_applicant_persons__1"]["city_kana"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(4)}：収入合算者",
                "big_class": "",
                "class": "町村丁目（フリガナ）",
                "field_name": "現住所　町村丁目　カナ",
                "filed_value": data["p_applicant_persons__1"]["district_kana"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(4)}：収入合算者",
                "big_class": "",
                "class": "丁目以下・建物名・部屋番号（フリガナ）",
                "field_name": "現住所　丁目以下・建物名・部屋番号　カナ",
                "filed_value": "",
            }
        )

        # tep05
        json_data.append(
            {
                "step": f"STEP {get_step_code(5)}：収入合算者の職業",
                "big_class": "ご職業",
                "class": "",
                "field_name": "勤務先　職業",
                "filed_value": CODE_CONFIGS["p_applicant_persons__1.office_occupation"].get(
                    data["p_applicant_persons__1"]["office_occupation"], ""
                ),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(5)}：収入合算者の職業",
                "big_class": "",
                "class": "その他",
                "field_name": "勤務先　職業（その他）",
                "filed_value": data["p_applicant_persons__1"]["office_occupation_other"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(5)}：収入合算者の職業",
                "big_class": "業種",
                "class": "",
                "field_name": "勤務先　業種",
                "filed_value": CODE_CONFIGS["p_applicant_persons__1.office_industry"].get(
                    data["p_applicant_persons__1"]["office_industry"], ""
                ),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(5)}：収入合算者の職業",
                "big_class": "",
                "class": "その他",
                "field_name": "勤務先　業種（その他）",
                "filed_value": data["p_applicant_persons__1"]["office_industry_other"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(5)}：収入合算者の職業",
                "big_class": "職種",
                "class": "",
                "field_name": "勤務先　職種",
                "filed_value": CODE_CONFIGS["p_applicant_persons__1.office_occupation_detail"].get(
                    data["p_applicant_persons__1"]["office_occupation_detail"], ""
                ),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(5)}：収入合算者の職業",
                "big_class": "",
                "class": "その他",
                "field_name": "勤務先　職種（その他）",
                "filed_value": data["p_applicant_persons__1"]["office_occupation_detail_other"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(5)}：収入合算者の職業",
                "big_class": "勤務先名",
                "class": "",
                "field_name": "勤務先　名　漢字",
                "filed_value": data["p_applicant_persons__1"]["office_name_kanji"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(5)}：収入合算者の職業",
                "big_class": "所属部課",
                "class": "",
                "field_name": "勤務先　所属部署",
                "filed_value": data["p_applicant_persons__1"]["office_department"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(5)}：収入合算者の職業",
                "big_class": "勤務先の電話番号",
                "class": "",
                "field_name": "勤務先　電話番号",
                "filed_value": data["p_applicant_persons__1"]["office_phone"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(5)}：収入合算者の職業",
                "big_class": "勤務先の住所",
                "class": "郵便番号",
                "field_name": "勤務先　郵便番号",
                "filed_value": data["p_applicant_persons__1"]["office_postal_code"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(5)}：収入合算者の職業",
                "big_class": "",
                "class": "都道府県",
                "field_name": "勤務先　都道府県　漢字",
                "filed_value": data["p_applicant_persons__1"]["office_prefecture_kanji"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(5)}：収入合算者の職業",
                "big_class": "",
                "class": "市区町村郡",
                "field_name": "勤務先　市区町村郡　漢字",
                "filed_value": data["p_applicant_persons__1"]["office_city_kanji"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(5)}：収入合算者の職業",
                "big_class": "",
                "class": "町村丁目",
                "field_name": "勤務先　町村丁目　漢字",
                "filed_value": data["p_applicant_persons__1"]["office_district_kanji"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(5)}：収入合算者の職業",
                "big_class": "",
                "class": "丁目以下・建物名・部屋番号",
                "field_name": "丁目以下・建物名・部屋番号",
                "filed_value": data["p_applicant_persons__1"]["office_other_address_kanji"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(5)}：収入合算者の職業",
                "big_class": "勤務先の住所（フリガナ）",
                "class": "都道府県（フリガナ）",
                "field_name": "勤務先　都道府県　カナ",
                "filed_value": data["p_applicant_persons__1"]["office_prefecture_kana"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(5)}：収入合算者の職業",
                "big_class": "",
                "class": "市区町村郡（フリガナ）",
                "field_name": "勤務先　市区町村郡　カナ",
                "filed_value": data["p_applicant_persons__1"]["office_city_kana"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(5)}：収入合算者の職業",
                "big_class": "",
                "class": "町村丁目（フリガナ）",
                "field_name": "勤務先　町村丁目　カナ",
                "filed_value": data["p_applicant_persons__1"]["office_district_kana"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(5)}：収入合算者の職業",
                "big_class": "",
                "class": "丁目以下・建物名・部屋番号（フリガナ）",
                "field_name": "勤務先　丁目以下・建物名・部屋番号　カナ",
                "filed_value": "",
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(5)}：収入合算者の職業",
                "big_class": "従業員数",
                "class": "",
                "field_name": "勤務先　従業員数",
                "filed_value": format_ja_numeric(data["p_applicant_persons__1"]["office_employee_num"], "名"),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(5)}：収入合算者の職業",
                "big_class": "入社年月",
                "class": "",
                "field_name": "入社年月",
                "filed_value": format_js_date_ym(data["p_applicant_persons__1"]["office_joining_date"]),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(5)}：収入合算者の職業",
                "big_class": "ご年収",
                "class": "前年度年収",
                "field_name": "ご年収　前年度年収",
                "filed_value": format_ja_numeric(data["p_applicant_persons__1"]["last_year_income"], "万円"),
            }
        )

        if is_mcj:
            json_data.append(
                {
                    "step": f"STEP {get_step_code(5)}：収入合算者の職業",
                    "big_class": "",
                    "class": "うち、ボーナス",
                    "field_name": "ご年収　うち、ボーナス",
                    "filed_value": format_ja_numeric(data["p_applicant_persons__1"]["last_year_bonus_income"], "万円"),
                }
            )
            json_data.append(
                {
                    "step": f"STEP {get_step_code(5)}：収入合算者の職業",
                    "big_class": "",
                    "class": "前々年度年収 （MCJ固有項目）",
                    "field_name": "ご年収　前々年度年収 （MCJ固有項目）",
                    "filed_value": format_ja_numeric(data["p_applicant_persons__1"]["before_last_year_income"], "万円"),
                }
            )
        json_data.append(
            {
                "step": f"STEP {get_step_code(5)}：収入合算者の職業",
                "big_class": "収入源",
                "class": "",
                "field_name": "収入源",
                "filed_value": ",　".join(
                    [
                        CODE_CONFIGS["p_applicant_persons__1.income_sources"].get(item, "")
                        for item in data["p_applicant_persons__1"]["income_sources"]
                    ]
                ),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(5)}：収入合算者の職業",
                "big_class": "確定申告をしていますか？",
                "class": "",
                "field_name": "確定申告をしていますか？",
                "filed_value": CODE_CONFIGS["p_applicant_persons__1.tax_return"].get(
                    data["p_applicant_persons__1"]["tax_return"], ""
                ),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(5)}：収入合算者の職業",
                "big_class": "確定申告の理由",
                "class": "",
                "field_name": "確定申告の理由",
                "filed_value": ",　".join(
                    [
                        CODE_CONFIGS["p_applicant_persons__1.tax_return_reasons"].get(item, "")
                        for item in data["p_applicant_persons__1"]["tax_return_reasons"]
                    ]
                ),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(5)}：収入合算者の職業",
                "big_class": "確定申告の理由（その他）",
                "class": "",
                "field_name": "確定申告の理由（その他）",
                "filed_value": data["p_applicant_persons__1"]["tax_return_reason_other"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(5)}：収入合算者の職業",
                "big_class": "現在、出向（派遣）していますか？",
                "class": "",
                "field_name": "出向（派遣）有無",
                "filed_value": CODE_CONFIGS["p_applicant_persons__1.transfer_office"].get(
                    data["p_applicant_persons__1"]["transfer_office"], ""
                ),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(5)}：収入合算者の職業",
                "big_class": "出向（派遣）勤務先名",
                "class": "",
                "field_name": "出向（派遣）先　名　漢字",
                "filed_value": data["p_applicant_persons__1"]["transfer_office_name_kanji"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(5)}：収入合算者の職業",
                "big_class": "出向（派遣）勤務先名（フリガナ）",
                "class": "",
                "field_name": "出向（派遣）先　名　カナ",
                "filed_value": data["p_applicant_persons__1"]["transfer_office_name_kana"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(5)}：収入合算者の職業",
                "big_class": "出向（派遣）先　電話番号",
                "class": "",
                "field_name": "出向（派遣）先　電話番号",
                "filed_value": data["p_applicant_persons__1"]["transfer_office_phone"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(5)}：収入合算者の職業",
                "big_class": "出向（派遣）先　住所",
                "class": "郵便番号",
                "field_name": "出向（派遣）先　郵便番号",
                "filed_value": data["p_applicant_persons__1"]["transfer_office_postal_code"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(5)}：収入合算者の職業",
                "big_class": "",
                "class": "都道府県",
                "field_name": "出向（派遣）先　都道府県　漢字",
                "filed_value": data["p_applicant_persons__1"]["transfer_office_prefecture_kanji"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(5)}：収入合算者の職業",
                "big_class": "",
                "class": "市区町村郡",
                "field_name": "出向（派遣）先　市区町村郡　漢字",
                "filed_value": data["p_applicant_persons__1"]["transfer_office_city_kanji"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(5)}：収入合算者の職業",
                "big_class": "",
                "class": "町村丁目",
                "field_name": "出向（派遣）先　町村丁目　漢字",
                "filed_value": data["p_applicant_persons__1"]["transfer_office_district_kanji"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(5)}：収入合算者の職業",
                "big_class": "",
                "class": "丁目以下・建物名・部屋番号",
                "field_name": "出向（派遣）先　丁目以下・建物名・部屋番号",
                "filed_value": data["p_applicant_persons__1"]["transfer_office_other_address_kanji"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(5)}：収入合算者の職業",
                "big_class": "産休・育休の取得状況※該当する方のみお答えください。",
                "class": "",
                "field_name": "産休・育休の取得状況",
                "filed_value": CODE_CONFIGS["p_applicant_persons__1.maternity_paternity_leave"].get(
                    data["p_applicant_persons__1"]["maternity_paternity_leave"], ""
                ),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(5)}：収入合算者の職業",
                "big_class": "取得開始時期",
                "class": "",
                "field_name": "産休・育休取得開始期間",
                "filed_value": format_js_date_ym(
                    data["p_applicant_persons__1"]["maternity_paternity_leave_start_date"]
                ),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(5)}：収入合算者の職業",
                "big_class": "取得終了時期",
                "class": "",
                "field_name": "産休・育休取得終了期間",
                "filed_value": format_js_date_ym(data["p_applicant_persons__1"]["maternity_paternity_leave_end_date"]),
            }
        )
        if is_mcj:
            json_data.append(
                {
                    "step": f"STEP {get_step_code(5)}：収入合算者の職業",
                    "big_class": "介護休暇の取得状況（MCJ固有項目）※該当する方のみお答えください。",
                    "class": "",
                    "field_name": "介護休取得状況",
                    "filed_value": CODE_CONFIGS["p_applicant_persons__1.maternity_paternity_leave_start_date"].get(
                        data["p_applicant_persons__1"]["maternity_paternity_leave_start_date"], ""
                    ),
                }
            )
    # step06
    if data["p_application_headers"]["join_guarantor_umu"] == "1":
        for p_join_guarantor in data["p_join_guarantors"]:
            json_data.append(
                {
                    "step": f"STEP {get_step_code(6)}：担保提供者",
                    "big_class": "担保提供者の氏名",
                    "class": "姓",
                    "field_name": "担保提供者　姓　漢字",
                    "filed_value": p_join_guarantor["last_name_kanji"],
                }
            )
            json_data.append(
                {
                    "step": f"STEP {get_step_code(6)}：担保提供者",
                    "big_class": "",
                    "class": "名",
                    "field_name": "担保提供者　名　漢字",
                    "filed_value": p_join_guarantor["first_name_kanji"],
                }
            )
            json_data.append(
                {
                    "step": f"STEP {get_step_code(6)}：担保提供者",
                    "big_class": "担保提供者の氏名（フリガナ）",
                    "class": "セイ",
                    "field_name": "担保提供者　姓　メイ",
                    "filed_value": p_join_guarantor["last_name_kana"],
                }
            )
            json_data.append(
                {
                    "step": f"STEP {get_step_code(6)}：担保提供者",
                    "big_class": "",
                    "class": "メイ",
                    "field_name": "担保提供者　名　メイ",
                    "filed_value": p_join_guarantor["first_name_kana"],
                }
            )
            json_data.append(
                {
                    "step": f"STEP {get_step_code(6)}：担保提供者",
                    "big_class": "性別",
                    "class": "",
                    "field_name": "性別",
                    "filed_value": CODE_CONFIGS["p_join_guarantors.gender"].get(p_join_guarantor["gender"], ""),
                }
            )
            json_data.append(
                {
                    "step": f"STEP {get_step_code(6)}：担保提供者",
                    "big_class": "続柄",
                    "class": "",
                    "field_name": "担保提供者　続柄",
                    "filed_value": p_join_guarantor["rel_to_applicant_a_name"],
                }
            )
            json_data.append(
                {
                    "step": f"STEP {get_step_code(6)}：担保提供者",
                    "big_class": "生年月日",
                    "class": "",
                    "field_name": "生年月日",
                    "filed_value": format_js_date_ymd(p_join_guarantor["birthday"]),
                }
            )
            json_data.append(
                {
                    "step": f"STEP {get_step_code(6)}：担保提供者",
                    "big_class": "電話番号",
                    "class": "携帯",
                    "field_name": "携帯電話番号",
                    "filed_value": p_join_guarantor["mobile_phone"],
                }
            )
            json_data.append(
                {
                    "step": f"STEP {get_step_code(6)}：担保提供者",
                    "big_class": "",
                    "class": "自宅",
                    "field_name": "自宅電話番号",
                    "filed_value": p_join_guarantor["home_phone"],
                }
            )
            json_data.append(
                {
                    "step": f"STEP {get_step_code(6)}：担保提供者",
                    "big_class": "担保提供者の住所",
                    "class": "郵便番号",
                    "field_name": "郵便番号",
                    "filed_value": p_join_guarantor["postal_code"],
                }
            )
            json_data.append(
                {
                    "step": f"STEP {get_step_code(6)}：担保提供者",
                    "big_class": "",
                    "class": "都道府県",
                    "field_name": "都道府県　漢字",
                    "filed_value": p_join_guarantor["prefecture_kanji"],
                }
            )
            json_data.append(
                {
                    "step": f"STEP {get_step_code(6)}：担保提供者",
                    "big_class": "",
                    "class": "市区町村郡",
                    "field_name": "市区町村郡　漢字",
                    "filed_value": p_join_guarantor["city_kanji"],
                }
            )
            json_data.append(
                {
                    "step": f"STEP {get_step_code(6)}：担保提供者",
                    "big_class": "",
                    "class": "町村丁目",
                    "field_name": "町村丁目　漢字",
                    "filed_value": p_join_guarantor["district_kanji"],
                }
            )
            json_data.append(
                {
                    "step": f"STEP {get_step_code(6)}：担保提供者",
                    "big_class": "",
                    "class": "丁目以下・建物名・部屋番号",
                    "field_name": "丁目以下・建物名・部屋番号　漢字",
                    "filed_value": p_join_guarantor["other_address_kanji"],
                }
            )

            json_data.append(
                {
                    "step": f"STEP {get_step_code(6)}：担保提供者",
                    "big_class": "担保提供者の住所（フリガナ）",
                    "class": "都道府県（フリガナ）",
                    "field_name": "都道府県　カナ",
                    "filed_value": p_join_guarantor["prefecture_kana"],
                }
            )
            json_data.append(
                {
                    "step": f"STEP {get_step_code(6)}：担保提供者",
                    "big_class": "",
                    "class": "市区町村郡（フリガナ）",
                    "field_name": "市区町村郡　カナ",
                    "filed_value": p_join_guarantor["city_kana"],
                }
            )
            json_data.append(
                {
                    "step": f"STEP {get_step_code(6)}：担保提供者",
                    "big_class": "",
                    "class": "町村丁目（フリガナ）",
                    "field_name": "町村丁目　カナ",
                    "filed_value": p_join_guarantor["district_kana"],
                }
            )
            json_data.append(
                {
                    "step": f"STEP {get_step_code(6)}：担保提供者",
                    "big_class": "",
                    "class": "丁目以下・建物名・部屋番号（フリガナ）",
                    "field_name": "丁目以下・建物名・部屋番号　カナ",
                    "filed_value": "",
                }
            )
    # step07
    json_data.append(
        {
            "step": f"STEP {get_step_code(7)}：お住まいについて",
            "big_class": "現在のお住まいの居住年数",
            "class": "現在居住　居住年数（年）",
            "field_name": "現在居住　居住年数（年）",
            "filed_value": format_ja_numeric(data["p_application_headers"]["curr_house_lived_year"], "年"),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(7)}：お住まいについて",
            "big_class": "",
            "class": "現在居住　居住年数（ヶ月）",
            "field_name": "現在居住　居住年数（ヶ月）",
            "filed_value": format_ja_numeric(data["p_application_headers"]["curr_house_lived_month"], "ヶ月"),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(7)}：お住まいについて",
            "big_class": "現在のお住まいの種類",
            "class": "",
            "field_name": "現在のお住まいの種類",
            "filed_value": CODE_CONFIGS["p_application_headers.curr_house_residence_type"].get(
                data["p_application_headers"]["curr_house_residence_type"], ""
            ),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(7)}：お住まいについて",
            "big_class": "所有者の氏名",
            "class": "",
            "field_name": "現在居住　所有者の氏名",
            "filed_value": data["p_application_headers"]["curr_house_owner_name"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(7)}：お住まいについて",
            "big_class": "続柄",
            "class": "",
            "field_name": "現在居住　所有者の続柄",
            "filed_value": data["p_application_headers"]["curr_house_owner_rel"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(7)}：お住まいについて",
            "big_class": "持ち家の処分方法",
            "class": "",
            "field_name": "持家　処分方法",
            "filed_value": CODE_CONFIGS["p_application_headers.curr_house_schedule_disposal_type"].get(
                data["p_application_headers"]["curr_house_schedule_disposal_type"], ""
            ),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(7)}：お住まいについて",
            "big_class": "",
            "class": "その他の方は詳細を入力ください。",
            "field_name": "持家　処分方法（その他）",
            "filed_value": data["p_application_headers"]["curr_house_schedule_disposal_type_other"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(7)}：お住まいについて",
            "big_class": "売却予定時期",
            "class": "",
            "field_name": "持家　売却予定時期",
            "filed_value": format_js_date_ym(data["p_application_headers"]["curr_house_shell_scheduled_date"]),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(7)}：お住まいについて",
            "big_class": "売却予定価格",
            "class": "",
            "field_name": "持家　売却予定価格",
            "filed_value": format_ja_numeric(data["p_application_headers"]["curr_house_shell_scheduled_price"], "万円"),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(7)}：お住まいについて",
            "big_class": "ローン残高",
            "class": "",
            "field_name": "持家　ローン残高有無",
            "filed_value": CODE_CONFIGS["p_application_headers.curr_house_loan_balance_type"].get(
                data["p_application_headers"]["curr_house_loan_balance_type"], ""
            ),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(7)}：お住まいについて",
            "big_class": "物件についての書類",
            "class": "画像アップロード",
            "field_name": "画像アップロード",
            "filed_value": ", ".join([item["name"] for item in data["p_application_headers"]["G"]]),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(7)}：お住まいについて",
            "big_class": "※チラシ等がない場合物件情報が掲載されたURL添付",
            "class": "",
            "field_name": "物件情報が掲載されたURL",
            "filed_value": data["p_application_headers"]["property_publish_url"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(7)}：お住まいについて",
            "big_class": "新しい住居を必要とする理由",
            "class": "",
            "field_name": "住宅取得理由",
            "filed_value": CODE_CONFIGS["p_application_headers.new_house_acquire_reason"].get(
                data["p_application_headers"]["new_house_acquire_reason"], ""
            ),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(7)}：お住まいについて",
            "big_class": "",
            "class": "その他の方は詳細を入力ください。",
            "field_name": "住宅取得理由（その他）",
            "filed_value": data["p_application_headers"]["new_house_acquire_reason_other"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(7)}：お住まいについて",
            "big_class": "新しい住居に、あなたは居住しますか？",
            "class": "",
            "field_name": "新しい住居に、あなたは居住しますか？",
            "filed_value": CODE_CONFIGS["p_application_headers.new_house_self_resident"].get(
                data["p_application_headers"]["new_house_self_resident"], ""
            ),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(7)}：お住まいについて",
            "big_class": "",
            "class": "「いいえ」の方は理由を入力ください。",
            "field_name": "新しい住居に、居住しない理由",
            "filed_value": data["p_application_headers"]["new_house_self_not_resident_reason"],
        }
    )
    overview = []
    count = 0
    if data["p_application_headers"]["new_house_planned_resident_overview"]["spouse"]:
        overview.append("配偶者")
        count += int(data["p_application_headers"]["new_house_planned_resident_overview"]["spouse"])
    if data["p_application_headers"]["new_house_planned_resident_overview"]["children"]:
        overview.append("子ども")
        count += int(data["p_application_headers"]["new_house_planned_resident_overview"]["children"])
    if data["p_application_headers"]["new_house_planned_resident_overview"]["father"]:
        overview.append("父")
        count += int(data["p_application_headers"]["new_house_planned_resident_overview"]["father"])
    if data["p_application_headers"]["new_house_planned_resident_overview"]["mother"]:
        overview.append("母")
        count += int(data["p_application_headers"]["new_house_planned_resident_overview"]["mother"])
    if data["p_application_headers"]["new_house_planned_resident_overview"]["brothers_sisters"]:
        overview.append("兄弟姉妹")
        count += int(data["p_application_headers"]["new_house_planned_resident_overview"]["brothers_sisters"])
    if data["p_application_headers"]["new_house_planned_resident_overview"]["fiance"]:
        overview.append("婚約者")
        count += int(data["p_application_headers"]["new_house_planned_resident_overview"]["fiance"])
    if data["p_application_headers"]["new_house_planned_resident_overview"]["others"]:
        overview.append("その他")
        count += int(data["p_application_headers"]["new_house_planned_resident_overview"]["others"])

    json_data.append(
        {
            "step": f"STEP {get_step_code(7)}：お住まいについて",
            "big_class": "あなた以外の入居予定者※該当する方のみお答えください。",
            "class": "入居予定者",
            "field_name": "入居予定者",
            "filed_value": ", ".join(overview),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(7)}：お住まいについて",
            "big_class": "",
            "class": "子ども　　人",
            "field_name": "居住予定　子供",
            "filed_value": format_ja_numeric(
                data["p_application_headers"]["new_house_planned_resident_overview"]["children"], "人"
            ),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(7)}：お住まいについて",
            "big_class": "",
            "class": "兄弟姉妹　　人",
            "field_name": "居住予定　兄弟姉妹",
            "filed_value": format_ja_numeric(
                data["p_application_headers"]["new_house_planned_resident_overview"]["brothers_sisters"], "人"
            ),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(7)}：お住まいについて",
            "big_class": "",
            "class": "その他　　人",
            "field_name": "居住予定　人数 (その他)",
            "filed_value": format_ja_numeric(
                data["p_application_headers"]["new_house_planned_resident_overview"]["others"], "人"
            ),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(7)}：お住まいについて",
            "big_class": "",
            "class": "その他の方は続柄をご入力ください。",
            "field_name": "居住予定　続柄 (その他)",
            "filed_value": data["p_application_headers"]["new_house_planned_resident_overview"]["others_rel"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(7)}：お住まいについて",
            "big_class": "",
            "class": "ご本人を除き、合計",
            "field_name": "ご本人を除き、合計",
            "filed_value": format_ja_numeric(count, "人"),
        }
    )

    json_data.append(
        {
            "step": f"STEP {get_step_code(7)}：お住まいについて",
            "big_class": "新しい住居（融資対象物件）の事業性※該当する方のみお答えください。",
            "class": "",
            "field_name": "融資対象物件の事業性",
            "filed_value": ", ".join(
                [
                    CODE_CONFIGS["p_application_headers.property_business_type"].get(item, "")
                    for item in data["p_application_headers"]["property_business_type"]
                ]
            ),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(7)}：お住まいについて",
            "big_class": "ご購入物件の所在地",
            "class": "都道府県",
            "field_name": "融資対象物件　都道府県",
            "filed_value": data["p_application_headers"]["property_prefecture"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(7)}：お住まいについて",
            "big_class": "",
            "class": "市区町村郡",
            "field_name": "融資対象物件　市区町村郡",
            "filed_value": data["p_application_headers"]["property_city"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(7)}：お住まいについて",
            "big_class": "",
            "class": "以下地番",
            "field_name": "融資対象物件　地番",
            "filed_value": data["p_application_headers"]["property_district"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(7)}：お住まいについて",
            "big_class": "",
            "class": "マンション名・部屋番号",
            "field_name": "融資対象物件　マンション名・部屋番号",
            "filed_value": data["p_application_headers"]["property_apartment_and_room_no"],
        }
    )
    if data["p_application_headers"]["loan_target"] in ["2", "3"]:
        json_data.append(
            {
                "step": f"STEP {get_step_code(7)}：お住まいについて",
                "big_class": "ご購入物件の面積",
                "class": "専有面積",
                "field_name": "融資対象物件　専有面積",
                "filed_value": (
                    data["p_application_headers"]["property_private_area"] + "m²"
                    if data["p_application_headers"]["property_private_area"]
                    else ""
                ),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(7)}：お住まいについて",
                "big_class": "",
                "class": "マンション全体の延べ床面積",
                "field_name": "融資対象物件　マンション全体の延べ床面積",
                "filed_value": (
                    data["p_application_headers"]["property_total_floor_area"] + "m²"
                    if data["p_application_headers"]["property_total_floor_area"]
                    else ""
                ),
            }
        )
    else:
        json_data.append(
            {
                "step": f"STEP {get_step_code(7)}：お住まいについて",
                "big_class": "",
                "class": "土地の敷地面積",
                "field_name": "融資対象物件　土地の敷地面積",
                "filed_value": (
                    data["p_application_headers"]["property_land_area"] + "m²"
                    if data["p_application_headers"]["property_land_area"]
                    else ""
                ),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(7)}：お住まいについて",
                "big_class": "",
                "class": "建物の延べ床面積",
                "field_name": "融資対象物件　建物の延べ床面積",
                "filed_value": (
                    data["p_application_headers"]["property_floor_area"] + "m²"
                    if data["p_application_headers"]["property_floor_area"]
                    else ""
                ),
            }
        )
    if is_mcj:
        json_data.append(
            {
                "step": f"STEP {get_step_code(7)}：お住まいについて",
                "big_class": "現在のお住まいの床面積 (MCJ固有項目)",
                "class": "",
                "field_name": "現在居住　床面積",
                "filed_value": (
                    data["p_application_headers"]["curr_house_floor_area"] + "m²"
                    if data["p_application_headers"]["curr_house_floor_area"]
                    else ""
                ),
            }
        )
    for p_resident in data["p_residents"]:
        json_data.append(
            {
                "step": f"STEP {get_step_code(7)}：お住まいについて",
                "big_class": "ご入居予定者の情報 (MCJ固有項目)",
                "class": "入居予定者の氏名　姓",
                "field_name": "入居予定者　姓　漢字",
                "filed_value": p_resident["last_name_kanji"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(7)}：お住まいについて",
                "big_class": "",
                "class": "入居予定者の氏名　名",
                "field_name": "入居予定者　名　漢字",
                "filed_value": p_resident["first_name_kanji"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(7)}：お住まいについて",
                "big_class": "",
                "class": "入居予定者の氏名（フリガナ）　セイ",
                "field_name": "入居予定者　姓　カナ",
                "filed_value": p_resident["last_name_kana"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(7)}：お住まいについて",
                "big_class": "",
                "class": "入居予定者の氏名（フリガナ）　メイ",
                "field_name": "入居予定者　名　カナ",
                "filed_value": p_resident["first_name_kana"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(7)}：お住まいについて",
                "big_class": "",
                "class": "続柄",
                "field_name": "続柄",
                "filed_value": p_resident["rel_to_applicant_a_name"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(7)}：お住まいについて",
                "big_class": "",
                "class": "国籍",
                "field_name": "国籍",
                "filed_value": CODE_CONFIGS["p_residents.nationality"].get(p_resident["nationality"], ""),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(7)}：お住まいについて",
                "big_class": "",
                "class": "生年月日",
                "field_name": "入居予定者　生年月日",
                "filed_value": format_js_date_ymd(p_resident["birthday"]),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(7)}：お住まいについて",
                "big_class": "",
                "class": "住宅金融支援機構（旧：公庫）からの融資の有無",
                "field_name": "住宅金融支援機構（旧：公庫）からの融資の有無",
                "filed_value": CODE_CONFIGS["p_residents.loan_from_japan_house_finance_agency"].get(
                    p_resident["loan_from_japan_house_finance_agency"], ""
                ),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(7)}：お住まいについて",
                "big_class": "",
                "class": "電話番号",
                "field_name": "電話番号",
                "filed_value": p_resident["contact_phone"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(7)}：お住まいについて",
                "big_class": "",
                "class": "住所　郵便番号",
                "field_name": "郵便番号",
                "filed_value": p_resident["postal_code"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(7)}：お住まいについて",
                "big_class": "",
                "class": "住所　都道府県",
                "field_name": "現住所　都道府県　漢字",
                "filed_value": p_resident["prefecture_kanji"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(7)}：お住まいについて",
                "big_class": "",
                "class": "住所　市区町村郡",
                "field_name": "現住所　市区町村郡　漢字",
                "filed_value": p_resident["city_kanji"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(7)}：お住まいについて",
                "big_class": "",
                "class": "住所　町村丁目",
                "field_name": "現住所　町村丁目　漢字",
                "filed_value": p_resident["district_kanji"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(7)}：お住まいについて",
                "big_class": "",
                "class": "住所　丁目以下・建物名・部屋番号",
                "field_name": "現住所　丁目以下・建物名・部屋番号　漢字",
                "filed_value": p_resident["other_address_kanji"],
            }
        )
    if is_mcj:
        json_data.append(
            {
                "step": f"STEP {get_step_code(7)}：お住まいについて",
                "big_class": "ご購入物件の土地権利※該当する方のみお答えください。(MCJ固有項目)",
                "class": "",
                "field_name": "土地の情報　土地権利",
                "filed_value": CODE_CONFIGS["p_application_headers.property_land_type"].get(
                    data["p_application_headers"]["property_land_type"], ""
                ),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(7)}：お住まいについて",
                "big_class": "買戻・保留地・仮換地※該当する方のみお答えください。(MCJ固有項目)",
                "class": "",
                "field_name": "土地の情報　買戻・保留地・仮換地",
                "filed_value": CODE_CONFIGS["p_application_headers.property_purchase_type"].get(
                    data["p_application_headers"]["property_purchase_type"], ""
                ),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(7)}：お住まいについて",
                "big_class": "都市計画区域等 (MCJ固有項目)※「市街化区域」以外の方のみお答えください。",
                "class": "",
                "field_name": "土地の情報　都市計画区域",
                "filed_value": CODE_CONFIGS["p_application_headers.property_planning_area"].get(
                    data["p_application_headers"]["property_planning_area"], ""
                ),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(7)}：お住まいについて",
                "big_class": "",
                "class": "その他の方は詳細を入力ください。",
                "field_name": "土地の情報　都市計画区域（その他）",
                "filed_value": data["p_application_headers"]["property_planning_area_other"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(7)}：お住まいについて",
                "big_class": "上記に該当する場合の「再建築理由」を教えてください。※該当する方のみお答えください。(MCJ固有項目)",
                "class": "",
                "field_name": "土地の情報　再建築理由",
                "filed_value": CODE_CONFIGS["p_application_headers.property_rebuilding_reason"].get(
                    data["p_application_headers"]["property_rebuilding_reason"], ""
                ),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(7)}：お住まいについて",
                "big_class": "",
                "class": "その他の方は詳細を入力ください。",
                "field_name": "土地の情報　再建築理由（その他）",
                "filed_value": data["p_application_headers"]["property_rebuilding_reason_other"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(7)}：お住まいについて",
                "big_class": "フラット35S（優良住宅取得支援制度）対象項目※該当する方のみお答えください。(MCJ固有項目)",
                "class": "",
                "field_name": "その他物件情報　フラット35S適用プラン",
                "filed_value": CODE_CONFIGS["p_application_headers.property_flat_35_plan"].get(
                    data["p_application_headers"]["property_flat_35_plan"], ""
                ),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(7)}：お住まいについて",
                "big_class": "維持保全型※該当する方のみお答えください。(MCJ固有項目)",
                "class": "",
                "field_name": "その他物件情報　維持保全型",
                "filed_value": CODE_CONFIGS["p_application_headers.property_maintenance_type"].get(
                    data["p_application_headers"]["property_maintenance_type"], ""
                ),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(7)}：お住まいについて",
                "big_class": "フラット35S（優良住宅取得支援制度）対象項目②※該当する方のみお答えください。(MCJ固有項目)",
                "class": "",
                "field_name": "その他物件情報　フラット35S満たす技術基準",
                "filed_value": CODE_CONFIGS["p_application_headers.property_flat_35_tech"].get(
                    data["p_application_headers"]["property_flat_35_tech"], ""
                ),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(7)}：お住まいについて",
                "big_class": "地域連携型・地方移住支援型※該当する方のみお答えください。(MCJ固有項目)",
                "class": "",
                "field_name": "その他物件情報　地域連携型・地方移住支援型",
                "filed_value": CODE_CONFIGS["p_application_headers.property_region_type"].get(
                    data["p_application_headers"]["property_region_type"], ""
                ),
            }
        )
    # step08
    json_data.append(
        {
            "step": f"STEP {get_step_code(8)}：現在のお借入状況",
            "big_class": "あなたや連帯保証人予定者に、現在お借入はありますか？",
            "class": "",
            "field_name": "あなたや連帯保証人予定者に、現在お借入はありますか？",
            "filed_value": CODE_CONFIGS["p_application_headers.curr_borrowing_status"].get(
                data["p_application_headers"]["curr_borrowing_status"], ""
            ),
        }
    )
    for p_borrowing in data["p_borrowings"]:
        json_data.append(
            {
                "step": f"STEP {get_step_code(8)}：現在のお借入状況",
                "big_class": "借入名義人",
                "class": "",
                "field_name": "借入名義人",
                "filed_value": CODE_CONFIGS["p_borrowings.borrower"].get(p_borrowing["borrower"], ""),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(8)}：現在のお借入状況",
                "big_class": "お借入の種類は？",
                "class": "",
                "field_name": "借入分類",
                "filed_value": CODE_CONFIGS["p_borrowings.type"].get(p_borrowing["type"], ""),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(8)}：現在のお借入状況",
                "big_class": "返済予定表・利用明細等の画像をアップロードするか",
                "class": "",
                "field_name": "返済予定表・利用明細等の画像をアップロードするか",
                "filed_value": ", ".join([item["name"] for item in p_borrowing["I"]]),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(8)}：現在のお借入状況",
                "big_class": "借入先（金融機関）",
                "class": "",
                "field_name": "借入先（金融機関）",
                "filed_value": p_borrowing["lender"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(8)}：現在のお借入状況",
                "big_class": "住宅金融支援機構からの借入ですか？",
                "class": "",
                "field_name": "住宅金融支援機構からの借入ですか？",
                "filed_value": CODE_CONFIGS["p_borrowings.borrowing_from_house_finance_agency"].get(
                    p_borrowing["borrowing_from_house_finance_agency"], ""
                ),
            }
        )
        if p_borrowing["type"] != "4":
            json_data.append(
                {
                    "step": f"STEP {get_step_code(8)}：現在のお借入状況",
                    "big_class": "お借入の目的",
                    "class": "",
                    "field_name": "お借入の目的",
                    "filed_value": CODE_CONFIGS["p_borrowings.loan_purpose"].get(p_borrowing["loan_purpose"], ""),
                }
            )
            json_data.append(
                {
                    "step": f"STEP {get_step_code(8)}：現在のお借入状況",
                    "big_class": "お借入の目的",
                    "class": "その他の方は詳細を入力ください。",
                    "field_name": "資金使途（その他）",
                    "filed_value": p_borrowing["loan_purpose_other"],
                }
            )

        if p_borrowing["type"] == "4":
            json_data.append(
                {
                    "step": f"STEP {get_step_code(8)}：現在のお借入状況",
                    "big_class": "お借入の目的",
                    "class": "",
                    "field_name": "お借入の目的",
                    "filed_value": CODE_CONFIGS["p_borrowings.loan_business_target"].get(
                        p_borrowing["loan_business_target"], ""
                    ),
                }
            )
            json_data.append(
                {
                    "step": f"STEP {get_step_code(8)}：現在のお借入状況",
                    "big_class": "お借入の目的",
                    "class": "その他の方は詳細を入力ください。",
                    "field_name": "資金使途（その他）",
                    "filed_value": p_borrowing["loan_business_target_other"],
                }
            )
        json_data.append(
            {
                "step": f"STEP {get_step_code(8)}：現在のお借入状況",
                "big_class": "借入区分",
                "class": "",
                "field_name": "借入区分",
                "filed_value": CODE_CONFIGS["p_borrowings.category"].get(p_borrowing["category"], ""),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(8)}：現在のお借入状況",
                "big_class": "当初カード契約年月当初借入年月",
                "class": "",
                "field_name": "当初借入日／カード契約年",
                "filed_value": format_js_date_ym(p_borrowing["loan_start_date"]),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(8)}：現在のお借入状況",
                "big_class": "借入限度額当初借入額",
                "class": "",
                "field_name": "借入限度額／当初借入額",
                "filed_value": format_ja_numeric(p_borrowing["loan_amount"], "万円"),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(8)}：現在のお借入状況",
                "big_class": "現在の残高",
                "class": "",
                "field_name": "現在の残高",
                "filed_value": format_ja_numeric(p_borrowing["curr_loan_balance_amount"], "万円"),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(8)}：現在のお借入状況",
                "big_class": "年間返済額",
                "class": "",
                "field_name": "年間返済額",
                "filed_value": format_ja_numeric(p_borrowing["annual_repayment_amount"], "万円"),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(8)}：現在のお借入状況",
                "big_class": "カード有効期限",
                "class": "",
                "field_name": "カード有効期限",
                "filed_value": format_js_date_ym(p_borrowing["card_expiry_date"]),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(8)}：現在のお借入状況",
                "big_class": "今回のお借入までに完済の予定はありますか？",
                "class": "",
                "field_name": "今回のお借入までに完済の予定はありますか？",
                "filed_value": CODE_CONFIGS["p_borrowings.scheduled_loan_payoff"].get(
                    p_borrowing["scheduled_loan_payoff"], ""
                ),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(8)}：現在のお借入状況",
                "big_class": "完済（予定）年月最終期限最終返済年月",
                "class": "",
                "field_name": "最終期限／最終返済年月",
                "filed_value": format_js_date_ym(p_borrowing["loan_end_date"]),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(8)}：現在のお借入状況",
                "big_class": "完済（予定）年月",
                "class": "",
                "field_name": "完済（予定）年月",
                "filed_value": format_js_date_ym(p_borrowing["scheduled_loan_payoff_date"]),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(8)}：現在のお借入状況",
                "big_class": "賃貸戸（室）数",
                "class": "",
                "field_name": "賃貸戸（室）数",
                "filed_value": format_ja_numeric(p_borrowing["rental_room_num"], "戸（室）"),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(8)}：現在のお借入状況",
                "big_class": "共同住宅",
                "class": "",
                "field_name": "共同住宅",
                "filed_value": CODE_CONFIGS["p_borrowings.common_housing"].get(p_borrowing["common_housing"], ""),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(8)}：現在のお借入状況",
                "big_class": "不動産担保設定",
                "class": "",
                "field_name": "不動産担保設定",
                "filed_value": CODE_CONFIGS["p_borrowings.estate_setting"].get(p_borrowing["estate_setting"], ""),
            }
        )

    if is_mcj:
        json_data.append(
            {
                "step": f"STEP {get_step_code(8)}：現在のお借入状況",
                "big_class": "完済予定のお借入がある場合の完済原資について教えてください。（MCJ固有項目）",
                "class": "完済原資の種類",
                "field_name": "完済原資",
                "filed_value": ", ".join(
                    [
                        CODE_CONFIGS["p_application_headers.refund_source_type"].get(item, "")
                        for item in data["p_application_headers"]["refund_source_type"]
                    ]
                ),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(8)}：現在のお借入状況",
                "big_class": "",
                "class": "その他の方は詳細を入力ください。",
                "field_name": "完済原資（その他）",
                "filed_value": data["p_application_headers"]["refund_source_type_other"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(8)}：現在のお借入状況",
                "big_class": "",
                "class": "完済原資の内容 ※金融機関・預貯金種類など",
                "field_name": "完済原資　内容",
                "filed_value": data["p_application_headers"]["refund_source_content"],
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(8)}：現在のお借入状況",
                "big_class": "",
                "class": "完済原資の金額 ※金融機関・預貯金種類など",
                "field_name": "完済原資　金額",
                "filed_value": format_ja_numeric(data["p_application_headers"]["refund_source_amount"], "万円"),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(8)}：現在のお借入状況",
                "big_class": "今回の住宅取得後も継続する支払地代・支払家賃があれば記入してください。（MCJ固有項目）",
                "class": "支払地代",
                "field_name": "支払いをしている方",
                "filed_value": CODE_CONFIGS["p_application_headers.rent_to_be_paid_land_borrower"].get(
                    data["p_application_headers"]["rent_to_be_paid_land_borrower"], ""
                ),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(8)}：現在のお借入状況",
                "big_class": "",
                "class": "支払地代",
                "field_name": "月間の支払金額",
                "filed_value": format_ja_numeric(data["p_application_headers"]["rent_to_be_paid_land"], "円"),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(8)}：現在のお借入状況",
                "big_class": "",
                "class": "支払家賃",
                "field_name": "支払いをしている方",
                "filed_value": CODE_CONFIGS["p_application_headers.rent_to_be_paid_house_borrower"].get(
                    data["p_application_headers"]["rent_to_be_paid_house_borrower"], ""
                ),
            }
        )
        json_data.append(
            {
                "step": f"STEP {get_step_code(8)}：現在のお借入状況",
                "big_class": "",
                "class": "支払家賃",
                "field_name": "月間の支払金額",
                "filed_value": format_ja_numeric(data["p_application_headers"]["rent_to_be_paid_house"], "円"),
            }
        )
    # step09
    json_data.append(
        {
            "step": f"STEP {get_step_code(9)}：資金計画について",
            "big_class": "必要資金",
            "class": "物件価格建物マンション価格",
            "field_name": "必要資金内訳　物件価格／マンション価格",
            "filed_value": format_ja_numeric(data["p_application_headers"]["required_funds_house_amount"], "万円"),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(9)}：資金計画について",
            "big_class": "",
            "class": "諸費用等",
            "field_name": "必要資金内訳　諸費用等",
            "filed_value": format_ja_numeric(data["p_application_headers"]["required_funds_additional_amount"], "万円"),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(9)}：資金計画について",
            "big_class": "",
            "class": "住宅ローンプラス利用",
            "field_name": "必要資金内訳　住宅ローンプラス利用",
            "filed_value": format_ja_numeric(data["p_application_headers"]["required_funds_loan_plus_amount"], "万円"),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(9)}：資金計画について",
            "big_class": "",
            "class": "土地",
            "field_name": "必要資金内訳　土地",
            "filed_value": format_ja_numeric(data["p_application_headers"]["required_funds_land_amount"], "万円"),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(9)}：資金計画について",
            "big_class": "",
            "class": "付帯設備",
            "field_name": "必要資金内訳　付帯設備",
            "filed_value": format_ja_numeric(data["p_application_headers"]["required_funds_accessory_amount"], "万円"),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(9)}：資金計画について",
            "big_class": "",
            "class": "借換対象ローン残債",
            "field_name": "必要資金内訳　借換対象ローン残債",
            "filed_value": format_ja_numeric(
                data["p_application_headers"]["required_funds_refinance_loan_balance"], "万円"
            ),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(9)}：資金計画について",
            "big_class": "",
            "class": "増改築費",
            "field_name": "必要資金内訳　増改築",
            "filed_value": format_ja_numeric(data["p_application_headers"]["required_funds_upgrade_amount"], "万円"),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(9)}：資金計画について",
            "big_class": "",
            "class": "必要資金　合計",
            "field_name": "必要資金　合計",
            "filed_value": format_ja_numeric(data["p_application_headers"]["required_funds_total_amount"], "万円"),
        }
    )

    json_data.append(
        {
            "step": f"STEP {get_step_code(9)}：資金計画について",
            "big_class": "調達資金",
            "class": "預貯金",
            "field_name": "調達資金内訳　預貯金(金融機関1)",
            "filed_value": format_ja_numeric(data["p_application_headers"]["funding_saving_amount"], "万円"),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(9)}：資金計画について",
            "big_class": "",
            "class": "不動産売却代金",
            "field_name": "調達資金内訳　不動産売却代金",
            "filed_value": format_ja_numeric(data["p_application_headers"]["funding_estate_sale_amount"], "万円"),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(9)}：資金計画について",
            "big_class": "",
            "class": "有価証券売却など",
            "field_name": "調達資金内訳　有価証券売却など",
            "filed_value": format_ja_numeric(data["p_application_headers"]["funding_other_saving_amount"], "万円"),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(9)}：資金計画について",
            "big_class": "",
            "class": "親族からの贈与",
            "field_name": "調達資金内訳　親族からの贈与",
            "filed_value": format_ja_numeric(data["p_application_headers"]["funding_relative_donation_amount"], "万円"),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(9)}：資金計画について",
            "big_class": "",
            "class": "本件ローン",
            "field_name": "調達資金内訳　本件ローン",
            "filed_value": format_ja_numeric(data["p_application_headers"]["funding_loan_amount"], "万円"),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(9)}：資金計画について",
            "big_class": "",
            "class": "ペアローン",
            "field_name": "調達資金内訳　ペアローン",
            "filed_value": format_ja_numeric(data["p_application_headers"]["funding_pair_loan_amount"], "万円"),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(9)}：資金計画について",
            "big_class": "",
            "class": "その他",
            "field_name": "調達資金内訳　その他額",
            "filed_value": format_ja_numeric(data["p_application_headers"]["funding_other_amount"], "万円"),
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(9)}：資金計画について",
            "big_class": "",
            "class": "",
            "field_name": "調達資金内訳　その他額（明細）",
            "filed_value": data["p_application_headers"]["funding_other_amount_detail"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(9)}：資金計画について",
            "big_class": "",
            "class": "調達資金　合計",
            "field_name": "調達資金　合計",
            "filed_value": format_ja_numeric(data["p_application_headers"]["funding_total_amount"], "万円"),
        }
    )
    # step10
    json_data.append(
        {
            "step": f"STEP {get_step_code(10)}：書類添付",
            "big_class": "本人確認書類",
            "class": "",
            "field_name": "本人確認書類",
            "filed_value": CODE_CONFIGS["p_applicant_persons__0.identity_verification_type"].get(
                data["p_applicant_persons__0"]["identity_verification_type"], ""
            ),
        }
    )

    if data["p_applicant_persons__0"]["A__01__a"]:
        json_data.append(
            {
                "step": f"STEP {get_step_code(10)}：書類添付",
                "big_class": "運転免許証〈表面〉",
                "class": "",
                "field_name": "運転免許証〈表面〉",
                "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__0"]["A__01__a"]]),
            }
        )
    if data["p_applicant_persons__0"]["A__01__b"]:
        json_data.append(
            {
                "step": f"STEP {get_step_code(10)}：書類添付",
                "big_class": "運転免許証〈裏面〉",
                "class": "",
                "field_name": "運転免許証〈裏面〉",
                "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__0"]["A__01__b"]]),
            }
        )
    if data["p_applicant_persons__0"]["A__02"]:
        json_data.append(
            {
                "step": f"STEP {get_step_code(10)}：書類添付",
                "big_class": "マイナンバーカード",
                "class": "",
                "field_name": "マイナンバーカード",
                "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__0"]["A__02"]]),
            }
        )
    if data["p_applicant_persons__0"]["A__03__a"]:
        json_data.append(
            {
                "step": f"STEP {get_step_code(10)}：書類添付",
                "big_class": "住民基本台帳カード（顔写真付き）〈表面〉",
                "class": "",
                "field_name": "住民基本台帳カード（顔写真付き）〈表面〉",
                "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__0"]["A__03__a"]]),
            }
        )
    if data["p_applicant_persons__0"]["A__03__b"]:
        json_data.append(
            {
                "step": f"STEP {get_step_code(10)}：書類添付",
                "big_class": "住民基本台帳カード（顔写真付き）〈裏面〉",
                "class": "",
                "field_name": "住民基本台帳カード（顔写真付き）〈裏面〉",
                "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__0"]["A__03__b"]]),
            }
        )
    if data["p_applicant_persons__0"]["B__a"]:
        json_data.append(
            {
                "step": f"STEP {get_step_code(10)}：書類添付",
                "big_class": "健康保険証〈表面〉",
                "class": "",
                "field_name": "健康保険証〈表面〉",
                "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__0"]["B__a"]]),
            }
        )
    if data["p_applicant_persons__0"]["B__b"]:
        json_data.append(
            {
                "step": f"STEP {get_step_code(10)}：書類添付",
                "big_class": "健康保険証〈裏面〉",
                "class": "",
                "field_name": "健康保険証〈裏面〉",
                "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__0"]["B__b"]]),
            }
        )
    if data["p_applicant_persons__0"]["C__01"]:
        json_data.append(
            {
                "step": f"STEP {get_step_code(10)}：書類添付",
                "big_class": "収入に関する書類",
                "class": "",
                "field_name": "源泉徴収票（前年度分）",
                "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__0"]["C__01"]]),
            }
        )
    if data["p_applicant_persons__0"]["C__02"]:
        json_data.append(
            {
                "step": f"STEP {get_step_code(10)}：書類添付",
                "big_class": "",
                "class": "",
                "field_name": "源泉徴収票（前々年度分）",
                "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__0"]["C__02"]]),
            }
        )
    if data["p_applicant_persons__0"]["C__03"]:
        json_data.append(
            {
                "step": f"STEP {get_step_code(10)}：書類添付",
                "big_class": "収入に関する書類",
                "class": "",
                "field_name": "確定申告書（1期前）",
                "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__0"]["C__03"]]),
            }
        )
    if data["p_applicant_persons__0"]["C__04"]:
        json_data.append(
            {
                "step": f"STEP {get_step_code(10)}：書類添付",
                "big_class": "",
                "class": "",
                "field_name": "確定申告書（2期前）",
                "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__0"]["C__04"]]),
            }
        )
    if data["p_applicant_persons__0"]["C__05"]:
        json_data.append(
            {
                "step": f"STEP {get_step_code(10)}：書類添付",
                "big_class": "",
                "class": "",
                "field_name": "確定申告書（3期前）",
                "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__0"]["C__05"]]),
            }
        )
    if data["p_applicant_persons__0"]["D__01"]:
        json_data.append(
            {
                "step": f"STEP {get_step_code(10)}：書類添付",
                "big_class": "非上場企業の役員の方は下記の書類も添付してください。",
                "class": "",
                "field_name": "会社の決算報告書（1期前）",
                "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__0"]["D__01"]]),
            }
        )
    if data["p_applicant_persons__0"]["D__02"]:
        json_data.append(
            {
                "step": f"STEP {get_step_code(10)}：書類添付",
                "big_class": "",
                "class": "",
                "field_name": "会社の決算報告書（2期前）",
                "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__0"]["D__02"]]),
            }
        )
    if data["p_applicant_persons__0"]["D__03"]:
        json_data.append(
            {
                "step": f"STEP {get_step_code(10)}：書類添付",
                "big_class": "",
                "class": "",
                "field_name": "会社の決算報告書（3期前）",
                "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__0"]["D__03"]]),
            }
        )
    if data["p_applicant_persons__0"]["E"]:
        json_data.append(
            {
                "step": f"STEP {get_step_code(10)}：書類添付",
                "big_class": "雇用契約に関する書類",
                "class": "",
                "field_name": "雇用契約書",
                "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__0"]["E"]]),
            }
        )
    if data["p_applicant_persons__0"]["F__01"]:
        json_data.append(
            {
                "step": f"STEP {get_step_code(10)}：書類添付",
                "big_class": "親族経営の会社等にご勤務の方は下記の書類も添付してください。",
                "class": "",
                "field_name": "会社の決算報告書または経営する親族の確定申告書（1期前）",
                "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__0"]["F__01"]]),
            }
        )
    if data["p_applicant_persons__0"]["F__02"]:
        json_data.append(
            {
                "step": f"STEP {get_step_code(10)}：書類添付",
                "big_class": "",
                "class": "",
                "field_name": "会社の決算報告書または経営する親族の確定申告書（2期前）",
                "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__0"]["F__02"]]),
            }
        )
    if data["p_applicant_persons__0"]["F__03"]:
        json_data.append(
            {
                "step": f"STEP {get_step_code(10)}：書類添付",
                "big_class": "",
                "class": "",
                "field_name": "会社の決算報告書または経営する親族の確定申告書（3期前）",
                "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__0"]["F__03"]]),
            }
        )
    if data["p_applicant_persons__0"]["K"]:
        json_data.append(
            {
                "step": f"STEP {get_step_code(10)}：書類添付",
                "big_class": "その他の書類",
                "class": "",
                "field_name": "その他の書類",
                "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__0"]["K"]]),
            }
        )

    # step11
    if data["p_application_headers"]["loan_type"] in ["3", "4"]:
        json_data.append(
            {
                "step": f"STEP {get_step_code(11)}：収入合算者の書類",
                "big_class": "本人確認書類",
                "class": "",
                "field_name": "本人確認書類",
                "filed_value": CODE_CONFIGS["p_applicant_persons__1.identity_verification_type"].get(
                    data["p_applicant_persons__1"]["identity_verification_type"], ""
                ),
            }
        )

        if data["p_applicant_persons__1"]["A__01__a"]:
            json_data.append(
                {
                    "step": f"STEP {get_step_code(11)}：収入合算者の書類",
                    "big_class": "運転免許証〈表面〉",
                    "class": "",
                    "field_name": "運転免許証〈表面〉",
                    "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__1"]["A__01__a"]]),
                }
            )
        if data["p_applicant_persons__1"]["A__01__b"]:
            json_data.append(
                {
                    "step": f"STEP {get_step_code(11)}：収入合算者の書類",
                    "big_class": "運転免許証〈裏面〉",
                    "class": "",
                    "field_name": "運転免許証〈裏面〉",
                    "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__1"]["A__01__b"]]),
                }
            )
        if data["p_applicant_persons__1"]["A__02"]:
            json_data.append(
                {
                    "step": f"STEP {get_step_code(11)}：収入合算者の書類",
                    "big_class": "マイナンバーカード",
                    "class": "",
                    "field_name": "マイナンバーカード",
                    "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__1"]["A__02"]]),
                }
            )
        if data["p_applicant_persons__1"]["A__03__a"]:
            json_data.append(
                {
                    "step": f"STEP {get_step_code(11)}：収入合算者の書類",
                    "big_class": "住民基本台帳カード（顔写真付き）〈表面〉",
                    "class": "",
                    "field_name": "住民基本台帳カード（顔写真付き）〈表面〉",
                    "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__1"]["A__03__a"]]),
                }
            )
        if data["p_applicant_persons__1"]["A__03__b"]:
            json_data.append(
                {
                    "step": f"STEP {get_step_code(11)}：収入合算者の書類",
                    "big_class": "住民基本台帳カード（顔写真付き）〈裏面〉",
                    "class": "",
                    "field_name": "住民基本台帳カード（顔写真付き）〈裏面〉",
                    "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__1"]["A__03__b"]]),
                }
            )
        if data["p_applicant_persons__1"]["B__a"]:
            json_data.append(
                {
                    "step": f"STEP {get_step_code(11)}：収入合算者の書類",
                    "big_class": "健康保険証〈表面〉",
                    "class": "",
                    "field_name": "健康保険証〈表面〉",
                    "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__1"]["B__a"]]),
                }
            )
        if data["p_applicant_persons__1"]["B__b"]:
            json_data.append(
                {
                    "step": f"STEP {get_step_code(11)}：収入合算者の書類",
                    "big_class": "健康保険証〈裏面〉",
                    "class": "",
                    "field_name": "健康保険証〈裏面〉",
                    "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__1"]["B__b"]]),
                }
            )
        if data["p_applicant_persons__1"]["C__01"]:
            json_data.append(
                {
                    "step": f"STEP {get_step_code(11)}：収入合算者の書類",
                    "big_class": "収入に関する書類",
                    "class": "",
                    "field_name": "源泉徴収票（前年度分）",
                    "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__1"]["C__01"]]),
                }
            )
        if data["p_applicant_persons__1"]["C__02"]:
            json_data.append(
                {
                    "step": f"STEP {get_step_code(11)}：収入合算者の書類",
                    "big_class": "",
                    "class": "",
                    "field_name": "源泉徴収票（前々年度分）",
                    "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__1"]["C__02"]]),
                }
            )
        if data["p_applicant_persons__1"]["C__03"]:
            json_data.append(
                {
                    "step": f"STEP {get_step_code(11)}：収入合算者の書類",
                    "big_class": "収入に関する書類",
                    "class": "",
                    "field_name": "確定申告書（1期前）",
                    "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__1"]["C__03"]]),
                }
            )
        if data["p_applicant_persons__1"]["C__04"]:
            json_data.append(
                {
                    "step": f"STEP {get_step_code(11)}：収入合算者の書類",
                    "big_class": "",
                    "class": "",
                    "field_name": "確定申告書（2期前）",
                    "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__1"]["C__04"]]),
                }
            )
        if data["p_applicant_persons__1"]["C__05"]:
            json_data.append(
                {
                    "step": f"STEP {get_step_code(11)}：収入合算者の書類",
                    "big_class": "",
                    "class": "",
                    "field_name": "確定申告書（3期前）",
                    "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__1"]["C__05"]]),
                }
            )
        if data["p_applicant_persons__1"]["D__01"]:
            json_data.append(
                {
                    "step": f"STEP {get_step_code(11)}：収入合算者の書類",
                    "big_class": "非上場企業の役員の方は下記の書類も添付してください。",
                    "class": "",
                    "field_name": "会社の決算報告書（1期前）",
                    "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__1"]["D__01"]]),
                }
            )
        if data["p_applicant_persons__1"]["D__02"]:
            json_data.append(
                {
                    "step": f"STEP {get_step_code(11)}：収入合算者の書類",
                    "big_class": "",
                    "class": "",
                    "field_name": "会社の決算報告書（2期前）",
                    "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__1"]["D__02"]]),
                }
            )
        if data["p_applicant_persons__1"]["D__03"]:
            json_data.append(
                {
                    "step": f"STEP {get_step_code(11)}：収入合算者の書類",
                    "big_class": "",
                    "class": "",
                    "field_name": "会社の決算報告書（3期前）",
                    "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__1"]["D__03"]]),
                }
            )
        if data["p_applicant_persons__1"]["E"]:
            json_data.append(
                {
                    "step": f"STEP {get_step_code(11)}：収入合算者の書類",
                    "big_class": "雇用契約に関する書類",
                    "class": "",
                    "field_name": "雇用契約書",
                    "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__1"]["E"]]),
                }
            )
        if data["p_applicant_persons__1"]["F__01"]:
            json_data.append(
                {
                    "step": f"STEP {get_step_code(11)}：収入合算者の書類",
                    "big_class": "親族経営の会社等にご勤務の方は下記の書類も添付してください。",
                    "class": "",
                    "field_name": "会社の決算報告書または経営する親族の確定申告書（1期前）",
                    "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__1"]["F__01"]]),
                }
            )
        if data["p_applicant_persons__1"]["F__02"]:
            json_data.append(
                {
                    "step": f"STEP {get_step_code(11)}：収入合算者の書類",
                    "big_class": "",
                    "class": "",
                    "field_name": "会社の決算報告書または経営する親族の確定申告書（2期前）",
                    "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__1"]["F__02"]]),
                }
            )
        if data["p_applicant_persons__1"]["F__03"]:
            json_data.append(
                {
                    "step": f"STEP {get_step_code(11)}：収入合算者の書類",
                    "big_class": "",
                    "class": "",
                    "field_name": "会社の決算報告書または経営する親族の確定申告書（3期前）",
                    "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__1"]["F__03"]]),
                }
            )
        if data["p_applicant_persons__1"]["K"]:
            json_data.append(
                {
                    "step": f"STEP {get_step_code(11)}：収入合算者の書類",
                    "big_class": "その他の書類",
                    "class": "",
                    "field_name": "その他の書類",
                    "filed_value": ", ".join([item["name"] for item in data["p_applicant_persons__1"]["K"]]),
                }
            )

    # step12
    json_data.append(
        {
            "step": f"STEP {get_step_code(12)}：担当者情報",
            "big_class": "担当者の名刺はありますか？※名刺添付で入力を省略できます",
            "class": "",
            "field_name": "提携会社の担当者名刺",
            "filed_value": ", ".join([item["name"] for item in data["p_application_headers"]["J"]]),
        }
    )
    target = list(filter(lambda x: x["id"] == data["p_application_headers"]["sales_company_id"], orgs))
    json_data.append(
        {
            "step": f"STEP {get_step_code(12)}：担当者情報",
            "big_class": "提携会社（不動産会社・住宅メーカー等）",
            "class": "",
            "field_name": "提携会社（不動産会社・住宅メーカー等）",
            "filed_value": target[0]["name"] if target else "",
        }
    )
    target = list(filter(lambda x: x["id"] == data["p_application_headers"]["sales_area_id"], orgs))
    json_data.append(
        {
            "step": f"STEP {get_step_code(12)}：担当者情報",
            "big_class": "エリア",
            "class": "",
            "field_name": "エリア",
            "filed_value": target[0]["name"] if target else "",
        }
    )
    target = list(filter(lambda x: x["id"] == data["p_application_headers"]["sales_exhibition_hall_id"], orgs))
    json_data.append(
        {
            "step": f"STEP {get_step_code(12)}：担当者情報",
            "big_class": "展示場",
            "class": "",
            "field_name": "展示場",
            "filed_value": target[0]["name"] if target else "",
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(12)}：担当者情報",
            "big_class": "担当者名",
            "class": "",
            "field_name": "担当者名",
            "filed_value": data["p_application_headers"]["vendor_name"],
        }
    )
    json_data.append(
        {
            "step": f"STEP {get_step_code(12)}：担当者情報",
            "big_class": "携帯電話番号",
            "class": "",
            "field_name": "携帯電話番号",
            "filed_value": data["p_application_headers"]["vendor_phone"],
        }
    )

    df = pd.DataFrame(
        json_data,
    )
    excel_buffer = BytesIO()

    df.to_excel(excel_buffer, header=False, index=False)
    excel_buffer.seek(0)

    upload_buffer_to_s3(f"{p_application_header_id}/row_data.xlsx", excel_buffer)
