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


# ENUM
class USER_STATUS(Enum):
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
    REGISTER = "新規登録"
    LOGIN = "ログイン"
    LOGOUT = "ログアウト"
    UPDATE = "更新"
    DELETE = "削除"
    DOWNLOAD = "ダウンロード"
