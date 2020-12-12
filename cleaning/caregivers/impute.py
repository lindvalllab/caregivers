import pandas as pd


def admission_age(df: pd.DataFrame) -> pd.DataFrame:
    """Median age of those whose DOB were shifted is 91.4.
    
    For details, see: https://mimic.physionet.org/mimictables/patients/
    """
    shifted = (df["ADMISSION_AGE"] < 0)
    
    df.loc[shifted, "ADMISSION_AGE"] = 91.4
    
    return df
