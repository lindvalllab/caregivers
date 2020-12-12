import numpy as np
import pandas as pd


def los_hadm(df: pd.DataFrame) -> pd.DataFrame:
    df["LOS_HADM"] = df["DISCHTIME"].subtract(df["ADMITTIME"]) / np.timedelta64(1, "D")
    return df
    
    
def admission_age(df: pd.DataFrame) -> pd.DataFrame:
    df["ADMISSION_AGE"] = df["ADMITTIME"].subtract(df["DOB"]) / np.timedelta64(1, "Y")
    return df


def time_to_death(df: pd.DataFrame) -> pd.DataFrame:
    df["DAYS_TO_DEATH"] = df["DOD"].subtract(df["ADMITTIME"]) / np.timedelta64(1, "D")
    
    # exclude rows with missing DOD info (so mortality values are NA rather than False)
    days_to_death = df[df["DAYS_TO_DEATH"].notna()]["DAYS_TO_DEATH"]
    
    df["MORTALITY_3MO"] = days_to_death < 90
    df["MORTALITY_1Y"] = days_to_death < 365
    
    return df


def time_to_vent(df: pd.DataFrame) -> pd.DataFrame:
    df["VENT_TIME_FROM_HADM"] = df["STARTTIME"].subtract(df["ADMITTIME"]) / np.timedelta64(1, "h")
    df["VENT_TIME_FROM_ICU"] = df["STARTTIME"].subtract(df["INTIME"]) / np.timedelta64(1, "h")

    df["VENT_FIRST_48_HADM"] = df["VENT_TIME_FROM_HADM"] < 48
    df["VENT_FIRST_48_ICU"] = df["VENT_TIME_FROM_ICU"] < 48
    
    return df
