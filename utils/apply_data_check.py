def applicant_data_check(data: dict, role_type: int):
    errors = {}

    # step-id-2
    step_id_2_errors = []
    if data["p_applicant_persons__0"]["prefecture_kana"] and len(data["p_applicant_persons__0"]["prefecture_kana"]) > 8:
        step_id_2_errors.append("都道府県（フリガナ）")

    if data["p_applicant_persons__0"]["city_kana"] and len(data["p_applicant_persons__0"]["city_kana"]) > 20:
        step_id_2_errors.append("市区郡（フリガナ）")

    if data["p_applicant_persons__0"]["district_kana"] and len(data["p_applicant_persons__0"]["district_kana"]) > 30:
        step_id_2_errors.append("町村丁目（フリガナ）")

    if data["p_applicant_persons__0"]["nationality"] == "2":
        if len(data["p_applicant_persons__0"]["H__a"]) == 0 or len(data["p_applicant_persons__0"]["H__b"]) == 0:
            step_id_2_errors.append("〈現在の国籍〉在留カードまたは特別永住者証明書を添付してください')")

    if step_id_2_errors:
        errors["あなたの情報"] = step_id_2_errors

    # step-id-3
    step_id_3_errors = []
    if (
        data["p_applicant_persons__0"]["office_prefecture_kana"]
        and len(data["p_applicant_persons__0"]["office_prefecture_kana"]) > 8
    ):
        step_id_3_errors.append("都道府県（フリガナ）")

    if (
        data["p_applicant_persons__0"]["office_city_kana"]
        and len(data["p_applicant_persons__0"]["office_city_kana"]) > 20
    ):
        step_id_3_errors.append("市区郡（フリガナ）")

    if (
        data["p_applicant_persons__0"]["office_district_kana"]
        and len(data["p_applicant_persons__0"]["office_district_kana"]) > 30
    ):
        step_id_3_errors.append("町村丁目（フリガナ）")

    if step_id_3_errors:
        errors["あなたのご職業"] = step_id_3_errors

    if data["p_application_headers"]["loan_type"] in ["3", "4"]:
        # step-id-4
        step_id_4_errors = []
        if (
            data["p_applicant_persons__1"]["prefecture_kana"]
            and len(data["p_applicant_persons__1"]["prefecture_kana"]) > 8
        ):
            step_id_4_errors.append("都道府県（フリガナ）")

        if data["p_applicant_persons__1"]["city_kana"] and len(data["p_applicant_persons__1"]["city_kana"]) > 20:
            step_id_4_errors.append("市区郡（フリガナ）")

        if (
            data["p_applicant_persons__1"]["district_kana"]
            and len(data["p_applicant_persons__1"]["district_kana"]) > 30
        ):
            step_id_4_errors.append("町村丁目（フリガナ）")

        if data["p_applicant_persons__1"]["nationality"] == "2":
            if len(data["p_applicant_persons__1"]["H__a"]) == 0 or len(data["p_applicant_persons__1"]["H__b"]) == 0:
                step_id_2_errors.append("〈現在の国籍〉在留カードまたは特別永住者証明書を添付してください')")

        if step_id_4_errors:
            errors["収入合算者"] = step_id_4_errors

        # step-id-5
        step_id_5_errors = []

        if (
            data["p_applicant_persons__1"]["office_prefecture_kana"]
            and len(data["p_applicant_persons__1"]["office_prefecture_kana"]) > 8
        ):
            step_id_5_errors.append("都道府県（フリガナ）")

        if (
            data["p_applicant_persons__1"]["office_city_kana"]
            and len(data["p_applicant_persons__1"]["office_city_kana"]) > 20
        ):
            step_id_5_errors.append("市区郡（フリガナ）")

        if (
            data["p_applicant_persons__1"]["office_district_kana"]
            and len(data["p_applicant_persons__1"]["office_district_kana"]) > 30
        ):
            step_id_5_errors.append("町村丁目（フリガナ）")

        if step_id_5_errors:
            errors["収入合算者の職業"] = step_id_5_errors

    if data["p_application_headers"]["join_guarantor_umu"]:
        # step-id-6
        for index, p_join_guarantor in enumerate(data["p_join_guarantors"]):
            step_id_6_errors = []
            if p_join_guarantor["prefecture_kana"] and len(p_join_guarantor["prefecture_kana"]) > 8:
                step_id_6_errors.append("都道府県（フリガナ）")

            if p_join_guarantor["city_kana"] and len(p_join_guarantor["city_kana"]) > 20:
                step_id_6_errors.append("市区郡（フリガナ）")

            if p_join_guarantor["district_kana"] and len(p_join_guarantor["district_kana"]) > 30:
                step_id_6_errors.append("町村丁目（フリガナ）")

            if step_id_6_errors:
                errors[f"担保提供者{index + 1}人目"] = step_id_6_errors

    # step-id-7
    for index, p_resident in enumerate(data["p_residents"]):
        step_id_7_errors = []
        if p_resident["prefecture_kana"] and len(p_resident["prefecture_kana"]) > 8:
            step_id_7_errors.append("都道府県（フリガナ）")

        if p_resident["city_kana"] and len(p_resident["city_kana"]) > 20:
            step_id_7_errors.append("市区郡（フリガナ）")

        if p_resident["district_kana"] and len(p_resident["district_kana"]) > 30:
            step_id_7_errors.append("町村丁目（フリガナ）")

        if step_id_7_errors:
            errors["お住まいのご入居予定者の情報"] = step_id_7_errors
    # step-id-10
    step_id_10_errors = []
    if data["p_applicant_persons__0"]["identity_verification_type"] == "1":
        if len(data["p_applicant_persons__0"]["A__01__a"]) == 0 or len(data["p_applicant_persons__0"]["A__01__b"]) == 0:
            step_id_10_errors.append("本人確認書類")
    if data["p_applicant_persons__0"]["identity_verification_type"] == "2":
        if len(data["p_applicant_persons__0"]["A__02"]) == 0:
            step_id_10_errors.append("本人確認書類")
    if data["p_applicant_persons__0"]["identity_verification_type"] == "3":
        if len(data["p_applicant_persons__0"]["A__03__a"]) == 0 or len(data["p_applicant_persons__0"]["A__03__b"]) == 0:
            step_id_10_errors.append("本人確認書類")
    if role_type == 2:
        if len(data["p_applicant_persons__0"]["S"]) == 0:
            step_id_10_errors.append("サインをしてください")
    if step_id_10_errors:
        errors["書類添付"] = step_id_10_errors
    # step-id-11
    if data["p_application_headers"]["loan_type"] in ["3", "4"]:
        step_id_11_errors = []
        if data["p_applicant_persons__1"]["identity_verification_type"] == "1":
            if (
                len(data["p_applicant_persons__1"]["A__01__a"]) == 0
                or len(data["p_applicant_persons__1"]["A__01__b"]) == 0
            ):
                step_id_11_errors.append("本人確認書類")
        if data["p_applicant_persons__1"]["identity_verification_type"] == "2":
            if len(data["p_applicant_persons__1"]["A__02"]) == 0:
                step_id_11_errors.append("本人確認書類")
        if data["p_applicant_persons__1"]["identity_verification_type"] == "3":
            if (
                len(data["p_applicant_persons__1"]["A__03__a"]) == 0
                or len(data["p_applicant_persons__1"]["A__03__b"]) == 0
            ):
                step_id_11_errors.append("本人確認書類")
        if step_id_11_errors:
            errors["収入合算者の書類"] = step_id_11_errors
