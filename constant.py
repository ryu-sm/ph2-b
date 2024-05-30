from enum import Enum

DEFAULT_200_MSG = {"message": "successful"}
DEFAULT_500_MSG = {"message": "An unknown exception occurred, please try again later."}

JSON_FIELD_KEYS = [
    #
    "new_house_planned_resident_overview",
    "property_business_type",
    "refund_source_type",
    #
    "income_sources",
    "tax_return_reasons",
]

JSON_DICT_FIELD_KEYS = ["new_house_planned_resident_overview"]
JSON_LIST_FIELD_KEYS = ["property_business_type", "refund_source_type", "income_sources", "tax_return_reasons"]
INIT_NEW_HOUSE_PLANNED_RESIDENT_OVERVIEW = {
    "father": None,
    "fiance": None,
    "mother": None,
    "others": None,
    "spouse": None,
    "children": None,
    "father_umu": False,
    "fiance_umu": False,
    "mother_umu": False,
    "others_rel": None,
    "others_umu": False,
    "spouse_umu": False,
    "children_umu": False,
    "brothers_sisters": None,
    "brothers_sisters_umu": False,
}


P_APPLICATION_HEADERS_FILE_FIELF_KEYS = ["G", "J", "R"]
P_BORROWINGS_FILE_FIELF_KEYS = ["I"]
P_APPLICANT_PERSONS_FILE_FIELF_KEYS = [
    "H__a",
    "H__b",
    "A__01__a",
    "A__01__b",
    "A__02",
    "A__03__a",
    "A__03__b",
    "B__a",
    "B__b",
    "C__01",
    "C__02",
    "C__03",
    "C__04",
    "C__05",
    "D__01",
    "D__02",
    "D__03",
    "E",
    "F__01",
    "F__02",
    "F__03",
    "K",
    "S",
]

FILE_FIELF_KEYS = [
    # p_application_headers関連
    "G",
    "J",
    "R",
    # p_applicant_persons関連
    "H__a",
    "H__b",
    "A__01__a",
    "A__01__b",
    "A__02",
    "A__03__a",
    "A__03__b",
    "B__a",
    "B__b",
    "C__01",
    "C__02",
    "C__03",
    "C__04",
    "C__05",
    "D__01",
    "D__02",
    "D__03",
    "E",
    "F__01",
    "F__02",
    "F__03",
    "K",
    "S",
    # p_borrowings関連
    "I",
]

OWNER_TYPE_EN_MAPS = {
    1: "USER",
    2: "SALES_PERSON",
    3: "MANAGER",
}

MANN_TRANSLATE_FIELDS = [
    # 年收入
    "last_year_income",
    "last_year_bonus_income",
    "before_last_year_income",
    # 剩余LOAN
    "curr_house_shell_scheduled_price",
    # 物件
    "property_building_price",
    "property_land_price",
    "property_total_price",
    # 资金计划
    "required_funds_land_amount",
    "required_funds_house_amount",
    "required_funds_accessory_amount",
    "required_funds_additional_amount",
    "required_funds_refinance_loan_balance",
    "required_funds_upgrade_amount",
    "required_funds_loan_plus_amount",
    "required_funds_total_amount",
    "funding_saving_amount",
    "funding_other_saving_amount",
    "funding_estate_sale_amount",
    "funding_self_amount",
    "funding_relative_donation_amount",
    "funding_loan_amount",
    "funding_pair_loan_amount",
    "funding_other_amount",
    "funding_other_loan_amount",
    "funding_other_refinance_amount",
    "funding_total_amount",
    # 完済原資
    "refund_source_amount",
    # 借入
    "desired_loan_amount",
    "bonus_repayment_amount",
    "loan_amount",
    "curr_loan_balance_amount",
    "annual_repayment_amount",
]


# ENUM
class USER_STATUS(Enum):
    NORMAL = "1"
    LOCK = "2"


class SALES_PERSON_STATUS(Enum):
    NORMAL = "1"
    LOCK = "2"


class SALES_PERSON_TYPE(Enum):
    EMAIL = "1"
    AZURE = "2"


class MANAGER_STATUS(Enum):
    NORMAL = "1"
    LOCK = "2"


class AGENT_SENDED(Enum):
    DEFAULT = "0"
    SENDED = "1"


class UNSUBCRIBED(Enum):
    UNSUBCRIBED = "1"


class BANK_CODE(Enum):
    SBI = "0038"
    MCJ = "0039"


class TOKEN_ROLE_TYPE(Enum):
    USER = 1
    SALES_PERSON = 2
    MANAGER = 3


class LOAN_TYPE(Enum):
    ALONE = "1"
    PAIR_LOAN = "2"
    TOTAL_INCOME_EQUITY = "3"
    TOTAL_INCOME_NO_EQUITY = "4"


class P_UPLOAD_FILE_TYPE(Enum):
    APPLICANT = "0"
    TOTAL_INCOME = "1"


class P_APPLICANT_PERSONS_TYPE(Enum):
    APPLICANT = "0"
    TOTAL_INCOME = "1"


class P_BORROWING_DETAILS_TIME_TYPE(Enum):
    ONE_TIME = "1"
    TWO_TIME = "2"


class LAND_ADVANCE_PLAN(Enum):
    HOPE = "1"
    NOT_HOPE = "0"


class JOIN_GUARANTOR_UMU(Enum):
    HAVE = "1"
    NONE = "0"


class CURR_BORROWING_STATUS(Enum):
    HAVE = "1"
    NONE = "0"


class OPERATE_TYPE(Enum):
    APPLY = "0"
    UPDATE = "1"
    CREATE = "2"
    DELETE = "9"


class ACCESS_LOG_OPERATION(Enum):
    LOGIN = "ログイン"
    LOGOUT = "ログアウト"
    UPDATE = "更新"
    DELETE = "削除"
    DOWNLOAD = "ダウンロード"
    REGISTER = "登録"
    UNSUBCRIBED = "退会"


class ACCESS_ROLE(Enum):
    GENERAL = "1"
    MANAGER = "9"


ORG_OTHER_ID = "999999999999999999"
