import pandas as pd
from pathlib import Path


def get_project_root() -> Path:
    return Path(__file__).parent.parent


def get_cols_with_na_values(df):
    return df.columns[df.isna().any()]


def print_cols_with_na_values(df):
    cols = get_cols_with_na_values(df)

    print("Columns with NaN values:\n\n{}".format(df[cols].isna().sum()))

    return df


def remove_constant_cols(df):
    """Returns the given dataframe with the constant columns removed."""
    return df.loc[:, (df != df.iloc[0]).any()]


def handle_datetime_types(df):
    """Attempts to automatically convert datetime columns to the correct type.
    """
    for col in df.columns:
        if df[col].dtype == "object":
            try:
                df[col] = pd.to_datetime(df[col])

            except ValueError:
                pass

    return df


def handle_datetime_cols(df, datetime_cols):
    for col in datetime_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
    
    return df


def is_constant_col(df, group_by=None, dropna=True):
    """Returns a list of columns with constant value across all rows.
       group_by : Group the DataFrame by group_by first.
       dropna   : Don't include NaN in the counts.
    """
    if group_by:
        return [col for col in df.columns if col != group_by and
                all(nunique == 1
                    for nunique in df.groupby(group_by)[col]
                                     .agg('nunique', dropna=dropna).values)]

    else:
        return list(df.columns[df.nunique(dropna=dropna) <= 1])


def squish_dataframe(df, group_by, dropna=True):
    """Aggregates by list for columns with more than one distinct value.
        For constant columns it simply takes that value.
    """
    constant_cols = is_constant_col(df, group_by, dropna)
    aggfuncs = {col: (lambda values: values.mode()) if col in constant_cols
                else list for col in df.columns if col != group_by}

    return df.groupby(group_by).agg(aggfuncs).reset_index()


def squish(s: pd.Series):
    if len(s) == 0:
        return None
    
    elif len(s.unique()) == 1:
        return s.unique()[0]

    else:
        raise IndexError("Values not unique, can't squish.")
