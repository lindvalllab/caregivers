FORMULA_CONTROL = "C(SEX, Treatment(reference='M')) + "\
    "C(MARITAL_STATUS, Treatment(reference='MARRIED')) + "\
    "C(ETHNICITY, Treatment(reference='(NON-HISPANIC) WHITE')) + "\
    "ADMISSION_AGE + "\
    "ELIX_SCORE + "\
    "SOFA"


FORMULA_CONTROL_WITH_GOC = "C(SEX, Treatment(reference='M')) + "\
    "C(MARITAL_STATUS, Treatment(reference='MARRIED')) + "\
    "C(ETHNICITY, Treatment(reference='(NON-HISPANIC) WHITE')) + "\
    "ADMISSION_AGE + "\
    "ELIX_SCORE + "\
    "SOFA + "\
    "IDENTIFIED_CONV_GOC"
