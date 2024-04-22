-- CREATE SCHEMA `mortgage_staging` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;

use mortgage_staging;

SET FOREIGN_KEY_CHECKS = 0;
-- ----------------------------
-- Table structure for c_access_logs
-- ----------------------------
DROP TABLE IF EXISTS `c_access_logs`;
CREATE TABLE `c_access_logs` (
  `id` bigint unsigned NOT NULL COMMENT 'ID',
  `apply_no` varchar(14) DEFAULT NULL COMMENT '受付番号',
  `account_id` bigint unsigned DEFAULT NULL COMMENT 'アカウントID',
  `account_type` tinyint DEFAULT NULL COMMENT 'アカウント区分',
  `ip` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT 'IP',
  `operation` varchar(128) DEFAULT NULL COMMENT '操作',
  `operation_content` varchar(512) DEFAULT NULL COMMENT '操作内容',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '作成日付',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日付',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `s_access_logs_i` (`created_at`) USING BTREE
) COMMENT='アクセスログ';

-- ----------------------------
-- Table structure for c_archive_files
-- ----------------------------
DROP TABLE IF EXISTS `c_archive_files`;
CREATE TABLE `c_archive_files` (
  `id` bigint unsigned NOT NULL COMMENT 'ID',
  `s_sales_company_org_id` bigint unsigned NOT NULL COMMENT '連携先ID',
  `s_sales_person_id` bigint unsigned NOT NULL COMMENT '業者ID',
  `note` varchar(1024) DEFAULT NULL COMMENT '備考内容',
  `deleted` tinyint DEFAULT NULL COMMENT '論理削除',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '作成日付',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日付',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `c_archive_files_i` (`created_at`) USING BTREE,
  KEY `c_archive_files_fk_s_sales_company_org_id` (`s_sales_person_id`) USING BTREE,
  KEY `c_archive_files_fk_s_sales_company_orgs_id` (`s_sales_company_org_id`),
  CONSTRAINT `c_archive_files_fk_s_sales_company_orgs_id` FOREIGN KEY (`s_sales_company_org_id`) REFERENCES `s_sales_company_orgs` (`id`),
  CONSTRAINT `c_archive_files_fk_s_sales_person_id` FOREIGN KEY (`s_sales_person_id`) REFERENCES `s_sales_persons` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) COMMENT='業者共有書類';

-- ----------------------------
-- Table structure for c_archive_uploaded_files
-- ----------------------------
DROP TABLE IF EXISTS `c_archive_uploaded_files`;
CREATE TABLE `c_archive_uploaded_files` (
  `id` bigint unsigned NOT NULL COMMENT 'ID',
  `owner_id` bigint unsigned DEFAULT NULL COMMENT '所有者ID',
  `record_id` bigint unsigned DEFAULT NULL COMMENT '関連レコードID',
  `s3_key` varchar(255) DEFAULT NULL COMMENT 'S3キー',
  `file_name` varchar(255) DEFAULT NULL COMMENT 'ファイル名',
  `deleted` tinyint DEFAULT NULL COMMENT '論理削除',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '作成日付',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日付',
  PRIMARY KEY (`id`)
) COMMENT='業者共有書類アップロードファイル';

-- ----------------------------
-- Table structure for c_messages
-- ----------------------------
DROP TABLE IF EXISTS `c_messages`;
CREATE TABLE `c_messages` (
  `id` bigint unsigned NOT NULL COMMENT 'ID',
  `c_user_id` bigint unsigned DEFAULT NULL COMMENT 'ユーザーID',
  `p_application_header_id` bigint unsigned DEFAULT NULL COMMENT '案件メイン情報ID',
  `sender_type` tinyint DEFAULT NULL COMMENT '送信者区分',
  `sender_id` bigint unsigned DEFAULT NULL COMMENT '送信者ID',
  `content` varchar(255) DEFAULT NULL COMMENT 'メッセージ内容',
  `viewed` json DEFAULT NULL COMMENT '既読',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '作成日付',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日付',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `c_messages_i` (`created_at`) USING BTREE,
  KEY `c_messages_fk_p_application_header_id` (`p_application_header_id`) USING BTREE,
  CONSTRAINT `c_messages_fk_p_application_header_id` FOREIGN KEY (`p_application_header_id`) REFERENCES `p_application_headers` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) COMMENT='チャットメッセージ';

-- ----------------------------
-- Table structure for c_users
-- ----------------------------
DROP TABLE IF EXISTS `c_users`;
CREATE TABLE `c_users` (
  `id` bigint unsigned NOT NULL COMMENT 'ID',
  `email` varchar(128) NOT NULL COMMENT 'Eメール',
  `hashed_pwd` varchar(128) NOT NULL COMMENT 'パスワード',
  `s_sales_company_org_id` bigint unsigned DEFAULT NULL COMMENT 'QRコードから組織ID',
  `agent_sended` tinyint DEFAULT '0' COMMENT '銀行送信区分',
  `status` tinyint NOT NULL DEFAULT '1' COMMENT '状態',
  `failed_time` tinyint DEFAULT '0' COMMENT 'ログイン失敗回数',
  `failed_first_at` datetime DEFAULT NULL COMMENT 'ログイン失敗初回日付',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '作成日付',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日付',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `c_users_i` (`created_at`) USING BTREE,
  KEY `c_users_fk_s_sales_company_org_id` (`s_sales_company_org_id`) USING BTREE,
  CONSTRAINT `c_users_fk_s_sales_company_org_id` FOREIGN KEY (`s_sales_company_org_id`) REFERENCES `s_sales_company_orgs` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) COMMENT='ユーザー';

-- ----------------------------
-- Table structure for p_activities
-- ----------------------------
DROP TABLE IF EXISTS `p_activities`;
CREATE TABLE `p_activities` (
  `id` bigint unsigned NOT NULL COMMENT 'ID',
  `p_application_header_id` bigint unsigned DEFAULT NULL COMMENT '案件ID',
  `operator_type` tinyint DEFAULT NULL COMMENT '操作者区分',
  `operator_id` bigint unsigned DEFAULT NULL COMMENT '操作者ID',
  `table_name` varchar(255) DEFAULT NULL COMMENT 'テーブル名',
  `field_name` varchar(255) DEFAULT NULL COMMENT 'フィールド名',
  `table_id` bigint unsigned DEFAULT NULL COMMENT 'テーブルID',
  `content` varchar(1024) DEFAULT NULL COMMENT '内容',
  `operate_type` tinyint DEFAULT NULL COMMENT '操作種類',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '作成日付',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日付',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `p_activities_i` (`created_at`) USING BTREE,
  KEY `p_activities_fk_p_application_header_id` (`p_application_header_id`) USING BTREE,
  CONSTRAINT `p_activities_fk_p_application_header_id` FOREIGN KEY (`p_application_header_id`) REFERENCES `p_application_headers` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) COMMENT='案件更新履歴';

-- ----------------------------
-- Table structure for p_applicant_persons
-- ----------------------------
DROP TABLE IF EXISTS `p_applicant_persons`;
CREATE TABLE `p_applicant_persons` (
  `id` bigint unsigned NOT NULL COMMENT 'ID',
  `p_application_header_id` bigint unsigned NOT NULL COMMENT '案件メイン情報ID',
  `type` tinyint NOT NULL COMMENT '申込者や連帯債務者区分',
  `rel_to_applicant_a_name` varchar(48) DEFAULT NULL COMMENT '連帯債務者　申込者に対して続柄名　入力項目',
  `rel_to_applicant_a` tinyint DEFAULT NULL COMMENT '連帯債務者　申込者に対して続柄',
  `rel_to_applicant_a_other` varchar(100) DEFAULT NULL COMMENT '連帯債務者　申込者に対して続柄　その他',
  `identity_verification_type` tinyint DEFAULT NULL COMMENT '本人確認書類タイプ',
  `first_name_kanji` varchar(48) DEFAULT NULL COMMENT '名　漢字',
  `last_name_kanji` varchar(48) DEFAULT NULL COMMENT '姓　漢字',
  `first_name_kana` varchar(48) DEFAULT NULL COMMENT '名　カナ',
  `last_name_kana` varchar(48) DEFAULT NULL COMMENT '姓　カナ',
  `gender` tinyint DEFAULT NULL COMMENT '性別',
  `birthday` date DEFAULT NULL COMMENT '生年月日',
  `nationality` tinyint DEFAULT '1' COMMENT '国籍',
  `spouse` tinyint DEFAULT NULL COMMENT '配偶者有無',
  `mobile_phone` varchar(17) DEFAULT NULL COMMENT '携帯電話番号',
  `home_phone` varchar(17) DEFAULT NULL COMMENT '自宅電話番号',
  `emergency_contact` varchar(17) DEFAULT NULL COMMENT '緊急連絡先',
  `email` varchar(128) DEFAULT NULL COMMENT 'Eメール',
  `postal_code` varchar(8) DEFAULT NULL COMMENT '郵便番号',
  `prefecture_kanji` varchar(20) DEFAULT NULL COMMENT '都道府県　漢字',
  `city_kanji` varchar(20) DEFAULT NULL COMMENT '市区郡　漢字',
  `district_kanji` varchar(40) DEFAULT NULL COMMENT '町村字丁目　漢字',
  `other_address_kanji` varchar(99) DEFAULT NULL COMMENT '補足　漢字',
  `prefecture_kana` varchar(20) DEFAULT NULL COMMENT '都道府県　カナ',
  `city_kana` varchar(20) DEFAULT NULL COMMENT '市区郡　カナ',
  `district_kana` varchar(30) DEFAULT NULL COMMENT '町村字丁目　カナ',
  `other_address_kana` varchar(138) DEFAULT NULL COMMENT '補足　カナ',
  `last_year_income` bigint DEFAULT NULL COMMENT '前年年収　総額',
  `last_year_bonus_income` bigint DEFAULT NULL COMMENT '前年年収　総額内ボーナス分（MCJ）',
  `before_last_year_income` bigint DEFAULT NULL COMMENT '前々年度年収 （MCJ固有項目）',
  `income_sources` json DEFAULT NULL COMMENT '収入源',
  `main_income_source` tinyint DEFAULT NULL COMMENT 'メイン収入源　銀代入力項目',
  `tax_return` tinyint DEFAULT NULL COMMENT '確定申告有無',
  `tax_return_reasons` json DEFAULT NULL COMMENT '確定申告理由',
  `tax_return_reason_other` varchar(50) DEFAULT NULL COMMENT '確定申告理由　その他',
  `maternity_paternity_leave` tinyint DEFAULT NULL COMMENT '産休・育休',
  `maternity_paternity_leave_start_date` varchar(7) DEFAULT NULL COMMENT '産休・育休開始',
  `maternity_paternity_leave_end_date` varchar(7) DEFAULT NULL COMMENT '産休・育休終了',
  `nursing_leave` tinyint DEFAULT NULL COMMENT '介護休',
  `office_name_kanji` varchar(48) DEFAULT NULL COMMENT '勤務先　名　漢字',
  `office_name_kana` varchar(48) DEFAULT NULL COMMENT '勤務先　名　カナ',
  `office_capital_stock` bigint DEFAULT NULL COMMENT '勤務先　資本金',
  `office_listed_division` tinyint DEFAULT NULL COMMENT '勤務先　上場区分',
  `office_employee_num` int DEFAULT NULL COMMENT '勤務先　従業員数',
  `office_establishment_date` date DEFAULT NULL COMMENT '勤務先　設立年月日',
  `office_phone` varchar(17) DEFAULT NULL COMMENT '勤務先　電話番号',
  `office_head_location` varchar(30) DEFAULT NULL COMMENT '勤務先　本社所在地',
  `office_postal_code` varchar(8) DEFAULT NULL COMMENT '勤務先　郵便番号',
  `office_prefecture_kanji` varchar(20) DEFAULT NULL COMMENT '勤務先　都道府県　漢字',
  `office_city_kanji` varchar(20) DEFAULT NULL COMMENT '勤務先　市区郡　漢字',
  `office_district_kanji` varchar(40) DEFAULT NULL COMMENT '勤務先　町村字丁目　漢字',
  `office_other_address_kanji` varchar(99) DEFAULT NULL COMMENT '勤務先　補足　漢字',
  `office_prefecture_kana` varchar(20) DEFAULT NULL COMMENT '勤務先　都道府県　カナ',
  `office_city_kana` varchar(20) DEFAULT NULL COMMENT '勤務先　市区郡　カナ',
  `office_district_kana` varchar(30) DEFAULT NULL COMMENT '勤務先　町村字丁目　カナ',
  `office_other_address_kana` varchar(138) DEFAULT NULL COMMENT '勤務先　補足　カナ',
  `office_occupation` tinyint DEFAULT NULL COMMENT '勤務先　職業',
  `office_occupation_other` varchar(40) DEFAULT NULL COMMENT '勤務先　職業　その他',
  `office_industry` tinyint DEFAULT NULL COMMENT '勤務先　業種',
  `office_industry_other` varchar(40) DEFAULT NULL COMMENT '勤務先　業種　その他',
  `office_occupation_detail` tinyint DEFAULT NULL COMMENT '勤務先　職種',
  `office_occupation_detail_other` varchar(40) DEFAULT NULL COMMENT '勤務先　職種　その他',
  `office_joining_date` varchar(7) DEFAULT NULL COMMENT '勤務先　入社年月',
  `office_department` varchar(46) DEFAULT NULL COMMENT '勤務先　所属部署',
  `office_employment_type` tinyint DEFAULT NULL COMMENT '勤務先　雇用形態',
  `office_role` tinyint DEFAULT NULL COMMENT '勤務先　役職',
  `transfer_office` tinyint DEFAULT NULL COMMENT '出向（派遣）有無',
  `transfer_office_name_kanji` varchar(48) DEFAULT NULL COMMENT '出向（派遣）先　名　漢字',
  `transfer_office_name_kana` varchar(48) DEFAULT NULL COMMENT '出向（派遣）先　名　カナ',
  `transfer_office_phone` varchar(17) DEFAULT NULL COMMENT '出向（派遣）先　電話番号',
  `transfer_office_postal_code` varchar(8) DEFAULT NULL COMMENT '出向（派遣）先　郵便番号',
  `transfer_office_prefecture_kanji` varchar(20) DEFAULT NULL COMMENT '出向（派遣）先　都道府県　漢字',
  `transfer_office_city_kanji` varchar(20) DEFAULT NULL COMMENT '出向（派遣）先　市区郡　漢字',
  `transfer_office_district_kanji` varchar(40) DEFAULT NULL COMMENT '出向（派遣）先　町村字丁目　漢字',
  `transfer_office_other_address_kanji` varchar(99) DEFAULT NULL COMMENT '出向（派遣）先　補足　漢字',
  `job_change` tinyint DEFAULT NULL COMMENT '転職有無',
  `job_change_office_name_kana` varchar(48) DEFAULT NULL COMMENT '転職前勤務先　名　カナ',
  `job_change_office_name_kanji` varchar(48) DEFAULT NULL COMMENT '転職前勤務先　名　漢字',
  `prev_office_year_num` tinyint DEFAULT NULL COMMENT '転職前勤務先　勤続年数　年',
  `prev_office_industry` tinyint DEFAULT NULL COMMENT '転職前勤務先　業種',
  `prev_office_industry_other` varchar(40) DEFAULT NULL COMMENT '転職前勤務先　業種（その他）',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '作成日付',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日付',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `p_applicant_persons_i` (`created_at`) USING BTREE,
  KEY `p_applicant_persons_fk_p_application_header_id` (`p_application_header_id`) USING BTREE,
  CONSTRAINT `p_applicant_persons_fk_p_application_header_id` FOREIGN KEY (`p_application_header_id`) REFERENCES `p_application_headers` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) COMMENT='申込者・連帯債務者';

-- ----------------------------
-- Table structure for p_application_banks
-- ----------------------------
DROP TABLE IF EXISTS `p_application_banks`;
CREATE TABLE `p_application_banks` (
  `id` bigint unsigned NOT NULL COMMENT 'ID',
  `p_application_header_id` bigint unsigned NOT NULL COMMENT '案件メイン情報ID',
  `s_bank_id` bigint unsigned NOT NULL COMMENT '銀行ID',
  `provisional_status` tinyint DEFAULT NULL COMMENT '仮審査ステータス',
  `provisional_result` tinyint DEFAULT NULL COMMENT '仮審査結果',
  `provisional_after_result` tinyint DEFAULT NULL COMMENT '仮審査後結果',
  `soudan_no` varchar(10) DEFAULT NULL COMMENT '相談番号',
  `delivery_date` datetime DEFAULT NULL COMMENT '送付日付',
  `interface_status` tinyint DEFAULT NULL COMMENT 'IF連携結果',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '作成日付',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日付',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `p_application_banks_i` (`created_at`) USING BTREE,
  KEY `p_application_banks_fk_application_header_id` (`p_application_header_id`) USING BTREE,
  KEY `p_application_banks_fk_s_bank_id` (`s_bank_id`) USING BTREE,
  CONSTRAINT `p_application_banks_fk_application_header_id` FOREIGN KEY (`p_application_header_id`) REFERENCES `p_application_headers` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `p_application_banks_fk_s_bank_id` FOREIGN KEY (`s_bank_id`) REFERENCES `s_banks` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) COMMENT='申込銀行';

-- ----------------------------
-- Table structure for p_application_headers
-- ----------------------------
DROP TABLE IF EXISTS `p_application_headers`;
CREATE TABLE `p_application_headers` (
  `id` bigint unsigned NOT NULL COMMENT 'ID',
  `c_user_id` bigint unsigned DEFAULT NULL COMMENT 'ユーザーID',
  `s_sales_person_id` bigint unsigned DEFAULT NULL COMMENT '業者ID',
  `s_manager_id` bigint unsigned DEFAULT NULL COMMENT '銀代担当者ID',
  `sales_company_id` bigint unsigned DEFAULT NULL COMMENT '紹介会社ID',
  `sales_area_id` bigint unsigned DEFAULT NULL COMMENT 'エリアID',
  `sales_exhibition_hall_id` bigint unsigned DEFAULT NULL COMMENT '展示場ID',
  `apply_no` varchar(14) DEFAULT NULL COMMENT '受付番号',
  `apply_date` date DEFAULT NULL COMMENT '申込日兼同意日',
  `move_scheduled_date` varchar(7) DEFAULT NULL COMMENT '入居予定年月',
  `loan_type` tinyint DEFAULT NULL COMMENT '借入形態',
  `loan_target_type` tinyint DEFAULT '0' COMMENT '借入目的',
  `loan_target` tinyint DEFAULT NULL COMMENT '資金使途',
  `pair_loan_id` bigint unsigned DEFAULT NULL COMMENT 'ペアローン相手ID',
  `pair_loan_first_name` varchar(48) DEFAULT NULL COMMENT 'ペアローン相手名',
  `pair_loan_last_name` varchar(48) DEFAULT NULL COMMENT 'ペアローン相手姓',
  `pair_loan_rel` tinyint DEFAULT NULL COMMENT 'ペアローン相手続柄',
  `pair_loan_rel_name` varchar(48) DEFAULT NULL COMMENT 'ペアローン相手続柄名称　入力項目',
  `join_guarantor_umu` tinyint DEFAULT NULL COMMENT '担保提供者有無',
  `loan_plus` tinyint DEFAULT NULL COMMENT '住宅ローンプラス',
  `land_advance_plan` tinyint DEFAULT NULL COMMENT '土地先行プラン希望',
  `curr_borrowing_status` tinyint DEFAULT NULL COMMENT '現在利用中のローン',
  `pre_examination_status` tinyint DEFAULT NULL COMMENT '事前審査結果',
  `vendor_business_card` tinyint DEFAULT NULL COMMENT '業者名刺',
  `vendor_name` varchar(48) DEFAULT NULL COMMENT '業者名　入力項目',
  `vendor_phone` varchar(17) DEFAULT NULL COMMENT '業者電話番号　入力項目',
  `curr_house_residence_type` tinyint DEFAULT NULL COMMENT '現居　お住まいの種類',
  `curr_house_owner_rel` varchar(40) DEFAULT NULL COMMENT '現居　所有者の続柄',
  `curr_house_owner_name` varchar(96) DEFAULT NULL COMMENT '現居　所有者の氏名',
  `curr_house_schedule_disposal_type` tinyint DEFAULT NULL COMMENT '現居　持家　処分方法',
  `curr_house_schedule_disposal_type_other` varchar(40) DEFAULT NULL COMMENT '現居　持家　処分方法　その他',
  `curr_house_shell_scheduled_date` varchar(7) DEFAULT NULL COMMENT '現居　持家　売却予定時期',
  `curr_house_shell_scheduled_price` bigint DEFAULT NULL COMMENT '現居　持家　売却予定価格',
  `curr_house_loan_balance_type` tinyint DEFAULT NULL COMMENT '現居　持家　ローン残高有無',
  `curr_house_lived_year` int DEFAULT NULL COMMENT '現居　居住年数　ヶ年',
  `curr_house_lived_month` int DEFAULT NULL COMMENT '現居　居住年数　ヶ月',
  `curr_house_floor_area` decimal(9,2) DEFAULT NULL COMMENT '現居　床面積（MCJ）',
  `new_house_self_resident` tinyint DEFAULT NULL COMMENT '新居　申込人本人住居区分',
  `new_house_self_not_resident_reason` varchar(40) DEFAULT NULL COMMENT '新居　申込人本人住居しない理由',
  `new_house_residence_type` tinyint DEFAULT NULL COMMENT '新居　居住区分',
  `new_house_acquire_reason` tinyint DEFAULT NULL COMMENT '新居　申込人住宅取得理由',
  `new_house_acquire_reason_other` varchar(40) DEFAULT NULL COMMENT '新居　申込人住宅取得理由　その他',
  `new_house_planned_resident_overview` json DEFAULT NULL COMMENT '新居　申込人以外居住予定者概要',
  `property_type` tinyint DEFAULT NULL COMMENT '物件　種類',
  `property_joint_ownership_type` varchar(255) DEFAULT NULL COMMENT '物件　共有区分',
  `property_business_type` json DEFAULT NULL COMMENT '物件　事業性区分',
  `property_publish_url` varchar(512) DEFAULT NULL COMMENT '物件　掲載URL',
  `property_postal_code` varchar(8) DEFAULT NULL COMMENT '物件　郵便番号',
  `property_prefecture` varchar(20) DEFAULT NULL COMMENT '物件　都道府県',
  `property_city` varchar(20) DEFAULT NULL COMMENT '物件　市区町村郡',
  `property_district` varchar(30) DEFAULT NULL COMMENT '物件　以下地番',
  `property_apartment_and_room_no` varchar(40) DEFAULT NULL COMMENT '物件　マンション名・部屋番号',
  `property_address_kana` varchar(40) DEFAULT NULL COMMENT '物件　所在地　カナ',
  `property_land_acquire_date` date DEFAULT NULL COMMENT '物件　土地取得時期',
  `property_land_area` decimal(9,2) DEFAULT NULL COMMENT '物件　土地の敷地面積',
  `property_floor_area` decimal(9,2) DEFAULT NULL COMMENT '物件　建物の延床面積',
  `property_private_area` decimal(9,2) DEFAULT NULL COMMENT '物件　マンションの専有面積',
  `property_total_floor_area` decimal(9,2) DEFAULT NULL COMMENT '物件　マンション全体の延床面積',
  `property_building_ratio_numerator` bigint DEFAULT NULL COMMENT '物件　建物割合分子',
  `property_building_ratio_denominator` bigint DEFAULT NULL COMMENT '物件　建物割合分母',
  `property_land_ratio_numerator` bigint DEFAULT NULL COMMENT '物件　土地割合分子',
  `property_land_ratio_denominator` bigint DEFAULT NULL COMMENT '物件　土地割合分母',
  `property_building_price` bigint DEFAULT NULL COMMENT '物件　建物価格',
  `property_land_price` bigint DEFAULT NULL COMMENT '物件　土地価格',
  `property_total_price` bigint DEFAULT NULL COMMENT '物件　合計価格',
  `property_land_type` tinyint DEFAULT NULL COMMENT '物件　土地権利（MCJ）',
  `property_purchase_type` tinyint DEFAULT NULL COMMENT '物件　買戻・保留地・仮換地（MCJ）',
  `property_planning_area` tinyint DEFAULT NULL COMMENT '物件　都市計画区域（MCJ）',
  `property_planning_area_other` varchar(128) DEFAULT NULL COMMENT '物件　都市計画区域　その他（MCJ）',
  `property_rebuilding_reason` tinyint DEFAULT NULL COMMENT '物件　再建築理由（MCJ）',
  `property_rebuilding_reason_other` varchar(128) DEFAULT NULL COMMENT '物件　再建築理由　その他（MCJ）',
  `property_maintenance_type` tinyint DEFAULT NULL COMMENT '物件　維持保全型区分（MCJ）',
  `property_flat_35_plan` tinyint DEFAULT NULL COMMENT '物件　フラット35S適用プラン（MCJ）',
  `property_flat_35_tech` tinyint DEFAULT NULL COMMENT '物件　フラット35S技術基準（MCJ）',
  `property_region_type` tinyint DEFAULT NULL COMMENT '物件　地域区分（MCJ）',
  `required_funds_land_amount` bigint DEFAULT NULL COMMENT '必要資金　土地価格',
  `required_funds_house_amount` bigint DEFAULT NULL COMMENT '必要資金　建物・物件価格・マンション価格',
  `required_funds_accessory_amount` bigint DEFAULT NULL COMMENT '必要資金　付帯設備',
  `required_funds_additional_amount` bigint DEFAULT NULL COMMENT '必要資金　諸費用等',
  `required_funds_refinance_loan_balance` bigint DEFAULT NULL COMMENT '必要資金　借換対象ローン残債',
  `required_funds_upgrade_amount` bigint DEFAULT NULL COMMENT '必要資金　増改築',
  `required_funds_loan_plus_amount` bigint DEFAULT NULL COMMENT '必要資金　住宅ローンプラス',
  `required_funds_total_amount` bigint DEFAULT NULL COMMENT '必要資金　必要資金合計',
  `funding_saving_amount` bigint DEFAULT NULL COMMENT '調達資金　預貯金',
  `funding_other_saving_amount` bigint DEFAULT NULL COMMENT '調達資金　有価証券等',
  `funding_estate_sale_amount` bigint DEFAULT NULL COMMENT '調達資金　不動産売却代金',
  `funding_self_amount` bigint DEFAULT NULL COMMENT '調達資金　自己資金',
  `funding_relative_donation_amount` bigint DEFAULT NULL COMMENT '調達資金　親族からの贈与',
  `funding_loan_amount` bigint DEFAULT NULL COMMENT '調達資金　本件ローン',
  `funding_pair_loan_amount` bigint DEFAULT NULL COMMENT '調達資金　ペアローン',
  `funding_other_amount` bigint DEFAULT NULL COMMENT '調達資金　その他額',
  `funding_other_amount_detail` varchar(48) DEFAULT NULL COMMENT '調達資金　その他額名',
  `funding_other_loan_amount` bigint DEFAULT NULL COMMENT '調達資金　その他の借り入れ',
  `funding_other_refinance_amount` bigint DEFAULT NULL COMMENT '調達資金　その他借換',
  `funding_total_amount` bigint DEFAULT NULL COMMENT '調達資金　調達資金合計',
  `refund_source_type` json DEFAULT NULL COMMENT '完済原資　区分（MCJ）',
  `refund_source_type_other` varchar(40) DEFAULT NULL COMMENT '完済原資　区分　その他（MCJ）',
  `refund_source_content` varchar(20) DEFAULT NULL COMMENT '完済原資　内容（MCJ）',
  `refund_source_amount` bigint DEFAULT NULL COMMENT '完済原資　金額（MCJ）',
  `rent_to_be_paid_land` bigint DEFAULT NULL COMMENT '今回の住宅・土地取得以外の借入　地代（MCJ）',
  `rent_to_be_paid_land_borrower` tinyint DEFAULT NULL COMMENT '地代支払いをしている方',
  `rent_to_be_paid_house` bigint DEFAULT NULL COMMENT '今回の住宅・土地取得以外の借入　家賃（MCJ）',
  `rent_to_be_paid_house_borrower` tinyint DEFAULT NULL COMMENT '家賃支払いをしている方',
  `approver_confirmation` tinyint DEFAULT NULL COMMENT '承認者確認',
  `unsubcribed` tinyint DEFAULT NULL COMMENT '退会区分',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '作成日付',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日付',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `p_application_headers_i` (`created_at`) USING BTREE,
  KEY `p_application_headers_fk_c_user_id` (`c_user_id`) USING BTREE,
  KEY `p_application_headers_fk_s_sales_person_id` (`s_sales_person_id`) USING BTREE,
  KEY `p_application_headers_fk_s_manager_id` (`s_manager_id`) USING BTREE,
  KEY `p_application_headers_fk_s_sales_company_org_id` (`sales_company_id`) USING BTREE,
  CONSTRAINT `p_application_headers_fk_c_user_id` FOREIGN KEY (`c_user_id`) REFERENCES `c_users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `p_application_headers_fk_s_manager_id` FOREIGN KEY (`s_manager_id`) REFERENCES `s_managers` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `p_application_headers_fk_s_sales_company_org_id` FOREIGN KEY (`sales_company_id`) REFERENCES `s_sales_company_orgs` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `p_application_headers_fk_s_sales_person_id` FOREIGN KEY (`s_sales_person_id`) REFERENCES `s_sales_persons` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) COMMENT='案件メイン情報';

-- ----------------------------
-- Table structure for p_bank_api_send_histories
-- ----------------------------
DROP TABLE IF EXISTS `p_bank_api_send_histories`;
CREATE TABLE `p_bank_api_send_histories` (
  `id` bigint unsigned NOT NULL COMMENT 'ID',
  `p_application_bank_id` bigint unsigned NOT NULL COMMENT '申込銀行ID',
  `set_num` varchar(12) DEFAULT NULL COMMENT 'SET番号',
  `request_number` varchar(17) DEFAULT NULL COMMENT '申込認識番号',
  `pair_loan_id` bigint unsigned DEFAULT NULL COMMENT 'ペアローン相手ID',
  `request_body` json DEFAULT NULL COMMENT 'リクエストボディ',
  `status_code` char(3) DEFAULT NULL COMMENT 'ステータスコード',
  `response_body` json DEFAULT NULL COMMENT 'レスポンスボディ',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '作成日付',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日付',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `p_bank_api_send_histories_id` (`created_at`) USING BTREE,
  KEY `p_bank_api_send_histories` (`p_application_bank_id`) USING BTREE,
  CONSTRAINT `p_bank_api_send_histories` FOREIGN KEY (`p_application_bank_id`) REFERENCES `p_application_banks` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) COMMENT='銀行API送信履歴';

-- ----------------------------
-- Table structure for p_borrowing_details
-- ----------------------------
DROP TABLE IF EXISTS `p_borrowing_details`;
CREATE TABLE `p_borrowing_details` (
  `id` bigint unsigned NOT NULL COMMENT 'ID',
  `p_application_header_id` bigint unsigned NOT NULL COMMENT '案件メイン情報ID',
  `time_type` tinyint DEFAULT NULL COMMENT '回目区分',
  `desired_borrowing_date` date DEFAULT NULL COMMENT '借入希望日',
  `desired_loan_amount` bigint DEFAULT NULL COMMENT '借入希望額',
  `bonus_repayment_amount` bigint DEFAULT NULL COMMENT 'ボーナス返済分',
  `bonus_repayment_month` tinyint DEFAULT NULL COMMENT 'ボーナス返済月',
  `repayment_method` tinyint DEFAULT NULL COMMENT '返済方法',
  `loan_term_year` int DEFAULT NULL COMMENT '借入期間　ヶ年',
  `loan_term_month` int DEFAULT NULL COMMENT '借入期間　ヶ月',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '作成日付',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日付',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `p_borrowing_details_i` (`created_at`) USING BTREE,
  KEY `p_borrowing_details_fk_p_application_header_id` (`p_application_header_id`) USING BTREE,
  CONSTRAINT `p_borrowing_details_fk_p_application_header_id` FOREIGN KEY (`p_application_header_id`) REFERENCES `p_application_headers` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) COMMENT='借入内容明細';

-- ----------------------------
-- Table structure for p_borrowings
-- ----------------------------
DROP TABLE IF EXISTS `p_borrowings`;
CREATE TABLE `p_borrowings` (
  `id` bigint unsigned NOT NULL COMMENT 'ID',
  `p_application_header_id` bigint unsigned NOT NULL COMMENT '案件メイン情報ID',
  `self_input` tinyint DEFAULT NULL COMMENT '入力タイプ',
  `type` tinyint DEFAULT NULL COMMENT 'お借入の種類',
  `category` tinyint DEFAULT NULL COMMENT '借入区分',
  `borrower` tinyint DEFAULT NULL COMMENT '借入名義人',
  `lender` varchar(40) DEFAULT NULL COMMENT '借入先',
  `loan_amount` bigint DEFAULT NULL COMMENT '当初借入額・借入限度額',
  `curr_loan_balance_amount` bigint DEFAULT NULL COMMENT '借入残高・現在残高',
  `annual_repayment_amount` bigint DEFAULT NULL COMMENT '年間返済額',
  `loan_purpose` tinyint DEFAULT NULL COMMENT 'お借入の目的　カードローン・キャッシング等',
  `loan_purpose_other` varchar(40) DEFAULT NULL COMMENT 'お借入の目的　カードローン・キャッシング等　その他',
  `loan_start_date` varchar(7) DEFAULT NULL COMMENT '当初借入年月・カード契約年月',
  `loan_end_date` varchar(7) DEFAULT NULL COMMENT '最終期限・最終返済年月',
  `card_expiry_date` varchar(7) DEFAULT NULL COMMENT 'カード有効期限',
  `scheduled_loan_payoff` tinyint DEFAULT NULL COMMENT '完済予定有無',
  `scheduled_loan_payoff_date` varchar(7) DEFAULT NULL COMMENT '完済予定年月',
  `loan_business_target` tinyint DEFAULT NULL COMMENT 'お借入の目的　事業用のお借入',
  `loan_business_target_other` varchar(40) DEFAULT NULL COMMENT 'お借入の目的　事業用のお借入　その他',
  `include_in_examination` tinyint DEFAULT NULL COMMENT '審査に含める',
  `rental_room_num` int DEFAULT NULL COMMENT '賃貸戸（室）数',
  `common_housing` tinyint DEFAULT NULL COMMENT '共同住宅',
  `estate_setting` tinyint DEFAULT NULL COMMENT '不動産担保設定',
  `borrowing_from_house_finance_agency` tinyint DEFAULT NULL COMMENT '住宅金融支援機構からの借入',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '作成日付',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日付',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `p_borrowings_i` (`created_at`) USING BTREE,
  KEY `p_borrowings_fk_p_application_header_id` (`p_application_header_id`) USING BTREE,
  CONSTRAINT `p_borrowings_fk_p_application_header_id` FOREIGN KEY (`p_application_header_id`) REFERENCES `p_application_headers` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) COMMENT='現在借入情報';

-- ----------------------------
-- Table structure for p_drafts
-- ----------------------------
DROP TABLE IF EXISTS `p_drafts`;
CREATE TABLE `p_drafts` (
  `id` bigint unsigned NOT NULL COMMENT 'ID',
  `c_user_id` bigint unsigned DEFAULT NULL COMMENT 'ユーザーID',
  `data` json DEFAULT NULL COMMENT 'データー',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '作成日付',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日付',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `p_drafts_i` (`created_at`) USING BTREE,
  KEY `p_drafts_fk_c_user_id` (`c_user_id`) USING BTREE,
  CONSTRAINT `p_drafts_fk_c_user_id` FOREIGN KEY (`c_user_id`) REFERENCES `c_users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) COMMENT='ドラフト';

-- ----------------------------
-- Table structure for p_examine_status_error_logs
-- ----------------------------
DROP TABLE IF EXISTS `p_examine_status_error_logs`;
CREATE TABLE `p_examine_status_error_logs` (
  `id` bigint unsigned NOT NULL COMMENT 'ID',
  `p_application_bank_id` bigint unsigned NOT NULL COMMENT '申込銀行ID',
  `s3_key` varchar(128) NOT NULL COMMENT 's3キー',
  `s3_bucket` varchar(128) NOT NULL COMMENT 's3バケット',
  `request_no` varchar(17) DEFAULT NULL COMMENT '申込認識番号',
  `error_detail` json NOT NULL COMMENT 'エラー',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '作成日付',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日付',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `p_examine_status_error_logs_i` (`created_at`) USING BTREE,
  KEY `p_examine_status_error_logs_fk_p_application_bank_id` (`p_application_bank_id`) USING BTREE,
  CONSTRAINT `p_examine_status_error_logs_fk_p_application_bank_id` FOREIGN KEY (`p_application_bank_id`) REFERENCES `p_application_banks` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) COMMENT='審査スターテスエラーログ';

-- ----------------------------
-- Table structure for p_examine_status_histories
-- ----------------------------
DROP TABLE IF EXISTS `p_examine_status_histories`;
CREATE TABLE `p_examine_status_histories` (
  `p_application_bank_id` bigint unsigned NOT NULL COMMENT '申込銀行ID',
  `status` tinyint NOT NULL COMMENT '審査状態',
  `status_origin` json DEFAULT NULL COMMENT '審査状態源',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '作成日付',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日付',
  PRIMARY KEY (`p_application_bank_id`,`status`) USING BTREE,
  KEY `p_examine_status_histories_i` (`created_at`) USING BTREE,
  CONSTRAINT `p_examine_status_histories_fk_p_application_bank_id` FOREIGN KEY (`p_application_bank_id`) REFERENCES `p_application_banks` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) COMMENT='審査状態履歴';

-- ----------------------------
-- Table structure for p_join_guarantors
-- ----------------------------
DROP TABLE IF EXISTS `p_join_guarantors`;
CREATE TABLE `p_join_guarantors` (
  `id` bigint unsigned NOT NULL COMMENT 'ID',
  `p_application_header_id` bigint unsigned NOT NULL COMMENT '案件メイン情報ID',
  `rel_to_applicant_a_name` varchar(48) DEFAULT NULL COMMENT '申込人に対して続柄名',
  `rel_to_applicant_a` tinyint DEFAULT NULL COMMENT '申込人に対して続柄',
  `rel_to_applicant_a_other` varchar(20) DEFAULT NULL COMMENT '申込人に対して続柄　その他',
  `first_name_kanji` varchar(48) DEFAULT NULL COMMENT '名　漢字',
  `last_name_kanji` varchar(48) DEFAULT NULL COMMENT '姓　漢字',
  `first_name_kana` varchar(48) DEFAULT NULL COMMENT '名　カナ',
  `last_name_kana` varchar(48) DEFAULT NULL COMMENT '姓　カナ',
  `gender` tinyint DEFAULT NULL COMMENT '性別',
  `birthday` date DEFAULT NULL COMMENT '生年月日',
  `mobile_phone` varchar(17) DEFAULT NULL COMMENT '携帯電話番号',
  `home_phone` varchar(17) DEFAULT NULL COMMENT '自宅電話番号',
  `emergency_contact` varchar(17) DEFAULT NULL COMMENT '緊急連絡先',
  `email` varchar(128) DEFAULT NULL COMMENT 'Eメール',
  `postal_code` varchar(8) DEFAULT NULL COMMENT '郵便番号',
  `prefecture_kanji` varchar(20) DEFAULT NULL COMMENT '都道府県　漢字',
  `city_kanji` varchar(20) DEFAULT NULL COMMENT '市区郡　漢字',
  `district_kanji` varchar(40) DEFAULT NULL COMMENT '町村字丁目　漢字',
  `other_address_kanji` varchar(99) DEFAULT NULL COMMENT '補足　漢字',
  `prefecture_kana` varchar(20) DEFAULT NULL COMMENT '都道府県　カナ',
  `city_kana` varchar(20) DEFAULT NULL COMMENT '市区郡　カナ',
  `district_kana` varchar(30) DEFAULT NULL COMMENT '町村字丁目　カナ',
  `other_address_kana` varchar(138) DEFAULT NULL COMMENT '補足住所　カナ',
  `last_year_income` bigint DEFAULT NULL COMMENT '前年年収',
  `work_name_kanji` varchar(40) DEFAULT NULL COMMENT '勤務先　名称　漢字',
  `work_name_kana` varchar(40) DEFAULT NULL COMMENT '勤務先　名称　カナ',
  `work_office_phone` varchar(17) DEFAULT NULL COMMENT '勤務先　電話番号',
  `work_postal_code` varchar(8) DEFAULT NULL COMMENT '勤務先　郵便番号',
  `work_address_kanji` varchar(99) DEFAULT NULL COMMENT '勤務先　住所　漢字',
  `work_address_kana` varchar(138) DEFAULT NULL COMMENT '勤務先　住所　カナ',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '作成日付',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日付',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `p_join_guarantors_i` (`created_at`) USING BTREE,
  KEY `p_join_guarantors_fk_p_application_header_id` (`p_application_header_id`) USING BTREE,
  CONSTRAINT `p_join_guarantors_fk_p_application_header_id` FOREIGN KEY (`p_application_header_id`) REFERENCES `p_application_headers` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) COMMENT='担保提供者';

-- ----------------------------
-- Table structure for p_memos
-- ----------------------------
DROP TABLE IF EXISTS `p_memos`;
CREATE TABLE `p_memos` (
  `id` bigint unsigned NOT NULL COMMENT 'ID',
  `p_application_header_id` bigint unsigned NOT NULL COMMENT '案件メイン情報ID',
  `s_manager_id` bigint unsigned DEFAULT NULL COMMENT '業者ID',
  `content` varchar(1024) DEFAULT NULL COMMENT '内容',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '作成日付',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新日付',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `p_memos_i` (`created_at`) USING BTREE,
  KEY `p_memos_fk_p_application_header_id` (`p_application_header_id`) USING BTREE,
  KEY `p_memos_fk_ s_manager_id` (`s_manager_id`) USING BTREE,
  CONSTRAINT `p_memos_fk_ s_manager_id` FOREIGN KEY (`s_manager_id`) REFERENCES `s_managers` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `p_memos_fk_p_application_header_id` FOREIGN KEY (`p_application_header_id`) REFERENCES `p_application_headers` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) COMMENT='案件メモ';

-- ----------------------------
-- Table structure for p_residents
-- ----------------------------
DROP TABLE IF EXISTS `p_residents`;
CREATE TABLE `p_residents` (
  `id` bigint unsigned NOT NULL COMMENT 'ID',
  `p_application_header_id` bigint unsigned DEFAULT NULL COMMENT '案件メイン情報ID',
  `one_roof` tinyint DEFAULT NULL COMMENT '申込人と同居有無',
  `rel_to_applicant_a_name` varchar(48) DEFAULT NULL COMMENT '申込人に対して相手続柄名　入力項目',
  `rel_to_applicant_a` tinyint DEFAULT NULL COMMENT '申込人に対して相手続柄',
  `rel_to_applicant_a_other` varchar(40) DEFAULT NULL COMMENT '申込人に対して相手続柄　その他',
  `last_name_kanji` varchar(48) DEFAULT NULL COMMENT '姓　漢字',
  `first_name_kanji` varchar(48) DEFAULT NULL COMMENT '名　漢字',
  `last_name_kana` varchar(48) DEFAULT NULL COMMENT '姓　カナ',
  `first_name_kana` varchar(48) DEFAULT NULL COMMENT '名　カナ',
  `gender` tinyint DEFAULT NULL COMMENT '性別',
  `birthday` date DEFAULT NULL COMMENT '生年月日',
  `nationality` tinyint DEFAULT NULL COMMENT '国籍',
  `contact_phone` varchar(17) DEFAULT NULL COMMENT '電話番号',
  `postal_code` varchar(255) DEFAULT NULL COMMENT '郵便番号',
  `prefecture_kanji` varchar(255) DEFAULT NULL COMMENT '都道府県　漢字',
  `city_kanji` varchar(255) DEFAULT NULL COMMENT '市区郡／市区町村　漢字',
  `district_kanji` varchar(255) DEFAULT NULL COMMENT '町村字丁目／丁目･番地･号　漢字',
  `other_address_kanji` varchar(255) DEFAULT NULL COMMENT '補足／建物名･部屋番号等　漢字',
  `prefecture_kana` varchar(255) DEFAULT NULL COMMENT '都道府県　カナ',
  `city_kana` varchar(255) DEFAULT NULL COMMENT '市区郡／市区町村　カナ',
  `district_kana` varchar(255) DEFAULT NULL COMMENT '町村字丁目／丁目･番地･号　カナ',
  `other_address_kana` varchar(255) DEFAULT NULL COMMENT '補足／建物名･部屋番号等　カナ',
  `loan_from_japan_house_finance_agency` tinyint DEFAULT NULL COMMENT '住宅金融支援機構（旧：公庫）からの融資の有無',
  `resident_type` tinyint DEFAULT '1' COMMENT '入居予定者代表の区分',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '作成日付',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日付',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `p_residents_i` (`created_at`) USING BTREE,
  KEY `p_residents_fk_application_header_id` (`p_application_header_id`) USING BTREE,
  CONSTRAINT `p_residents_fk_application_header_id` FOREIGN KEY (`p_application_header_id`) REFERENCES `p_application_headers` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) COMMENT='居住予定者詳細';

-- ----------------------------
-- Table structure for p_uploaded_files
-- ----------------------------
DROP TABLE IF EXISTS `p_uploaded_files`;
CREATE TABLE `p_uploaded_files` (
  `id` bigint unsigned NOT NULL COMMENT 'ID',
  `owner_type` tinyint DEFAULT NULL COMMENT '所有者区分',
  `owner_id` bigint unsigned DEFAULT NULL COMMENT '所有者ID',
  `p_application_header_id` bigint unsigned DEFAULT NULL COMMENT '案件メイン情報ID',
  `record_id` bigint unsigned DEFAULT NULL COMMENT '関連レコードID',
  `type` varchar(1) DEFAULT NULL COMMENT '区分',
  `s3_key` varchar(255) DEFAULT NULL COMMENT 'S3キー',
  `file_name` varchar(255) DEFAULT NULL COMMENT 'ファイル名',
  `deleted` tinyint DEFAULT NULL COMMENT '論理削除',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '作成日付',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日付',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `p_uploaded_files_i` (`created_at`) USING BTREE
) COMMENT='案件書類';

-- ----------------------------
-- Table structure for s_banks
-- ----------------------------
DROP TABLE IF EXISTS `s_banks`;
CREATE TABLE `s_banks` (
  `id` bigint unsigned NOT NULL COMMENT 'ID',
  `name` varchar(40) NOT NULL COMMENT '名称',
  `name_kana` varchar(40) NOT NULL COMMENT '名称　カナ',
  `code` varchar(10) NOT NULL COMMENT 'コード',
  `interest_rate` decimal(5,3) DEFAULT NULL COMMENT '適用金利',
  `type_export` tinyint DEFAULT NULL COMMENT '送付方法',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '作成日付',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日付',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `s_banks` (`created_at`) USING BTREE
) COMMENT='銀行マスター';

-- ----------------------------
-- Table structure for s_dynamic_options
-- ----------------------------
DROP TABLE IF EXISTS `s_dynamic_options`;
CREATE TABLE `s_dynamic_options` (
  `id` bigint unsigned NOT NULL COMMENT 'ID',
  `field_name_ja` varchar(50) DEFAULT NULL COMMENT '項目名(日本語)',
  `field_name_en` varchar(50) DEFAULT NULL COMMENT '項目名(英語)',
  `option_name` varchar(50) DEFAULT NULL COMMENT 'オップション名',
  `option_code` tinyint DEFAULT NULL COMMENT 'オップションコード',
  `sort_order` tinyint DEFAULT NULL COMMENT '順番',
  `display_flg` tinyint DEFAULT NULL COMMENT '表示フラッグ',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '作成日付',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日付',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `s_dynamic_options_i` (`created_at`) USING BTREE
) COMMENT='オープション管理';

-- ----------------------------
-- Table structure for s_if_configs
-- ----------------------------
DROP TABLE IF EXISTS `s_if_configs`;
CREATE TABLE `s_if_configs` (
  `id` bigint unsigned NOT NULL COMMENT 'ID',
  `s_bank_id` bigint unsigned NOT NULL COMMENT '銀行ID',
  `field_name` varchar(255) NOT NULL COMMENT 'フィールド',
  `to_10000_unit` tinyint DEFAULT NULL COMMENT '万単位',
  `min_length` int DEFAULT NULL COMMENT '最小長',
  `max_length` int DEFAULT NULL COMMENT '最大長',
  `min_value` bigint DEFAULT NULL COMMENT '最小値',
  `max_value` bigint DEFAULT NULL COMMENT '最大値',
  `to_han` tinyint DEFAULT NULL COMMENT '半角',
  `to_zen` tinyint DEFAULT NULL COMMENT '全角',
  `regex` varchar(255) DEFAULT NULL COMMENT '正規表現',
  `module` varchar(255) DEFAULT NULL COMMENT 'モジュール',
  `mapping` json DEFAULT NULL COMMENT 'マッピング',
  `is_required` tinyint DEFAULT NULL COMMENT '必須',
  `date_format` varchar(64) DEFAULT NULL COMMENT '日付形式',
  `data_origin` json DEFAULT NULL COMMENT 'データ源',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '作成日付',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日付',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `s_if_configs_i` (`created_at`) USING BTREE,
  KEY `s_if_configs_fk_s_bank_id` (`s_bank_id`) USING BTREE,
  CONSTRAINT `s_if_configs_fk_s_bank_id` FOREIGN KEY (`s_bank_id`) REFERENCES `s_banks` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) COMMENT='インターフェイス設定';

-- ----------------------------
-- Table structure for s_managers
-- ----------------------------
DROP TABLE IF EXISTS `s_managers`;
CREATE TABLE `s_managers` (
  `id` bigint unsigned NOT NULL COMMENT 'ID',
  `email` varchar(128) NOT NULL COMMENT 'Eメール',
  `hashed_pwd` varchar(128) NOT NULL COMMENT 'パスワード',
  `name_kanji` varchar(48) NOT NULL COMMENT '名前　漢字',
  `role` tinyint NOT NULL COMMENT '役割',
  `status` tinyint NOT NULL COMMENT '状態',
  `failed_time` tinyint DEFAULT '0' COMMENT 'ログイン失敗回数',
  `failed_first_at` datetime DEFAULT NULL COMMENT 'ログイン失敗初回日付',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '作成日付',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日付',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `s_managers_i` (`created_at`) USING BTREE
) COMMENT='銀代担当者';

-- ----------------------------
-- Table structure for s_sales_company_orgs
-- ----------------------------
DROP TABLE IF EXISTS `s_sales_company_orgs`;
CREATE TABLE `s_sales_company_orgs` (
  `id` bigint unsigned NOT NULL COMMENT 'ID',
  `pid` bigint unsigned DEFAULT NULL COMMENT '親ID',
  `category` varchar(1) DEFAULT NULL COMMENT '区分',
  `code` varchar(10) DEFAULT NULL COMMENT 'コード',
  `name` varchar(48) NOT NULL COMMENT '名称',
  `contact_phone1` varchar(17) DEFAULT NULL COMMENT '電話番号1',
  `contact_phone2` varchar(17) DEFAULT NULL COMMENT '電話番号2',
  `fax` varchar(17) DEFAULT NULL COMMENT 'FAX',
  `upload_file` tinyint DEFAULT '1' COMMENT '書類アップロード',
  `display_pdf` tinyint DEFAULT '1' COMMENT '結果PDF閲覧',
  `status` tinyint DEFAULT '1' COMMENT '状態',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '作成日付',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日付',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `s_sale_company_orgs_i` (`created_at`) USING BTREE
) COMMENT='販売会社組織階層';

-- ----------------------------
-- Table structure for s_sales_person_s_sales_company_org_rels
-- ----------------------------
DROP TABLE IF EXISTS `s_sales_person_s_sales_company_org_rels`;
CREATE TABLE `s_sales_person_s_sales_company_org_rels` (
  `s_sales_person_id` bigint unsigned NOT NULL COMMENT '業者ID',
  `s_sales_company_org_id` bigint unsigned NOT NULL COMMENT '組織階層ID',
  `role` tinyint NOT NULL COMMENT '役割',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '作成日付',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日付',
  PRIMARY KEY (`s_sales_person_id`,`s_sales_company_org_id`,`role`) USING BTREE,
  KEY `s_sale_person_s_sale_company_org_rels_i` (`created_at`) USING BTREE,
  KEY `rels_fk_s_sales_company_org_id` (`s_sales_company_org_id`) USING BTREE,
  CONSTRAINT `rels_fk_s_sales_company_org_id` FOREIGN KEY (`s_sales_company_org_id`) REFERENCES `s_sales_company_orgs` (`id`),
  CONSTRAINT `rels_fk_s_sales_person_id` FOREIGN KEY (`s_sales_person_id`) REFERENCES `s_sales_persons` (`id`)
) COMMENT='業者・販売会社組織階層関係';

-- ----------------------------
-- Table structure for s_sales_persons
-- ----------------------------
DROP TABLE IF EXISTS `s_sales_persons`;
CREATE TABLE `s_sales_persons` (
  `id` bigint unsigned NOT NULL COMMENT 'ID',
  `code` varchar(20) NOT NULL COMMENT 'コード',
  `email` varchar(128) NOT NULL COMMENT 'Eメール',
  `name_kanji` varchar(48) NOT NULL COMMENT '名前　漢字',
  `direct_phone` varchar(17) DEFAULT NULL COMMENT '直通番号',
  `mobile_phone` varchar(17) DEFAULT NULL COMMENT '携帯番号',
  `fax` varchar(17) DEFAULT NULL COMMENT 'FAX',
  `hashed_pwd` varchar(128) DEFAULT NULL COMMENT 'パスワード',
  `status` tinyint NOT NULL COMMENT '状態',
  `failed_time` tinyint DEFAULT NULL COMMENT 'ログイン失敗回数',
  `failed_first_at` datetime DEFAULT NULL COMMENT 'ログイン失敗初回日付',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '作成日付',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日付',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `s_sales_persons_i` (`created_at`) USING BTREE
) COMMENT='業者';

SET FOREIGN_KEY_CHECKS = 1;