import re

from schemas.regex import REGEX


def manager_data_check(data: dict):
    errors = {}

    mcj_id = "100730412732514738"

    # お借入のご希望
    tab1_errors = []

    if not data["p_application_headers"]["loan_target"]:
        tab1_errors.append("お借入の目的")

    if data["p_application_headers"]["loan_target"] == "6" and not data["p_application_headers"]["land_advance_plan"]:
        tab1_errors.append("「土地先行プラン」を希望ですか？")

    if not data["p_application_headers"]["loan_type"]:
        tab1_errors.append("お借入形態")

    if data["p_application_headers"]["loan_type"] == "2":
        if not data["p_application_headers"]["pair_loan_last_name"]:
            tab1_errors.append("ペアローン　お名前（姓）")
        if not data["p_application_headers"]["pair_loan_first_name"]:
            tab1_errors.append("ペアローン　お名前（名）")
        if not data["p_application_headers"]["pair_loan_rel"]:
            tab1_errors.append("ペアローン　続柄（プルダウン）")
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
        data["p_borrowing_details__1"]["bonus_repayment_month"] != "1"
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
    if tab1_errors:
        errors["お借入のご希望"] = tab1_errors
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
        result = re.fullmatch(REGEX["mobile_phone"], data["p_applicant_persons__0"]["mobile_phone"])
        if not result:
            tab2_errors.append("電話番号携帯")
    if data["p_applicant_persons__0"]["home_phone"]:
        result = re.fullmatch(REGEX["home_phone"], data["p_applicant_persons__0"]["home_phone"])
        if not result:
            tab2_errors.append("電話番号自宅")
    if data["p_applicant_persons__0"]["emergency_contact"]:
        result = re.fullmatch(REGEX["emergency_contact"], data["p_applicant_persons__0"]["emergency_contact"])
        if not result:
            tab2_errors.append("緊急連絡先")

    if data["p_applicant_persons__0"]["postal_code"]:
        result = re.fullmatch(REGEX["postal_code"], data["p_applicant_persons__0"]["postal_code"])
        if not result:
            tab2_errors.append("郵便番号")

    if not data["p_applicant_persons__0"]["prefecture_kanji"]:
        tab2_errors.append("都道府県")

    if (
        data["p_applicant_persons__0"]["prefecture_kanji"]
        and len(data["p_applicant_persons__0"]["prefecture_kanji"]) > 8
    ):
        tab2_errors.append("都道府県")

    if not data["p_applicant_persons__0"]["city_kanji"]:
        tab2_errors.append("市区郡")

    if data["p_applicant_persons__0"]["city_kanji"] and len(data["p_applicant_persons__0"]["city_kanji"]) > 20:
        tab2_errors.append("市区郡")

    if not data["p_applicant_persons__0"]["district_kanji"]:
        tab2_errors.append("町村丁目")

    if data["p_applicant_persons__0"]["district_kanji"] and len(data["p_applicant_persons__0"]["district_kanji"]) > 40:
        tab2_errors.append("町村丁目")

    if not data["p_applicant_persons__0"]["other_address_kanji"]:
        tab2_errors.append("丁目以下・建物名・部屋番号")

    if (
        data["p_applicant_persons__0"]["other_address_kanji"]
        and len(data["p_applicant_persons__0"]["other_address_kanji"]) > 99
    ):
        tab2_errors.append("丁目以下・建物名・部屋番号")

    if not data["p_applicant_persons__0"]["prefecture_kana"]:
        tab2_errors.append("都道府県（フリガナ）")

    if data["p_applicant_persons__0"]["prefecture_kana"] and len(data["p_applicant_persons__0"]["prefecture_kana"]) > 8:
        tab2_errors.append("都道府県（フリガナ）")

    if not data["p_applicant_persons__0"]["city_kana"]:
        tab2_errors.append("市区郡（フリガナ）")

    if data["p_applicant_persons__0"]["city_kana"] and len(data["p_applicant_persons__0"]["city_kana"]) > 20:
        tab2_errors.append("市区郡（フリガナ）")

    if not data["p_applicant_persons__0"]["district_kana"]:
        tab2_errors.append("町村丁目（フリガナ）")

    if data["p_applicant_persons__0"]["district_kana"] and len(data["p_applicant_persons__0"]["district_kana"]) > 30:
        tab2_errors.append("町村丁目（フリガナ）")

    if not data["p_applicant_persons__0"]["other_address_kana"]:
        tab2_errors.append("丁目以下・建物名・部屋番号（フリガナ）")

    if (
        data["p_applicant_persons__0"]["other_address_kana"]
        and len(data["p_applicant_persons__0"]["other_address_kana"]) > 138
    ):
        tab2_errors.append("丁目以下・建物名・部屋番号（フリガナ）")

    if not data["p_applicant_persons__0"]["email"]:
        tab2_errors.append("ご連絡先用メールアドレス")

    if data["p_applicant_persons__0"]["email"]:
        result = re.fullmatch(REGEX["email"], data["p_applicant_persons__0"]["email"])
        if not result:
            tab2_errors.append("ご連絡先用メールアドレス")
    if tab2_errors:
        errors["あなたの情報"] = tab2_errors
    # ご職業
    tab3_errors = []

    if not data["p_applicant_persons__0"]["office_occupation"]:
        tab3_errors.append("ご職業")
    if (
        data["p_applicant_persons__0"]["office_occupation"] == "99"
        and not data["p_applicant_persons__0"]["office_occupation_other"]
    ):
        tab3_errors.append("勤務先　職業（その他）")

    if (
        data["p_applicant_persons__0"]["office_industry"] == "99"
        and not data["p_applicant_persons__0"]["office_industry_other"]
    ):
        tab3_errors.append("勤務先　業種（その他）")

    if not data["p_applicant_persons__0"]["office_occupation"]:
        tab3_errors.append("職種")
    if (
        data["p_applicant_persons__0"]["office_occupation_detail"] == "99"
        and not data["p_applicant_persons__0"]["office_occupation_detail_other"]
    ):
        tab3_errors.append("勤務先　職種（その他）")

    if not data["p_applicant_persons__0"]["office_employment_type"]:
        tab3_errors.append("雇用形態")

    if not data["p_applicant_persons__0"]["office_name_kanji"]:
        tab3_errors.append("勤務先名")

    if (
        data["p_applicant_persons__0"]["office_name_kanji"]
        and len(data["p_applicant_persons__0"]["office_name_kanji"]) > 48
    ):
        tab3_errors.append("勤務先名")

    if not data["p_applicant_persons__0"]["office_name_kana"]:
        tab3_errors.append("勤務先名（フリガナ）")

    if (
        data["p_applicant_persons__0"]["office_name_kana"]
        and len(data["p_applicant_persons__0"]["office_name_kana"]) > 48
    ):
        tab3_errors.append("勤務先名（フリガナ）")

    if (
        data["p_applicant_persons__0"]["office_department"]
        and len(data["p_applicant_persons__0"]["office_department"]) > 46
    ):
        tab3_errors.append("所属部課")

    if not data["p_applicant_persons__0"]["office_phone"]:
        tab3_errors.append("勤務先の電話番号")

    if data["p_applicant_persons__0"]["office_phone"]:
        result = re.fullmatch(REGEX["home_phone"], data["p_applicant_persons__0"]["office_phone"])
        if not result:
            tab3_errors.append("勤務先の電話番号")

    if not data["p_applicant_persons__0"]["office_head_location"]:
        tab3_errors.append("勤務先本社所在地")

    if (
        data["p_applicant_persons__0"]["office_head_location"]
        and len(data["p_applicant_persons__0"]["office_head_location"]) > 48
    ):
        tab3_errors.append("勤務先本社所在地")

    if data["p_applicant_persons__0"]["office_establishment_date"]:
        result = re.fullmatch(REGEX["ymd"], data["p_applicant_persons__0"]["office_establishment_date"])
        if not result:
            tab3_errors.append("勤務先設立年月日")

    if not data["p_applicant_persons__0"]["office_postal_code"]:
        tab3_errors.append("郵便番号")

    if data["p_applicant_persons__0"]["office_postal_code"]:
        result = re.fullmatch(REGEX["postal_code"], data["p_applicant_persons__0"]["office_postal_code"])
        if not result:
            tab3_errors.append("郵便番号")

    if not data["p_applicant_persons__0"]["office_prefecture_kanji"]:
        tab3_errors.append("都道府県")

    if (
        data["p_applicant_persons__0"]["office_prefecture_kanji"]
        and len(data["p_applicant_persons__0"]["office_prefecture_kanji"]) > 8
    ):
        tab3_errors.append("都道府県")

    if (
        data["p_applicant_persons__0"]["office_city_kanji"]
        and len(data["p_applicant_persons__0"]["office_city_kanji"]) > 20
    ):
        tab3_errors.append("市区郡")

    if (
        data["p_applicant_persons__0"]["office_district_kanji"]
        and len(data["p_applicant_persons__0"]["office_district_kanji"]) > 40
    ):
        tab3_errors.append("町村丁目")

    if (
        data["p_applicant_persons__0"]["office_other_address_kanji"]
        and len(data["p_applicant_persons__0"]["office_other_address_kanji"]) > 99
    ):
        tab3_errors.append("丁目以下・建物名・部屋番号")

    if not data["p_applicant_persons__0"]["office_prefecture_kana"]:
        tab3_errors.append("都道府県（フリガナ）")

    if (
        data["p_applicant_persons__0"]["office_prefecture_kana"]
        and len(data["p_applicant_persons__0"]["office_prefecture_kana"]) > 8
    ):
        tab3_errors.append("都道府県（フリガナ）")

    if (
        data["p_applicant_persons__0"]["office_city_kana"]
        and len(data["p_applicant_persons__0"]["office_city_kana"]) > 20
    ):
        tab3_errors.append("市区郡（フリガナ）")

    if (
        data["p_applicant_persons__0"]["office_district_kana"]
        and len(data["p_applicant_persons__0"]["office_district_kana"]) > 30
    ):
        tab3_errors.append("町村丁目（フリガナ）")

    if (
        data["p_applicant_persons__0"]["office_other_address_kana"]
        and len(data["p_applicant_persons__0"]["office_other_address_kana"]) > 138
    ):
        tab3_errors.append("丁目以下・建物名・部屋番号（フリガナ）")

    if not data["p_applicant_persons__0"]["office_employee_num"]:
        tab3_errors.append("従業員数")

    if not data["p_applicant_persons__0"]["last_year_income"]:
        tab3_errors.append("前年度年収")

    if not data["p_applicant_persons__0"]["main_income_source"]:
        tab3_errors.append("収入源（銀行送信用）")

    if data["p_applicant_persons__0"]["tax_return"] == "1":
        if not data["p_applicant_persons__0"]["tax_return_reasons"]:
            tab3_errors.append("確定申告の理由")
        if (
            data["p_applicant_persons__0"]["tax_return_reasons"] == "99"
            and not data["p_applicant_persons__0"]["tax_return_reason_other"]
        ):
            tab3_errors.append("確定申告の理由　その他")
    if data["p_applicant_persons__0"]["transfer_office"] == "1":
        if not data["p_applicant_persons__0"]["transfer_office_name_kanji"]:
            tab3_errors.append("出向（派遣）勤務先名")
        if (
            data["p_applicant_persons__0"]["transfer_office_name_kanji"]
            and len(data["p_applicant_persons__0"]["transfer_office_name_kanji"]) > 48
        ):
            tab3_errors.append("出向（派遣）勤務先名")

        if not data["p_applicant_persons__0"]["transfer_office_name_kana"]:
            tab3_errors.append("出向（派遣）勤務先名（フリガナ）")
        if (
            data["p_applicant_persons__0"]["transfer_office_name_kana"]
            and len(data["p_applicant_persons__0"]["transfer_office_name_kana"]) > 48
        ):
            tab3_errors.append("出向（派遣）勤務先名（フリガナ）")

        if not data["p_applicant_persons__0"]["transfer_office_phone"]:
            tab3_errors.append("出向（派遣）先 電話番号")

        if data["p_applicant_persons__0"]["transfer_office_phone"]:
            result = re.fullmatch(REGEX["home_phone"], data["p_applicant_persons__0"]["transfer_office_phone"])
            if not result:
                tab3_errors.append("出向（派遣）先 電話番号")

        if not data["p_applicant_persons__0"]["transfer_office_postal_code"]:
            tab3_errors.append("出向（派遣）先 郵便番号")

        if data["p_applicant_persons__0"]["transfer_office_postal_code"]:
            result = re.fullmatch(REGEX["postal_code"], data["p_applicant_persons__0"]["transfer_office_postal_code"])
            if not result:
                tab3_errors.append("出向（派遣）先 郵便番号")

        if not data["p_applicant_persons__0"]["transfer_office_prefecture_kanji"]:
            tab3_errors.append("出向（派遣）先 都道府県")
        if (
            data["p_applicant_persons__0"]["transfer_office_prefecture_kanji"]
            and len(data["p_applicant_persons__0"]["transfer_office_prefecture_kanji"]) > 8
        ):
            tab3_errors.append("出向（派遣）先 都道府県")

        if (
            data["p_applicant_persons__0"]["transfer_office_city_kanji"]
            and len(data["p_applicant_persons__0"]["transfer_office_city_kanji"]) > 20
        ):
            tab3_errors.append("出向（派遣）先 市区郡")

        if (
            data["p_applicant_persons__0"]["transfer_office_district_kanji"]
            and len(data["p_applicant_persons__0"]["transfer_office_district_kanji"]) > 40
        ):
            tab3_errors.append("出向（派遣）先 町村丁目")

        if (
            data["p_applicant_persons__0"]["transfer_office_other_address_kanji"]
            and len(data["p_applicant_persons__0"]["transfer_office_other_address_kanji"]) > 99
        ):
            tab3_errors.append("出向（派遣）先 丁目以下・建物名・部屋番号")
    if data["p_applicant_persons__0"]["maternity_paternity_leave"]:
        if not data["p_applicant_persons__0"]["maternity_paternity_leave_start_date"]:
            tab3_errors.append("取得開始時期")

        if not data["p_applicant_persons__0"]["maternity_paternity_leave_end_date"]:
            tab3_errors.append("取得終了時期")
    if tab3_errors:
        errors["ご職業"] = tab3_errors

    # 担保提供者
    if data["p_application_headers"]["join_guarantor_umu"]:
        for index, p_join_guarantor in enumerate(data["p_join_guarantors"]):
            tab4_errors = []

            if not p_join_guarantor["last_name_kanji"]:
                tab4_errors.append("担保提供者の氏名（姓）")
            if p_join_guarantor["last_name_kanji"] and len(p_join_guarantor["last_name_kanji"]) > 48:
                tab4_errors.append("担保提供者の氏名（姓）")

            if not p_join_guarantor["first_name_kanji"]:
                tab4_errors.append("担保提供者の氏名（名）")
            if p_join_guarantor["first_name_kanji"] and len(p_join_guarantor["first_name_kanji"]) > 48:
                tab4_errors.append("担保提供者の氏名（名）")

            if not p_join_guarantor["last_name_kana"]:
                tab4_errors.append("担保提供者の氏名（姓）（フリガナ）")
            if p_join_guarantor["last_name_kana"] and len(p_join_guarantor["last_name_kana"]) > 48:
                tab4_errors.append("担保提供者の氏名（姓）（フリガナ）")

            if not p_join_guarantor["first_name_kana"]:
                tab4_errors.append("担保提供者の氏名（名）（フリガナ）")
            if p_join_guarantor["first_name_kana"] and len(p_join_guarantor["first_name_kana"]) > 48:
                tab4_errors.append("担保提供者の氏名（名）（フリガナ）")

            if not p_join_guarantor["birthday"]:
                tab4_errors.append("生年月日")

            if p_join_guarantor["birthday"]:
                result = re.fullmatch(REGEX["ymd"], p_join_guarantor["birthday"])
                if not result:
                    tab4_errors.append("生年月日")

            if not p_join_guarantor["mobile_phone"] and not p_join_guarantor["home_phone"]:
                tab4_errors.append("電話番号携帯")
                tab4_errors.append("電話番号自宅")
            if p_join_guarantor["mobile_phone"]:
                result = re.fullmatch(REGEX["mobile_phone"], p_join_guarantor["mobile_phone"])
                if not result:
                    tab4_errors.append("電話番号携帯")
            if p_join_guarantor["home_phone"]:
                result = re.fullmatch(REGEX["home_phone"], p_join_guarantor["home_phone"])
                if not result:
                    tab4_errors.append("電話番号自宅")
            if p_join_guarantor["emergency_contact"]:
                result = re.fullmatch(REGEX["emergency_contact"], p_join_guarantor["emergency_contact"])
                if not result:
                    tab4_errors.append("緊急連絡先")

            if p_join_guarantor["postal_code"]:
                result = re.fullmatch(REGEX["postal_code"], p_join_guarantor["postal_code"])
                if not result:
                    tab4_errors.append("郵便番号")

            if not p_join_guarantor["prefecture_kanji"]:
                tab4_errors.append("都道府県")

            if p_join_guarantor["prefecture_kanji"] and len(p_join_guarantor["prefecture_kanji"]) > 8:
                tab4_errors.append("都道府県")

            if not p_join_guarantor["city_kanji"]:
                tab4_errors.append("市区郡")

            if p_join_guarantor["city_kanji"] and len(p_join_guarantor["city_kanji"]) > 20:
                tab4_errors.append("市区郡")

            if not p_join_guarantor["district_kanji"]:
                tab4_errors.append("町村丁目")

            if p_join_guarantor["district_kanji"] and len(p_join_guarantor["district_kanji"]) > 40:
                tab4_errors.append("町村丁目")

            if not p_join_guarantor["other_address_kanji"]:
                tab4_errors.append("丁目以下・建物名・部屋番号")

            if p_join_guarantor["other_address_kanji"] and len(p_join_guarantor["other_address_kanji"]) > 99:
                tab4_errors.append("丁目以下・建物名・部屋番号")

            if p_join_guarantor["prefecture_kana"] and len(p_join_guarantor["prefecture_kana"]) > 8:
                tab4_errors.append("都道府県（フリガナ）")

            if p_join_guarantor["city_kana"] and len(p_join_guarantor["city_kana"]) > 20:
                tab4_errors.append("市区郡（フリガナ）")

            if p_join_guarantor["district_kana"] and len(p_join_guarantor["district_kana"]) > 30:
                tab4_errors.append("町村丁目（フリガナ）")

            if p_join_guarantor["other_address_kana"] and len(p_join_guarantor["other_address_kana"]) > 138:
                tab4_errors.append("丁目以下・建物名・部屋番号（フリガナ）")

            if p_join_guarantor["email"]:
                result = re.fullmatch(REGEX["email"], p_join_guarantor["email"])
                if not result:
                    tab4_errors.append("ご連絡先用メールアドレス")

            if tab4_errors:
                errors[f"担保提供者（{index + 1}人目）"] = tab4_errors

    # お住まい
    tab5_errors = []
    if not data["p_application_headers"]["curr_house_lived_year"]:
        tab5_errors.append("現在居住　居住年数（年）")

    if not data["p_application_headers"]["curr_house_lived_month"]:
        tab5_errors.append("現在居住　居住年数（ヶ月）")

    if not data["p_application_headers"]["curr_house_residence_type"]:
        tab5_errors.append("現在のお住まいの種類")

    if data["p_application_headers"]["curr_house_residence_type"] == "4":
        if not data["p_application_headers"]["curr_house_owner_name"]:
            tab5_errors.append("所有者の氏名")
        if not data["p_application_headers"]["curr_house_owner_rel"]:
            tab5_errors.append("続柄")

    if data["p_application_headers"]["curr_house_residence_type"] == "6":
        if not data["p_application_headers"]["curr_house_schedule_disposal_type"]:
            tab5_errors.append("持家　処分方法")
        if (
            data["p_application_headers"]["curr_house_schedule_disposal_type"] == "99"
            and not data["p_application_headers"]["curr_house_schedule_disposal_type_other"]
        ):
            tab5_errors.append("持家　処分方法（その他）")

    if not data["p_application_headers"]["new_house_acquire_reason"]:
        tab5_errors.append("新しい住居を必要とする理由")
    if (
        data["p_application_headers"]["new_house_acquire_reason"] == "99"
        and not data["p_application_headers"]["new_house_acquire_reason_other"]
    ):
        tab5_errors.append("新しい住居を必要とする理由（その他）")

    if not data["p_application_headers"]["new_house_self_resident"]:
        tab5_errors.append("新しい住居に、あなたは居住しますか？")

    if data["p_application_headers"]["property_postal_code"]:
        result = re.fullmatch(REGEX["postal_code"], data["p_application_headers"]["property_postal_code"])
        if not result:
            tab5_errors.append("融資対象物件　郵便番号")

    if not data["p_application_headers"]["property_prefecture"]:
        tab5_errors.append("融資対象物件　都道府県")

    if (
        data["p_application_headers"]["property_prefecture"]
        and len(data["p_application_headers"]["property_prefecture"]) > 8
    ):
        tab5_errors.append("融資対象物件　都道府県")

    if not data["p_application_headers"]["property_city"]:
        tab5_errors.append("融資対象物件　市区町村郡")

    if data["p_application_headers"]["property_city"] and len(data["p_application_headers"]["property_city"]) > 20:
        tab5_errors.append("融資対象物件　市区町村郡")

    if not data["p_application_headers"]["property_district"]:
        tab5_errors.append("融資対象物件　以下地番")
    if (
        data["p_application_headers"]["property_district"]
        and len(data["p_application_headers"]["property_district"]) > 40
    ):
        tab5_errors.append("融資対象物件　以下地番")

    if data["p_application_headers"]["loan_target"] in ["2", "3"]:
        if not data["p_application_headers"]["property_apartment_and_room_no"]:
            tab5_errors.append("融資対象物件　マンション名・部屋番号")

    if not data["p_application_headers"]["property_type"]:
        tab5_errors.append("担保物件種類")

    for index, p_resident in enumerate(data["p_residents"]):
        if not p_resident["last_name_kanji"]:
            tab5_errors.append(f"入居家族{index + 1} 姓　漢字")
        if p_resident["last_name_kanji"] and len(p_resident["last_name_kanji"]) > 48:
            tab5_errors.append(f"入居家族{index + 1} 姓　漢字")

        if not p_resident["first_name_kanji"]:
            tab5_errors.append(f"入居家族{index + 1} 名　漢字")
        if p_resident["first_name_kanji"] and len(p_resident["first_name_kanji"]) > 48:
            tab5_errors.append(f"入居家族{index + 1} 名　漢字")

        if not p_resident["last_name_kana"]:
            tab5_errors.append(f"入居家族{index + 1} 姓　カナ")
        if p_resident["last_name_kana"] and len(p_resident["last_name_kana"]) > 48:
            tab5_errors.append(f"入居家族{index + 1} 姓　カナ")

        if not p_resident["first_name_kana"]:
            tab5_errors.append(f"入居家族{index + 1} 名　カナ")
        if p_resident["first_name_kana"] and len(p_resident["first_name_kana"]) > 48:
            tab5_errors.append(f"入居家族{index + 1} 名　カナ")

        if not p_resident["rel_to_applicant_a"]:
            tab5_errors.append(f"入居家族{index + 1} 続柄")
    # 現在の借入状況
    for index, p_borrowing in enumerate(data["p_borrowings"]):
        tab6_errors = []
        if not p_borrowing["loan_start_date"]:
            tab6_errors.append("当初カード契約年月" if p_borrowing["type"] == "2" else "当初借入年月")
        if not p_borrowing["loan_amount"]:
            tab6_errors.append("借入限度額" if p_borrowing["type"] == "2" else "当初借入額")
        if tab6_errors:
            errors[f"現在の借入状況（{index + 1}件目）"] = tab6_errors
    # 現在の借入状況
    tab6_errors_basic = []
    if (
        mcj_id in data["p_application_banks"]
        and len([item for item in data["p_borrowings"] if item["scheduled_loan_payoff"] == "1"]) > 0
    ):
        if not data["p_application_headers"]["refund_source_type"]:
            tab6_errors_basic.append("完済原資の種類")
    if tab6_errors_basic:
        errors["現在の借入状況"] = tab6_errors_basic

    # 資金計画
    tab7_errors = []
    if not data["p_application_headers"]["required_funds_additional_amount"]:
        tab7_errors.append("諸費用等")
    if not data["p_application_headers"]["funding_self_amount"]:
        tab7_errors.append("自己資金")
    if not data["p_application_headers"]["funding_other_loan_amount"]:
        tab7_errors.append("その他の借り入れ")
    if (
        data["p_application_headers"]["funding_other_amount"]
        and not data["p_application_headers"]["funding_other_amount_detail"]
    ):
        tab7_errors.append("※詳細を入力ください。")

    if tab7_errors:
        errors["資金計画"] = tab7_errors

    # 収入合算者
    if data["p_application_headers"]["loan_type"] in ["3", "4"]:
        tab2_1_errors = []
        if (
            not data["p_applicant_persons__1"]["last_name_kanji"]
            or len(data["p_applicant_persons__1"]["last_name_kanji"]) > 48
        ):
            tab2_1_errors.append("お名前（姓）")

        if (
            not data["p_applicant_persons__1"]["first_name_kanji"]
            or len(data["p_applicant_persons__1"]["first_name_kanji"]) > 48
        ):
            tab2_1_errors.append("お名前（名）")

        if (
            not data["p_applicant_persons__1"]["last_name_kana"]
            or len(data["p_applicant_persons__1"]["last_name_kana"]) > 48
        ):
            tab2_1_errors.append("お名前（姓）（フリガナ）")

        if (
            not data["p_applicant_persons__1"]["first_name_kana"]
            or len(data["p_applicant_persons__1"]["first_name_kana"]) > 48
        ):
            tab2_1_errors.append("お名前（名）（フリガナ）")

        if not data["p_applicant_persons__1"]["gender"]:
            tab2_1_errors.append("性別")

        if not data["p_applicant_persons__1"]["birthday"]:
            tab2_1_errors.append("生年月日")

        if not data["p_applicant_persons__1"]["mobile_phone"] and not data["p_applicant_persons__1"]["home_phone"]:
            tab2_1_errors.append("電話番号携帯")
            tab2_1_errors.append("電話番号自宅")
        if data["p_applicant_persons__1"]["mobile_phone"]:
            result = re.fullmatch(REGEX["mobile_phone"], data["p_applicant_persons__1"]["mobile_phone"])
            if not result:
                tab2_1_errors.append("電話番号携帯")
        if data["p_applicant_persons__1"]["home_phone"]:
            result = re.fullmatch(REGEX["home_phone"], data["p_applicant_persons__1"]["home_phone"])
            if not result:
                tab2_1_errors.append("電話番号自宅")
        if data["p_applicant_persons__1"]["emergency_contact"]:
            result = re.fullmatch(REGEX["emergency_contact"], data["p_applicant_persons__1"]["emergency_contact"])
            if not result:
                tab2_1_errors.append("緊急連絡先")

        if data["p_applicant_persons__1"]["postal_code"]:
            result = re.fullmatch(REGEX["postal_code"], data["p_applicant_persons__1"]["postal_code"])
            if not result:
                tab2_1_errors.append("郵便番号")

        if not data["p_applicant_persons__1"]["prefecture_kanji"]:
            tab2_1_errors.append("都道府県")

        if (
            data["p_applicant_persons__1"]["prefecture_kanji"]
            and len(data["p_applicant_persons__1"]["prefecture_kanji"]) > 8
        ):
            tab2_1_errors.append("都道府県")

        if not data["p_applicant_persons__1"]["city_kanji"]:
            tab2_1_errors.append("市区郡")

        if data["p_applicant_persons__1"]["city_kanji"] and len(data["p_applicant_persons__1"]["city_kanji"]) > 20:
            tab2_1_errors.append("市区郡")

        if not data["p_applicant_persons__1"]["district_kanji"]:
            tab2_1_errors.append("町村丁目")

        if (
            data["p_applicant_persons__1"]["district_kanji"]
            and len(data["p_applicant_persons__1"]["district_kanji"]) > 40
        ):
            tab2_1_errors.append("町村丁目")

        if not data["p_applicant_persons__1"]["other_address_kanji"]:
            tab2_1_errors.append("丁目以下・建物名・部屋番号")

        if (
            data["p_applicant_persons__1"]["other_address_kanji"]
            and len(data["p_applicant_persons__1"]["other_address_kanji"]) > 99
        ):
            tab2_1_errors.append("丁目以下・建物名・部屋番号")

        if not data["p_applicant_persons__1"]["prefecture_kana"]:
            tab2_1_errors.append("都道府県（フリガナ）")

        if (
            data["p_applicant_persons__1"]["prefecture_kana"]
            and len(data["p_applicant_persons__1"]["prefecture_kana"]) > 8
        ):
            tab2_1_errors.append("都道府県（フリガナ）")

        if not data["p_applicant_persons__1"]["city_kana"]:
            tab2_1_errors.append("市区郡（フリガナ）")

        if data["p_applicant_persons__1"]["city_kana"] and len(data["p_applicant_persons__1"]["city_kana"]) > 20:
            tab2_1_errors.append("市区郡（フリガナ）")

        if not data["p_applicant_persons__1"]["district_kana"]:
            tab2_1_errors.append("町村丁目（フリガナ）")

        if (
            data["p_applicant_persons__1"]["district_kana"]
            and len(data["p_applicant_persons__1"]["district_kana"]) > 30
        ):
            tab2_1_errors.append("町村丁目（フリガナ）")

        if not data["p_applicant_persons__1"]["other_address_kana"]:
            tab2_1_errors.append("丁目以下・建物名・部屋番号（フリガナ）")

        if (
            data["p_applicant_persons__1"]["other_address_kana"]
            and len(data["p_applicant_persons__1"]["other_address_kana"]) > 138
        ):
            tab2_1_errors.append("丁目以下・建物名・部屋番号（フリガナ）")

        if not data["p_applicant_persons__1"]["email"]:
            tab2_1_errors.append("ご連絡先用メールアドレス")

        if data["p_applicant_persons__1"]["email"]:
            result = re.fullmatch(REGEX["email"], data["p_applicant_persons__1"]["email"])
            if not result:
                tab2_1_errors.append("ご連絡先用メールアドレス")
        if tab2_1_errors:
            errors["収入合算者情報"] = tab2_1_errors

        # 収入合算者の職業
        tab3_1_errors = []

        if not data["p_applicant_persons__1"]["office_occupation"]:
            tab3_1_errors.append("ご職業")
        if (
            data["p_applicant_persons__1"]["office_occupation"] == "99"
            and not data["p_applicant_persons__1"]["office_occupation_other"]
        ):
            tab3_1_errors.append("勤務先　職業（その他）")

        if (
            data["p_applicant_persons__1"]["office_industry"] == "99"
            and not data["p_applicant_persons__1"]["office_industry_other"]
        ):
            tab3_1_errors.append("勤務先　業種（その他）")

        if not data["p_applicant_persons__1"]["office_occupation"]:
            tab3_1_errors.append("職種")
        if (
            data["p_applicant_persons__1"]["office_occupation_detail"] == "99"
            and not data["p_applicant_persons__1"]["office_occupation_detail_other"]
        ):
            tab3_1_errors.append("勤務先　職種（その他）")

        if not data["p_applicant_persons__1"]["office_employment_type"]:
            tab3_1_errors.append("雇用形態")

        if not data["p_applicant_persons__1"]["office_name_kanji"]:
            tab3_1_errors.append("勤務先名")

        if (
            data["p_applicant_persons__1"]["office_name_kanji"]
            and len(data["p_applicant_persons__1"]["office_name_kanji"]) > 48
        ):
            tab3_1_errors.append("勤務先名")

        if not data["p_applicant_persons__1"]["office_name_kana"]:
            tab3_1_errors.append("勤務先名（フリガナ）")

        if (
            data["p_applicant_persons__1"]["office_name_kana"]
            and len(data["p_applicant_persons__1"]["office_name_kana"]) > 48
        ):
            tab3_1_errors.append("勤務先名（フリガナ）")

        if (
            data["p_applicant_persons__1"]["office_department"]
            and len(data["p_applicant_persons__1"]["office_department"]) > 46
        ):
            tab3_1_errors.append("所属部課")

        if not data["p_applicant_persons__1"]["office_phone"]:
            tab3_1_errors.append("勤務先の電話番号")

        if data["p_applicant_persons__1"]["office_phone"]:
            result = re.fullmatch(REGEX["home_phone"], data["p_applicant_persons__1"]["office_phone"])
            if not result:
                tab3_1_errors.append("勤務先の電話番号")

        if not data["p_applicant_persons__1"]["office_head_location"]:
            tab3_1_errors.append("勤務先本社所在地")

        if (
            data["p_applicant_persons__1"]["office_head_location"]
            and len(data["p_applicant_persons__1"]["office_head_location"]) > 48
        ):
            tab3_1_errors.append("勤務先本社所在地")

        if data["p_applicant_persons__1"]["office_establishment_date"]:
            result = re.fullmatch(REGEX["ymd"], data["p_applicant_persons__1"]["office_establishment_date"])
            if not result:
                tab3_1_errors.append("勤務先設立年月日")

        if not data["p_applicant_persons__1"]["office_postal_code"]:
            tab3_1_errors.append("郵便番号")

        if data["p_applicant_persons__1"]["office_postal_code"]:
            result = re.fullmatch(REGEX["postal_code"], data["p_applicant_persons__1"]["office_postal_code"])
            if not result:
                tab3_1_errors.append("郵便番号")

        if not data["p_applicant_persons__1"]["office_prefecture_kanji"]:
            tab3_1_errors.append("都道府県")

        if (
            data["p_applicant_persons__1"]["office_prefecture_kanji"]
            and len(data["p_applicant_persons__1"]["office_prefecture_kanji"]) > 8
        ):
            tab3_1_errors.append("都道府県")

        if (
            data["p_applicant_persons__1"]["office_city_kanji"]
            and len(data["p_applicant_persons__1"]["office_city_kanji"]) > 20
        ):
            tab3_1_errors.append("市区郡")

        if (
            data["p_applicant_persons__1"]["office_district_kanji"]
            and len(data["p_applicant_persons__1"]["office_district_kanji"]) > 40
        ):
            tab3_1_errors.append("町村丁目")

        if (
            data["p_applicant_persons__1"]["office_other_address_kanji"]
            and len(data["p_applicant_persons__1"]["office_other_address_kanji"]) > 99
        ):
            tab3_1_errors.append("丁目以下・建物名・部屋番号")

        if not data["p_applicant_persons__1"]["office_prefecture_kana"]:
            tab3_1_errors.append("都道府県（フリガナ）")

        if (
            data["p_applicant_persons__1"]["office_prefecture_kana"]
            and len(data["p_applicant_persons__1"]["office_prefecture_kana"]) > 8
        ):
            tab3_1_errors.append("都道府県（フリガナ）")

        if (
            data["p_applicant_persons__1"]["office_city_kana"]
            and len(data["p_applicant_persons__1"]["office_city_kana"]) > 20
        ):
            tab3_1_errors.append("市区郡（フリガナ）")

        if (
            data["p_applicant_persons__1"]["office_district_kana"]
            and len(data["p_applicant_persons__1"]["office_district_kana"]) > 30
        ):
            tab3_1_errors.append("町村丁目（フリガナ）")

        if (
            data["p_applicant_persons__1"]["office_other_address_kana"]
            and len(data["p_applicant_persons__1"]["office_other_address_kana"]) > 138
        ):
            tab3_1_errors.append("丁目以下・建物名・部屋番号（フリガナ）")

        if not data["p_applicant_persons__1"]["office_employee_num"]:
            tab3_1_errors.append("従業員数")

        if not data["p_applicant_persons__1"]["last_year_income"]:
            tab3_1_errors.append("前年度年収")

        if not data["p_applicant_persons__1"]["main_income_source"]:
            tab3_1_errors.append("収入源（銀行送信用）")

        if data["p_applicant_persons__1"]["tax_return"] == "1":
            if not data["p_applicant_persons__1"]["tax_return_reasons"]:
                tab3_1_errors.append("確定申告の理由")
            if (
                data["p_applicant_persons__1"]["tax_return_reasons"] == "99"
                and not data["p_applicant_persons__1"]["tax_return_reason_other"]
            ):
                tab3_1_errors.append("確定申告の理由　その他")
        if data["p_applicant_persons__1"]["transfer_office"] == "1":
            if not data["p_applicant_persons__1"]["transfer_office_name_kanji"]:
                tab3_1_errors.append("出向（派遣）勤務先名")
            if (
                data["p_applicant_persons__1"]["transfer_office_name_kanji"]
                and len(data["p_applicant_persons__1"]["transfer_office_name_kanji"]) > 48
            ):
                tab3_1_errors.append("出向（派遣）勤務先名")

            if not data["p_applicant_persons__1"]["transfer_office_name_kana"]:
                tab3_1_errors.append("出向（派遣）勤務先名（フリガナ）")
            if (
                data["p_applicant_persons__1"]["transfer_office_name_kana"]
                and len(data["p_applicant_persons__1"]["transfer_office_name_kana"]) > 48
            ):
                tab3_1_errors.append("出向（派遣）勤務先名（フリガナ）")

            if not data["p_applicant_persons__1"]["transfer_office_phone"]:
                tab3_1_errors.append("出向（派遣）先 電話番号")

            if data["p_applicant_persons__1"]["transfer_office_phone"]:
                result = re.fullmatch(REGEX["home_phone"], data["p_applicant_persons__1"]["transfer_office_phone"])
                if not result:
                    tab3_1_errors.append("出向（派遣）先 電話番号")

            if not data["p_applicant_persons__1"]["transfer_office_postal_code"]:
                tab3_1_errors.append("出向（派遣）先 郵便番号")

            if data["p_applicant_persons__1"]["transfer_office_postal_code"]:
                result = re.fullmatch(
                    REGEX["postal_code"], data["p_applicant_persons__1"]["transfer_office_postal_code"]
                )
                if not result:
                    tab3_1_errors.append("出向（派遣）先 郵便番号")

            if not data["p_applicant_persons__1"]["transfer_office_prefecture_kanji"]:
                tab3_1_errors.append("出向（派遣）先 都道府県")
            if (
                data["p_applicant_persons__1"]["transfer_office_prefecture_kanji"]
                and len(data["p_applicant_persons__1"]["transfer_office_prefecture_kanji"]) > 8
            ):
                tab3_1_errors.append("出向（派遣）先 都道府県")

            if (
                data["p_applicant_persons__1"]["transfer_office_city_kanji"]
                and len(data["p_applicant_persons__1"]["transfer_office_city_kanji"]) > 20
            ):
                tab3_1_errors.append("出向（派遣）先 市区郡")

            if (
                data["p_applicant_persons__1"]["transfer_office_district_kanji"]
                and len(data["p_applicant_persons__1"]["transfer_office_district_kanji"]) > 40
            ):
                tab3_1_errors.append("出向（派遣）先 町村丁目")

            if (
                data["p_applicant_persons__1"]["transfer_office_other_address_kanji"]
                and len(data["p_applicant_persons__1"]["transfer_office_other_address_kanji"]) > 99
            ):
                tab3_1_errors.append("出向（派遣）先 丁目以下・建物名・部屋番号")
        if data["p_applicant_persons__1"]["maternity_paternity_leave"]:
            if not data["p_applicant_persons__1"]["maternity_paternity_leave_start_date"]:
                tab3_1_errors.append("取得開始時期")

            if not data["p_applicant_persons__1"]["maternity_paternity_leave_end_date"]:
                tab3_1_errors.append("取得終了時期")
        if tab3_1_errors:
            errors["収入合算者の職業"] = tab3_1_errors

    return errors
