import pandas as pd

from cleaning.utils import (
    handle_datetime_types,
    squish
)
from cleaning.caregivers import (
    annotations,
    mimic,
    neuroner,
    compute,
    collapse,
    impute,
    hadm
)


def get_hadm_vent_data(df):
    vent_cols = [
        "HADM_ID",
        "ICUSTAY_ID",
        "INTIME",
        "STARTTIME",
        "ENDTIME",
        "VENTNUM",
        "DURATION_HOURS",
        "HOURS_TO_VENT_HADM",
        "HOURS_TO_VENT_ICUSTAY",
        "HAS_VENT_FIRST_48_HADM",
        "HAS_VENT_FIRST_48_ICUSTAY"
    ]
    
    df = df[vent_cols].drop_duplicates()

    group_hadm = df.groupby("HADM_ID")
    group_icu = df.groupby(["HADM_ID", "ICUSTAY_ID"])
    
    # get data for first ICUSTAY of each HADM
    vent_first_icu = df.loc[group_hadm["INTIME"].idxmin()]\
                       .reset_index(drop=True)

    vent_first_icu = vent_first_icu[[
        "HADM_ID",
        "HOURS_TO_VENT_ICUSTAY",
        "HAS_VENT_FIRST_48_ICUSTAY"
    ]]
    
    # total hours spent on vent by HADM_ID
    vent_total_hours = group_hadm["DURATION_HOURS"].sum()\
                            .rename("VENT_TOTAL_HOURS")\
                            .reset_index()
    
    # total vent events per ICUSTAY_ID
    vent_count = group_icu["VENTNUM"].nunique()\
                    .rename("VENT_COUNT")\
                    .reset_index()
    
    # total vent events per HADM_ID
    vent_total_count = vent_count.groupby("HADM_ID")["VENT_COUNT"].sum()\
                        .rename("VENT_TOTAL_COUNT")\
                        .reset_index()
        
    df = vent_first_icu.merge(vent_total_hours)\
                       .merge(vent_total_count)
    
    return df


def process_all():
    df = annotations.load_data()
    df = df.merge(mimic.load_data())
    df = df.merge(neuroner.load_data())
    df = handle_datetime_types(df)
    df = compute.time_to_vent(df)
    df = compute.time_to_death(df)
    df = compute.los_hadm(df)
    df = compute.admission_age(df)
    df = impute.admission_age(df)
    df = collapse.hospital_expire_flag_to_bool(df)
    df = collapse.ethnicity(df)
    df = collapse.marital_status(df)
    df = collapse.language(df)
    df = collapse.discharge_location(df)
    
    return df


def load_data_full():
    """Get full, unaggregated data."""
    return process_all()

def load_data():
    """Get hospital admission level data."""
    df = load_data_full()
    
    df_h = df.groupby("HADM_ID").agg(
        SEX=("GENDER", squish),
        MARITAL_STATUS=("MARITAL_STATUS", squish),
        ETHNICITY=("ETHNICITY", squish),
        LANGUAGE=("LANGUAGE", squish),
        ADMISSION_AGE=("ADMISSION_AGE", squish),
        LOS_HADM=("LOS_HADM", squish),
        DISCHARGE_LOCATION=("DISCHARGE_LOCATION", squish),
        N_ICUSTAYS=("ICUSTAY_ID", "nunique"),
        N_TEXTS=("TEXT", "nunique"),
        ANNOTATION_CHILD=("ANNOTATION_CHILD", squish),
        ANNOTATION_SPOUSE=("ANNOTATION_SPOUSE", squish),
        ANNOTATION_BOTH=("ANNOTATION_BOTH", squish),
        ANNOTATION_ANY=("ANNOTATION_ANY", squish),
        IDENTIFIED_CONV_GOC=("CAR", "any"),
        IDENTIFIED_CONV_LIM=("LIM", "any"),
        HOSPITAL_EXPIRE_FLAG=("HOSPITAL_EXPIRE_FLAG", squish),
        MORTALITY_3MO=("MORTALITY_3MO", squish),
        MORTALITY_1Y=("MORTALITY_1Y", squish),
        VENT_TIME_FROM_HADM=("VENT_TIME_FROM_HADM", "min"),
        VENT_FIRST_48_HADM=("VENT_FIRST_48_HADM", "any")
    ).reset_index()
    
    
    # SOFA
    df_h = df_h.merge(hadm.earliest_sofa(df))
    
    # Ventilation
    df_h = df_h.merge(hadm.vent_total_hours(df))
    df_h = df_h.merge(hadm.vent_total_count(df))
    df_h = df_h.merge(hadm.vent_time_from_first_icu(df))
    df_h = df_h.merge(hadm.vent_first_48_first_icu(df))
            
    return df_h
