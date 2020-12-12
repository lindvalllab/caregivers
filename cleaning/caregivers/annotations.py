import pandas as pd
from cleaning.clinical_regex import (
    join_id_with_annotations,
    has_only_one_annotation_value_per_id
)
from cleaning.utils import get_project_root


PROJECT_ROOT = get_project_root()


def process_annotations(df):
    """Takes a ClinicalRegex output file and returns a DataFrame
    containing only the
        * id (HADM_ID in this case), and
        * annotation values (0, 1, 9 in this case) for each
        * label (ANNOTATION_CHILD and ANNOTATION_SPOUSE in this case).
    """
    df = join_id_with_annotations(df)
    df = df.rename(columns={
        "id": "HADM_ID",
        "L1_annotation": "ANNOTATION_CHILD",
        "L2_annotation": "ANNOTATION_SPOUSE"
    })
    
    df = df[[
        "HADM_ID",
        "ANNOTATION_CHILD",
        "ANNOTATION_SPOUSE"
    ]]
    
    df = df.groupby("HADM_ID", as_index=False)\
           .agg(lambda s: s.unique())
    
    return df


def resolve_annotations(df):
    """Handles missing annotations and converts
    to boolean values.
    
    Annotation Key:
        1 = "true positive" -> 1 -> True
        9 = "false positive" -> 0 -> False
        0 = "true negative" -> 0 -> False
    """
    cols = [
        "ANNOTATION_CHILD",
        "ANNOTATION_SPOUSE"
    ]
    
    for col in cols:
        df[col] = df[col].replace(9, 0)
        df[col] = df[col].fillna(0)
        df[col] = df[col].astype(bool)
        
    return df


def add_computed_columns(df):
    """"""
    df["ANNOTATION_BOTH"] = df["ANNOTATION_CHILD"] & df["ANNOTATION_SPOUSE"]
    df["ANNOTATION_ANY"] = df["ANNOTATION_CHILD"] | df["ANNOTATION_SPOUSE"]
    
    return df


def merge_original_data(df_annotations, df_original):
    df = df_original.merge(df_annotations, how="left", on="HADM_ID")
    
    return df


def process(df_annotations, df_original):
    df = process_annotations(df_annotations)
    df = merge_original_data(df, df_original)
    df = resolve_annotations(df)
    df = add_computed_columns(df)
    
    return df
    
    
def load_data():
    path_annotations = PROJECT_ROOT / "data/raw/kmd_annotations_1163_11.19.20.csv"
    path_original = PROJECT_ROOT / "data/raw/caregivers_set13Jul2020.csv"

    df_annotations = pd.read_csv(path_annotations)
    df_original = pd.read_csv(path_original)

    assert has_only_one_annotation_value_per_id(df_annotations).all()
    
    df = process(df_annotations, df_original)
    
    return df
