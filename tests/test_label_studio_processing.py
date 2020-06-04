import logging
import pytest
from pathlib import Path
from cleaning.label_studio_processing import process_files


PATH = Path(__file__).resolve()
PROJECT_ROOT = PATH.parent
TEST_DATA_DIR = PROJECT_ROOT / 'data'


@pytest.fixture
def long_annotation():
    return TEST_DATA_DIR / "label_studio_long_annotation.json"


@pytest.fixture
def normal_file():
    return TEST_DATA_DIR / "label_studio_normal_file.json"


def test_process_files(normal_file):
    file_columns = process_files([normal_file]).columns
    expected_columns = ['LS_NOTE_TEXT',
                        'LS_TEXT_STRING',
                        'LS_FIRST_INDEX',
                        'LS_LAST_INDEX',
                        'LS_LABEL']

    assert len(file_columns.difference(expected_columns)) == 0


def test_process_files_long_annotation_warning(long_annotation, caplog):
    with caplog.at_level(logging.WARNING):
        process_files([long_annotation])

    assert 'Very long annotation string encountered, skipping...'\
        in caplog.text
