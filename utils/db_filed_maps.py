p_application_header_parameters = {
    "s_sale_person_id": "s_sales_person_id",
    "manager_id": "s_manager_id",
    "application_number": "apply_no",  # 受付番号
    "scheduled_date_moving": "move_scheduled_date",  # 入居予定年月
    "loan_apply_date": "apply_date",  # 申込日兼同意日
    "loan_type": "loan_type",  # 借入形態
    "loan_target": "loan_target",  # 資金使途
    "person_occupancy": "new_house_self_resident",  # 新居　申込人本人住居区分
    "non_resident_reason": "new_house_self_not_resident_reason",  # 新居　申込人本人住居しない理由
    "residence_category": "new_house_residence_type",
    "business_ability": "property_business_type",  # 物件　事業性区分
    "is_home_loan_plus": "loan_plus",  # 住宅ローンプラス
    "real_estate_sale_price": "funding_estate_sale_amount",  # 調達資金　不動産売却代金
    "house_purchase_price": "required_funds_house_amount",  # 必要資金　建物・物件価格・マンション価格
    "land_purchase_price": "required_funds_land_amount",  # 必要資金　土地価格
    "accessory_cost": "required_funds_accessory_amount",  # 必要資金　付帯設備
    "additional_cost": "required_funds_additional_amount",  # 必要資金　諸費用等
    "refinancing_loan_balance": "required_funds_refinance_loan_balance",  # 必要資金　借換対象ローン残債
    "house_upgrade_cost": "required_funds_upgrade_amount",  # 必要資金　増改築
    "require_funds_breakdown_mortgage": "required_funds_loan_plus_amount",  # 必要資金　住宅ローンプラス
    "saving_amount": "funding_self_amount",  # 調達資金　自己資金
    "deposit_savings_1": "funding_saving_amount",  # 調達資金　預貯金
    "other_saving_amount": "funding_other_saving_amount",  # 調達資金　有価証券等
    "relative_donation_amount": "funding_relative_donation_amount",  # 調達資金　親族からの贈与
    "loan_amount": "funding_loan_amount",  # 調達資金　本件ローン
    "pair_loan_amount": "funding_pair_loan_amount",  # 調達資金　ペアローン
    "other_procurement_breakdown": "funding_other_amount",  # 調達資金　その他額
    "other_procurement_breakdown_content": "funding_other_amount_detail",  # 調達資金　その他額名
    "amount_any_loans": "funding_other_loan_amount",  # 調達資金　その他の借り入れ
    "amount_others": "funding_other_refinance_amount",  # 調達資金　その他借換
    "has_land_advance_plan": "land_advance_plan",  # 土地先行プラン希望
    "property_postal_code": "property_postal_code",  # 物件　郵便番号
    "acquisition_time_of_the_land": "property_land_acquire_date",  # 物件　土地取得時期
    "collateral_address_kana": "property_address_kana",  # 物件　所在地　カナ
    "collateral_prefecture": "property_prefecture",  # 物件　都道府県
    "collateral_city": "property_city",  # 物件　市区町村郡
    "collateral_lot_number": "property_district",  # 物件　以下地番
    "condominium_name": "property_apartment_and_room_no",  # 物件　マンション名・部屋番号
    "occupied_area": "property_private_area",  # 物件　マンションの専有面積
    "collateral_land_area": "property_land_area",  # 物件　土地の敷地面積
    "collateral_total_floor_area": "property_total_floor_area",  # 物件　マンション全体の延床面積
    "collateral_floor_area": "property_floor_area",  # 物件　建物の延床面積
    "collateral_type": "property_type",  # 物件　種類
    "joint_ownership_division": "property_joint_ownership_type",  # 物件　共有区分
    "building_ratio_numerator": "property_building_ratio_numerator",  # 物件　建物割合分子
    "building_ratio_denominator": "property_building_ratio_denominator",  # 物件　建物割合分母
    "land_ratio_numerator": "property_land_ratio_numerator",  # 物件　土地割合分子
    "land_ratio_denominator": "property_land_ratio_denominator",  # 物件　土地割合分母
    "land_price": "property_land_price",  # 物件　土地価格
    "building_price": "property_building_price",  # 物件　建物価格
    "land_and_building_price": "property_total_price",  # 物件　合計価格
    "flat_35_applicable_plan": "property_flat_35_plan",  # 物件　フラット35S適用プラン（MCJ）
    "maintenance_type": "property_maintenance_type",  # 物件　維持保全型区分（MCJ）
    "flat_35_application": "property_flat_35_tech",  # 物件　フラット35S技術基準（MCJ）
    "purchase_purpose": "property_purchase_type",  # 物件　買戻・保留地・仮換地（MCJ）
    "planning_area": "property_planning_area",  # 物件　都市計画区域（MCJ）
    "other_planning_area": "property_planning_area_other",  # 物件　都市計画区域　その他（MCJ）
    "rebuilding_reason": "property_rebuilding_reason",  # 物件　再建築理由（MCJ）
    "other_rebuilding_reason": "property_rebuilding_reason_other",  # 物件　再建築理由　その他（MCJ）
    "region_type": "property_region_type",  # 物件　地域区分（MCJ）
    "land_ownership": "property_land_type",  # 物件　土地権利（MCJ）
    "completely_repayment_type": "refund_source_type",  # 完済原資　区分（MCJ）
    "other_complete_repayment_type": "refund_source_type_other",  # 完済原資　区分　その他（MCJ）
    "refund_content": "refund_source_content",  # 完済原資　内容（MCJ）
    "refund_amount": "refund_source_amount",  # 完済原資　金額（MCJ）
    "pair_loan_applicant_first_name": "pair_loan_first_name",  # ペアローン相手名
    "pair_loan_applicant_last_name": "pair_loan_last_name",  # ペアローン相手姓
    "pair_loan_relationship": "pair_loan_rel",  # ペアローン相手続柄
    "property_information_url": "property_publish_url",  # 物件　掲載URL
    "pair_loan_relationship_name": "pair_loan_rel_name",  # ペアローン相手続柄名称　入力項目
    "sale_person_phone_number": "vendor_phone",  # 業者電話番号　入力項目
    "sale_person_name_input": "vendor_name",  # 業者名　入力項目
    "loan_target_zero": "loan_target_type",
}

p_applicant_person_parameters_0_h = {
    "has_join_guarantor": "join_guarantor_umu",  # 担保提供者有無
    "current_residence": "curr_house_residence_type",  # 現居　お住まいの種類
    "owner_full_name": "curr_house_owner_name",  # 現居　所有者の氏名
    "owner_relationship": "curr_house_owner_rel",  # 現居　所有者の続柄
    "buyingand_selling_schedule_type": "curr_house_schedule_disposal_type",  # 現居　持家　処分方法
    "other_buyingand_selling_schedule_type": "curr_house_schedule_disposal_type_other",  # 現居　持家　処分方法　その他
    "scheduled_time_sell_house": "curr_house_shell_scheduled_date",  # 現居　持家　売却予定時期
    "expected_house_selling_price": "curr_house_shell_scheduled_price",  # 現居　持家　売却予定価格
    "current_home_loan": "curr_house_loan_balance_type",  # 現居　持家　ローン残高有無
    "lived_length_year_num": "curr_house_lived_year",  # 現居　居住年数　ヶ年
    "lived_length_month_num": "curr_house_lived_month",  # 現居　居住年数　ヶ月
    "current_residence_floor_area": "curr_house_floor_area",  # 現居　床面積（MCJ）
    "reason_acquire_home": "new_house_acquire_reason",  # 新居　申込人住宅取得理由
    "other_reason_acquire_home": "new_house_acquire_reason_other",  # 新居　申込人住宅取得理由　その他
    "borrowing_status": "curr_borrowing_status",  # 現在利用中のローン
}

p_applicant_person_parameters_0 = {
    "first_name_kanji": "first_name_kanji",  # 名　漢字
    "last_name_kanji": "last_name_kanji",  # 姓　漢字
    "first_name_kana": "first_name_kana",  # 名　カナ
    "last_name_kana": "last_name_kana",  # 姓　カナ
    "sex": "gender",  # 性別
    "birthday": "birthday",  # 生年月日
    "mobile_phone_number": "mobile_phone",  # 携帯電話番号
    "home_phone_number": "home_phone",  # 自宅電話番号
    "emergency_contact_number": "emergency_contact",  # 緊急連絡先
    "postal_code": "postal_code",  # 郵便番号
    "prefecture_kanji": "prefecture_kanji",  # 都道府県　漢字
    "city_kanji": "city_kanji",  # 市区郡　漢字
    "district_kanji": "district_kanji",  # 町村字丁目　漢字
    "other_address_kanji": "other_address_kanji",  # 補足　漢字
    "prefecture_kana": "prefecture_kana",  # 都道府県　カナ
    "city_kana": "city_kana",  # 市区郡　カナ
    "district_kana": "district_kana",  # 町村字丁目　カナ
    "other_address_kana": "other_address_kana",  # 補足　カナ
    "owner_email": "email",  # Eメール
    "last_year_income": "last_year_income",  # 前年年収　総額
    "bonus_income": "last_year_bonus_income",  # 前年年収　総額内ボーナス分（MCJ）
    "two_years_ago_income": "before_last_year_income",  # 前々年度年収 （MCJ）
    "headquarters_location": "office_head_location",  # 勤務先　本社所在地
    "office_name_kanji": "office_name_kanji",  # 勤務先　名　漢字
    "office_name_kana": "office_name_kana",  # 勤務先　名　カナ
    "office_phone_number": "office_phone",  # 勤務先　電話番号
    "employment_started_date": "office_joining_date",  # 勤務先　入社年月
    "number_of_employee": "office_employee_num",  # 勤務先　従業員数
    "emplmt_form_code": "office_employment_type",  # 勤務先　雇用形態
    "listed_division": "office_listed_division",  # 勤務先　上場区分
    "office_establishment_date": "office_establishment_date",  # 勤務先　設立年月日
    "office_prefecture_kanji": "office_prefecture_kanji",  # 勤務先　都道府県　漢字
    "office_city_kanji": "office_city_kanji",  # 勤務先　市区郡　漢字
    "office_district_kanji": "office_district_kanji",  # 勤務先　町村字丁目　漢字
    "other_office_address_kanji": "office_other_address_kanji",  # 勤務先　補足　漢字
    "office_prefecture_kana": "office_prefecture_kana",  # 勤務先　都道府県　カナ
    "office_city_kana": "office_city_kana",  # 勤務先　市区郡　カナ
    "office_district_kana": "office_district_kana",  # 勤務先　町村字丁目　カナ
    "other_office_address_kana": "office_other_address_kana",  # 勤務先　補足　カナ
    "office_postal_code": "office_postal_code",  # 勤務先　郵便番号
    "industry": "office_industry",  # 勤務先　業種
    "other_industry": "office_industry_other",  # 勤務先　業種　その他
    "occupation": "office_occupation",  # 勤務先　職業
    "other_occupation": "office_occupation_other",  # 勤務先　職業　その他
    "occupation_detail": "office_occupation_detail",  # 勤務先　職種
    "other_occupation_detail": "office_occupation_detail_other",  # 勤務先　職種　その他
    "income_source": "income_sources",  # 収入源
    "tax_return": "tax_return",  # 確定申告有無
    "type_tax_return": "tax_return_reasons",  # 確定申告理由
    "other_type_tax_return": "tax_return_reason_other",  # 確定申告理由　その他
    "maternity_paternity_leave_status": "maternity_paternity_leave",  # 産休・育休
    "maternity_paternity_leave_start_time": "maternity_paternity_leave_start_date",  # 産休・育休開始
    "maternity_paternity_leave_end_time": "maternity_paternity_leave_end_date",  # 産休・育休終了
    "nursing_leave_status": "nursing_leave",  # 介護休
    "capital_stock": "office_capital_stock",  # 勤務先　資本金
    "department": "office_department",  # 勤務先　所属部署
    "position": "office_role",  # 勤務先　役職
    "job_change": "job_change",  # 転職有無
    "job_change_company_name_kana": "job_change_office_name_kana",  # 転職前勤務先　名　カナ
    "job_change_company_name_kanji": "job_change_office_name_kanji",  # 転職前勤務先　名　漢字
    "prev_company_year_num": "prev_office_year_num",  # 転職前勤務先　勤続年数　年
    "prev_company_industry": "prev_office_industry",  # 転職前勤務先　業種
    "other_prev_company_industry": "prev_office_industry_other",  # 転職前勤務先　業種（その他）
    "transfer_office": "transfer_office",  # 出向（派遣）有無
    "transfer_office_name_kanji": "transfer_office_name_kanji",  # 出向（派遣）先　名　漢字
    "transfer_office_name_kana": "transfer_office_name_kana",  # 出向（派遣）先　名　カナ
    "transfer_office_phone_number": "transfer_office_phone",  # 出向（派遣）先　電話番号
    "transfer_office_postal_code": "transfer_office_postal_code",  # 出向（派遣）先　郵便番号
    "transfer_office_prefecture_kanji": "transfer_office_prefecture_kanji",  # 出向（派遣）先　都道府県　漢字
    "transfer_office_city_kanji": "transfer_office_city_kanji",  # 出向（派遣）先　市区郡　漢字
    "transfer_office_district_kanji": "transfer_office_district_kanji",  # 出向（派遣）先　町村字丁目　漢字
    "transfer_office_other_address_kanji": "transfer_office_other_address_kanji",  # 出向（派遣）先　補足　漢字
    "nationality": "nationality",  # 国籍
    "land_rent_to_be_paid": "rent_to_be_paid_land",  # 今回の住宅・土地取得以外の借入　地代（MCJ）
    "house_rent_to_be_paid": "rent_to_be_paid_house",  # 今回の住宅・土地取得以外の借入　家賃（MCJ）
    "identity_verification": "identity_verification_type",  # 本人確認書類タイプ
    "main_income_source": "main_income_source",  # メイン収入源　銀代入力項目
}


p_applicant_person_parameters_1 = {
    "name_relationship_to_applicant": "rel_to_applicant_a_name",  # 連帯債務者　申込者に対して続柄名　入力項目
    "relationship_to_applicant": "rel_to_applicant_a",  # 連帯債務者　申込者に対して続柄
    "other_relationship_to_applicant": "rel_to_applicant_a_other",  # 連帯債務者　申込者に対して続柄　その他
    "first_name_kanji": "first_name_kanji",  # 名　漢字
    "last_name_kanji": "last_name_kanji",  # 姓　漢字
    "first_name_kana": "first_name_kana",  # 名　カナ
    "last_name_kana": "last_name_kana",  # 姓　カナ
    "sex": "gender",  # 性別
    "birthday": "birthday",  # 生年月日
    "mobile_phone_number": "mobile_phone",  # 携帯電話番号
    "home_phone_number": "home_phone",  # 自宅電話番号
    "emergency_contact_number": "emergency_contact",  # 緊急連絡先
    "postal_code": "postal_code",  # 郵便番号
    "prefecture_kanji": "prefecture_kanji",  # 都道府県　漢字
    "city_kanji": "city_kanji",  # 市区郡　漢字
    "district_kanji": "district_kanji",  # 町村字丁目　漢字
    "other_address_kanji": "other_address_kanji",  # 補足　漢字
    "prefecture_kana": "prefecture_kana",  # 都道府県　カナ
    "city_kana": "city_kana",  # 市区郡　カナ
    "district_kana": "district_kana",  # 町村字丁目　カナ
    "other_address_kana": "other_address_kana",  # 補足　カナ
    "owner_email": "email",  # Eメール
    "last_year_income": "last_year_income",  # 前年年収　総額
    "bonus_income": "last_year_bonus_income",  # 前年年収　総額内ボーナス分（MCJ）
    "two_years_ago_income": "before_last_year_income",  # 前々年度年収 （MCJ）
    "headquarters_location": "office_head_location",  # 勤務先　本社所在地
    "office_name_kanji": "office_name_kanji",  # 勤務先　名　漢字
    "office_name_kana": "office_name_kana",  # 勤務先　名　カナ
    "office_phone_number": "office_phone",  # 勤務先　電話番号
    "employment_started_date": "office_joining_date",  # 勤務先　入社年月
    "number_of_employee": "office_employee_num",  # 勤務先　従業員数
    "emplmt_form_code": "office_employment_type",  # 勤務先　雇用形態
    "listed_division": "office_listed_division",  # 勤務先　上場区分
    "office_establishment_date": "office_establishment_date",  # 勤務先　設立年月日
    "office_prefecture_kanji": "office_prefecture_kanji",  # 勤務先　都道府県　漢字
    "office_city_kanji": "office_city_kanji",  # 勤務先　市区郡　漢字
    "office_district_kanji": "office_district_kanji",  # 勤務先　町村字丁目　漢字
    "other_office_address_kanji": "office_other_address_kanji",  # 勤務先　補足　漢字
    "office_prefecture_kana": "office_prefecture_kana",  # 勤務先　都道府県　カナ
    "office_city_kana": "office_city_kana",  # 勤務先　市区郡　カナ
    "office_district_kana": "office_district_kana",  # 勤務先　町村字丁目　カナ
    "other_office_address_kana": "office_other_address_kana",  # 勤務先　補足　カナ
    "office_postal_code": "office_postal_code",  # 勤務先　郵便番号
    "industry": "office_industry",  # 勤務先　業種
    "other_industry": "office_industry_other",  # 勤務先　業種　その他
    "occupation": "office_occupation",  # 勤務先　職業
    "other_occupation": "office_occupation_other",  # 勤務先　職業　その他
    "occupation_detail": "office_occupation_detail",  # 勤務先　職種
    "other_occupation_detail": "office_occupation_detail_other",  # 勤務先　職種　その他
    "income_source": "income_sources",  # 収入源
    "tax_return": "tax_return",  # 確定申告有無
    "type_tax_return": "tax_return_reasons",  # 確定申告理由
    "other_type_tax_return": "tax_return_reason_other",  # 確定申告理由　その他
    "maternity_paternity_leave_status": "maternity_paternity_leave",  # 産休・育休
    "maternity_paternity_leave_start_time": "maternity_paternity_leave_start_date",  # 産休・育休開始
    "maternity_paternity_leave_end_time": "maternity_paternity_leave_end_date",  # 産休・育休終了
    "nursing_leave_status": "nursing_leave",  # 介護休
    "capital_stock": "office_capital_stock",  # 勤務先　資本金
    "department": "office_department",  # 勤務先　所属部署
    "position": "office_role",  # 勤務先　役職
    "job_change": "job_change",  # 転職有無
    "job_change_company_name_kana": "job_change_office_name_kana",  # 転職前勤務先　名　カナ
    "job_change_company_name_kanji": "job_change_office_name_kanji",  # 転職前勤務先　名　漢字
    "prev_company_year_num": "prev_office_year_num",  # 転職前勤務先　勤続年数　年
    "prev_company_industry": "prev_office_industry",  # 転職前勤務先　業種
    "other_prev_company_industry": "prev_office_industry_other",  # 転職前勤務先　業種（その他）
    "transfer_office": "transfer_office",  # 出向（派遣）有無
    "transfer_office_name_kanji": "transfer_office_name_kanji",  # 出向（派遣）先　名　漢字
    "transfer_office_name_kana": "transfer_office_name_kana",  # 出向（派遣）先　名　カナ
    "transfer_office_phone_number": "transfer_office_phone",  # 出向（派遣）先　電話番号
    "transfer_office_postal_code": "transfer_office_postal_code",  # 出向（派遣）先　郵便番号
    "transfer_office_prefecture_kanji": "transfer_office_prefecture_kanji",  # 出向（派遣）先　都道府県　漢字
    "transfer_office_city_kanji": "transfer_office_city_kanji",  # 出向（派遣）先　市区郡　漢字
    "transfer_office_district_kanji": "transfer_office_district_kanji",  # 出向（派遣）先　町村字丁目　漢字
    "transfer_office_other_address_kanji": "transfer_office_other_address_kanji",  # 出向（派遣）先　補足　漢字
    "nationality": "nationality",  # 国籍
    "land_rent_to_be_paid": "rent_to_be_paid_land",  # 今回の住宅・土地取得以外の借入　地代（MCJ）
    "house_rent_to_be_paid": "rent_to_be_paid_house",  # 今回の住宅・土地取得以外の借入　家賃（MCJ）
    "identity_verification": "identity_verification_type",  # 本人確認書類タイプ
    "main_income_source": "main_income_source",  # メイン収入源　銀代入力項目
}


p_applicant_person_parameters_files = {
    "driver_license_back_image": "A__01__a",
    "driver_license_front_image": "A__01__b",
    "card_number_front_image": "A__02",
    "resident_register_back_image": "A__03__a",
    "resident_register_front_image": "A__03__b",
    "insurance_file": "B__a",
    "insurance_file_back_image": "B__b",
    "first_withholding_slip_file": "C__01",
    "second_withholding_slip_file": "C__02",
    "first_income_file": "C__03",
    "second_income_file": "C__04",
    "third_income_file": "C__05",
    "financial_statement_1_file": "D__01",
    "financial_statement_2_file": "D__02",
    "financial_statement_3_file": "D__03",
    "employment_agreement_file": "E",
    "business_tax_return_1_file": "F__01",
    "business_tax_return_2_file": "F__02",
    "business_tax_return_3_file": "F__03",
    "residence_file": "H__a",
    "residence_file_back_image": "H__b",
    "repayment_schedule_image": "I",
    "other_document_file": "K",
}


p_borrowings_parameters = {
    "borrowing_type": "type",  # お借入の種類
    "borrower": "borrower",  # 借入名義人
    "expected_repayment_date": "scheduled_loan_payoff_date",  # 完済予定年月
    "borrowing_category": "category",  # 借入区分
    "rental_room_number": "rental_room_num",  # 賃貸戸（室）数
    "common_housing": "common_housing",  # 共同住宅
    "estate_mortgage": "estate_setting",  # 不動産担保設定
    "lender": "lender",  # 借入先
    "loan_amount": "loan_amount",  # 当初借入額・借入限度額
    "current_balance_amount": "curr_loan_balance_amount",  # 借入残高・現在残高
    "loan_purpose": "loan_purpose",  # お借入の目的
    "other_purpose": "loan_purpose_other",  # お借入の目的　その他
    "specific_loan_purpose": "loan_business_target_other",  # お借入の目的　事業用のお借入　その他
    "annual_repayment_amount": "annual_repayment_amount",  # 年間返済額
    "loan_start_date": "loan_start_date",  # 当初借入年月・カード契約年月
    "loan_deadline_date": "loan_end_date",  # 最終期限・最終返済年月
    "scheduled_loan_payoff": "scheduled_loan_payoff",  # 完済予定有無
    "business_borrowing_type": "loan_business_target",  # お借入の目的　事業用のお借入
    "include_in_examination": "include_in_examination",  # 審査に含める
    "borrowing_from_housing_finance_agency": "borrowing_from_house_finance_agency",  # 住宅金融支援機構からの借入
    "card_expiry_date": "card_expiry_date",  # カード有効期限
}
