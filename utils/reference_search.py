from nltk import ngrams
import pandas as pd

TSN_PATH = "./data/tsn.csv"
SN_PATH = "./data/sn.csv"


def _get_ngrams(sentence, ngram_num=6):
    if len(sentence.split()) <= ngram_num:
        return [sentence, ]
    sentence = sentence.replace("(", "").replace(")", "")
    return [" ".join(ngr).lower().strip() for ngr in ngrams(sentence.split(), ngram_num)]


def find_in_reference_book(job_name, job_id=None, df_reference=None,
                           col_result=None, col_job_name=None, col_job_id=None,
                           job_name_filter=None):
    if df_reference is None:
        raise ValueError("You should define the dataframe")

    col_result = "Наименование СПГЗ" if col_result is None else col_result
    col_job_name = "Наименование работ и затрат" if col_job_name is None else col_job_name
    col_job_id = "Шифр расценки и коды ресурсов" if col_job_id is None else col_job_id
    job_name_filter = "" if job_name_filter is None else job_name_filter
    job_name_filter = '|'.join(r"\b{}\b".format(x).lower() for x in job_name_filter)

    patterns = _get_ngrams(job_name, 4)
    pat = '|'.join(r"\b{}\b".format(x).lower() for x in patterns)
    job_id = str(job_id).lower()
    # print(f"{job_name.upper()} | patterns: {patterns} | idx: {job_id}")

    try:
        results_by_pattern = df_reference.loc[df_reference[col_job_name].str.lower().str.contains(pat) == True,]
        results_by_id = df_reference.loc[df_reference[col_job_id].str.lower().str.contains(job_id) == True,]

        if results_by_pattern.shape[0] > 0 and patterns != ['']:
            results1 = results_by_pattern.loc[results_by_pattern[col_job_name].str.lower()
                                                  .str.contains(job_name_filter) == True]
            results2 = df_reference.loc[df_reference[col_job_name].str.lower().str.contains(job_name.lower())]

            # if job_name_filter is not None:
            #     results = results.loc[job_name_filter, col_job_name]

            results = pd.concat((results1, results2))
            results = results.drop_duplicates()[col_result].unique()
            return results

        elif results_by_pattern.shape[0] == 0:
            results = df_reference.loc[df_reference[col_job_name].str.lower().str.contains(job_name.lower())]
            results = results[col_result].unique()
            return results

        if results_by_id.shape[0] > 0:
            print(f"{job_name.upper()} | id: {job_id}")
            results = results_by_id.loc[results_by_id[col_job_name].str.lower().str.contains(job_name_filter) == True]
            results = results[col_result].unique()
            return results

    except Exception as e:
        print(f"ERROR: {e} | patterns: {patterns}")
