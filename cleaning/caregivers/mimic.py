import pandas as pd

from cleaning.utils import get_project_root


PROJECT_ROOT = get_project_root()


def path_to_mimic(file):
    return PROJECT_ROOT / "data/raw/mimic-iii/{}.csv".format(file)


def path_to_mimic_derived(file):
    return PROJECT_ROOT / "data/raw/mimic-iii-derived/{}.csv".format(file)


def load_main_tables():
    df_admissions = pd.read_csv(path_to_mimic("ADMISSIONS"))
    df_icustays = pd.read_csv(path_to_mimic("ICUSTAYS"))
    df_patients = pd.read_csv(path_to_mimic("PATIENTS"))
    
    df_admissions = df_admissions.drop(columns=["ROW_ID"])
    df_icustays = df_icustays.drop(columns=["ROW_ID"])
    df_patients = df_patients.drop(columns=["ROW_ID"])
    
    df = df_admissions.merge(df_patients,
                             on="SUBJECT_ID")\
                      .merge(df_icustays,
                             on=["SUBJECT_ID", "HADM_ID"])
    
    return df


def load_ventduration_table():
    df = pd.read_csv(path_to_mimic_derived("ventdurations"))
    
    # columns in this one are lowercase for some reason
    df.columns = df.columns.str.upper()
    
    # drop rows with no ICUSTAY_ID; we won't be able to use them
    df = df.dropna(subset=["ICUSTAY_ID"])
    
    # now we can make ICUSTAY_ID into an int column
    df["ICUSTAY_ID"] = df["ICUSTAY_ID"].astype(int)

    return df


def load_sofa_table():
    df = pd.read_csv(path_to_mimic_derived("sofa"))
    
    # columns in this one are lowercase for some reason
    df.columns = df.columns.str.upper()
    
    return df
    

def load_data():
    df_main = load_main_tables()
    df_vent = load_ventduration_table()
    df_sofa = load_sofa_table()
    
    df = df_main.merge(df_vent)\
                .merge(df_sofa)
    
    return df
