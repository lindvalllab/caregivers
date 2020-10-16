import json
import pandas as pd


def reshape_cr_json(df):
    """Convert ClinicalRegex's 'annotationValues' from a 'JSON' string
    (into appropriate columns)."""
    df_annotations = pd.json_normalize(df['annotationValues'].map(json.loads))

    return pd.concat([df, df_annotations], axis=1)
