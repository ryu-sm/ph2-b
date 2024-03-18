import re


def manager_data_check(data: dict):
    errors = []
    mcj_id = ""

    # お借入のご希望
    tab1_errors = []

    if not data["p_application_headers"]["loan_target"]:
        tab1_errors.append("お借入の目的")

    if data["p_application_headers"]["loan_target"] and not data["p_application_headers"]["land_advance_plan"]:
        tab1_errors.append("「土地先行プラン」を希望ですか？")

    if not data["p_application_headers"]["loan_type"]:
        tab1_errors.append("お借入形態")

    if data["p_application_headers"]["loan_type"] == "2":
        if not data["p_application_headers"]["pair_loan_last_name"]:
            tab1_errors.append("ペアローン　お名前（姓）")
        if not data["p_application_headers"]["pair_loan_first_name"]:
            tab1_errors.append("ペアローン　お名前（名）")
        if not data["p_application_headers"]["pair_loan_rel"]:
            tab1_errors.append("ペアローン　続柄")
    if not data["p_borrowing_details__1"]["desired_borrowing_date"]:
        tab1_errors.append("お借入希望日")

    if not data["p_borrowing_details__1"]["desired_loan_amount"]:
        tab1_errors.append("お借入希望額")

    if (
        data["p_borrowing_details__1"]["bonus_repayment_amount"]
        and not data["p_borrowing_details__1"]["bonus_repayment_month"]
    ):
        tab1_errors.append("ボーナス返済月")

    if (
        data["p_borrowing_details__1"]["bonus_repayment_month"]
        and not data["p_borrowing_details__1"]["bonus_repayment_amount"]
    ):
        tab1_errors.append("お借入内容　うち、ボーナス返済分")

    if not data["p_borrowing_details__1"]["loan_term_year"]:
        tab1_errors.append("お借入内容　お借入期間（年）")

    if not data["p_borrowing_details__1"]["repayment_method"]:
        tab1_errors.append("お借入内容　返済方法")

    if data["p_application_headers"]["land_advance_plan"] == "1":
        if not data["p_borrowing_details__2"]["desired_borrowing_date"]:
            tab1_errors.append("お借入希望日（2回目融資）")

        if not data["p_borrowing_details__2"]["desired_loan_amount"]:
            tab1_errors.append("お借入希望額（2回目融資）")

    # あなたの情報
    tab2_errors = []

    if (
        not data["p_applicant_persons__0"]["last_name_kanji"]
        or len(data["p_applicant_persons__0"]["last_name_kanji"]) > 48
    ):
        tab2_errors.append("お名前（姓）")

    if (
        not data["p_applicant_persons__0"]["first_name_kanji"]
        or len(data["p_applicant_persons__0"]["first_name_kanji"]) > 48
    ):
        tab2_errors.append("お名前（名）")

    if (
        not data["p_applicant_persons__0"]["last_name_kana"]
        or len(data["p_applicant_persons__0"]["last_name_kana"]) > 48
    ):
        tab2_errors.append("お名前（姓）（フリガナ）")

    if (
        not data["p_applicant_persons__0"]["first_name_kana"]
        or len(data["p_applicant_persons__0"]["first_name_kana"]) > 48
    ):
        tab2_errors.append("お名前（名）（フリガナ）")

    if not data["p_applicant_persons__0"]["gender"]:
        tab2_errors.append("性別")

    if not data["p_applicant_persons__0"]["birthday"]:
        tab2_errors.append("生年月日")

    if not data["p_applicant_persons__0"]["mobile_phone"] and not data["p_applicant_persons__0"]["home_phone"]:
        tab2_errors.append("電話番号携帯")
        tab2_errors.append("電話番号自宅")
    if data["p_applicant_persons__0"]["mobile_phone"]:
        result = re.fullmatch(r"^(090|080|070)-\d{4}-\d{4}$", data["p_applicant_persons__0"]["mobile_phone"])
        if not result:
            tab2_errors.append("電話番号携帯")
    if data["p_applicant_persons__0"]["home_phone"]:
        result = re.fullmatch(
            r"^0([0-9]-[0-9]{4}|[0-9]{2}-[0-9]{3}|[0-9]{3}-[0-9]{2}|[0-9]{4}-[0-9])-[0-9]{4}$",
            data["p_applicant_persons__0"]["mobile_phone"],
        )
        if not result:
            tab2_errors.append("電話番号自宅")
    if data["p_applicant_persons__0"]["emergency_contact"]:
        result = re.fullmatch(
            r"^0([0-9]-[0-9]{4}|[0-9]{2}-[0-9]{3}|[0-9]{3}-[0-9]{2}|[0-9]{4}-[0-9])-[0-9]{4}$|^(090|080|070)-\d{4}-\d{4}$",
            data["p_applicant_persons__0"]["emergency_contact"],
        )
        if not result:
            tab2_errors.append("緊急連絡先")
