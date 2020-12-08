import json
import pandas as pd


def reshape_cr_json(df):
    """Convert ClinicalRegex's 'annotationValues' from a 'JSON' string
    (into appropriate columns)."""
    df = pd.json_normalize(df['annotationValues'].map(json.loads))

    return df


def join_id_with_annotations(df):
    df = pd.concat([
        df[["id"]],
        reshape_cr_json(df)
    ], axis="columns")
    
    return df


def has_only_one_annotation_value_per_id(df):
    df = join_id_with_annotations(df)
    df = df.groupby("id", as_index=False)\
           .agg("nunique")
    df = df.drop("id", axis=1)
    
    return (df == 1).all()
