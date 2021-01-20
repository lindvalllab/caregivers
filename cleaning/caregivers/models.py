import pandas as pd

from cleaning.caregivers import (
    main
)

COLS_TO_USE = [
    "HADM_ID",
    "SUBJECT_ID",
    "ADMISSION_AGE",
    "SEX",
    "MARITAL_STATUS",
    "ETHNICITY",
    "ELIX_SCORE",
    "SOFA",
    "ANNOTATION_CHILD",
    "ANNOTATION_SPOUSE",
    "ANNOTATION",
    "IDENTIFIED_CONV_GOC",
    "IDENTIFIED_CONV_LIM",
    "HOSPITAL_EXPIRE_FLAG",
    "MORTALITY_3MO_FROM_HADM_ADMIT",
    "MORTALITY_1Y_FROM_HADM_ADMIT",
    "MORTALITY_6MO_FROM_ICU_OUT"
]


def latest_hadm(df: pd.DataFrame) -> pd.DataFrame:
    latest = df.groupby("SUBJECT_ID")["ADMISSION_AGE"].idxmax()
    
    df = df.loc[latest]
    
    return df.reset_index(drop=True)


def encode_binary_cols(df):
    df = df.copy()
    
    df["SEX"] = df["SEX"].map({"M": 0, "F": 1})
    
    bool_cols = [
        "ANNOTATION_CHILD",
        "ANNOTATION_SPOUSE",
        "IDENTIFIED_CONV_GOC",
        "IDENTIFIED_CONV_LIM",
        "HOSPITAL_EXPIRE_FLAG",
        "MORTALITY_3MO_FROM_HADM_ADMIT",
        "MORTALITY_1Y_FROM_HADM_ADMIT",
        "MORTALITY_6MO_FROM_ICU_OUT"
    ]
    
    for col in bool_cols:
        df[col] = df[col].map({False: 0, True: 1})
    
    return df


def load_data():
    df = main.load_data()
    df = df[COLS_TO_USE].copy()
#     df = latest_hadm(df)
    df = encode_binary_cols(df)
    
    return df
