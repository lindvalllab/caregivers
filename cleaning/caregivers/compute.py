import numpy as np
import pandas as pd

from cleaning import elixhauser_weights
from cleaning.caregivers import mimic


def los_hadm(df: pd.DataFrame) -> pd.DataFrame:
    df["LOS_HADM"] = df["DISCHTIME"].subtract(df["ADMITTIME"]) / np.timedelta64(1, "D")
    return df
    
    
def admission_age(df: pd.DataFrame) -> pd.DataFrame:
    df["ADMISSION_AGE"] = df["ADMITTIME"].subtract(df["DOB"]) / np.timedelta64(1, "Y")
    return df


def time_to_death(df: pd.DataFrame) -> pd.DataFrame:
    df["DAYS_TO_DEATH_HADM"] = df["DOD"].subtract(df["ADMITTIME"]) / np.timedelta64(1, "D")
    df["DAYS_TO_DEATH_ICU"] = df["DOD"].subtract(df["OUTTIME"]) / np.timedelta64(1, "D")
        
    # Null values imply patient has survived (not sure of source)
    # These will get mapped to False in the comparisons below
    days_to_death_hadm = df["DAYS_TO_DEATH_HADM"]
    days_to_death_icu = df["DAYS_TO_DEATH_ICU"]    
    
    df["MORTALITY_3MO_FROM_HADM_ADMIT"] = days_to_death_hadm < 90
    df["MORTALITY_1Y_FROM_HADM_ADMIT"] = days_to_death_hadm < 365
    df["MORTALITY_6MO_FROM_ICU_OUT"] = days_to_death_icu < 180

    return df


def time_to_vent(df: pd.DataFrame) -> pd.DataFrame:
    df["VENT_TIME_FROM_HADM"] = df["STARTTIME"].subtract(df["ADMITTIME"]) / np.timedelta64(1, "h")
    df["VENT_TIME_FROM_ICU"] = df["STARTTIME"].subtract(df["INTIME"]) / np.timedelta64(1, "h")

    df["VENT_FIRST_48_HADM"] = df["VENT_TIME_FROM_HADM"] < 48
    df["VENT_FIRST_48_ICU"] = df["VENT_TIME_FROM_ICU"] < 48
    
    return df


def elixhauser_scores(df: pd.DataFrame) -> pd.DataFrame:
    vw = elixhauser_weights.vw
    ahrq = elixhauser_weights.ahrq
    
    # vw should be the same as ahrq
    df["ELIX_UNWEIGHTED"] = df[vw.keys()].sum(1)
    df["ELIX_WEIGHTED_VW"] = (df[vw.keys()]*vw).sum(1)
    df["ELIX_WEIGHTED_AHRQ"] = (df[ahrq.keys()]*ahrq).sum(1)
    
    return df


def readmission(df: pd.DataFrame) -> pd.DataFrame:
    # reload mimic data (more readable than efficient)
    df_m = mimic.load_data()
    df_m = df_m[["SUBJECT_ID", "HADM_ID", "ADMITTIME"]].drop_duplicates()
    
    # check each ADMITTIME only has one HADM_ID associated with it
    # for a given subject
    assert (df_m.groupby(["ADMITTIME", "SUBJECT_ID"])["HADM_ID"].nunique() == 1).all()
    
    # find the admittimes of the last hospital admit for each patient
    df_subj = df_m.groupby("SUBJECT_ID")\
                  .agg(ADMITTIME_LATEST=("ADMITTIME", "max"))\
                  .reset_index()
    
    df_m = df_m.merge(df_subj)
    
    df_m["HAS_READMISSION"] = df_m["ADMITTIME"] < df_m["ADMITTIME_LATEST"]
    
    df_m = df_m[["SUBJECT_ID", "HADM_ID", "HAS_READMISSION"]].drop_duplicates()
    
    df = df.merge(df_m)
    
    return df
    