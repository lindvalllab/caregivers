#!/usr/bin/env python

"""Loops through data/raw/label-studio-annotations/*.json files and outputs a
Pandas DataFrame with the following columns:
    - LS_NOTE_TEXT: The full note text. (Note: Label Studio note text may
                                         differ slightly from original, hence
                                         the prefix.)
    - LS_TEXT_STRING: The string of NOTE_TEXT_LS that corresponds to LABEL_VAR.
    - LS_FIRST_INDEX: The start index of TEXT_STRING within NOTE_TEXT_LS.
    - LS_LAST_INDEX: The last index of TEXT_STRING within NOTE_TEXT_LS.
    - LS_LABEL: The annotation/label.
"""


import glob
import json
import logging
import pandas as pd

from pathlib import Path

PATH = Path(__file__).resolve()
PROJECT_ROOT = PATH.parent.parent
DATA_DIR = PROJECT_ROOT / 'data/raw/label-studio-annotations/'
INTERIM_DIR = PROJECT_ROOT / 'data/interim/label-studio-annotations/'
FILES = DATA_DIR.glob('*.json')

OUTPUT_FILE = INTERIM_DIR / 'ls-annotations.csv'


# For debugging, if necessary
def pretty_json(data):
    '''Pretty prints a JSON object, using json.dumps().'''
    return json.dumps(data, sort_keys=True, indent=4)


# For checking each row only has one label
def is_length_one(arr):
    return len(arr) == 1


def has_only_one_item_per_row(series):
    return (series.apply(len) == 1).all()


def process_ls_files(files):
    df = pd.DataFrame()

    for file_path in files:
        logging.info('Reading data from {}...'.format(file_path))

        with open(file_path) as file:
            ls_data = json.load(file)

            assert 'text' in ls_data['data'].keys()

            ls_text = ls_data['data']['text']

            for completion in ls_data['completions']:
                completion_id = completion['id']
                completion_results = completion['result']

                for result in completion_results:
                    try:
                        result_id = result['id']
                        result_index_start = result['value']['start']
                        result_index_end = result['value']['end']
                        result_string = result['value']['text']
                        result_labels = result['value']['labels']

                        df = df.append({"LS_NOTE_TEXT": ls_text,
                                        "LS_FIRST_INDEX": result_index_start,
                                        "LS_LAST_INDEX": result_index_end,
                                        "LS_TEXT_STRING": result_string,
                                        "LS_LABEL": result_labels},
                                       ignore_index=True)

                    except KeyError as error:
                        logging.warning('Reading file: {}\n'
                                        'No annotation info in this '
                                        'completion (id = {:>8}). Skipping.\n'
                                        '\tKeyError: Key {} not found.'
                                        .format(file_path, completion_id, error))
                        continue

    if has_only_one_item_per_row(df['LS_LABEL']):
        df['LS_LABEL'] = df['LS_LABEL'].apply(lambda items: items[0])

    else:
        raise ValueError('Some entry has multiple labels associated with it.')

    return df


if __name__ == '__main__':
    processed_df = process_ls_files(FILES)

    print('Writing to {}...'.format(OUTPUT_FILE))

    if OUTPUT_FILE.is_file():
        overwrite = input('Output file {} already exists, overwrite? [y/N]: '
                          .format(OUTPUT_FILE))

        while True:
            if overwrite == '' or overwrite.lower() == 'n':
                print('Canceling write...')
                break

            elif overwrite.lower() == 'y':
                print('Overwriting file {}.'.format(OUTPUT_FILE))
                processed_df.to_csv(OUTPUT_FILE, index=False)
                break

            else:
                overwrite = input('Invalid input, please try again: ')
