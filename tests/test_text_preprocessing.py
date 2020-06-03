import logging
import pytest
from cleaning.text_preprocessing import preprocess_text, \
                                        remove_redactions


@pytest.fixture
def typical_note():
    return 'The patient is a 81yo m who was found down in [** location **] on'\
           '[** date **]\n\n'


@pytest.fixture
def obfuscation():
    return '[** redacted **]'


def test_preprocess_text(typical_note, obfuscation):
    assert preprocess_text(typical_note) == 'the patient is a yo m who was '\
                                            'found down in on'


def test_remove_redactions(obfuscation):
    assert remove_redactions(obfuscation) == ''
