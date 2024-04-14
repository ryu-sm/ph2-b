p_application_headers_field_maps = {
    "s_sales_person_id": "s_sale_person_id",  # --業者ID
    "s_manager_id": "manager_id",  # --銀代担当者ID
    # "sales_company_id": "",  # --紹介会社ID
    # "sales_area_id": "",  #  --展示場ID
    # "sales_exhibition_hall_id": "",  #  --展示場ID
    "move_scheduled_date": "scheduled_date_moving",  #  --入居予定年月
    "loan_type": "loan_type",  #  --借入形態
    # "loan_target_type": "",  #  --借入目的
    "loan_target": "loan_target",  #  --資金使途
    "pair_loan_id": "linking_number",  #  --ペアローン相手ID
    "pair_loan_first_name": "pair_loan_applicant_first_name",  #  --ペアローン相手名
    "pair_loan_last_name": "pair_loan_applicant_last_name",  #  --ペアローン相手姓
    "pair_loan_rel": "pair_loan_relationship",  #  --ペアローン相手続柄
    "pair_loan_rel_name": "pair_loan_relationship_name",  #  --ペアローン相手続柄名称　入力項目
    "join_guarantor_umu": "has_join_guarantor",  #  --担保提供者有無
    "loan_plus": "is_home_loan_plus",  #  --住宅ローンプラス
    "land_advance_plan": "has_land_advance_plan",  #  --土地先行プラン希望
    # "curr_borrowing_status": "",  #  --現在利用中のローン 在另外的一个表里面
    "pre_examination_status": "status_result",  #  --事前審査結果
    "vendor_business_card": "",  #  --業者名刺
    "vendor_name": "",  #  --業者名　入力項目
    "vendor_phone": "",  #  --業者電話番号　入力項目
    "curr_house_residence_type": "",  #  --現居　お住まいの種類
    "curr_house_owner_rel": "",  #  -- 現居　所有者の続柄
    "curr_house_owner_name": "",  #  --現居　所有者の氏名
    "curr_house_schedule_disposal_type": "",  #  --現居　持家　処分方法
    "curr_house_schedule_disposal_type_other": "",  #  --現居　持家　処分方法　その他
    "curr_house_shell_scheduled_date": "",  #  --現居　持家　売却予定時期
    "curr_house_shell_scheduled_price": "",  #  --現居　持家　売却予定価格
    "curr_house_loan_balance_type": "",  #  --現居　持家　ローン残高有無
    "curr_house_lived_year": "",  #  --現居　居住年数　ヶ年
    "curr_house_lived_month": "",  #  --現居　居住年数　ヶ月
    "curr_house_floor_area": "",  #  --現居　床面積（MCJ）
    "new_house_self_resident": "",  #  --新居　申込人本人住居区分
    "new_house_self_not_resident_reason": "",  #  --新居　申込人本人住居しない理由
    "new_house_residence_type": "",  #  --新居　居住区分
    "new_house_acquire_reason": "",  #  --新居　申込人住宅取得理由
    "new_house_acquire_reason_other": "",  #  --新居　申込人住宅取得理由　その他
    #
    "new_house_planned_resident_overview": "",  #  --新居　申込人以外居住予定者概要
    #
    "property_type": "",  #  --物件　種類
    "property_joint_ownership_type": "",  #  --物件　共有区分
    "property_business_type": "",  #  --物件　事業性区分
    "property_publish_url": "",  #  --物件　掲載URL
    "property_postal_code": "",  #  --物件　郵便番号
    "property_prefecture": "",  #  --物件　都道府県
    "property_city": "",  #  --物件　市区町村郡
    "property_district": "",  #  --物件　以下地番
    "property_apartment_and_room_no": "",  #  --物件　マンション名・部屋番号
    "property_address_kana": "",  #  --物件　所在地　カナ
    "property_land_acquire_date": "",  #  --物件　土地取得時期
    "property_land_area": "",  #  --物件　土地の敷地面積
    "property_floor_area": "",  #  --物件　建物の延床面積
    "property_private_area": "",  #  --物件　マンションの専有面積
    "property_total_floor_area": "",  #  --物件　マンション全体の延床面積
    "property_building_ratio_numerator": "",  #  --物件　建物割合分子
    "property_building_ratio_denominator": "",  #  --物件　建物割合分母
    "property_land_ratio_numerator": "",  #  --物件　土地割合分子
    "property_land_ratio_denominator": "",  #  --物件　土地割合分母
    "property_building_price": "",  #  --物件　建物価格
    "property_land_price": "",  #  --物件　土地価格
    "property_total_price": "",  #  --物件　合計価格
    "property_land_type": "",  #  --物件　土地権利（MCJ）
    "property_purchase_type": "",  #  --物件　買戻・保留地・仮換地（MCJ）
    "property_planning_area": "",  #  --物件　都市計画区域（MCJ）
    "property_planning_area_other": "",  #  --物件　都市計画区域　その他（MCJ）
    "property_rebuilding_reason": "",  #  --物件　再建築理由（MCJ）
    "property_rebuilding_reason_other": "",  #  --物件　再建築理由　その他（MCJ）
    "property_maintenance_type": "",  #  --物件　維持保全型区分（MCJ）
    "property_flat_35_plan": "",  #  --物件　フラット35S適用プラン（MCJ）
    "property_flat_35_tech": "",  #  --物件　フラット35S技術基準（MCJ）
    "property_region_type": "",  #  --物件　地域区分（MCJ）
    "required_funds_land_amount": "",  #  --必要資金　土地価格
    "required_funds_house_amount": "",  #  --必要資金　建物・物件価格・マンション価格
    "required_funds_accessory_amount": "",  #  --必要資金　付帯設備
    "required_funds_additional_amount": "",  #  --必要資金　諸費用等
    "required_funds_refinance_loan_balance": "",  #  --必要資金　借換対象ローン残債
    "required_funds_upgrade_amount": "",  #  --必要資金　増改築
    "required_funds_loan_plus_amount": "",  #  --必要資金　住宅ローンプラス
    "required_funds_total_amount": "",  #  --必要資金　必要資金合計
    "funding_saving_amount": "",  #  --調達資金　預貯金
    "funding_other_saving_amount": "",  #  --調達資金　有価証券等
    "funding_estate_sale_amount": "",  #  --調達資金　不動産売却代金
    "funding_self_amount": "",  #  --調達資金　自己資金
    "funding_relative_donation_amount": "",  #  --調達資金　親族からの贈与
    "funding_loan_amount": "",  #  --調達資金　本件ローン
    "funding_pair_loan_amount": "",  #  --調達資金　ペアローン
    "funding_other_amount": "",  #  --調達資金　その他額
    "funding_other_amount_detail": "",  #  --調達資金　その他額名
    "funding_other_loan_amount": "",  #  --調達資金　その他の借り入れ
    "funding_other_refinance_amount": "",  #  --調達資金　その他借換
    "funding_total_amount": "",  #  --調達資金　調達資金合計
    "refund_source_type": "",  #  --完済原資　区分（MCJ）
    "refund_source_type_other": "",  #  --完済原資　区分　その他（MCJ）
    "refund_source_content": "",  #  --完済原資　内容（MCJ）
    "refund_source_amount": "",  #  --完済原資　金額（MCJ）
    "rent_to_be_paid_land": "",  #  --今回の住宅・土地取得以外の借入　地代（MCJ）
    "rent_to_be_paid_land_borrower": "",  #  --地代支払いをしている方
    "rent_to_be_paid_house": "",  #  --今回の住宅・土地取得以外の借入　家賃（MCJ）
    "rent_to_be_paid_house_borrower": "",  #  --家賃支払いをしている方
}
