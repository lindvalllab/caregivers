import numpy as np
import pandas as pd
import patsy
import statsmodels.api as sm

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


def encode_binary_cols(df):
    df = df.copy()
    
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
    df = encode_binary_cols(df)
    
    return df


def format_logit_results(model):
    odds_ratios = np.exp(model.params)
    ci = np.exp(model.conf_int())
    pvals = model.pvalues
    
    decimals = 4
    odds_ratios = np.around(odds_ratios, decimals=decimals)
    ci = np.around(ci, decimals=decimals)
    pvals = np.around(pvals, decimals=decimals)
    
    results = pd.DataFrame({
        "odds ratio": odds_ratios,
        "95% CI, lower": ci[0],
        "95% CI, upper": ci[1],
        "p-value": pvals
    })
    
    pattern = r"C\((?P<name>.+)\, .+\)\[T.(?P<value>.+)\]"
    replace = lambda match: "{name}[T.{value}]".format(
        name=match.group("name"),
        value=match.group("value")
    )
    
    renamed_index = results\
                    .index\
                    .to_series()\
                    .astype(str)\
                    .str\
                    .replace(pattern, replace, regex=True)
    
    results = results.rename(index=renamed_index)
    
    return results


def run_logit(formula, df, *args, **kwargs):
    y, X = patsy.dmatrices(formula, df, return_type="dataframe")
    model = sm.Logit(y, X).fit(*args, **kwargs)

    return model
