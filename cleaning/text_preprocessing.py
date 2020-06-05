import re


def remove_redactions(text):
    '''Remove obfuscations between square brackets.'''
    return re.sub(r'\[.*?\]', '', text)


def remove_carriage_returns(text):
    return text.replace(r'\r', '')\
               .replace(r'\n', '')


def remove_repeated_spaces(text):
    '''"Squishes" multiple spaces into one.'''
    return re.sub(r'\s+', r'\s', text)


def remove_carriage_returns_and_repeated_spaces(text):
    '''Removes all carriage returns and trailing whitespace. Replaces repeated
       whitespace characters with a single space.

       "Shortcut" for remove_carriage_returns and remove_repeated_spaces.
    '''
    return ' '.join(text.split())


def remove_non_alphabetic(text):
    '''Remove all non-alphabetic characters, including digits and punctuation.
       Excludes spaces.'''
    return re.sub(r'[^a-zA-Z\s]', '', text)


def preprocess_text(text):
    text = text.lower()
    text = remove_redactions(text)
    text = remove_non_alphabetic(text)
    text = remove_carriage_returns_and_repeated_spaces(text)

    return text
