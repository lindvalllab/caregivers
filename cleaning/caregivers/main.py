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


def process_all():
    df = annotations.load_data()
    df = df.merge(mimic.load_data())
    df = df.merge(neuroner.load_data())
    df = handle_datetime_types(df)
    df = compute.time_to_vent(df)
    df = compute.time_to_death(df)
    df = compute.los_hadm(df)
    df = compute.admission_age(df)
    df = compute.elixhauser_scores(df)
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
        ANNOTATION=("ANNOTATION", squish),
        IDENTIFIED_CONV_GOC=("CAR", "any"),
        IDENTIFIED_CONV_LIM=("LIM", "any"),
        HOSPITAL_EXPIRE_FLAG=("HOSPITAL_EXPIRE_FLAG", squish),
        MORTALITY_3MO_FROM_HADM_ADMIT=("MORTALITY_3MO_FROM_HADM_ADMIT", squish),
        MORTALITY_1Y_FROM_HADM_ADMIT=("MORTALITY_1Y_FROM_HADM_ADMIT", squish),
        VENT_TIME_FROM_HADM=("VENT_TIME_FROM_HADM", "min"),
        VENT_FIRST_48_HADM=("VENT_FIRST_48_HADM", "any"),
        
        # elixhauser
        CONGESTIVE_HEART_FAILURE=("CONGESTIVE_HEART_FAILURE", squish),
        CARDIAC_ARRHYTHMIAS=("CARDIAC_ARRHYTHMIAS", squish),
        VALVULAR_DISEASE=("VALVULAR_DISEASE", squish),
        PULMONARY_CIRCULATION=("PULMONARY_CIRCULATION", squish),
        PERIPHERAL_VASCULAR=("PERIPHERAL_VASCULAR", squish),
        HYPERTENSION=("HYPERTENSION", squish),
        PARALYSIS=("PARALYSIS", squish),
        OTHER_NEUROLOGICAL=("OTHER_NEUROLOGICAL", squish),
        CHRONIC_PULMONARY=("CHRONIC_PULMONARY", squish),
        DIABETES_UNCOMPLICATED=("DIABETES_UNCOMPLICATED", squish),
        DIABETES_COMPLICATED=("DIABETES_COMPLICATED", squish),
        HYPOTHYROIDISM=("HYPOTHYROIDISM", squish),
        RENAL_FAILURE=("RENAL_FAILURE", squish),
        LIVER_DISEASE=("LIVER_DISEASE", squish),
        PEPTIC_ULCER=("PEPTIC_ULCER", squish),
        AIDS=("AIDS", squish),
        LYMPHOMA=("LYMPHOMA", squish),
        METASTATIC_CANCER=("METASTATIC_CANCER", squish),
        SOLID_TUMOR=("SOLID_TUMOR", squish),
        RHEUMATOID_ARTHRITIS=("RHEUMATOID_ARTHRITIS", squish),
        COAGULOPATHY=("COAGULOPATHY", squish),
        OBESITY=("OBESITY", squish),
        WEIGHT_LOSS=("WEIGHT_LOSS", squish),
        FLUID_ELECTROLYTE=("FLUID_ELECTROLYTE", squish),
        BLOOD_LOSS_ANEMIA=("BLOOD_LOSS_ANEMIA", squish),
        DEFICIENCY_ANEMIAS=("DEFICIENCY_ANEMIAS", squish),
        ALCOHOL_ABUSE=("ALCOHOL_ABUSE", squish),
        DRUG_ABUSE=("DRUG_ABUSE", squish),
        PSYCHOSES=("PSYCHOSES", squish),
        DEPRESSION=("DEPRESSION", squish),
        ELIX_SCORE=("ELIX_UNWEIGHTED", squish),
        ELIX_WEIGHTED_VW=("ELIX_WEIGHTED_VW", squish),
        ELIX_WEIGHTED_AHRQ=("ELIX_WEIGHTED_AHRQ", squish)
    ).reset_index()
    
    
    # SOFA
    df_h = df_h.merge(hadm.earliest_sofa(df))
    
    # Ventilation
    df_h = df_h.merge(hadm.vent_total_hours(df))
    df_h = df_h.merge(hadm.vent_total_count(df))
    df_h = df_h.merge(hadm.vent_time_from_first_icu(df))
    df_h = df_h.merge(hadm.vent_first_48_first_icu(df))
    
    # Post ICU mortality
    df_h = df_h.merge(hadm.post_icu_mortality(df))
            
    return df_h
