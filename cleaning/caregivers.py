import numpy as np
import pandas as pd

from tableone import TableOne

from cleaning.clinical_regex import (
    join_id_with_annotations,
    has_only_one_annotation_value_per_id
)
from cleaning.neuroner import load_neuroner_results


def process_annotations(df):
    df = join_id_with_annotations(df)
    df = df.rename(columns={
        "id": "HADM_ID",
        "L1_annotation": "ANNOTATION_CHILD",
        "L2_annotation": "ANNOTATION_SPOUSE"
    })
    
    df = df[[
        "HADM_ID",
        "ANNOTATION_CHILD",
        "ANNOTATION_SPOUSE"
    ]]
    
    df = df.groupby("HADM_ID", as_index=False)\
           .agg(lambda s: s.unique())
    
    return df


def resolve_annotations(df):
    cols = [
        "ANNOTATION_CHILD",
        "ANNOTATION_SPOUSE"
    ]
    
    for col in cols:
        df[col] = df[col].replace(9, 0)
        df[col] = df[col].fillna(0)
        df[col] = df[col].astype(bool)
        
    return df


def add_annotation_combined_col(df):
    df["ANNOTATION_BOTH"] = df["ANNOTATION_CHILD"] & df["ANNOTATION_SPOUSE"]
    df["ANNOTATION_EITHER"] = df["ANNOTATION_CHILD"] | df["ANNOTATION_SPOUSE"]
    
    return df


def merge_original_data_file(df, df_original):
    df = df_original.merge(df, how="outer", on="HADM_ID")
    return df


def merge_mimic_data(df, *mimic_dfs):
    if len(mimic_dfs) == 0: return df
    
    for name, df_m in mimic_dfs:
        if name != "NOTEEVENTS":
            to_merge = df_m.drop(columns=["ROW_ID"], errors="ignore")
            
        else:
            to_merge = df_m.copy()

        to_merge.columns = to_merge.columns.str.upper()
        
        merge_cols = set(to_merge.columns)\
                   & set(df.columns)
        
        df = df.merge(to_merge, how="left", on=list(merge_cols))
        
    return df


def handle_datetime_cols(df, datetime_cols=None):
    if datetime_cols is None:
        datetime_cols = [
            "ADMITTIME",
            "DISCHTIME",
            "DEATHTIME",
            "EDREGTIME",
            "EDOUTTIME",
            "DOB",
            "DOD",
            "DOD_HOSP",
            "DOD_SSN"
        ]
    
    for col in datetime_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
    
    return df


def compute_los_hadm(df):
    df["LOS_HADM"] = df["DISCHTIME"] - df["ADMITTIME"]
    return df


def convert_los_hadm_to_days(df):
    df["LOS_HADM"] = df["LOS_HADM"] / np.timedelta64(1, "D")
    return df


def compute_admission_age(df):
    df["ADMISSION_AGE"] = df["ADMITTIME"].subtract(df["DOB"])
    return df


def convert_admission_age_to_years(df):
    df["ADMISSION_AGE"] = df["ADMISSION_AGE"] / np.timedelta64(1, "Y")
    return df


def convert_hospital_expire_flag_to_bool(df):
    df["HOSPITAL_EXPIRE_FLAG"] = df["HOSPITAL_EXPIRE_FLAG"].replace({
        0: False,
        1: True
    })
    return df


def impute_admission_age(df):
    """Median age of those whose DOB were shifted is 91.4.
    
    For details, see: https://mimic.physionet.org/mimictables/patients/
    """
    shifted = (df["ADMISSION_AGE"] < 0)
    
    df.loc[shifted, "ADMISSION_AGE"] = 91.4
    
    return df


def collapse_ethnicity_col(df):
    df["ETHNICITY"] = df["ETHNICITY"].replace({
        "^ASIAN.*": "ASIAN",
        "^BLACK.*": "BLACK/AFRICAN AMERICAN",
        "^HISPANIC.*": "HISPANIC/LATINO",
        "^WHITE.*": "WHITE",
        "AMERICAN INDIAN/ALASKA NATIVE FEDERALLY RECOGNIZED TRIBE": "AMERICAN INDIAN/ALASKA NATIVE",
        "PORTUGUESE": "OTHER",
        "MIDDLE EASTERN": "OTHER",
        "MULTI RACE ETHNICITY": "OTHER", 
        "UNABLE TO OBTAIN": "UNKNOWN/NOT SPECIFIED",
        "PATIENT DECLINED TO ANSWER": "UNKNOWN/NOT SPECIFIED"
    }, regex=True)
    
    return df


def collapse_discharge_location_col(df):
    df["DISCHARGE_LOCATION"] = df["DISCHARGE_LOCATION"].replace({
        ".*HOSPICE.*": "HOSPICE",
        "ICF": "SNF",
        "REHAB/DISTINCT PART HOSP": "SNF",
        "LEFT AGAINST MEDICAL ADVI": "OTHER",
        "SHORT TERM HOSPITAL": "OTHER",
        "DISC-TRAN TO FEDERAL HC": "OTHER",
        "DISCH-TRAN TO PSYCH HOSP": "OTHER",
        "OTHER FACILITY": "OTHER"
    }, regex=True)
    
    return df


def collapse_marital_status_col(df):
    df["MARITAL_STATUS"] = df["MARITAL_STATUS"].replace({
        "DIVORCED": "DIVORCED/SEPARATED",
        "SEPARATED": "DIVORCED/SEPARATED"
    })
    
    return df


def merge_neuroner_results(df):
    df_n = load_neuroner_results()
    df_n = df_n.drop(columns=["RESULT_STRING_CAR", "RESULT_STRING_LIM"])
    
    df = df.merge(df_n)

    return df


def process_all(df, df_original, *mimic_dfs):
    df = process_annotations(df)
    df = merge_original_data_file(df, df_original)
    df = resolve_annotations(df)
    df = add_annotation_combined_col(df)
    df = merge_mimic_data(df, *mimic_dfs)
    df = handle_datetime_cols(df)
    df = compute_los_hadm(df)
    df = convert_los_hadm_to_days(df)
    df = convert_hospital_expire_flag_to_bool(df)
    df = compute_admission_age(df)
    df = convert_admission_age_to_years(df)
    df = impute_admission_age(df)
    df = collapse_ethnicity_col(df)
    df = collapse_discharge_location_col(df)
    df = collapse_marital_status_col(df)
    df = merge_neuroner_results(df)
    
    return df


def load_data(include_noteevents=False):
    df_a = pd.read_csv("../data/raw/kmd_annotations_1163_11.19.20.csv")
    df_o = pd.read_csv("../data/raw/caregivers_set13Jul2020.csv")

    assert has_only_one_annotation_value_per_id(df_a).all()

    # mimic tables
    mimic_csvs = [
        "ADMISSIONS",
        "PATIENTS"
    ]
    
    if include_noteevents:
        mimic_csvs.append("NOTEEVENTS")
    
    mimic_dfs = [
        (file, pd.read_csv("../data/raw/mimic-iii/{}.csv".format(file)))
        for file in mimic_csvs
    ]
        
    df = process_all(df_a, df_o, *mimic_dfs)
        
    assert df["HADM_ID"].nunique() == df_o["HADM_ID"].nunique()
        
    return df


def get_hadm_data(df):
    df_h = df.drop([
        "ROW_ID",
        "TEXT",
        "CAR",
        "LIM"
    ], axis="columns")
    df_h = df_h.drop_duplicates()
    df_h = df_h.merge(
            df.groupby("HADM_ID").agg(
                N_TEXTS=("TEXT", "nunique"),
                CAR=("CAR", "any"),
                LIM=("LIM", "any")
            ).reset_index(),
            on="HADM_ID"
        )
    
    return df_h
    