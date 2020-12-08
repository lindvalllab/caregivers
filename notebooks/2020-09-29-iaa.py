import streamlit as st
import pandas as pd
from sklearn.metrics import cohen_kappa_score, confusion_matrix
from cleaning.iaa_utils import reshape_cr_json 


# khuyen and sandra
FILE_K = '../data/interim/2020-09-22-kd-200-annotations.csv'
FILE_S = '../data/interim/2020-09-28-sz-200-annotations.csv'

# annotation column names
COL_CHILD = 'child'
COL_SPOUSE = 'spouse'

ANNOTATION_COLS = [COL_CHILD,
                   COL_SPOUSE]

# clinical regex column names
COL_CR_ID = 'id'
COL_CR_L1_ANNOTATION = 'L1_annotation'
COL_CR_L2_ANNOTATION = 'L2_annotation'
COL_CR_TEXT = 'text'

# this had to be computed semi-manually, see notebook on why this is
N_ROWS = 234
N_EXPECTED_ANNOTATIONS = 200

df_k = pd.read_csv(FILE_K)
df_s = pd.read_csv(FILE_S)

ids_k = df_k[:N_ROWS][COL_CR_ID]
ids_s = df_s[:N_ROWS][COL_CR_ID]

common_ids = set(ids_k) & set(ids_s)

assert ids_k.equals(ids_s)
assert len(common_ids) == N_EXPECTED_ANNOTATIONS


# ============ processing steps ============ #

def resolve_annotations(annotations):
    """Clinical Regex appears to provide the data in a denormalized format;
       multiple annotations seem to occur sometimes for a given id."""

    if len(annotations) <= 0:
        return annotations

    unique = set(annotations)

    if len(unique) == 1:
        return list(annotations)[0]

    elif unique == {0, 1}:
        return 1

    else:
        raise ValueError('Resolution of annotations unclear/undefined.',
                         annotations)


def get_annotation_values(df,
                          COL_ID=COL_CR_ID,
                          COL_L1=COL_CR_L1_ANNOTATION,
                          COL_L2=COL_CR_L2_ANNOTATION,
                          COL_TEXT=COL_CR_TEXT):
    return df.groupby(COL_ID)\
             .agg({COL_L1: resolve_annotations,
                   COL_L2: resolve_annotations,
                   COL_TEXT: list})\
             .reset_index()

def rename_columns(df):
    return df.rename(columns={COL_CR_L1_ANNOTATION: COL_CHILD,
                              COL_CR_L2_ANNOTATION: COL_SPOUSE})

def select_common_rows(df,
                       ids=common_ids,
                       COL_ID=COL_CR_ID):
    """Select the rows annotated by both annotators."""
    return df[df[COL_ID].isin(ids)]

# =========================================== #

df_k = df_k.pipe(reshape_cr_json)\
           .pipe(get_annotation_values)\
           .pipe(rename_columns)\
           .pipe(select_common_rows)

df_s = df_s.pipe(reshape_cr_json)\
           .pipe(get_annotation_values)\
           .pipe(rename_columns)\
           .pipe(select_common_rows)

df_both = df_k.merge(df_s,
                     on=COL_CR_ID,
                     suffixes=('_khuyen', '_sandra')
                    ).drop(columns=['text_khuyen', 'text_sandra'])

df_value_counts = df_both.drop(columns=[COL_CR_ID])\
                         .apply(pd.Series.value_counts)\
                         .fillna(0)

kappa_cols = ANNOTATION_COLS[:] 
kappa_values = {col: cohen_kappa_score(df_k[col], df_s[col])
                for col in kappa_cols}

annotation_values = list(set(df_k[COL_CHILD]) |
                         set(df_s[COL_CHILD]) |
                         set(df_k[COL_SPOUSE]) |
                         set(df_s[COL_SPOUSE]))

cm_child = confusion_matrix(df_k[COL_CHILD],
                            df_s[COL_CHILD])

cm_spouse = confusion_matrix(df_k[COL_SPOUSE],
                             df_s[COL_SPOUSE])


@st.cache
def get_text_df(k, s, col):
    selected = (df_k[col] == k) & (df_s[col] == s)
    cols_keep = [COL_CR_ID, COL_CR_TEXT]

    # df_k in theory should give the same texts as df_s
    #   it turns out this is not exactly the case
    #     (if you look carefully, you can find an id where the
    #      text in df_k is different from the one in df_s),
    #   but we'll say this is good enough for here for now
    return df_k[selected][cols_keep]

# ============================================ # 
value_k = st.sidebar.selectbox('Khuyen', options=annotation_values)
value_s = st.sidebar.selectbox('Sandra', options=annotation_values)
label = st.sidebar.selectbox('Label', options=ANNOTATION_COLS)

st.sidebar.header('Kappa Values')

st.sidebar.write(pd.DataFrame(kappa_values, index=['cohen_kappa']))

st.sidebar.header('Value Counts')
st.sidebar.text("rows : Khuyen\n"\
                "columns : Sandra\n\n"\
                "0 : 'true negative'\n"\
                "1 : 'true positive'\n"\
                "5 : 'ambiguous'\n"\
                "9 : 'false positive'")
st.sidebar.subheader('Child')
st.sidebar.dataframe(pd.DataFrame(cm_child,
                          columns=annotation_values,
                          index=annotation_values)
                          )

st.sidebar.subheader('Spouse')
st.sidebar.dataframe(pd.DataFrame(cm_spouse,
                          columns=annotation_values,
                          index=annotation_values)
                          )

st.sidebar.write("The following HADM_IDs did not have matching texts between Khuyen and Sandra's files.")
st.sidebar.write([143414, 163321, 182863, 193351])

st.header('Example Texts')

if value_k is not None and value_s is not None:
    text_df = get_text_df(value_k,
                          value_s,
                          label)

    text_id_options = text_df[COL_CR_ID].tolist()

    if len(text_id_options) > 0:
        text_id = st.selectbox('HADM_ID', options=text_id_options)
        text_examples = text_df[text_df[COL_CR_ID] == text_id][COL_CR_TEXT]

        st.write(text_examples.iloc[0])

    else:
        st.write('No examples found.')
