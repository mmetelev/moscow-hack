import pandas as pd
from fuzzywuzzy import fuzz, process
from nltk import ngrams


def _get_ngrams(sentence, ngram_num=6):
    if len(sentence.split()) <= ngram_num:
        return [sentence, ]
    sentence = sentence.replace("(", "").replace(")", "")
    return [" ".join(ngr).lower().strip() for ngr in ngrams(sentence.split(), ngram_num)]


def find_matches(query, df=None, col=None):
    df = pd.read_csv("./data/template_clean.csv", index_col=0) if df is None else df
    col = 'spgz' if col is None else col

    try:
        choices = df[col].str.strip().str.lower().unique()
        matches = df.loc[df.spgz.str.lower().str.contains(query.lower())==True].spgz.tolist()

        if len(matches) < 4:
            matches_fuzz = process.extract(query.lower(), choices, limit=100, scorer=fuzz.ratio)
            matches_fuzz = [m for m in matches_fuzz if m[1] > 70]
            matches = list(set(matches + matches_fuzz))

        if len(matches) < 1:
            matches_fuzz = process.extract(query.lower(), choices, limit=100, scorer=fuzz.ratio)
            matches_fuzz = [m for m in matches_fuzz if m[1] > 59]

            patterns = _get_ngrams(query, 3)
            pat = '|'.join(r"\b{}\b".format(x).lower() for x in patterns)
            matches_pattern = df.loc[df.spgz.str.lower().str.contains(pat) == True].spgz.tolist()

            matches = list(set(matches + matches_fuzz + matches_pattern))[:100]
        else:
            matches = list(set(matches))

    except Exception as e:
        print(type(e), e)
        return []

    return matches


if __name__ == "__main__":
    df = pd.read_csv("./../data/template_clean.csv", index_col=0)
    query = "услуги по уборке территорий"
    mmm = find_matches(query, df)
    print(mmm)