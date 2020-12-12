import pandas as pd


def earliest_sofa(df: pd.DataFrame) -> pd.DataFrame:
    """Return a DataFrame of the earliest available SOFA value
    for each given HADM_ID.
    """
    
    # earliest INTIME (transfer to ICU) for a given HADM_ID
    earliest = df.groupby("HADM_ID")["INTIME"].idxmin()
    
    df = df.loc[earliest, ["HADM_ID", "SOFA"]]
    
    return df


def vent_total_hours(df: pd.DataFrame) -> pd.DataFrame:
    df = df[["HADM_ID", "ICUSTAY_ID", "VENTNUM", "DURATION_HOURS"]].drop_duplicates()

    df = df.groupby("HADM_ID")\
           .agg(VENT_TOTAL_HOURS=("DURATION_HOURS", "sum"))\
           .reset_index()

    return df


def vent_total_count(df: pd.DataFrame) -> pd.DataFrame:
    df = df[["HADM_ID", "ICUSTAY_ID", "VENTNUM", "DURATION_HOURS"]].drop_duplicates()
    
    df = df.groupby("HADM_ID")\
           .agg(VENT_TOTAL_COUNT=("VENTNUM", "nunique"))\
           .reset_index()
    
    return df


def vent_time_from_first_icu(df: pd.DataFrame) -> pd.DataFrame:
    """Time between INTIME for first ICUSTAY and ventilation event."""

    # earliest INTIME (transfer to ICU) for a given HADM_ID
    earliest = df.groupby("HADM_ID")["INTIME"].idxmin()

    df = df.loc[earliest, ["HADM_ID", "VENT_TIME_FROM_ICU"]]
    
    return df


def vent_first_48_first_icu(df: pd.DataFrame) -> pd.DataFrame:
    """Whether, for the first ICUSTAY, the first ventilation event
       began within the first 48 hours.
    """
    
    earliest = df.groupby("HADM_ID")["INTIME"].idxmin()
    
    df = df.loc[earliest, ["HADM_ID", "VENT_FIRST_48_ICU"]]
    
    return df
