use mortgage_staging;
SET FOREIGN_KEY_CHECKS = 0;


ALTER TABLE s_sales_company_orgs ADD COLUMN old_id bigINT;
ALTER TABLE s_sales_company_orgs ADD COLUMN path VARCHAR(255);
ALTER TABLE s_sales_persons ADD COLUMN old_id bigINT;
ALTER TABLE s_banks ADD COLUMN old_id bigINT;
ALTER TABLE s_managers ADD COLUMN old_id bigINT;
ALTER TABLE c_users ADD COLUMN old_id bigINT;
ALTER TABLE p_application_headers ADD COLUMN old_id bigINT;
ALTER TABLE p_application_headers ADD COLUMN old_user_id bigINT;
ALTER TABLE p_application_headers ADD COLUMN application_status INT;
ALTER TABLE p_application_headers ADD COLUMN provisional_result INT;
ALTER TABLE p_application_headers ADD COLUMN soudan_no bigINT;
ALTER TABLE p_application_headers ADD COLUMN under_review_status INT;
ALTER TABLE p_application_headers ADD COLUMN interface_status INT;
ALTER TABLE p_application_headers ADD COLUMN send_date datetime;
ALTER TABLE p_applicant_persons ADD COLUMN old_id bigINT;

ALTER TABLE p_applicant_persons ADD COLUMN p_borrowing_details INT;
ALTER TABLE p_applicant_persons ADD COLUMN p_borrowings INT;
ALTER TABLE p_applicant_persons ADD COLUMN p_drafts INT;
ALTER TABLE p_applicant_persons ADD COLUMN p_join_guarantors INT;
ALTER TABLE p_applicant_persons ADD COLUMN p_memos INT;
ALTER TABLE p_applicant_persons ADD COLUMN p_residents INT;

ALTER TABLE p_application_banks ADD COLUMN old_header_id INT;
ALTER TABLE p_application_banks ADD COLUMN bank_code varchar(10);


/*
ALTER TABLE s_sales_company_orgs DROP COLUMN old_id ;
ALTER TABLE s_sales_company_orgs DROP COLUMN path ;
ALTER TABLE s_sales_persons DROP COLUMN old_id ;
ALTER TABLE s_banks DROP COLUMN old_id ;
ALTER TABLE s_managers DROP COLUMN old_id ;
ALTER TABLE c_users DROP COLUMN old_id ;
ALTER TABLE p_application_headers DROP COLUMN old_id ;
ALTER TABLE p_application_headers DROP COLUMN old_user_id ;
ALTER TABLE p_application_headers DROP COLUMN application_status;
ALTER TABLE p_application_headers DROP COLUMN provisional_result ;
ALTER TABLE p_application_headers DROP COLUMN soudan_no ;
ALTER TABLE p_application_headers DROP COLUMN under_review_status ;
ALTER TABLE p_application_headers DROP COLUMN interface_status ;
ALTER TABLE p_application_headers DROP COLUMN send_date ;
ALTER TABLE p_applicant_persons DROP COLUMN old_id ;

ALTER TABLE p_applicant_persons DROP COLUMN p_borrowing_details ;
ALTER TABLE p_applicant_persons DROP COLUMN p_borrowings ;
ALTER TABLE p_applicant_persons DROP COLUMN p_drafts ;
ALTER TABLE p_applicant_persons DROP COLUMN p_join_guarantors ;
ALTER TABLE p_applicant_persons DROP COLUMN p_memos ;
ALTER TABLE p_applicant_persons DROP COLUMN p_residents ;

ALTER TABLE p_application_banks DROP COLUMN old_header_id ;
ALTER TABLE p_application_banks DROP COLUMN bank_code ;
*/

-- １，販売会社組織階層　データ移行
-- 1.1 既存データ削除
truncate table s_sales_company_orgs;
-- 1.2 ホールディングス　処理
insert into s_sales_company_orgs (
	id    --  ID        
	,pid    --  親ID        
	,category    --  category        
	,code    --  コード        
	,name    --  名称        
	,contact_phone1    --  電話番号1        
	,contact_phone2    --  電話番号2        
	,fax    --  FAX        1: アップロード
	,upload_file    --  書類アップロード        1: アップロード
	,display_pdf    --  結果PDF閲覧        1:結果PDF閲覧
	,status    --  状態        1: 正常; 2: ロック
	,created_at    --  作成日付        
	,updated_at    --  更新日付        
    ,path
    ,old_id
)
select 
	UUID_SHORT() as id    --  ID
	,null as pid    --  親ID
	,'H' as category    --  category
	,ra.name_id as code    --  コード
	,ra.name_kanji as name    --  名称
	,ra.phone_number as contact_phone1    --  電話番号1
	,ra.phone_number_2 as contact_phone2    --  電話番号2
	,ra.fax_number as fax    --  FAX
	,ra.edit_file_upload as upload_file    --  書類アップロード 1: アップロード
	,ra.display_pdf as display_pdf    --  結果PDF閲覧 1:結果PDF閲覧
	,1 as status    --  状態 1: 正常; 2: ロック
	,ra.created_at    --  作成日付
	,ra.updated_at    --  更新日付
    ,concat(ra.name_id, case  when ra.sale_agent_id is not  null and ra.sale_agent_id !='' then concat('/',ra.sale_agent_id) else '' end
	, case  when ra.store_id is not  null and ra.store_id !='' then concat('/',ra.store_id) else '' end
    , case  when ra.sale_office_id is not  null and ra.sale_office_id !='' then concat('/',ra.sale_office_id) else '' end
    , case  when ra.exhibition_id is not  null and ra.exhibition_id !='' then concat('/',ra.exhibition_id) else '' end
	)  as path
    ,ra.id as old_id
FROM mortgage_loan_tool_be_production.p_referral_agencies ra
where ra.name_id <>'' and ra.name_id is not null and ra.sale_agent_id is null
order by ra.id
;
-- 1.3 販売会社　処理
insert into s_sales_company_orgs (
	id    --  ID
	,pid    --  親ID
	,category    --  category
	,code    --  コード
	,name    --  名称
	,contact_phone1    --  電話番号1
	,contact_phone2    --  電話番号2
	,fax    --  FAX
	,upload_file    --  書類アップロード
	,display_pdf    --  結果PDF閲覧
	,status    --  状態
	,created_at    --  作成日付
	,updated_at    --  更新日付
    ,path
    ,old_id
)
SELECT 
	UUID_SHORT() as id    --  ID
	,sco.id as pid    --  親ID
	,'C' as category    --  category
	,ra.sale_agent_id as code    --  コード
	,ra.sale_agent_name_kanji as name    --  名称
	,ra.phone_number as contact_phone1    --  電話番号1
	,ra.phone_number_2 as contact_phone2    --  電話番号2
	,ra.fax_number as fax    --  FAX
	,ra.edit_file_upload as upload_file    --  書類アップロード 1: アップロード
	,ra.display_pdf as display_pdf    --  結果PDF閲覧 1:結果PDF閲覧
	,1 as status    --  状態 1: 正常; 2: ロック
	,ra.created_at    --  作成日付
	,ra.updated_at    --  更新日付
	,concat(ra.name_id, case  when ra.sale_agent_id is not  null and ra.sale_agent_id !='' then concat('/',ra.sale_agent_id) else '' end
	, case  when ra.store_id is not  null and ra.store_id !='' then concat('/',ra.store_id) else '' end
    , case  when ra.sale_office_id is not  null and ra.sale_office_id !='' then concat('/',ra.sale_office_id) else '' end
    , case  when ra.exhibition_id is not  null and ra.exhibition_id !='' then concat('/',ra.exhibition_id) else '' end
	)  as path
    ,ra.id as old_id
FROM s_sales_company_orgs sco
 inner join mortgage_loan_tool_be_production.p_referral_agencies ra
  on sco.code=ra.name_id and ra.sale_agent_id is not null and ra.store_id is null
     and concat(ra.name_id, case  when ra.sale_agent_id is not  null and ra.sale_agent_id !='' then concat('/',ra.sale_agent_id) else '' end
	, case  when ra.store_id is not  null and ra.store_id !='' then concat('/',ra.store_id) else '' end
    , case  when ra.sale_office_id is not  null and ra.sale_office_id !='' then concat('/',ra.sale_office_id) else '' end
    , case  when ra.exhibition_id is not  null and ra.exhibition_id !='' then concat('/',ra.exhibition_id) else '' end
	) like concat(sco.path,'%')
order by ra.id
;
-- 1.4 支店　処理
insert into s_sales_company_orgs (
	id    --  ID
	,pid    --  親ID
	,category    --  category
	,code    --  コード
	,name    --  名称
	,contact_phone1    --  電話番号1
	,contact_phone2    --  電話番号2
	,fax    --  FAX
	,upload_file    --  書類アップロード
	,display_pdf    --  結果PDF閲覧
	,status    --  状態
	,created_at    --  作成日付
	,updated_at    --  更新日付
    ,path
    ,old_id
)
SELECT 
	UUID_SHORT() as id    --  ID
	,sco.id as pid    --  親ID
	,'B' as category    --  category
	,ra.store_id as code    --  コード
	,ra.store_name_kanji as name    --  名称
	,ra.phone_number as contact_phone1    --  電話番号1
	,ra.phone_number_2 as contact_phone2    --  電話番号2
	,ra.fax_number as fax    --  FAX
	,ra.edit_file_upload as upload_file    --  書類アップロード 1: アップロード
	,ra.display_pdf as display_pdf    --  結果PDF閲覧 1:結果PDF閲覧
	,1 as status    --  状態 1: 正常; 2: ロック
	,ra.created_at    --  作成日付
	,ra.updated_at    --  更新日付
	,concat(ra.name_id, case  when ra.sale_agent_id is not  null and ra.sale_agent_id !='' then concat('/',ra.sale_agent_id) else '' end
	, case  when ra.store_id is not  null and ra.store_id !='' then concat('/',ra.store_id) else '' end
    , case  when ra.sale_office_id is not  null and ra.sale_office_id !='' then concat('/',ra.sale_office_id) else '' end
    , case  when ra.exhibition_id is not  null and ra.exhibition_id !='' then concat('/',ra.exhibition_id) else '' end
	)  as path
    ,ra.id as old_id
FROM s_sales_company_orgs sco
 inner join mortgage_loan_tool_be_production.p_referral_agencies ra
  on sco.code=ra.sale_agent_id and ra.store_id is not null and ra.sale_office_id is null
     and concat(ra.name_id, case  when ra.sale_agent_id is not  null and ra.sale_agent_id !='' then concat('/',ra.sale_agent_id) else '' end
	, case  when ra.store_id is not  null and ra.store_id !='' then concat('/',ra.store_id) else '' end
    , case  when ra.sale_office_id is not  null and ra.sale_office_id !='' then concat('/',ra.sale_office_id) else '' end
    , case  when ra.exhibition_id is not  null and ra.exhibition_id !='' then concat('/',ra.exhibition_id) else '' end
	) like concat(sco.path,'%')
order by ra.id
;
-- 1.5 Office　処理
insert into s_sales_company_orgs (
	id    --  ID
	,pid    --  親ID
	,category    --  category
	,code    --  コード
	,name    --  名称
	,contact_phone1    --  電話番号1
	,contact_phone2    --  電話番号2
	,fax    --  FAX
	,upload_file    --  書類アップロード
	,display_pdf    --  結果PDF閲覧
	,status    --  状態
	,created_at    --  作成日付
	,updated_at    --  更新日付
    ,path
    ,old_id
)
SELECT 
	UUID_SHORT() as id    --  ID
	,sco.id as pid    --  親ID
	,'O' as category    --  category
	,ra.sale_office_id as code    --  コード
	,ra.sale_office_name as name    --  名称
	,ra.phone_number as contact_phone1    --  電話番号1
	,ra.phone_number_2 as contact_phone2    --  電話番号2
	,ra.fax_number as fax    --  FAX
	,ra.edit_file_upload as upload_file    --  書類アップロード 1: アップロード
	,ra.display_pdf as display_pdf    --  結果PDF閲覧 1:結果PDF閲覧
	,1 as status    --  状態 1: 正常; 2: ロック
	,ra.created_at    --  作成日付
	,ra.updated_at    --  更新日付
	,concat(ra.name_id, case  when ra.sale_agent_id is not  null and ra.sale_agent_id !='' then concat('/',ra.sale_agent_id) else '' end
	, case  when ra.store_id is not  null and ra.store_id !='' then concat('/',ra.store_id) else '' end
    , case  when ra.sale_office_id is not  null and ra.sale_office_id !='' then concat('/',ra.sale_office_id) else '' end
    , case  when ra.exhibition_id is not  null and ra.exhibition_id !='' then concat('/',ra.exhibition_id) else '' end
	)  as path
    ,ra.id as old_id
FROM s_sales_company_orgs sco
 inner join mortgage_loan_tool_be_production.p_referral_agencies ra
  on sco.code=ra.store_id and ra.sale_office_id is not null and ra.exhibition_id is null
   and concat(ra.name_id, case  when ra.sale_agent_id is not  null and ra.sale_agent_id !='' then concat('/',ra.sale_agent_id) else '' end
	, case  when ra.store_id is not  null and ra.store_id !='' then concat('/',ra.store_id) else '' end
    , case  when ra.sale_office_id is not  null and ra.sale_office_id !='' then concat('/',ra.sale_office_id) else '' end
    , case  when ra.exhibition_id is not  null and ra.exhibition_id !='' then concat('/',ra.exhibition_id) else '' end
	) like concat(sco.path,'%')
order by ra.id
;
-- 1.6 展示場　処理
insert into s_sales_company_orgs (
	id    --  ID
	,pid    --  親ID
	,category    --  category
	,code    --  コード
	,name    --  名称
	,contact_phone1    --  電話番号1
	,contact_phone2    --  電話番号2
	,fax    --  FAX
	,upload_file    --  書類アップロード
	,display_pdf    --  結果PDF閲覧
	,status    --  状態
	,created_at    --  作成日付
	,updated_at    --  更新日付
    ,path
    ,old_id
)
SELECT 
	UUID_SHORT() as id    --  ID
	,sco.id as pid    --  親ID
	,'E' as category    --  category
	,ra.exhibition_id as code    --  コード
	,ra.exhibition_hall as name    --  名称
	,ra.phone_number as contact_phone1    --  電話番号1
	,ra.phone_number_2 as contact_phone2    --  電話番号2
	,ra.fax_number as fax    --  FAX
	,ra.edit_file_upload as upload_file    --  書類アップロード 1: アップロード
	,ra.display_pdf as display_pdf    --  結果PDF閲覧 1:結果PDF閲覧
	,1 as status    --  状態 1: 正常; 2: ロック　　→　１固定
	,ra.created_at    --  作成日付
	,ra.updated_at    --  更新日付
	,concat(ra.name_id, case  when ra.sale_agent_id is not  null and ra.sale_agent_id !='' then concat('/',ra.sale_agent_id) else '' end
	, case  when ra.store_id is not  null and ra.store_id !='' then concat('/',ra.store_id) else '' end
    , case  when ra.sale_office_id is not  null and ra.sale_office_id !='' then concat('/',ra.sale_office_id) else '' end
    , case  when ra.exhibition_id is not  null and ra.exhibition_id !='' then concat('/',ra.exhibition_id) else '' end
	)  as path
    ,ra.id as old_id
FROM s_sales_company_orgs sco
 inner join mortgage_loan_tool_be_production.p_referral_agencies ra
  on sco.code=ra.sale_office_id and ra.exhibition_id is not null
     and concat(ra.name_id, case  when ra.sale_agent_id is not  null and ra.sale_agent_id !='' then concat('/',ra.sale_agent_id) else '' end
	, case  when ra.store_id is not  null and ra.store_id !='' then concat('/',ra.store_id) else '' end
    , case  when ra.sale_office_id is not  null and ra.sale_office_id !='' then concat('/',ra.sale_office_id) else '' end
    , case  when ra.exhibition_id is not  null and ra.exhibition_id !='' then concat('/',ra.exhibition_id) else '' end
	) like concat(sco.path,'%')
order by ra.id
;

-- 2. 業者 s_sales_persons
truncate table s_sales_persons;
insert into s_sales_persons
(
	id    --  ID
	,code    --  コード
	,email    --  Eメール
	,name_kanji    --  名前　漢字
	,direct_phone    --  直通番号
	,mobile_phone    --  携帯番号
	,fax    --  FAX
	,hashed_pwd    --  パスワード
	,status    --  状態　　１：正常；２：ロック
	,failed_time    --  ログイン失敗回数
	,failed_first_at    --  ログイン失敗初回日付
	,created_at    --  作成日付
	,updated_at    --  更新日付
    ,old_id
)
select 
	UUID_SHORT() as id    --  ID
	,sp.sale_person_code as code    --  コード
	,sp.email as email    --  Eメール
	,sp.name_kanji as name_kanji    --  名前　漢字
	,sp.phone_number as direct_phone    --  直通番号
	,sp.mobile_phone_number as mobile_phone    --  携帯番号
	,sp.fax_number as fax    --  FAX
	,sp.encrypted_password as hashed_pwd    --  パスワード
	,case when locked_at is not null then 2 else 1 end as status    --  　　状態 　　　　→　　１：正常；２：ロック
	,sp.failed_attempts as failed_time    --  ログイン失敗回数
	,sp.first_failed_attempt_at as failed_first_at    --  ログイン失敗初回日付
	,sp.created_at    --  作成日付
	,sp.updated_at    --  更新日付
    ,sp.id as old_id
from mortgage_loan_tool_be_production.s_sale_persons sp
order by sp.id
;


-- 3. 業者・販売会社組織階層関係 s_sales_person_s_sales_company_org_rels 
truncate table s_sales_person_s_sales_company_org_rels;
insert into s_sales_person_s_sales_company_org_rels
(
	s_sales_person_id    --  業者ID
	,s_sales_company_org_id    --  組織階層ID
	,role    --  役割 1: 一般; 9: 管理
	,created_at    --  作成日付
	,updated_at    --  更新日付
)
select 
	sp.id as s_sales_person_id    --  業者ID
	,sco.id as s_sales_company_org_id    --  組織階層ID
	,(case when hu.role=1 then 9 else 1 end) as role    --  役割 {admin: 1, general_account: 2}　　→　 1: 一般; 9: 管理
	,hu.created_at    --  作成日付
	,hu.updated_at    --  更新日付
from mortgage_loan_tool_be_production.sale_company_hierarchy_users hu
	inner join s_sales_persons sp
      on hu.s_sale_person_id=sp.old_id
	inner join s_sales_company_orgs sco
      on hu.path=sco.path
order by hu.id
;

-- 4. 銀代担当者	s_managers
truncate table s_managers;
insert into s_managers
(
	id    --  ID
	,email    --  Eメール
	,hashed_pwd    --  パスワード
	,name_kanji    --  名前　漢字
	,role    --  役割 1: 一般; 9: 管理
	,status    --  状態 1: 正常; 2: ロック
	,failed_time    --  ログイン失敗回数
	,failed_first_at    --  ログイン失敗初回日付
	,created_at    --  作成日付
	,updated_at    --  更新日付
    ,old_id
)
select 
	UUID_SHORT() as id    --  ID
	,m.email    --  Eメール
	,m.encrypted_password as hashed_pwd    --  パスワード
	,m.name_kanji as name_kanji    --  名前　漢字
	,(case when m.role=1 then 9 else 1 end) as role    --  役割  admin: 1, general_account: 2  →　1: 一般; 9: 管理
	,case when m.locked_at is not null then 2 else 1 end as status    --  状態    →　1: 正常; 2: ロック
	,m.failed_attempts as failed_time    --  ログイン失敗回数 
	,m.first_failed_attempt_at as failed_first_at    --  ログイン失敗初回日付
	,m.created_at    --  作成日付
	,m.updated_at    --  更新日付
    ,m.id as old_id
from mortgage_loan_tool_be_production.managers m
order by m.id
;

-- 5. 銀行マスター s_banks
truncate table s_banks;
insert into s_banks
(
	id    --  ID
	,name    --  名称
	,name_kana    --  名称　カナ
	,code    --  コード
	,interest_rate    --  適用金利
	,type_export    --  送付方法
	,created_at    --  作成日付
	,updated_at    --  更新日付
    ,old_id
)
select 
	UUID_SHORT() as id    --  ID
	,mb.name as name    --  名称
	,mb.name_kana as name_kana    --  名称　カナ
	,mb.code as code    --  コード
	,mb.interest_rate as interest_rate    --  適用金利
	,mb.type_export as type_export    --  送付方法
	,mb.created_at    --  作成日付
	,mb.updated_at    --  更新日付
    ,mb.id as old_id
from mortgage_loan_tool_be_production.s_master_banks mb
order by mb.id
;


-- 6. ユーザー c_users
truncate table c_users;
insert into c_users
(
	id    --  ID
	,email    --  Eメール
	,hashed_pwd    --  パスワード
	,s_sales_company_org_id    --  QRコードから組織ID
	,agent_sended    --  銀行送信区分 ０：未送信；１：送信
	,status    --  状態 １：正常；２：ロック
	,failed_time    --  ログイン失敗回数
	,failed_first_at    --  ログイン失敗初回日付
	,created_at    --  作成日付
	,updated_at    --  更新日付
    ,old_id
)
select 
	UUID_SHORT() as id    --  ID
	,u.email    --  Eメール
	,u.encrypted_password as hashed_pwd    --  パスワード
	,sco.id as s_sales_company_org_id    --  QRコードから組織ID
	,null as agent_sended    --  銀行送信区分 　　→　
	,1 as status    --  状態　１：正常；２：ロック　　　→　　1固定
	,u.failed_attempts as failed_time    --  ログイン失敗回数
	,u.first_failed_attempt_at as failed_first_at    --  ログイン失敗初回日付
	,u.created_at    --  作成日付
	,u.updated_at    --  更新日付
    ,u.id as old_id
from mortgage_loan_tool_be_production.users u
 left join s_sales_company_orgs sco
   on sco.path like concat(case when u.sale_agent_id is not null then concat('%/',u.sale_agent_id) else '' end,case when u.store_id is not null then concat('/',u.store_id) else '' end,case when u.exhibition_id is not null then concat('/%/',u.exhibition_id) else '' end)
order by u.id
;
-- 7. 案件メイン情報	p_application_headers
truncate table p_application_headers;
insert into p_application_headers (
	id    --  ID        
	,c_user_id    --  ユーザーID        
	,s_sales_person_id    --  業者ID        
	,s_manager_id    --  銀代担当者ID        
	,sales_company_id    --  紹介会社ID        
	,sales_area_id    --  エリアID        
	,sales_exhibition_hall_id    --  展示場ID        
	,apply_no    --  受付番号        
	,apply_date    --  申込日兼同意日        
	,move_scheduled_date    --  入居予定年月        
	,loan_type    --  借入形態        1: おひとり; 2: ペアローン; 3: 収入合算（持分あり）; 4: 収入合算（持分なし）
	,loan_target_type    --  借入目的        0: 物件の購入・建築 ; 7: お借り換え; 8: 増改築（借り換え有）
	,loan_target    --  資金使途        7: お借り換え; 8: 増改築（借り換え有）; 1: 建売住宅の購入; 6: 土地を購入後に建物新築; 5: 建物だけ新築(既に土地をお持ちの方); 2: 中古住宅の購入; 3: 新築マンションの購入; 4: 中古マンションの購入
	,pair_loan_id    --  ペアローン相手ID        
	,pair_loan_first_name    --  ペアローン相手名        
	,pair_loan_last_name    --  ペアローン相手姓        
	,pair_loan_rel    --  ペアローン相手続柄        1:配偶者 ; 2:婚約者 ; 3:親 ; 4:子 ; 99: その他
	,pair_loan_rel_name    --  ペアローン相手続柄名称　入力項目        
	,join_guarantor_umu    --  担保提供者有無        1: 有
	,loan_plus    --  住宅ローンプラス        1: 申し込む
	,land_advance_plan    --  土地先行プラン希望        1: 希望する; 0: 希望しない
	,curr_borrowing_status    --  現在利用中のローン        1: 有; 0: 無
	,pre_examination_status    --  事前審査結果        0: 書類確認; 1: 書類不備対応中; 2: 内容確認; 3: 承認; 4: 銀行へデータ連携; 5: 提携会社へ審査結果公開; 6: 申込人へ審査結果公開
	,vendor_business_card    --  業者名刺        1: はい; 0: いいえ
	,vendor_name    --  業者名　入力項目        
	,vendor_phone    --  業者電話番号　入力項目        
	,curr_house_residence_type    --  現居　お住まいの種類        1: 賃貸マンション; 2: 公団・アパート; ３: 社宅・寮; ４: 持ち家（家族名義）; ５: 持ち家（本人名義）
	,curr_house_owner_rel    --  現居　所有者の続柄        
	,curr_house_owner_name    --  現居　所有者の氏名        
	,curr_house_schedule_disposal_type    --  現居　持家　処分方法        1: 売却; 2: 賃貸; ３: その他
	,curr_house_schedule_disposal_type_other    --  現居　持家　処分方法　その他        
	,curr_house_shell_scheduled_date    --  現居　持家　売却予定時期        
	,curr_house_shell_scheduled_price    --  現居　持家　売却予定価格        
	,curr_house_loan_balance_type    --  現居　持家　ローン残高有無        1: 有; 0: 無
	,curr_house_lived_year    --  現居　居住年数　ヶ年        
	,curr_house_lived_month    --  現居　居住年数　ヶ月        
	,curr_house_floor_area    --  現居　床面積（MCJ）        
	,new_house_self_resident    --  新居　申込人本人住居区分        1: 住居; 0: 住居しない
	,new_house_self_not_resident_reason    --  新居　申込人本人住居しない理由        
	,new_house_residence_type    --  新居　居住区分        0: 自己居住; 1: セカンドハウス; 2: 親族居住（親居住）; 3: 親族居住（子居住）
	,new_house_acquire_reason    --  新居　申込人住宅取得理由        1: 住宅が古い; 2: 住宅が狭い; 3: 結婚; 4: 世帯を分ける（結婚を除く）; 5: 環境が悪い; 6: 家賃が高い; 7: 立ち退き要求; 8: 通勤・通学に不便; 9: 持ち家希望; 99: その他
	,new_house_acquire_reason_other    --  新居　申込人住宅取得理由　その他        
	,new_house_planned_resident_overview    --  新居　申込人以外居住予定者概要        
	,property_type    --  物件　種類        1 : 新築マンション; 2 : 中古マンション; 3 : 中古住宅; 4 : 建売住宅; 5 : 住宅新築; 6 : 店舗併用住宅; 99 : その他
	,property_joint_ownership_type    --  物件　共有区分        1: 建物のみ; 2: 土地のみ; 3: 建物及び土地; 4: 未定
	,property_business_type    --  物件　事業性区分        1: 賃貸; 2: 事務所・店舗; 3: 太陽光発電による売電'
	,property_publish_url    --  物件　掲載URL        
	,property_postal_code    --  物件　郵便番号        
	,property_prefecture    --  物件　都道府県        
	,property_city    --  物件　市区町村郡        
	,property_district    --  物件　以下地番        
	,property_apartment_and_room_no    --  物件　マンション名・部屋番号        
	,property_address_kana    --  物件　所在地　カナ        
	,property_land_acquire_date    --  物件　土地取得時期        
	,property_land_area    --  物件　土地の敷地面積        
	,property_floor_area    --  物件　建物の延床面積        
	,property_private_area    --  物件　マンションの専有面積        
	,property_total_floor_area    --  物件　マンション全体の延床面積        
	,property_building_ratio_numerator    --  物件　建物割合分子        
	,property_building_ratio_denominator    --  物件　建物割合分母        
	,property_land_ratio_numerator    --  物件　土地割合分子        
	,property_land_ratio_denominator    --  物件　土地割合分母        
	,property_building_price    --  物件　建物価格        
	,property_land_price    --  物件　土地価格        
	,property_total_price    --  物件　合計価格        
	,property_land_type    --  物件　土地権利（MCJ）        1: 賃貸借; 2: 地上権; 3: 使用賃貸
	,property_purchase_type    --  物件　買戻・保留地・仮換地（MCJ）        1: 買戻特約付; 2: 保留地; 3: 仮換地
	,property_planning_area    --  物件　都市計画区域（MCJ）        1: 市街化調整区域; 2: 都市計画区域外; 99: その他
	,property_planning_area_other    --  物件　都市計画区域　その他（MCJ）        
	,property_rebuilding_reason    --  物件　再建築理由（MCJ）        1: 既存住宅; 99: その他
	,property_rebuilding_reason_other    --  物件　再建築理由　その他（MCJ）        
	,property_maintenance_type    --  物件　維持保全型区分（MCJ）        1: 長期優良住宅; 2: 予備認定マンション
	,property_flat_35_plan    --  物件　フラット35S適用プラン（MCJ）        1: ZEH; 2: Aプラン; 3: Bプラン
	,property_flat_35_tech    --  物件　フラット35S技術基準（MCJ）        1: 省エネルギー性; 2: 耐震性; 3: バリアフリー性; 4: 耐久性・可変性
	,property_region_type    --  物件　地域区分（MCJ）        1: 地域連携型（地域活性）; 2: 地域連携型（子育て支援）; 3: 地方移住支援型
	,required_funds_land_amount    --  必要資金　土地価格        
	,required_funds_house_amount    --  必要資金　建物・物件価格・マンション価格        
	,required_funds_accessory_amount    --  必要資金　付帯設備        
	,required_funds_additional_amount    --  必要資金　諸費用等        
	,required_funds_refinance_loan_balance    --  必要資金　借換対象ローン残債        
	,required_funds_upgrade_amount    --  必要資金　増改築        
	,required_funds_loan_plus_amount    --  必要資金　住宅ローンプラス        
	,required_funds_total_amount    --  必要資金　必要資金合計        
	,funding_saving_amount    --  調達資金　預貯金        
	,funding_other_saving_amount    --  調達資金　有価証券等        
	,funding_estate_sale_amount    --  調達資金　不動産売却代金        
	,funding_self_amount    --  調達資金　自己資金        調達資金　預貯金　＋　有価証券等　＋　不動産売却代金
	,funding_relative_donation_amount    --  調達資金　親族からの贈与        
	,funding_loan_amount    --  調達資金　本件ローン        
	,funding_pair_loan_amount    --  調達資金　ペアローン        
	,funding_other_amount    --  調達資金　その他額        
	,funding_other_amount_detail    --  調達資金　その他額名        
	,funding_other_loan_amount    --  調達資金　その他の借り入れ        
	,funding_other_refinance_amount    --  調達資金　その他借換        
	,funding_total_amount    --  調達資金　調達資金合計        
	,refund_source_type    --  完済原資　区分（MCJ）        
	,refund_source_type_other    --  完済原資　区分　その他（MCJ）        
	,refund_source_content    --  完済原資　内容（MCJ）        
	,refund_source_amount    --  完済原資　金額（MCJ）        
	,rent_to_be_paid_land    --  今回の住宅・土地取得以外の借入　地代（MCJ）        
	,rent_to_be_paid_land_borrower    --  地代支払いをしている方        0:申込者 ;1:連帯債務者
	,rent_to_be_paid_house    --  今回の住宅・土地取得以外の借入　家賃（MCJ）        
	,rent_to_be_paid_house_borrower    --  家賃支払いをしている方        0:申込者 ;1:連帯債務者
	,approver_confirmation    --  承認者確認        0: 未承認しない; 1: 承認した済
	,unsubcribed    --  退会区分        1: 退会
	,created_at    --  作成日付        
	,updated_at    --  更新日付        
    ,old_id
    ,old_user_id
    ,application_status 
	,provisional_result 
	,soudan_no 
	,under_review_status 
	,interface_status
    ,send_date
)
select 
	UUID_SHORT() as id    --  ID
	,u.id as c_user_id    --  ユーザーID
	,sp.id as s_sales_person_id    --  業者ID
	,m.id as s_manager_id    --  銀代担当者ID
	,case when sco.category='C' then sco.id
		  when sco.category='B' then sco.pid
          when sco.category='E' then  (select pid from s_sales_company_orgs x where x.id in ( select pid from s_sales_company_orgs sco_s where sco_s.id=sco.pid ))
          else null
    end as sales_company_id    --  紹介会社ID
	,case when sco.category='B' then sco.id  
          when sco.category='E' then ( select pid from s_sales_company_orgs sco_s where sco_s.id=sco.pid )
	  end as sales_area_id    --  エリアID
	,(case when sco.category='E' then sco.id else null end) as sales_exhibition_hall_id    --  展示場ID
	,h.application_number as apply_no    --  受付番号
	,h.loan_apply_date as apply_date    --  申込日兼同意日
	,h.scheduled_date_moving as move_scheduled_date    --  入居予定年月
	,h.loan_type as loan_type    --  借入形態 1: おひとり; 2: ペアローン; 3: 収入合算（持分あり）; 4: 収入合算（持分なし）
	,(case when h.loan_target =7 or h.loan_target=8 then h.loan_target else 0 end) as loan_target_type    --  借入目的　　→　loan_target =7,8以外は0：物件の購入・建築　をセットする
	,h.loan_target as loan_target    --  資金使途　7: お借り換え; 8: 増改築（借り換え有）; 1: 建売住宅の購入; 6: 土地を購入後に建物新築; 5: 建物だけ新築(既に土地をお持ちの方); 2: 中古住宅の購入; 3: 新築マンションの購入; 4: 中古マンションの購入
	,h.linking_number as pair_loan_id    --  ペアローン相手ID
	,h.pair_loan_applicant_first_name as pair_loan_first_name    --  ペアローン相手名
	,h.pair_loan_applicant_last_name as pair_loan_last_name    --  ペアローン相手姓
	-- ,case when h.pair_loan_relationship=5 then 99 else h.pair_loan_relationship end as pair_loan_rel    --  ペアローン相手続柄　1 => '配偶者', 2 => '婚約者', 3 => '親', 4 => '子', 5 => 'その他'  →　1:配偶者 ; 2:婚約者 ; 3:親 ; 4:子 ; 99: その他
    ,h.pair_loan_relationship as pair_loan_rel  -- ペアローン相手続柄　  1:配偶者 ; 2:婚約者 ; 3:親 ; 4:子 ; 99: その他
	,h.pair_loan_relationship_name as pair_loan_rel_name    --  ペアローン相手続柄名称　入力項目
	,p.has_join_guarantor as join_guarantor_umu    --  担保提供者有無  0 => '無し', 1 => '有り'  →　1: 有
	,h.is_home_loan_plus as loan_plus    --  住宅ローンプラス  1：申し込む
	,h.has_land_advance_plan as land_advance_plan    --  土地先行プラン希望  　1: 希望する; 0: 希望しない
	,p.borrowing_status as curr_borrowing_status    --  現在利用中のローン  1: 有; 0: 無
	,h.status_result as pre_examination_status    --  事前審査結果 0: 書類確認; 1: 書類不備対応中; 2: 内容確認; 3: 承認; 4: 銀行へデータ連携; 5: 提携会社へ審査結果公開; 6: 申込人へ審査結果公開
	,case when h.p_referral_agency_id is not null or h.sale_person_name_input is not null or h.sale_person_phone_number is not null then 0 else 1 end vendor_business_card    --  業者名刺 1: はい; 0: いいえ(自分で入力）　　→　入力データが存在する場合は、0: いいえ(自分で入力）をセットする
	,h.sale_person_name_input as vendor_name    --  業者名　入力項目
	,h.sale_person_phone_number as vendor_phone    --  業者電話番号　入力項目
	,p.current_residence as curr_house_residence_type    --  現居　お住まいの種類　　　1: 賃貸マンション; 2: 公団・アパート; ３: 社宅・寮; ４: 持ち家（家族名義）; ５: 持ち家（本人名義）
	,p.owner_relationship as curr_house_owner_rel    --  現居　所有者の続柄
	,p.owner_full_name as curr_house_owner_name    --  現居　所有者の氏名
	,p.buyingand_selling_schedule_type as curr_house_schedule_disposal_type    --  現居　持家　処分方法　　　1: 売却; 2: 賃貸; 99: その他
	,p.other_buyingand_selling_schedule_type as curr_house_schedule_disposal_type_other    --  現居　持家　処分方法　その他
	,p.scheduled_time_sell_house as curr_house_shell_scheduled_date    --  現居　持家　売却予定時期
	,p.expected_house_selling_price as curr_house_shell_scheduled_price    --  現居　持家　売却予定価格
	,p.current_home_loan as curr_house_loan_balance_type    --  現居　持家　ローン残高有無 1: 有; 0: 無
	,p.lived_length_year_num as curr_house_lived_year    --  現居　居住年数　ヶ年
	,p.lived_length_month_num as curr_house_lived_month    --  現居　居住年数　ヶ月
	,p.current_residence_floor_area as curr_house_floor_area    --  現居　床面積（MCJ）
	,h.person_occupancy as new_house_self_resident    --  新居　申込人本人住居区分 1: 住居; 0: 住居しない
	,h.non_resident_reason as new_house_self_not_resident_reason    --  新居　申込人本人住居しない理由
	,h.residence_category as new_house_residence_type    --  新居　居住区分  0: 自己居住; 1: セカンドハウス; 2: 親族居住（親居住）; 3: 親族居住（子居住）
	,p.reason_acquire_home as new_house_acquire_reason    --  新居　申込人住宅取得理由  1: 住宅が古い; 2: 住宅が狭い; 3: 結婚; 4: 世帯を分ける（結婚を除く）; 5: 環境が悪い; 6: 家賃が高い; 7: 立ち退き要求; 8: 通勤・通学に不便; 9: 持ち家希望; 99: その他
	,p.other_reason_acquire_home as new_house_acquire_reason_other    --  新居　申込人住宅取得理由　その他
	,concat('{', case when planned_cohabitant like '%1%' then '"spouse": "1","spouse_umu": true' else '"spouse": "","spouse_umu": false' end
		, case when h.planned_cohabitant like '%2%' then concat(',"children": "',h.children_number,'","children_umu": true') else ',"children": "","children_umu": false' end
		, case when h.planned_cohabitant like '%3%' then ',"father": "1","father_umu": true' else ',"father": "","father_umu": false' end
		, case when h.planned_cohabitant like '%4%' then ',"mother": "1","mother_umu": true' else ',"mother": "","mother_umu": false' end
		, case when h.planned_cohabitant like '%5%' then concat(',"brothers_sisters": "',h.siblings_number,'","brothers_sisters_umu": true') else ',"brothers_sisters": "","brothers_sisters_umu": false' end
		, case when h.planned_cohabitant like '%6%' then ',"fiance": "1","fiance_umu": true' else ',"fiance": "","fiance_umu": false' end
		, case when h.planned_cohabitant like '%99%' then concat(',"others": "',h.other_people_number,'","others_umu": true',',"others_rel": "',h.other_relationship,'"') else ',"others": "","others_umu": false, "others_rel": ""' end
        ,'}'
	) as new_house_planned_resident_overview    --  新居　申込人以外居住予定者概要
	,h.collateral_type as property_type    --  物件　種類  1 : 新築マンション; 2 : 中古マンション; 3 : 中古住宅; 4 : 建売住宅; 5 : 住宅新築; 6 : 店舗併用住宅; 99 : その他
	,h.joint_ownership_division as property_joint_ownership_type    --  物件　共有区分  1: 建物のみ; 2: 土地のみ; 3: 建物及び土地; 4: 未定
	,case when h.business_ability is not null then
		concat('[',replace( replace( replace( REPLACE(REPLACE(REPLACE(h.business_ability, '-', ''),' ',''),'\n',','),'\',','"') ,',\'','"'),'\'',',"'),']') else null
		end as property_business_type    --  物件　事業性区分 1: 賃貸;  2: 事務所・店舗;  3: 太陽光発電による売電'
	,h.property_information_url as property_publish_url    --  物件　掲載URL
	,h.property_postal_code as property_postal_code    --  物件　郵便番号
	,h.collateral_prefecture as property_prefecture    --  物件　都道府県
	,h.collateral_city as property_city    --  物件　市区町村郡
	,h.collateral_lot_number as property_district    --  物件　以下地番
	,h.condominium_name as property_apartment_and_room_no    --  物件　マンション名・部屋番号
	,h.collateral_address_kana as property_address_kana    --  物件　所在地　カナ
	,h.acquisition_time_of_the_land as property_land_acquire_date    --  物件　土地取得時期
	,h.collateral_land_area as property_land_area    --  物件　土地の敷地面積
	,h.collateral_floor_area as property_floor_area    --  物件　建物の延床面積
	,h.occupied_area as property_private_area    --  物件　マンションの専有面積
	,h.collateral_total_floor_area as property_total_floor_area    --  物件　マンション全体の延床面積
	,h.building_ratio_numerator as property_building_ratio_numerator    --  物件　建物割合分子
	,h.building_ratio_denominator as property_building_ratio_denominator    --  物件　建物割合分母
	,h.land_ratio_numerator as property_land_ratio_numerator    --  物件　土地割合分子
	,h.land_ratio_denominator as property_land_ratio_denominator    --  物件　土地割合分母
	,h.building_price as property_building_price    --  物件　建物価格
	,h.land_price as property_land_price    --  物件　土地価格
	,h.land_and_building_price as property_total_price    --  物件　合計価格
	,h.land_ownership as property_land_type    --  物件　土地権利（MCJ）  1: 賃貸借; 2: 地上権; 3: 使用賃貸
	,h.purchase_purpose as property_purchase_type    --  物件　買戻・保留地・仮換地（MCJ）  1: 買戻特約付; 2: 保留地; 3: 仮換地
	,h.planning_area as property_planning_area    --  物件　都市計画区域（MCJ）  1: 市街化調整区域; 2: 都市計画区域外;  99: その他
	,h.other_planning_area as property_planning_area_other    --  物件　都市計画区域　その他（MCJ）
	,h.rebuilding_reason as property_rebuilding_reason    --  物件　再建築理由（MCJ）  1: 既存住宅; 99: その他
	,h.other_rebuilding_reason as property_rebuilding_reason_other    --  物件　再建築理由　その他（MCJ）
	,h.maintenance_type as property_maintenance_type    --  物件　維持保全型区分（MCJ）  1: 長期優良住宅; 2: 予備認定マンション
	,h.flat_35_applicable_plan as property_flat_35_plan    --  物件　フラット35S適用プラン（MCJ）  1: ZEH;  2: Aプラン; 3: Bプラン
	,h.flat_35_application as property_flat_35_tech    --  物件　フラット35S技術基準（MCJ）  1: 省エネルギー性; 2: 耐震性; 3: バリアフリー性; 4: 耐久性・可変性
	,h.region_type as property_region_type    --  物件　地域区分（MCJ）  1: 地域連携型（地域活性）; 2: 地域連携型（子育て支援）; 3: 地方移住支援型
	,h.land_purchase_price as required_funds_land_amount    --  必要資金　土地価格
	,h.house_purchase_price as required_funds_house_amount    --  必要資金　建物・物件価格・マンション価格
	,h.accessory_cost as required_funds_accessory_amount    --  必要資金　付帯設備
	,h.additional_cost as required_funds_additional_amount    --  必要資金　諸費用等
	,h.refinancing_loan_balance as required_funds_refinance_loan_balance    --  必要資金　借換対象ローン残債
	,h.house_upgrade_cost as required_funds_upgrade_amount    --  必要資金　増改築
	,h.require_funds_breakdown_mortgage as required_funds_loan_plus_amount    --  必要資金　住宅ローンプラス
	,(h.land_purchase_price+h.house_purchase_price+h.accessory_cost+h.additional_cost+h.require_funds_breakdown_mortgage+h.refinancing_loan_balance+h.house_upgrade_cost) as required_funds_total_amount    --  必要資金　必要資金合計
	,h.deposit_savings_1  as funding_saving_amount    --  調達資金　預貯金
	,h.other_saving_amount as funding_other_saving_amount    --  調達資金　有価証券等
	,h.real_estate_sale_price as funding_estate_sale_amount    --  調達資金　不動産売却代金
	,h.saving_amount as funding_self_amount    --  調達資金　自己資金 : 調達資金　預貯金 + 調達資金　有価証券等 + 調達資金　不動産売却代金
	,h.relative_donation_amount as funding_relative_donation_amount    --  調達資金　親族からの贈与
	,h.loan_amount as funding_loan_amount    --  調達資金　本件ローン
	,h.pair_loan_amount as funding_pair_loan_amount    --  調達資金　ペアローン
	,h.other_procurement_breakdown as funding_other_amount    --  調達資金　その他額
	,h.other_procurement_breakdown_content as funding_other_amount_detail    --  調達資金　その他額名
	,h.amount_any_loans as funding_other_loan_amount    --  調達資金　その他の借り入れ
	,h.amount_others as funding_other_refinance_amount    --  調達資金　その他借換
	,h.saving_amount as funding_total_amount    --  調達資金　調達資金合計
-- 	,case when h.completely_repayment_type is null then null else '' end as refund_source_type    --  完済原資　区分（MCJ）
    ,case when h.completely_repayment_type is not null then
		concat('[',replace( replace( replace( REPLACE(REPLACE(REPLACE(h.completely_repayment_type, '-', ''),' ',''),'\n',','),'\',','"') ,',\'','"'),'\'',',"'),']') else null
		end as refund_source_type
	,h.other_complete_repayment_type as refund_source_type_other    --  完済原資　区分　その他（MCJ）
	,h.refund_content as refund_source_content    --  完済原資　内容（MCJ）
	,h.refund_amount as refund_source_amount    --  完済原資　金額（MCJ）
	,p.land_rent_to_be_paid as rent_to_be_paid_land    --  今回の住宅・土地取得以外の借入　地代（MCJ）
	,(case when p.land_rent_to_be_paid is not null then 0 else null end) as rent_to_be_paid_land_borrower    --  地代支払いをしている方 0:申込者 ;1:連帯債務者
	,p.house_rent_to_be_paid as rent_to_be_paid_house    --  今回の住宅・土地取得以外の借入　家賃（MCJ）
	,(case when p.house_rent_to_be_paid is not null then 0 else null end) as rent_to_be_paid_house_borrower    --  家賃支払いをしている方 0:申込者 ;1:連帯債務者
	,h.approver_confirmation as approver_confirmation    --  承認者確認 0: 承認しない; 1: 承認した
	,(case when h.user_id is null or h.user_id ='' or u.id is null then 1 else null end) as unsubcribed    --  退会区分 1: 退会
	,h.created_at as created_at    --  作成日付
	,h.updated_at as updated_at    --  更新日付
	,h.id as old_id
    ,h.user_id as old_user_id
    ,h.application_status -- 0 => "仮審査否決", 1 => "本審査", 2 => "本審査否決", 3 => "融資実行済み", 4 => "他行借入", 5 => "自宅購入取止め"
	,h.provisional_result  --  "承認": 0, "条件付承認": 1, "否決": 2 
	,h.soudan_no -- 相談番号
	,h.under_review_status --  仮審査中のステータス first_under_review: 1, second_under_review: 2, third_under_review: 3, fourth_under_review: 4, fifth_under_review: 5, sixth_under_review: 6
	,h.interface_error_status as interface_status -- IF連携結果 0 => "not_error", 1 => "error"
    ,api_h.send_date
from mortgage_loan_tool_be_production.p_application_headers h
 inner join mortgage_loan_tool_be_production.p_applicant_persons p
  on h.id=p.p_application_header_id and p.applicant_detail_type=0
 left join c_users u
   on h.user_id=u.old_id
 left join s_sales_persons sp
   on h.s_sale_person_id=sp.old_id
 left join s_managers m
   on h.manager_id=m.old_id
 left join s_sales_company_orgs sco
   on h.p_referral_agency_id=sco.old_id
 left join (select b.p_application_header_id,b.bank_code,max(b.send_date) send_date
from mortgage_loan_tool_be_production.api_histories b    
group by b.p_application_header_id,b.bank_code) api_h
   on h.id=api_h.p_application_header_id
order by h.id
;

-- 8. 申込者・連帯債務者	p_applicant_persons
truncate table p_applicant_persons;
insert into p_applicant_persons
(
	id    --  ID        
	,p_application_header_id    --  案件メイン情報ID        
	,type    --  申込者や連帯債務者区分        0:申込者 ;1:連帯債務者
	,rel_to_applicant_a_name    --  連帯債務者　申込者に対して続柄名　入力項目        
	,rel_to_applicant_a    --  連帯債務者　申込者に対して続柄        1:配偶者 ; 2:婚約者 ; 3:親 ; 4:子 ; 99: その他
	,rel_to_applicant_a_other    --  連帯債務者　申込者に対して続柄　その他        
	,identity_verification_type    --  本人確認書類タイプ        1:運転免許証 ; 2:マイナンバーカード ; 3:住民基本台帳カード（顔写真付き）
	,first_name_kanji    --  名　漢字        
	,last_name_kanji    --  姓　漢字        
	,first_name_kana    --  名　カナ        
	,last_name_kana    --  姓　カナ        
	,gender    --  性別        1 => '男性', 2 => '女性'
	,birthday    --  生年月日        
	,nationality    --  国籍        1: 日本国籍; 2: 外国籍
	,spouse    --  配偶者有無        1:有 ; 0:無
	,mobile_phone    --  携帯電話番号        
	,home_phone    --  自宅電話番号        
	,emergency_contact    --  緊急連絡先        
	,email    --  Eメール        
	,postal_code    --  郵便番号        
	,prefecture_kanji    --  都道府県　漢字        
	,city_kanji    --  市区郡　漢字        
	,district_kanji    --  町村字丁目　漢字        
	,other_address_kanji    --  補足　漢字        
	,prefecture_kana    --  都道府県　カナ        
	,city_kana    --  市区郡　カナ        
	,district_kana    --  町村字丁目　カナ        
	,other_address_kana    --  補足　カナ        
	,last_year_income    --  前年年収　総額        
	,last_year_bonus_income    --  前年年収　総額内ボーナス分（MCJ）        
	,before_last_year_income    --  前々年度年収 （MCJ）        
	,income_sources    --  収入源        1:給与（固定制）; 2: 給与（歩合給）; 3: 給与（年俸制）; 4: 事業収入; 5: 不動産収入
	,main_income_source    --  メイン収入源　銀代入力項目        1:給与（固定制）; 2: 給与（歩合給）; 3: 給与（年俸制）; 4: 事業収入; 5: 不動産収入
	,tax_return    --  確定申告有無        1:有 ; 0:無
	,tax_return_reasons    --  確定申告理由        1: 2カ所以上からの給与; 2: 事業収入; 3: 不動産収入; 4:医療費・寄付金控除; 5:株・配当; 6: 給与収入が2000万円超; 99:その他
	,tax_return_reason_other    --  確定申告理由　その他        
	,maternity_paternity_leave    --  産休・育休        1: 取得予定; 2: 取得中; 3: 取得済み
	,maternity_paternity_leave_start_date    --  産休・育休開始        
	,maternity_paternity_leave_end_date    --  産休・育休終了        
	,nursing_leave    --  介護休        1: 取得予定; 2: 取得中; 3: 取得済み
	,office_name_kanji    --  勤務先　名　漢字        
	,office_name_kana    --  勤務先　名　カナ        
	,office_capital_stock    --  勤務先　資本金        
	,office_listed_division    --  勤務先　上場区分        0: 上場; 1: 非上場; 2: 自営・経営者
	,office_employee_num    --  勤務先　従業員数        
	,office_establishment_date    --  勤務先　設立年月日        
	,office_phone    --  勤務先　電話番号        
	,office_head_location    --  勤務先　本社所在地        
	,office_postal_code    --  勤務先　郵便番号        
	,office_prefecture_kanji    --  勤務先　都道府県　漢字        
	,office_city_kanji    --  勤務先　市区郡　漢字        
	,office_district_kanji    --  勤務先　町村字丁目　漢字        
	,office_other_address_kanji    --  勤務先　補足　漢字        
	,office_prefecture_kana    --  勤務先　都道府県　カナ        
	,office_city_kana    --  勤務先　市区郡　カナ        
	,office_district_kana    --  勤務先　町村字丁目　カナ        
	,office_other_address_kana    --  勤務先　補足　カナ        
	,office_occupation    --  勤務先　職業        1: 会社役員（取締役・監査役）; 2: 会社員（管理職）; 3: 会社員（一般職）; 4: 教職員; 5: 自営業; 6: 契約社員; 7: 派遣社員・嘱託（契約期間１年以上）; 8: 派遣社員・嘱託（契約期間１年未満）; 9: 公務員・団体職員; 10: 農業漁業主; 11: パートアルバイト; 12: 年金受給者; 99: その他
	,office_occupation_other    --  勤務先　職業　その他        
	,office_industry    --  勤務先　業種        1: 製造業; 2: 農業; 3: 林業; 4: 漁業; 5: 鉱業; 6: 建設業; 7: 卸売・小売業; 8: 金融業; 9: 保険業; 10: 不動産業; 11: 運輸業; 12: 電気・ガス・熱供給・水道; 13: 飲食・宿泊; 14: 医療・福祉; 15: 教育・学習支援; 16: その他のサービス業; 17: 公務; 18: 公務 19: 複合サービス業; 99: その他
	,office_industry_other    --  勤務先　業種　その他        
	,office_occupation_detail    --  勤務先　職種        1: 医師; 2: 歯科医師; 3: 弁護士; 4: 弁理士; 5: 会計士; 6: 税理士; 7: 司法書士・行政書士; 8: 教職・公務員; 9: 販売・営業職; 10: 事務職; 11: 技術職; 12: 運転士; 99: その他
	,office_occupation_detail_other    --  勤務先　職種　その他        
	,office_joining_date    --  勤務先　入社年月        
	,office_department    --  勤務先　所属部署        
	,office_employment_type    --  勤務先　雇用形態        1: 経営者; 2: 正社員; 3: 嘱託; 4: アルバイト・パート; 5: 契約社員; 6: 派遣社員; 7: 学生・主婦; 8: 無職
	,office_role    --  勤務先　役職        1: 無職; 2: 代表・社長; 3: 役員・執行役員; 4: 管理職; 5: その他役職; 6: 一般職; 7: 学生・主婦
	,transfer_office    --  出向（派遣）有無        1:有 ; 0:無
	,transfer_office_name_kanji    --  出向（派遣）先　名　漢字        
	,transfer_office_name_kana    --  出向（派遣）先　名　カナ        
	,transfer_office_phone    --  出向（派遣）先　電話番号        
	,transfer_office_postal_code    --  出向（派遣）先　郵便番号        
	,transfer_office_prefecture_kanji    --  出向（派遣）先　都道府県　漢字        
	,transfer_office_city_kanji    --  出向（派遣）先　市区郡　漢字        
	,transfer_office_district_kanji    --  出向（派遣）先　町村字丁目　漢字        
	,transfer_office_other_address_kanji    --  出向（派遣）先　補足　漢字        
	,created_at    --  作成日付        
	,updated_at    --  更新日付        
    ,old_id
)
select 
	UUID_SHORT()  as id    --  ID
	,ah.id as p_application_header_id    --  案件メイン情報ID
	,ap.applicant_detail_type as type    --  申込者や連帯債務者区分 0:申込者 ;1:連帯債務者
	,ap.name_relationship_to_applicant as rel_to_applicant_a_name    --  連帯債務者　申込者に対して続柄名　入力項目
	,ap.relationship_to_applicant as rel_to_applicant_a    --  連帯債務者　申込者に対して続柄 　1:配偶者 ; 2:婚約者 ; 3:親 ; 4:子 ; 99: その他
	,ap.other_relationship_to_applicant as rel_to_applicant_a_other    --  連帯債務者　申込者に対して続柄　その他
	,(ap.identity_verification +1) as identity_verification_type    --  本人確認書類タイプ 0 => "運転免許証", 1 => "マイナンバーカード", 2 => "住民基本台帳カード"  →　1:運転免許証 ; 2:マイナンバーカード ; 3:住民基本台帳カード（顔写真付き）
	,ap.first_name_kanji as first_name_kanji    --  名　漢字
	,ap.last_name_kanji as last_name_kanji    --  姓　漢字
	,ap.first_name_kana as first_name_kana    --  名　カナ
	,ap.last_name_kana as last_name_kana    --  姓　カナ
	,ap.sex as gender    --  性別  1 => '男性', 2 => '女性'
	,ap.birthday as birthday    --  生年月日
	,ap.nationality as nationality    --  国籍 1: 日本国籍; 2: 外国籍
	,ap.spouse    --  配偶者有無 {0 => 'なし', 1 => 'あり'} →　1:有 ; 0:無
	,ap.mobile_phone_number as mobile_phone    --  携帯電話番号
	,ap.home_phone_number as home_phone    --  自宅電話番号
	,ap.emergency_contact_number as emergency_contact    --  緊急連絡先
	,ap.owner_email as email    --  Eメール
	,ap.postal_code as postal_code    --  郵便番号
	,ap.prefecture_kanji as prefecture_kanji    --  都道府県　漢字
	,ap.city_kanji as city_kanji    --  市区郡　漢字
	,ap.district_kanji as district_kanji    --  町村字丁目　漢字
	,ap.other_address_kanji as other_address_kanji    --  補足　漢字
	,ap.prefecture_kana as prefecture_kana    --  都道府県　カナ
	,ap.city_kana as city_kana    --  市区郡　カナ
	,ap.district_kana as district_kana    --  町村字丁目　カナ
	,ap.other_address_kana as other_address_kana    --  補足　カナ
	,ap.last_year_income as last_year_income    --  前年年収　総額
	,ap.bonus_income as last_year_bonus_income    --  前年年収　総額内ボーナス分（MCJ）
	,ap.last_year_income as before_last_year_income    --  前々年度年収 （MCJ）
	,case when ap.income_source is not null then
		concat('[',replace( replace( replace( REPLACE(REPLACE(REPLACE(ap.income_source, '-', ''),' ',''),'\n',','),'\',','"') ,',\'','"'),'\'',',"'),']') else null
		end as income_sources    --  収入源 1:給与（固定制）; 2: 給与（歩合給）; 3: 給与（年俸制）; 4: 事業収入; 5: 不動産収入
	,ap.main_income_source as main_income_source    --  メイン収入源　銀代入力項目 1:給与（固定制）; 2: 給与（歩合給）; 3: 給与（年俸制）; 4: 事業収入; 5: 不動産収入
	,ap.tax_return as tax_return    --  確定申告有無 1:有 ; 0:無
	,case when ap.type_tax_return is not null then
		concat('[',replace( replace( replace( REPLACE(REPLACE(REPLACE(ap.type_tax_return, '-', ''),' ',''),'\n',','),'\',','"') ,',\'','"'),'\'',',"'),']') else null
		end as tax_return_reasons    --  確定申告理由 1: 2カ所以上からの給与;  2: 事業収入; 3: 不動産収入; 4:医療費・寄付金控除; 5:株・配当; 6: 給与収入が2000万円超; 99:その他
	,ap.other_type_tax_return as tax_return_reason_other    --  確定申告理由　その他
	,ap.maternity_paternity_leave_status as maternity_paternity_leave    --  産休・育休 1: 取得予定; 2: 取得中; 3: 取得済み
	,DATE_FORMAT(ap.maternity_paternity_leave_start_time, '%Y/%m') as maternity_paternity_leave_start_date    --  産休・育休開始
	,DATE_FORMAT(ap.maternity_paternity_leave_end_time, '%Y/%m') as maternity_paternity_leave_end_date    --  産休・育休終了
	,ap.nursing_leave_status as nursing_leave    --  介護休 1: 取得予定; 2: 取得中; 3: 取得済み
	,ap.office_name_kanji as office_name_kanji    --  勤務先　名　漢字
	,ap.office_name_kana as office_name_kana    --  勤務先　名　カナ
	,ap.capital_stock as office_capital_stock    --  勤務先　資本金
	,ap.listed_division as office_listed_division    --  勤務先　上場区分 0: 上場; 1: 非上場; 2: 自営・経営者
	,ap.number_of_employee as office_employee_num    --  勤務先　従業員数
	,ap.office_establishment_date as office_establishment_date    --  勤務先　設立年月日
	,ap.office_phone_number as office_phone    --  勤務先　電話番号
	,ap.headquarters_location as office_head_location    --  勤務先　本社所在地
	,ap.office_postal_code as office_postal_code    --  勤務先　郵便番号
	,ap.office_prefecture_kanji as office_prefecture_kanji    --  勤務先　都道府県　漢字
	,ap.office_city_kanji as office_city_kanji    --  勤務先　市区郡　漢字
	,ap.office_district_kanji as office_district_kanji    --  勤務先　町村字丁目　漢字
	,ap.other_office_address_kanji as office_other_address_kanji    --  勤務先　補足　漢字
	,ap.office_prefecture_kana as office_prefecture_kana    --  勤務先　都道府県　カナ
	,ap.office_city_kana as office_city_kana    --  勤務先　市区郡　カナ
	,ap.office_district_kana as office_district_kana    --  勤務先　町村字丁目　カナ
	,ap.other_office_address_kana as office_other_address_kana    --  勤務先　補足　カナ
	,ap.occupation as office_occupation    --  勤務先　職業  1: 会社役員（取締役・監査役）; 2: 会社員（管理職）; 3: 会社員（一般職）; 4: 教職員; 5: 自営業; 6: 契約社員; 7: 派遣社員・嘱託（契約期間１年以上）; 8: 派遣社員・嘱託（契約期間１年未満）; 9: 公務員・団体職員; 10: 農業漁業主; 11: パートアルバイト; 12: 年金受給者; 99: その他
	,ap.other_occupation as office_occupation_other    --  勤務先　職業　その他
	,ap.industry as office_industry    --  勤務先　業種  1: 製造業; 2: 農業; 3: 林業; 4: 漁業; 5: 鉱業; 6: 建設業; 7: 卸売・小売業; 8: 金融業; 9: 保険業; 10: 不動産業; 11: 運輸業; 12: 電気・ガス・熱供給・水道; 13: 飲食・宿泊; 14: 医療・福祉; 15: 教育・学習支援; 16: その他のサービス業; 17: 公務; 18: 公務 19: 複合サービス業; 99: その他
	,ap.other_industry as office_industry_other    --  勤務先　業種　その他
	,ap.occupation_detail as office_occupation_detail    --  勤務先　職種 1: 医師; 2: 歯科医師; 3: 弁護士; 4: 弁理士; 5: 会計士; 6: 税理士; 7: 司法書士・行政書士; 8: 教職・公務員; 9: 販売・営業職; 10: 事務職; 11: 技術職; 12: 運転士; 99: その他
	,ap.other_occupation_detail as office_occupation_detail_other    --  勤務先　職種　その他
	,ap.employment_started_date as office_joining_date    --  勤務先　入社年月
	,ap.department as office_department    --  勤務先　所属部署
	,ap.emplmt_form_code as office_employment_type    --  勤務先　雇用形態  1: 経営者; 2: 正社員; 3: 嘱託; 4: アルバイト・パート; 5: 契約社員; 6: 派遣社員; 7: 学生・主婦; 8: 無職
	,ap.position as office_role    --  勤務先　役職 1: 無職; 2: 代表・社長; 3: 役員・執行役員; 4: 管理職; 5: その他役職; 6: 一般職; 7: 学生・主婦
	,ap.transfer_office as transfer_office    --  出向（派遣）有無 1:有 ; 0:無
	,ap.transfer_office_name_kanji as transfer_office_name_kanji    --  出向（派遣）先　名　漢字
	,ap.transfer_office_name_kana as transfer_office_name_kana    --  出向（派遣）先　名　カナ
	,ap.transfer_office_phone_number as transfer_office_phone    --  出向（派遣）先　電話番号
	,ap.transfer_office_postal_code as transfer_office_postal_code    --  出向（派遣）先　郵便番号
	,ap.transfer_office_prefecture_kanji as transfer_office_prefecture_kanji    --  出向（派遣）先　都道府県　漢字
	,ap.transfer_office_city_kanji as transfer_office_city_kanji    --  出向（派遣）先　市区郡　漢字
	,ap.transfer_office_district_kanji as transfer_office_district_kanji    --  出向（派遣）先　町村字丁目　漢字
	,ap.transfer_office_other_address_kanji as transfer_office_other_address_kanji    --  出向（派遣）先　補足　漢字
	,ap.created_at    --  作成日付
	,ap.updated_at    --  更新日付
	,ap.id as old_id
from mortgage_loan_tool_be_production.p_applicant_persons ap
	inner join p_application_headers ah
      on ap.p_application_header_id=ah.old_id
order by ap.id
;

-- 9. 借入内容明細	p_borrowing_details
truncate table p_borrowing_details;
insert into p_borrowing_details(
	id    --  ID        
	,p_application_header_id    --  案件メイン情報ID        
	,time_type    --  回目区分        1: 1回目; 2: 2回目;
	,desired_borrowing_date    --  借入希望日        
	,desired_loan_amount    --  借入希望額        
	,bonus_repayment_amount    --  ボーナス返済分        
	,bonus_repayment_month    --  ボーナス返済月        1: しない; 2: 1月/7月; 3: 2月/8月; 4: 3月/9月; 5: 4月/10月; 6: 5月/11月; 7: 6月/12月
	,repayment_method    --  返済方法        1: 元利均等返済; 2: 元金均等返済
	,loan_term_year    --  借入期間　ヶ年        
	,loan_term_month    --  借入期間　ヶ月        
	,created_at    --  作成日付        
	,updated_at    --  更新日付        
)
select
	UUID_SHORT() as id    --  ID        
	,ah.id as p_application_header_id    --  案件メイン情報ID        
	,bd.borrowing_detail_type as time_type    --  回目区分   1回目と2回目の借入区分 1 => first_borrowing_detail, 2 => second_borrowing_detail  =   1: 1回目; 2: 2回目;
	,bd.loan_desired_borrowing_date as desired_borrowing_date    --  借入希望日        
	,bd.temporary_desired_loan_amount as desired_loan_amount    --  借入希望額        
	,bd.halfyear_bonus as bonus_repayment_amount    --  ボーナス返済分        
	,bd.desired_monthly_bonus as bonus_repayment_month    --  ボーナス返済月        1: しない; 2: 1月/7月; 3: 2月/8月; 4: 3月/9月; 5: 4月/10月; 6: 5月/11月; 7: 6月/12月
	,bd.repayment_method as repayment_method    --  返済方法        1: 元利均等返済; 2: 元金均等返済
	,bd.loan_term_year_num as loan_term_year    --  借入期間　ヶ年        
	,bd.loan_term_month_num as loan_term_month    --  借入期間　ヶ月        
	,bd.created_at    --  作成日付        
	,bd.updated_at    --  更新日付        
from mortgage_loan_tool_be_production.p_borrowing_details bd
	inner join p_application_headers ah
      on bd.p_application_header_id=ah.old_id
order by bd.id
;

-- 10. 現在借入情報	p_borrowings
truncate table p_borrowings;
insert into p_borrowings(
	id    --  ID        
	,p_application_header_id    --  案件メイン情報ID        
	,self_input    --          
	,type    --  お借入の種類        1: 住宅ローン; 2: カードローン・キャッシング等; 3: アパートローン; 4: 事業用のお借入; 5: 車のローン; 6: 教育ローン; 7: 生活費補填のローン; 99: その他
	,category    --  借入区分        0: キャッシング; 1: カードローン; 2: ショッピング
	,borrower    --  借入名義人        0:申込者 ;1:連帯債務者
	,lender    --  借入先        
	,loan_amount    --  当初借入額・借入限度額        
	,curr_loan_balance_amount    --  借入残高・現在残高        
	,annual_repayment_amount    --  年間返済額        
	,loan_purpose    --  お借入の目的　カードローン・キャッシング等        1: 生活費補填のローン; 2: 家電; 3: 車; 4: 教育; 99: その他
	,loan_purpose_other    --  お借入の目的　カードローン・キャッシング等　その他        
	,loan_start_date    --  当初借入年月・カード契約年月        
	,loan_end_date    --  最終期限・最終返済年月        
	,card_expiry_date    --  カード有効期限        
    ,scheduled_loan_payoff    --  完済予定有無        1: 完済予定あり; 2: 完済予定なし; 3: 住宅ローンプラス利用により完済
	,scheduled_loan_payoff_date    --  完済予定年月        
	,loan_business_target    --  お借入の目的　事業用のお借入        1: 運転資金; 2: 設備資金; 3: リース; 99: その他
	,loan_business_target_other    --  お借入の目的　事業用のお借入　その他        
	,include_in_examination    --  審査に含める        0: なし; 1: あり
	,rental_room_num    --  賃貸戸（室）数        
	,common_housing    --  共同住宅        
	,estate_setting    --  不動産担保設定        0: 無担保; 1: 有担保
	,borrowing_from_house_finance_agency    --  住宅金融支援機構からの借入        0: いいえ; 1: はい
	,created_at    --  作成日付        
	,updated_at    --  更新日付        
)
select 
	UUID_SHORT() as id    --  ID        
	,ah.id as p_application_header_id    --  案件メイン情報ID        
	,case when b.lender is not null or b.lender!='' then 1 else 0 end self_input    --          
	,b.borrowing_type as type    --  お借入の種類        1: 住宅ローン; 2: カードローン・キャッシング等; 3: アパートローン; 4: 事業用のお借入; 5: 車のローン; 6: 教育ローン; 7: 生活費補填のローン; 99: その他
	,b.borrowing_category as category    --  借入区分        0: キャッシング; 1: カードローン; 2: ショッピング
	,case when b.borrower is not null then b.borrower else 1 end as borrower    --  借入名義人   1:申込人本人' ;2:収入合算者（連帯保証人予定者）
	,b.lender as lender    --  借入先        
	,b.loan_amount as loan_amount    --  当初借入額・借入限度額        
	,b.current_balance_amount as curr_loan_balance_amount    --  借入残高・現在残高        
	,b.annual_repayment_amount as annual_repayment_amount    --  年間返済額        
	,b.loan_purpose as loan_purpose    --  お借入の目的　カードローン・キャッシング等        1: 生活費補填のローン; 2: 家電; 3: 車; 4: 教育; 99: その他
	,b.other_purpose as loan_purpose_other    --  お借入の目的　カードローン・キャッシング等　その他        
	,b.loan_start_date as loan_start_date    --  当初借入年月・カード契約年月        
	,b.loan_deadline_date as loan_end_date    --  最終期限・最終返済年月        
	,b.card_expiry_date as card_expiry_date    --  カード有効期限        
	,b.scheduled_loan_payoff as scheduled_loan_payoff    --  完済予定有無       1: 完済予定あり; 2: 完済予定なし; 3: 住宅ローンプラス利用により完済
	,b.expected_repayment_date as scheduled_loan_payoff_date    --  完済予定年月        
	,b.business_borrowing_type as loan_business_target    --  お借入の目的　事業用のお借入        1: 運転資金; 2: 設備資金; 3: リース; 99: その他
	,b.specific_loan_purpose as loan_business_target_other    --  お借入の目的　事業用のお借入　その他        
	,b.include_in_examination as include_in_examination    --  審査に含める        0: なし; 1: あり
	,b.rental_room_number as rental_room_num    --  賃貸戸（室）数        
	,b.common_housing as common_housing    --  共同住宅        
	,b.estate_mortgage as estate_setting    --  不動産担保設定        0: 無担保; 1: 有担保
	,b.borrowing_from_housing_finance_agency as borrowing_from_house_finance_agency    --  住宅金融支援機構からの借入        0: いいえ; 1: はい
	,b.created_at    --  作成日付        
	,b.updated_at    --  更新日付        
from mortgage_loan_tool_be_production.p_borrowings b
  inner join p_application_headers ah
    on b.p_application_header_id=ah.old_id
order by b.id
;

-- 11. 担保提供者	p_join_guarantors
truncate table p_join_guarantors;
insert into p_join_guarantors(
	id    --  ID        
	,p_application_header_id    --  案件メイン情報ID        
	,rel_to_applicant_a_name    --  申込人に対して続柄名        
	,rel_to_applicant_a    --  申込人に対して続柄        1: 配偶者; 2: 婚約者; 3: 親; 4: 子; 5: 法人; 6: 法人代表者; 7: その他
	,rel_to_applicant_a_other    --  申込人に対して続柄　その他        
	,first_name_kanji    --  名　漢字        
	,last_name_kanji    --  姓　漢字        
	,first_name_kana    --  名　カナ        
	,last_name_kana    --  姓　カナ        
	,gender    --  性別        0: 男性; 1: 女性
	,birthday    --  生年月日        
	,mobile_phone    --  携帯電話番号        
	,home_phone    --  自宅電話番号        
	,emergency_contact    --  緊急連絡先        
	,email    --  Eメール        
	,postal_code    --  郵便番号        
	,prefecture_kanji    --  都道府県　漢字        
	,city_kanji    --  市区郡　漢字        
	,district_kanji    --  町村字丁目　漢字        
	,other_address_kanji    --  補足　漢字        
	,prefecture_kana    --  都道府県　カナ        
	,city_kana    --  市区郡　カナ        
	,district_kana    --  町村字丁目　カナ        
	,other_address_kana    --  補足住所　カナ        
	,last_year_income    --  前年年収        
	,work_name_kanji    --  勤務先　名称　漢字        
	,work_name_kana    --  勤務先　名称　カナ        
	,work_office_phone    --  勤務先　電話番号        
	,work_postal_code    --  勤務先　郵便番号        
	,work_address_kanji    --  勤務先　住所　漢字        
	,work_address_kana    --  勤務先　住所　カナ        
	,created_at    --  作成日付        
	,updated_at    --  更新日付        
)
select 
	UUID_SHORT() as id    --  ID        
	,ah.id as p_application_header_id    --  案件メイン情報ID        
	,js.guarantor_relationship_name as rel_to_applicant_a_name    --  申込人に対して続柄名        
	,js.guarantor_relationship_to_applicant as rel_to_applicant_a    --  申込人に対して続柄        1: 配偶者; 2: 婚約者; 3: 親; 4: 子; 5: 法人; 6: 法人代表者; 7: その他
	,js.other_relationship_to_applicant as rel_to_applicant_a_other    --  申込人に対して続柄　その他        
	,js.first_name_kanji as first_name_kanji    --  名　漢字        
	,js.last_name_kanji as last_name_kanji    --  姓　漢字        
	,js.first_name_kana as first_name_kana    --  名　カナ        
	,js.last_name_kana as last_name_kana    --  姓　カナ        
	,js.sex as gender    --  性別        0: 男性; 1: 女性
	,js.birthday as birthday    --  生年月日        
	,js.mobile_phone_number as mobile_phone    --  携帯電話番号        
	,js.home_phone_number as home_phone    --  自宅電話番号        
	,js.emergency_contact_number as emergency_contact    --  緊急連絡先        
	,js.owner_email as email    --  Eメール        
	,js.postal_code as postal_code    --  郵便番号        
	,js.prefecture_kanji as prefecture_kanji    --  都道府県　漢字        
	,js.city_kanji as city_kanji    --  市区郡　漢字        
	,js.district_kanji as district_kanji    --  町村字丁目　漢字        
	,js.other_address_kanji as other_address_kanji    --  補足　漢字        
	,js.prefecture_kana as prefecture_kana    --  都道府県　カナ        
	,js.city_kana as city_kana    --  市区郡　カナ        
	,js.district_kana as district_kana    --  町村字丁目　カナ        
	,js.other_address_kana as other_address_kana    --  補足住所　カナ        
	,js.last_year_income as last_year_income    --  前年年収        
	,js.office_name_kanji as work_name_kanji    --  勤務先　名称　漢字        
	,js.office_name_kana as work_name_kana    --  勤務先　名称　カナ        
	,js.office_phone_number as work_office_phone    --  勤務先　電話番号        
	,js.office_postal_code as work_postal_code    --  勤務先　郵便番号        
	,js.office_address_kanji as work_address_kanji    --  勤務先　住所　漢字        
	,js.office_address_kana as work_address_kana    --  勤務先　住所　カナ        
	,js.created_at    --  作成日付        
	,js.updated_at    --  更新日付        
from mortgage_loan_tool_be_production.p_join_guarantors js
  inner join p_application_headers ah
    on js.p_application_header_id=ah.old_id
order by js.id
;

-- 12. 居住予定者詳細	p_residents
truncate table p_residents;
insert into p_residents(
	id    --  ID        
	,p_application_header_id    --  案件メイン情報ID        
	,one_roof    --  申込人と同居有無        0: 無し; 1: 有り
	,rel_to_applicant_a_name    --  申込人に対して相手続柄名　入力項目        
	,rel_to_applicant_a    --  申込人に対して相手続柄        1: 配偶者; 2: 子供; 3: 父; 4: 母; 5: 兄弟姉妹; 6: 婚約者; 99: その他
	,rel_to_applicant_a_other    --  申込人に対して相手続柄　その他        
	,last_name_kanji    --  姓　漢字        
	,first_name_kanji    --  名　漢字        
	,last_name_kana    --  姓　カナ        
	,first_name_kana    --  名　カナ        
	,gender    --  性別        0: 男性; 1: 女性
	,birthday    --  生年月日        
	,nationality    --  国籍        1: 日本国籍; 2: 外国籍
	,contact_phone    --  電話番号        
	,postal_code    --  郵便番号        
	,prefecture_kanji    --  都道府県　漢字        
	,city_kanji    --  市区郡／市区町村　漢字        
	,district_kanji    --  町村字丁目／丁目･番地･号　漢字        
	,other_address_kanji    --  補足／建物名･部屋番号等　漢字        
	,prefecture_kana    --  都道府県　カナ        
	,city_kana    --  市区郡／市区町村　カナ        
	,district_kana    --  町村字丁目／丁目･番地･号　カナ        
	,other_address_kana    --  補足／建物名･部屋番号等　カナ        
	,loan_from_japan_house_finance_agency    --  住宅金融支援機構（旧：公庫）からの融資の有無        0: 無; 1: 有
	,created_at    --  作成日付        
	,updated_at    --  更新日付        
)
select 
	UUID_SHORT() as id    --  ID        
	,ah.id as p_application_header_id    --  案件メイン情報ID        
	,r.one_roof as one_roof    --  申込人と同居有無        0: 無し; 1: 有り
	,r.relationship_name as rel_to_applicant_a_name    --  申込人に対して相手続柄名　入力項目        
	,r.relationship as rel_to_applicant_a    --  申込人に対して相手続柄        1: 配偶者; 2: 子供; 3: 父; 4: 母; 5: 兄弟姉妹; 6: 婚約者; 99: その他
	,r.other_relationship as rel_to_applicant_a_other    --  申込人に対して相手続柄　その他        
	,r.last_name_kanji as last_name_kanji    --  姓　漢字        
	,r.first_name_kanji as first_name_kanji    --  名　漢字        
	,r.last_name_kana as last_name_kana    --  姓　カナ        
	,r.first_name_kana as first_name_kana    --  名　カナ        
	,r.sex as gender    --  性別        0: 男性; 1: 女性
	,r.birthday as birthday    --  生年月日        
	,r.nationality as nationality    --  国籍        1: 日本国籍; 2: 外国籍
	,r.mobile_phone_number as contact_phone    --  電話番号        
	,r.postal_code as postal_code    --  郵便番号        
	,r.prefecture_kanji as prefecture_kanji    --  都道府県　漢字        
	,r.city_kanji as city_kanji    --  市区郡／市区町村　漢字        
	,r.district_kanji as district_kanji    --  町村字丁目／丁目･番地･号　漢字        
	,r.other_address_kanji as other_address_kanji    --  補足／建物名･部屋番号等　漢字        
	,r.prefecture_kana as prefecture_kana    --  都道府県　カナ        
	,r.city_kana as city_kana    --  市区郡／市区町村　カナ        
	,r.district_kana as district_kana    --  町村字丁目／丁目･番地･号　カナ        
	,r.other_address_kana as other_address_kana    --  補足／建物名･部屋番号等　カナ        
	,r.loan_from_japan_housing_finance_agency as loan_from_japan_house_finance_agency    --  住宅金融支援機構（旧：公庫）からの融資の有無        0: 無; 1: 有
	,r.created_at    --  作成日付        
	,r.updated_at    --  更新日付        
from mortgage_loan_tool_be_production.p_residents r
  inner join p_application_headers ah
    on r.p_application_header_id=ah.old_id
order by r.id
;

-- 13. 申込銀行	p_application_banks
truncate table p_application_banks;
insert into p_application_banks(
	id    --  ID        
	,p_application_header_id    --  案件メイン情報ID        
	,s_bank_id    --  銀行ID        
	,provisional_status    --  仮審査ステータス        1:仮審査申込手続き; 2:仮審査中①; 3:仮審査中②; 4:仮審査中③; 5:仮審査中④; 6:仮審査中⑤
	,provisional_result    --  仮審査結果        0:承認 ; 1:条件付承認 ; 2: 否決
	,provisional_after_result    --  仮審査後結果        0: 仮審査否決; 1: 本審査; 2: 本審査否決; 3: 融資実行済み; 4: 他行借入; 5: 自宅購入取止め
	,soudan_no    --  相談番号        
	,delivery_date    --  送付日付        
	,interface_status    --  IF連携結果        0: 失敗; 1: 成功
	,created_at    --  作成日付        
	,updated_at    --  更新日付 
    ,old_header_id
    ,bank_code
    )
select 
	UUID_SHORT() as id    --  ID        
	,ah.id as p_application_header_id    --  案件メイン情報ID        
	,b.id as s_bank_id    --  銀行ID        
	,ah.under_review_status as provisional_status    --  仮審査ステータス   first_under_review: 1, second_under_review: 2, third_under_review: 3, fourth_under_review: 4, fifth_under_review: 5, sixth_under_review: 6   =  1:仮審査申込手続き; 2:仮審査中①; 3:仮審査中②; 4:仮審査中③; 5:仮審査中④; 6:仮審査中⑤
	,ah.provisional_result as provisional_result    --  仮審査結果        0:承認 ; 1:条件付承認 ; 2: 否決
	,ah.application_status as provisional_after_result    --  仮審査後結果        0: 仮審査否決; 1: 本審査; 2: 本審査否決; 3: 融資実行済み; 4: 他行借入; 5: 自宅購入取止め
	,ah.soudan_no as soudan_no    --  相談番号        
	,ah.send_date as delivery_date    --  送付日付        
	,case when ah.interface_status=0 then 1 else 0 end as interface_status    --  IF連携結果   0 => "not_error", 1 => "error"  →  0: 失敗; 1: 成功
	,ab.created_at    --  作成日付        
	,ab.updated_at    --  更新日付   
    ,ab.p_application_header_id as old_header_id
    ,b.code as bank_code
from mortgage_loan_tool_be_production.p_application_banks ab
 left join s_banks b
   on ab.s_master_bank_id=b.old_id
 left join p_application_headers ah
   on ab.p_application_header_id=ah.old_id
order by ab.id
;

-- 14. 審査状態履歴	p_examine_status_histories
truncate table p_examine_status_histories;
insert into p_examine_status_histories(
	p_application_bank_id    --  申込銀行ID        
	,status    --  審査状態        1:仮審査申込手続き; 2:仮審査中①; 3:仮審査中②; 4:仮審査中③; 5:仮審査中④; 6:仮審査中⑤
	,status_origin    --  審査状態源        
	,created_at    --  作成日付        
	,updated_at    --  更新日付        
)
select
	ab.id as p_application_bank_id    --  申込銀行ID        
	,sh.status    --  審査状態        1:仮審査申込手続き; 2:仮審査中①; 3:仮審査中②; 4:仮審査中③; 5:仮審査中④; 6:仮審査中⑤
	,sh.status_origin    --  審査状態源        
	,sh.created_at    --  作成日付        
	,sh.updated_at    --  更新日付        
from mortgage_loan_tool_be_production.examine_status_histories sh
  inner join p_application_banks ab
    on sh.p_application_header_id=ab.old_header_id and sh.bank_code=ab.bank_code
order by sh.created_at
;

-- 15. チャットメッセージ	c_messages
truncate table c_messages;
insert into c_messages(
	id    --  ID        
	,c_user_id    --  ユーザーID        
	,p_application_header_id    --  案件メイン情報ID        
	,sender_type    --  送信者区分        1：ユーザー；２：業者；３：銀代
	,sender_id    --  送信者ID        
	,content    --  メッセージ内容        
	,viewed    --  既読        
	,created_at    --  作成日付        
	,updated_at    --  更新日付        
)
select 
	UUID_SHORT() as id    --  ID        
	,u.id as c_user_id    --  ユーザーID        
	,ah.id as p_application_header_id    --  案件メイン情報ID        
	,case when m.sender_type='User' then 1 when m.sender_type='SSalePerson' then 2 when m.sender_type='Manager' then 3 end  as sender_type    --  送信者区分        1：ユーザー；２：業者；３：銀代
	,mt.id as sender_id    --  送信者ID        
	,m.content    --  メッセージ内容     
    ,replace( concat('['
    ,case when u2.id is not null then concat('"',u2.id,'"') else '' end
    ,case when sp2.id is not null then concat('"',sp2.id,'"') else '' end
    ,case when m2.id is not null then concat('"',m2.id,'"') else '' end
    ,']'),'""','","') as viewed
-- 	,concat('[', case when u2.id is not null then concat('"',u2.id,'"') else '' end  ,']')  as m.viewed    --  既読        
	,m.created_at    --  作成日付        
	,m.updated_at    --  更新日付      
from 
	(select *
        ,replace(replace( REGEXP_SUBSTR(
		 replace( replace(replace(viewed,'\n','') 
			,' '
            ,'')
            ,'viewed_account_'
            ,'')
            , 'id:([0-9]+)type:User')
		,'type:User'
        ,'')
        ,'id:'
        ,'')
            AS account_User
	,replace(replace(REGEXP_SUBSTR(
		 replace( replace(replace(viewed,'\n','') 
			,' '
            ,'')
            ,'viewed_account_'
            ,'')
            , 'id:([0-9]+)type:SSalePerson') 
		,'type:SSalePerson'
        ,'')
        ,'id:'
        ,'')
			AS account_SSalePerson
	,replace(replace(REGEXP_SUBSTR(
		 replace( replace(replace(viewed,'\n','') 
			,' '
            ,'')
            ,'viewed_account_'
            ,'')
            , 'id:([0-9]+)type:Manager')         
		,'type:Manager'
		,'')
        ,'id:'
        ,'')
            AS account_Manager
    from  mortgage_loan_tool_be_production.messages) m
	left join p_application_headers ah
		on m.conversation_id=ah.old_user_id
	left join c_users u 
		on m.conversation_id=u.old_id
	left join (select id,old_id,'User' as sender_type
		from c_users
		union all
		select id,old_id,'SSalePerson' as sender_type
		from s_sales_persons
		union all
		select id,old_id,'Manager' as sender_typem
		from s_managers) mt
		on m.sender_id=mt.old_id and m.sender_type=mt.sender_type
	left join c_users u2
		on m.account_User=u2.old_id
	left join s_sales_persons sp2
		on m.account_SSalePerson=sp2.old_id
	left join s_managers m2
		on m.account_Manager=m2.old_id
order by m.id	
;


-- 16. 案件メモ	p_memos
truncate table p_memos;
insert into p_memos(
	id    --  ID        
	,p_application_header_id    --  案件メイン情報ID        
	,s_manager_id    --  業者ID        
	,content    --  内容        
	,created_at    --  作成日付        
	,updated_at    --  更新日付        
)
select 
	UUID_SHORT() as id    --  ID        
	,ah.id as p_application_header_id    --  案件メイン情報ID        
	,sm.id as s_manager_id    --  業者ID        
	,m.memo as content    --  内容        
	,m.created_at    --  作成日付        
	,m.updated_at    --  更新日付        
from mortgage_loan_tool_be_production.memos m
	left join p_application_headers ah
		on m.p_application_header_id=ah.old_id
	left join s_managers sm 
		on m.manager_id=sm.old_id
;

-- 17. オープション管理	s_dynamic_options
truncate table s_dynamic_options;
insert into s_dynamic_options(
	id    --  ID        
	,field_name_ja    --  項目名(日本語)        
	,field_name_en    --  項目名(英語)        
	,option_name    --  オップション名        
	,option_code    --  オップションコード        
	,sort_order    --  順番        
	,display_flg    --  表示フラッグ        1: 表示; 0: 表示しない
	,created_at    --  作成日付        
	,updated_at    --  更新日付        
)
select 
	id    --  ID        
	,field_name_ja    --  項目名(日本語)        
	,field_name_en    --  項目名(英語)        
	,option_name    --  オップション名        
	,option_code    --  オップションコード        
	,sort_order    --  順番        
	,display_flg    --  表示フラッグ        1: 表示; 0: 表示しない
	,created_at    --  作成日付        
	,updated_at    --  更新日付        
from mortgage_loan_tool_be_production.p_dynamic_options
;

-- 18. 銀行API送信履歴	p_bank_api_send_histories
truncate table p_bank_api_send_histories;
insert into p_bank_api_send_histories(
	id    --  ID        
	,p_application_bank_id    --  申込銀行ID        
	,set_num    --  SET番号        
	,request_number    --  申込認識番号        
	,pair_loan_id    --  ペアローン相手ID        
	,request_body    --  リクエストボディ        
	,status_code    --  ステータスコード        
	,response_body    --  レスポンスボディ        
	,created_at    --  作成日付        
	,updated_at    --  更新日付        
)
select
	UUID_SHORT() as id    --  ID        
	,ab.id as p_application_bank_id    --  申込銀行ID        
	,h.set_num as set_num    --  SET番号        
	,h.request_number as request_number    --  申込認識番号        
	,ap.id as pair_loan_id    --  ペアローン相手ID        
	,h.request_body as request_body    --  リクエストボディ        
	,h.status_code as status_code    --  ステータスコード        
	,h.response_body as response_body    --  レスポンスボディ        
	,h.created_at    --  作成日付        
	,h.updated_at    --  更新日付        
from mortgage_loan_tool_be_production.api_histories h
  inner join p_application_banks ab
    on h.p_application_header_id = ab.old_header_id and h.bank_code=ab.bank_code
  left join p_application_headers ap
    on h.linking_number=ap.old_id
order by h.id
;

-- 19. インターフェイス設定	s_if_configs
truncate table s_if_configs;
insert into s_if_configs
(
	id    --  ID
	,s_bank_id    --  銀行ID
	,field_name    --  フィールド
	,to_10000_unit    --  万単位
	,min_length    --  最小長
	,max_length    --  最大長
	,min_value    --  最小値
	,max_value    --  最大値
	,to_han    --  半角
	,to_zen    --  全角
	,regex    --  正規表現
	,module    --  モジュール
	,mapping    --  マッピング
	,is_required    --  必須
	,date_format    --  日付形式
	,data_origin    --  データ源
	-- ,created_at    --  作成日付
	-- ,updated_at    --  更新日付
)
select
	UUID_SHORT() as id    --  ID
	,sb.id as s_bank_id    --  銀行ID
	,ic.field_name    --  フィールド
	,ic.to_10000_unit    --  万単位
	,ic.min_length    --  最小長
	,ic.max_length    --  最大長
	,ic.min_value    --  最小値
	,ic.max_value    --  最大値
	,ic.to_han    --  半角
	,ic.to_zen    --  全角
	,ic.regex    --  正規表現
	,ic.module    --  モジュール
	,ic.maps as mapping    --  マッピング
	,ic.is_required    --  必須
	,ic.date_format    --  日付形式
    ,concat('{"field": "',tb_info_new.COLUMN_NAME,'", "table": "',tb_info_new.Table
		,case when ic.where_value is not null then concat('", "where": "',case when  tb_info_old.Table='p_applicant_persons' and tb_info_new.Table='p_application_headers' then 'id={application_header_id}'
		else ic.where_value
        end,'"}') else '"}' end
    ) 
    as data_origin   --  データ源

from 
(
SELECT 
a.* 
,
case when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='sex' then 'gender'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='owner_email' then 'email'
    -- p_application_headers
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='person_occupancy' then 'new_house_self_resident'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='has_join_guarantor' then 'join_guarantor_umu'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='collateral_type' then 'property_type'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='joint_ownership_division' then 'property_joint_ownership_type'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='acquisition_time_of_the_land' then 'property_land_acquire_date'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='joint_ownership_division' then 'property_joint_ownership_type'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='relative_donation_amount' then 'funding_relative_donation_amount'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='amount_others' then 'funding_other_refinance_amount'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='house_purchase_price' then 'required_funds_house_amount'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='amount_any_loans' then 'funding_other_loan_amount'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='saving_amount' then 'funding_self_amount'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='additional_cost' then 'required_funds_additional_amount'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='land_and_building_price' then 'property_total_price'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='building_price' then 'property_building_price'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='land_ratio_denominator' then 'property_land_ratio_denominator'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='land_ratio_numerator' then 'property_land_ratio_numerator'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='building_ratio_denominator' then 'property_building_ratio_denominator'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='building_ratio_numerator' then 'property_building_ratio_numerator'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='collateral_address_kana' then 'property_address_kana'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='land_price' then 'property_land_price'
    
    -- p_applicant_persons
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='maternity_paternity_leave_status' then 'maternity_paternity_leave'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='industry' then 'office_industry'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='emplmt_form_code' then 'office_employment_type'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='occupation_detail' then 'office_occupation_detail'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='other_office_address_kana' then 'office_other_address_kana'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='other_office_address_kanji' then 'office_other_address_kanji'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='office_phone_number' then 'office_phone'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='headquarters_location' then 'office_head_location'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='number_of_employee' then 'office_employee_num'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='department' then 'office_department'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='position' then 'office_role'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='employment_started_date' then 'office_joining_date'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='listed_division' then 'office_listed_division'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='capital_stock' then 'office_capital_stock'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='department' then 'office_department'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='position' then 'office_role'
  	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='job_change_company_name_kanji' then 'job_change_office_name_kanji'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='prev_company_year_num' then 'prev_office_year_num'
   
    -- p_applicant_persons →　p_application_headers
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='current_residence' then 'curr_house_residence_type'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='lived_length_year_num' then 'curr_house_lived_year'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='lived_length_month_num' then 'curr_house_lived_month'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='occupation' then 'office_occupation'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='lived_length_year_num' then 'curr_house_lived_year'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='lived_length_month_num' then 'curr_house_lived_month'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='land_purchase_price' then 'required_funds_land_amount'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='region_type' then 'property_region_type'
    
    -- p_borrowing_details
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='temporary_desired_loan_amount' then 'desired_loan_amount'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='halfyear_bonus' then 'bonus_repayment_amount'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='loan_term_year_num' then 'loan_term_year'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='loan_term_month_num' then 'loan_term_month'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='loan_desired_borrowing_date' then 'desired_borrowing_date'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='desired_monthly_bonus' then 'bonus_repayment_month'
    
    -- p_join_guarantors
   	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='emergency_contact_number' then 'emergency_contact'
    -- p_residents
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='relationship' then 'rel_to_applicant_a'
    
    --  p_borrowings
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='current_balance_amount' then 'curr_loan_balance_amount'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='loan_deadline_date' then 'loan_end_date'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='borrowing_type' then 'type'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='borrowing_category' then 'category'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='other_purpose' then 'loan_purpose_other'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='expected_repayment_date' then 'scheduled_loan_payoff_date'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='business_borrowing_type' then 'loan_business_target'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='specific_loan_purpose' then 'loan_business_target_other'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='rental_room_number' then 'rental_room_num'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='estate_mortgage' then 'estate_setting'
	when JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='guaranteed_status' then 'estate_setting'
	else
		JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))
	end as field_value_new
,case when (JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.table')) ='p_applicant_persons' and JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='has_join_guarantor' )
		or (JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.table')) ='p_applicant_persons' and JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='current_residence' )
		or (JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.table')) ='p_applicant_persons' and JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='lived_length_year_num' )
		or (JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.table')) ='p_applicant_persons' and JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field'))='lived_length_month_num' )
	then 'p_application_headers'
	else
		JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.table')) 
	end AS table_value_new
-- ,JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.where')) AS where_value_new
,JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.field')) AS field_value
,JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.table')) AS table_value
,JSON_UNQUOTE(JSON_EXTRACT(a.data_origin, '$.where')) AS where_value
FROM mortgage_loan_tool_be_production.if_configs a ) ic
	left join 
	(
		SELECT 
		TABLE_NAME AS 'Table',
		COLUMN_NAME 
		FROM INFORMATION_SCHEMA.COLUMNS 
		WHERE TABLE_SCHEMA = 'mortgage_staging' 
		AND TABLE_NAME in ( 'p_applicant_persons','p_application_headers','p_join_guarantors','p_borrowing_details','p_residents','p_borrowings')
		) tb_info_new on ic.table_value_new =tb_info_new.table and ic.field_value_new=tb_info_new.COLUMN_NAME

	left join 
	(
		SELECT 
		TABLE_NAME AS 'Table',
		COLUMN_NAME 
		FROM INFORMATION_SCHEMA.COLUMNS 
		WHERE TABLE_SCHEMA = 'mortgage_staging' 
		AND TABLE_NAME in ( 'p_applicant_persons','p_application_headers','p_join_guarantors','p_borrowing_details','p_residents','p_borrowings')
		) tb_info on ic.table_value =tb_info.table and ic.field_value=tb_info.COLUMN_NAME
	left join
     (   
			SELECT 
		TABLE_NAME AS 'Table',
		COLUMN_NAME 
		FROM INFORMATION_SCHEMA.COLUMNS 
		WHERE TABLE_SCHEMA = 'mortgage_loan_tool_be_production' 
		AND TABLE_NAME in ( 'p_applicant_persons','p_application_headers','p_join_guarantors','p_borrowing_details','p_residents','p_borrowings')
		) tb_info_old on ic.table_value =tb_info_old.table and ic.field_value=tb_info_old.COLUMN_NAME
	left join s_banks sb
		on ic.bank_code=sb.code
;


-- -----------------　以下は、モジュール作成が必要
-- . 審査スターテスエラーログ	p_examine_status_error_logs
/*
truncate table p_examine_status_error_logs;
insert into p_examine_status_error_logs(
	id    --  ID        
	,p_application_bank_id    --  申込銀行ID        
	,s3_key    --  s3キー        
	,s3_bucket    --  s3バケット        
	,request_no    --  申込認識番号        
	,error_detail    --  エラー        
	,created_at    --  作成日付        
	,updated_at    --  更新日付        
)
select 
	UUID_SHORT() as id    --  ID        
	,ab.id as p_application_bank_id    --  申込銀行ID        
	,el.s3_key    --  s3キー        
	,el.s3_bucket    --  s3バケット        
	,el.request_number as request_no    --  申込認識番号        
	,el.error_detail    --  エラー        
	,el.created_at    --  作成日付        
	,el.updated_at    --  更新日付        
from mortgage_loan_tool_be_production.examine_status_error_logs el
  inner join p_application_banks ab
    on el.p_application_header_id=ab.old_header_id
  ;





  
-- . 案件更新履歴	p_activities
truncate table p_activities;
insert into p_activities(
	id    --  ID        
	,p_application_header_id    --  案件ID        
	,operator_type    --  操作者区分        1：ユーザー；２：業者；３：銀代
	,operator_id    --  操作者ID        
	,table_name    --  テーブル名        
	,field_name    --  フィールド名        
	,table_id    --  テーブルID        
	,content    --  内容        
	,operate_type    --  操作種類        1: 申込; 2:更新 ; 3追加: ; 9:削除
	,created_at    --  作成日付        
	,updated_at    --  更新日付        
)
select 
	UUID_SHORT() as id   
	,ah.id as p_application_header_id      
	,case when a.owner_type='User' then 1
			when a.owner_type='SSalePerson' then 2
            when a.owner_type='Manager' then 3
            end as operator_type
	,mt.id as operator_id    --  操作者ID        
	,case when a.trackable_type='PApplicationHeader' then 'p_application_headers'
			when a.trackable_type='PApplicantPerson' then 'p_applicant_persons'
			when a.trackable_type='PBorrowingDetail' then 'p_borrowing_details'
			when a.trackable_type='PBorrowing' then 'p_borrowings'
			when a.trackable_type='PJoinGuarantor' then 'p_join_guarantors'
			when a.trackable_type='PResident' then 'p_residents'
			when a.trackable_type='Memo' then 'p_memos'
			when a.trackable_type='Manager' then 's_managers'
			when a.trackable_type='Draft' then 'p_drafts'
			when a.trackable_type='ArchiveFile' then 'c_archive_files'
			when a.trackable_type='SSalePerson' then 's_sales_persons'
			when a.trackable_type='User' then 'c_users'
	end as table_name
	,replace( a.parameters
				,'---\n'
                ,'')
			as field_name 
	,id_m.table_id as table_id 
	,a.key as operate_type
	,a.created_at
	,a.updated_at 
from mortgage_loan_tool_be_production.activities a
	left join (select id,old_id,'User' as o_type
		from mortgage_staging.c_users
		union all
		select id,old_id,'SSalePerson' as o_type
		from mortgage_staging.s_sales_persons
		union all
		select id,old_id,'Manager' as o_type
		from mortgage_staging.s_managers) mt
	on a.owner_type=mt.o_type and a.owner_id=mt.old_id
    left join mortgage_staging.p_application_headers ah
		on a.recipient_id=ah.old_id
	left join(
				select old_id,id as table_id,'PApplicationHeader' as trackable_type
				from mortgage_staging.p_application_headers
				union all
				select old_id,id as table_id,'PApplicantPerson' as trackable_type
				from mortgage_staging.p_applicant_persons
				union all
				select old_id,id as table_id,'PBorrowingDetail' as trackable_type
				from mortgage_staging.p_borrowing_details
				union all
				select old_id,id as table_id,'PBorrowing' as trackable_type
				from mortgage_staging.p_borrowings
				union all
				select old_id,id as table_id,'PJoinGuarantor' as trackable_type
				from mortgage_staging.p_join_guarantors
				union all
				select old_id,id as table_id,'PResident' as trackable_type
				from mortgage_staging.p_residents
				union all
				select old_id,id as table_id,'Memo' as trackable_type
				from mortgage_staging.p_memos
				union all
				select old_id,id as table_id,'Manager' as trackable_type
				from mortgage_staging.s_managers
				union all
				select old_id,id as table_id,'SSalePerson' as trackable_type
				from mortgage_staging.s_sales_persons
				union all
				select old_id,id as table_id,'User' as trackable_type
				from mortgage_staging.c_users
				-- union all
				-- select old_id,id as table_id,'Draft' as trackable_type
				-- from mortgage_staging.p_drafts
				-- union all
				-- select old_id,id as table_id,'ArchiveFile' as trackable_type
				-- from mortgage_staging.c_archive_files
			) id_m
		on a.trackable_type=id_m.trackable_type and a.trackable_id=id_m.old_id
;

-- . 案件書類	p_uploaded_files
/*
truncate table p_uploaded_files;
insert into p_uploaded_files(
	id    --  ID        
	,owner_type    --  所有者区分        1：ユーザー；２：業者；３：銀代
	,owner_id    --  所有者ID        
	,p_application_header_id    --  案件メイン情報ID        
	,type    --  区分        未使用
	,s3_key    --  S3キー        
	,file_name    --  ファイル名        
	,deleted    --  論理削除        1: 削除
	,created_at    --  作成日付        
	,updated_at    --  更新日付        
)
select 
	id    --  ID        
	,owner_type    --  所有者区分        1：ユーザー；２：業者；３：銀代
	,owner_id    --  所有者ID        
	,p_application_header_id    --  案件メイン情報ID        
	,type    --  区分        未使用
	,s3_key    --  S3キー        
	,file_name    --  ファイル名        
	,deleted    --  論理削除        1: 削除
	,created_at    --  作成日付        
	,updated_at    --  更新日付        
from mortgage_loan_tool_be_production.


-- . 業者共有書類	c_archive_files
truncate table c_archive_files;
insert into c_archive_files(
	id    --  ID        
	,s_sales_company_org_id    --  連携先ID        
	,s_sales_person_id    --  業者ID        
	,file_names    --  ファイル名　複数        
	,note    --  備考内容        
	,s3_key    --  S3キー        
	,deleted    --  論理削除        1:削除
	,created_at    --  作成日付        
	,updated_at    --  更新日付        
)
select 
	id    --  ID        
	,s_sales_company_org_id    --  連携先ID        
	,s_sales_person_id    --  業者ID        
	,file_names    --  ファイル名　複数        
	,note    --  備考内容        
	,s3_key    --  S3キー        
	,deleted    --  論理削除        1:削除
	,created_at    --  作成日付        
	,updated_at    --  更新日付        
from mortgage_loan_tool_be_production.archive_files
;

-- . アクセスログ	c_access_logs
truncate table c_access_logs;
insert into c_access_logs(
	id    --  ID        
	,account_id    --  アカウントID        
	,ip    --  IP        
	,url    --  URL        
	,endpoint    --  エンドポイント        
	,method    --  メソッド        
	,params    --  パラメータ        
	,status_code    --  ステータスコード        
	,response_body    --  レスポンスボディ        
	,created_at    --  作成日付        
	,updated_at    --  更新日付        
)
select 
	id    --  ID        
	,account_id    --  アカウントID        
	,ip    --  IP        
	,url    --  URL        
	,endpoint    --  エンドポイント        
	,method    --  メソッド        
	,params    --  パラメータ        
	,status_code    --  ステータスコード        
	,response_body    --  レスポンスボディ        
	,created_at    --  作成日付        
	,updated_at    --  更新日付        
from mortgage_loan_tool_be_production.s_access_logs
;

-- . ドラフト	p_drafts
truncate table p_drafts;
insert into p_drafts(
	id    --  ID        
	,c_user_id    --  ユーザーID        
	,data    --  データー        
	,created_at    --  作成日付        
	,updated_at    --  更新日付        
)
select 
	id    --  ID        
	,c_user_id    --  ユーザーID        
	,data    --  データー        
	,created_at    --  作成日付        
	,updated_at    --  更新日付        
from mortgage_loan_tool_be_production.drafts;

*/

ALTER TABLE s_sales_company_orgs DROP COLUMN old_id ;
ALTER TABLE s_sales_company_orgs DROP COLUMN path ;
ALTER TABLE s_sales_persons DROP COLUMN old_id ;
ALTER TABLE s_banks DROP COLUMN old_id ;
ALTER TABLE s_managers DROP COLUMN old_id ;
ALTER TABLE c_users DROP COLUMN old_id ;
ALTER TABLE p_application_headers DROP COLUMN old_id ;
ALTER TABLE p_application_headers DROP COLUMN old_user_id ;
ALTER TABLE p_application_headers DROP COLUMN application_status;
ALTER TABLE p_application_headers DROP COLUMN provisional_result ;
ALTER TABLE p_application_headers DROP COLUMN soudan_no ;
ALTER TABLE p_application_headers DROP COLUMN under_review_status ;
ALTER TABLE p_application_headers DROP COLUMN interface_status ;
ALTER TABLE p_application_headers DROP COLUMN send_date ;
ALTER TABLE p_applicant_persons DROP COLUMN old_id ;

ALTER TABLE p_applicant_persons DROP COLUMN p_borrowing_details ;
ALTER TABLE p_applicant_persons DROP COLUMN p_borrowings ;
ALTER TABLE p_applicant_persons DROP COLUMN p_drafts ;
ALTER TABLE p_applicant_persons DROP COLUMN p_join_guarantors ;
ALTER TABLE p_applicant_persons DROP COLUMN p_memos ;
ALTER TABLE p_applicant_persons DROP COLUMN p_residents ;

ALTER TABLE p_application_banks DROP COLUMN old_header_id ;
ALTER TABLE p_application_banks DROP COLUMN bank_code ;


SET FOREIGN_KEY_CHECKS = 1;