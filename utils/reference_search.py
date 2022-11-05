from nltk import ngrams

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
        res_name = df_reference.loc[df_reference[col_job_name].
                                        str.lower().str.contains(pat) == True,].shape[0]
        res_id = df_reference.loc[df_reference[col_job_id].
                                      str.lower().str.contains(job_id) == True,].shape[0]
        if res_name > 0 and patterns != ['']:
            results = df_reference.loc[df_reference[col_job_name].
                                           str.lower().str.contains(pat) == True,]
            results = results.loc[results[col_job_name].
                                      str.lower().str.contains(job_name_filter) == True]
            # if job_name_filter is not None:
            #     results = results.loc[job_name_filter, col_job_name]
            results = results[col_result].unique()
            return results
        if res_id > 0:
            print(f"{job_name.upper()} | id: {job_id}")
            results = df_reference.loc[df_reference["Шифр расценки и коды ресурсов"].
                                           str.lower().str.contains(job_id) == True,]
            results = results.loc[results[col_job_name].
                                      str.lower().str.contains(job_name_filter) == True]
            results = results[col_result].unique()
            return results
    except Exception as e:
        print(f"ERROR: {e} | patterns: {patterns}")
