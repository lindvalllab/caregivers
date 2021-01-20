import pandas as pd


def ethnicity(df):
    df["ETHNICITY"] = df["ETHNICITY"].replace({
        "^ASIAN.*": "OTHER",
        "^BLACK.*": "OTHER",
        "^HISPANIC.*": "OTHER",
        "^WHITE.*": "(NON-HISPANIC) WHITE",
        "AMERICAN INDIAN/ALASKA NATIVE FEDERALLY RECOGNIZED TRIBE": "OTHER",
        "PORTUGUESE": "OTHER",
        "MIDDLE EASTERN": "OTHER",
        "MULTI RACE ETHNICITY": "OTHER", 
        "UNABLE TO OBTAIN": "UNKNOWN/NOT SPECIFIED",
        "PATIENT DECLINED TO ANSWER": "UNKNOWN/NOT SPECIFIED"
    }, regex=True)
    
    return df


def discharge_location(df):
    df["DISCHARGE_LOCATION"] = df["DISCHARGE_LOCATION"].replace({
        ".*HOSPICE.*": "HOSPICE",
        "ICF": "SNF",
        "REHAB/DISTINCT PART HOSP": "SNF",
        "SHORT TERM HOSPITAL": "OTHER",
        "DISC-TRAN TO FEDERAL HC": "OTHER",
        "DISCH-TRAN TO PSYCH HOSP": "OTHER",
        "OTHER FACILITY": "OTHER"
    }, regex=True)
    
    df["DISCHARGE_LOCATION"] = df["DISCHARGE_LOCATION"].replace({
        "DEAD/EXPIRED": "DEATH",
        "HOME HEALTH CARE": "HOME",
        "HOSPICE": "FACILITY",
        "LONG TERM CARE HOSPITAL": "FACILITY",
        "SNF": "FACILITY",
        "OTHER": "FACILITY",
        "LEFT AGAINST MEDICAL ADVI": "UNKNOWN/NOT SPECIFIED"
    })
    
    return df


def marital_status(df):
    df["MARITAL_STATUS"] = df["MARITAL_STATUS"].replace({
        "SINGLE": "NOT MARRIED",
        "WIDOWED": "NOT MARRIED",
        "DIVORCED": "NOT MARRIED",
        "SEPARATED": "NOT MARRIED"
    }, regex=True)
    
    df["MARITAL_STATUS"] = df["MARITAL_STATUS"].fillna("UNKNOWN/NOT SPECIFIED")
    
    return df


def language(df):
    is_engl = df["LANGUAGE"] == "ENGL"
    is_ptun = df["LANGUAGE"] == "PTUN"
    is_span = df["LANGUAGE"] == "SPAN"
    is_russ = df["LANGUAGE"] == "RUSS"
    
    to_keep = is_engl | is_ptun | is_span | is_russ
        
    df.loc[~to_keep, "LANGUAGE"] = "OTHER"
    
    return df


def hospital_expire_flag_to_bool(df):
    df["HOSPITAL_EXPIRE_FLAG"] = df["HOSPITAL_EXPIRE_FLAG"].replace({
        0: False,
        1: True
    })
    return df
