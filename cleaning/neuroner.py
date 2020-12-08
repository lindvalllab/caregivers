import pandas as pd
from pathlib import Path


def load_neuroner_results_into_df(results_path, column_name):
    """Takes .ann files in a given directory and loads them
    as strings into a DataFrame under a given column name.
    
    Assumes the filenames are integers corresponding to ROW_ID
    in the original data file."""
    results_files = Path(results_path).rglob("*.ann")
    
    results = {}
    
    for result_file in results_files:
        with open(result_file, "r") as file:
            contents = file.read()
            
        filename = int(result_file.stem)
        
        results[filename] = contents
    
    df = pd.DataFrame.from_dict(
        results,
        orient="index",
        columns=[column_name]
    )
    
    df = df.rename_axis("ROW_ID")\
           .reset_index()

    return df


def load_neuroner_results():
    path_car = "../data/output_PM2018_NeuroNER_models/car_model/processed_2020-12-04_16-06-49-54894/brat/"
    path_lim = "../data/output_PM2018_NeuroNER_models/lim_model/processed_2020-12-04_18-13-43-397123/brat/"
    
    path_original = "../data/raw/caregivers_set13Jul2020.csv"
    
    column_name_str_car = "RESULT_STRING_CAR"
    column_name_str_lim = "RESULT_STRING_LIM"
    
    column_name_car = "CAR"
    column_name_lim = "LIM"
    
    df_car = load_neuroner_results_into_df(path_car, column_name_str_car)
    df_lim = load_neuroner_results_into_df(path_lim, column_name_str_lim)
    
    df_o = pd.read_csv(path_original)

    df = df_o.merge(df_car, on="ROW_ID")\
             .merge(df_lim, on="ROW_ID")
    
    df[column_name_car] = df[column_name_str_car].str.len() != 0
    df[column_name_lim] = df[column_name_str_lim].str.len() != 0
    
    return df