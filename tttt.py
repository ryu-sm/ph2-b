import json


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

temp = {}

for k, v in p_applicant_person_parameters_files.items():
    temp[v] = k

print(json.dumps(temp, ensure_ascii=False, indent=4))
