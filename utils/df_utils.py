from datetime import datetime
from fuzzywuzzy import fuzz
import os
import re
import ntpath
import pandas as pd
import numpy as np

from utils.vis_utils.vis_prompt import SysColors
from utils.vis_utils.numberspell import num2glosses, NUM_DICT
from utils.streamlit_utils.st_constants import TO_CHECK, TO_ADD, \
    DOUBLE_MEANING_DF, MISSED_GLOSSES_DF, CHECKED_GLOSSES_DF, ROOT_DIR, ALL_GLOSSES_DF

pd.options.mode.chained_assignment = None
VERBOSE = False


def create_table(df_path, row, column_names):
    """
    If table doesn't exist creates new table - IN USE
    """

    is_exist = os.path.exists(df_path)
    folder = os.path.dirname(df_path)
    is_folder_exist = os.path.exists(folder)

    # column_names = COLUMNS_ADMIN if admin else COLUMNS_USER
    columns = ",".join(column_names)

    if is_exist:
        with open(df_path, "a", encoding="utf-8") as writer:
            writer.write(row + "\n")
    else:
        if not is_folder_exist:
            os.makedirs(folder, exist_ok=True)
        with open(df_path, "w", encoding="utf-8") as writer:
            writer.write(columns + "\n")
            writer.write(row + "\n")

    return True


def convert_gloss_name(gloss_name, verbose=VERBOSE):
    if gloss_name is None:
        return gloss_name
    new_name = re.sub('[^A-Za-z_ ]+', '', gloss_name.upper())
    new_name = new_name.replace(" ", "_")
    if verbose:
        print(f"GLOSS: {SysColors.OK}{new_name}{SysColors.RESET} from INPUT: {gloss_name}")
    return new_name


def get_unchecked(df_path=TO_CHECK):
    df = pd.read_csv(df_path)
    return df


def get_unique_glosses_from_csv(df_object=TO_CHECK, df_col="gloss_main", filter_col=None):
    if isinstance(df_object, pd.DataFrame):
        df = df_object
    else:
        df = pd.read_csv(df_object)

    try:
        if filter_col is not None:
            df = df.loc[~df[filter_col]]

        if df.shape[0] > 0:
            return df[df_col].unique().tolist()

    except Exception as e:
        print(f"{SysColors.FAIL}{type(e)}{SysColors.RESET}: {e}")

    return


def create_csv(df_path, columns: tuple):
    columns_row = ",".join(columns)
    with open(df_path, "w", encoding="utf-8") as writer:
        writer.write(columns_row + "\n")


def get_token(gloss_name, df_dm=DOUBLE_MEANING_DF):
    if not os.path.exists(df_dm):
        columns = ("dm", "text", "meaning", "token", "source")
        create_csv(df_dm, columns=columns)

    df = pd.read_csv(df_dm)
    df["gloss_name"] = df.dm.str.upper()
    df = df.loc[df.gloss_name == gloss_name.upper()]

    if df.shape[0] != 0:
        text, meaning, token = \
            df.text.tolist(), df.meaning.tolist(), df.token.tolist()
        return text, meaning, token

    return


def create_log_files():
    if not os.path.exists(MISSED_GLOSSES_DF):
        with open(MISSED_GLOSSES_DF, "w", encoding="utf-8") as writer:
            writer.write("TIMESTAMP,GLOSS,TOKEN,COUNT,ADDED\n")


def remove_from_working_list(gloss, df_file, is_added=False):
    if not is_added or not os.path.exists(df_file):
        return
    df = pd.read_csv(df_file)
    df.loc[df['GLOSS'] == gloss, 'ADDED'] = True
    df.to_csv(df_file, index=False)


def update_log_files(gloss, token, df_file=MISSED_GLOSSES_DF, is_added=False):
    if gloss == "":
        return
    else:
        gloss = gloss.replace(" ", "_").replace("-", "_")

    create_log_files()

    data = pd.read_csv(df_file)
    glosses = data.GLOSS.tolist()

    count = data.loc[data.GLOSS == gloss, 'COUNT'].count()
    count += 0 if is_added else 1
    ts = get_timestamp(raw=True)

    # #############################################################################
    if gloss in glosses:
        data.loc[data.GLOSS == gloss, 'COUNT'] = count
        data.loc[data.GLOSS == gloss, 'ADDED'] = is_added

    else:
        new_row = {'TIMESTAMP': ts,
                   'GLOSS': gloss,
                   'TOKEN': token,
                   'COUNT': count,
                   'ADDED': is_added}
        df_ = pd.DataFrame(new_row, index=[0])
        data = data.append(df_, ignore_index=True)

    data.to_csv(MISSED_GLOSSES_DF, index=False)


def path_leaf(path: str):
    """
    The function returns folder name or file name without extension
    :param path: str // full path
    :return: str // name
    """
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def get_timestamp(delimiter1="_", delimiter2="", raw=True):
    """
    The function returns timestamp in the following format:
    YYYY{$d2}MM{$d2}DD{$d1}HH{$d2}MM{$d2}SS
    where $d1 is delimiter1, $d2 is delimiter2
    """
    timestamp_obj = datetime.now()
    if raw:
        return timestamp_obj
    date_str = f"%d{delimiter2}%b{delimiter2}%Y"
    time_str = f"%H{delimiter2}%M{delimiter2}%S"
    time_format = f"{date_str}{delimiter1}{time_str}"
    return timestamp_obj.strftime(time_format)


def find_similar(w_search, w_all):
    """
    The function returns the most similar word from the list of words
    """
    scores = []
    w_search = w_search.lower()
    w_all = np.array([w.lower() for w in w_all])
    for idx, w in enumerate(w_all):
        scores.append(fuzz.partial_ratio(w_search, w))
        # scores.append(fuzz.WRatio(w_search, w))
    scores = np.array(scores)
    idxs = scores.argsort()[::-1]
    sims = [w for w in w_all[idxs] if w != w_search]
    return sims, scores


def find_similar_glosses_in_df(gloss, df, k=None):
    """
    The function returns top-k of most similar glosses from the dataframe
    """
    all_glosses = df.gloss_main.unique().tolist()
    sim, _ = find_similar(gloss, all_glosses)
    sim = [s for s in sim if len(s) > 1]
    if k is not None:
        k = min(k, len(sim))
        sim = list(sim[:k])
    return sim


def find_gloss(gloss, df=None, df_file=None, token=None, return_list=False, verbose=VERBOSE):
    """
    Finds the best gloss and returns path as a string
    :param gloss: str // gloss name to find
    :param df: pd.DataFrame // dataframe with all checked glosses to search in
    :param df_file: str // path to the dataframe with all checked glosses
    :param token: str // token for double meaning if exists
    :param return_list: bool // if True, returns list of all paths
    :param verbose: bool // verbose mode
    :return: str // path to gloss
    """
    gloss = gloss.upper()

    if verbose:
        print(f"{SysColors.FAIL}{gloss} - {token}{SysColors.RESET}")

    if df is None and df_file is None:
        raise AttributeError("You should define either df or df_file")
    else:
        df = df if df is not None else pd.read_csv(df_file)
    search_gloss = df.loc[(df.gloss_main == gloss) & (df.gloss_rank != -1)]
    similar_glosses = find_similar_glosses_in_df(gloss, df, k=6)
    search_gloss.token = pd.to_numeric(search_gloss["token"], errors='ignore', downcast='integer')

    # TODO: TEST
    if search_gloss.shape[0] == 0:
        gloss = gloss.replace(" ", "_")
        search_gloss = df.loc[(df.gloss_main == gloss) & (df.gloss_rank != -1)]

    if token is not None:
        try:
            token = int(token)
        except ValueError as e:
            print(f"{e}")

        search_gloss = search_gloss.loc[search_gloss.token == token]

    # print gloss status, if gloss is missing >> save gloss name
    if search_gloss.shape[0] > 0:
        if verbose:
            print(f"{SysColors.OK}{gloss} in the database{SysColors.RESET}")
    else:
        if verbose:
            print(df.loc[(df.gloss_main == gloss) & (df.gloss_rank != -1)])
            print(f"{SysColors.FAIL}{gloss} is missing{SysColors.RESET}")
        update_log_files(gloss, token, df_file=MISSED_GLOSSES_DF)

    if return_list:
        return _return_paths_with_info(gloss, gloss_df=search_gloss), similar_glosses

    best_gloss = search_gloss.loc[search_gloss.gloss_rank == search_gloss.gloss_rank.min()].path.tolist()

    if len(best_gloss) == 0:
        return f"#{gloss}"
    else:
        # in the case if we have two or more glosses, which are best (rank 0), we will use the latest [-1]
        return best_gloss[-1]


def recombine_dict(path_dict, log_missed=True):
    """
    The function updates the dictionary with adjusted paths
    """
    new_dict = {}
    for k, v in path_dict.items():
        full_path = os.path.join(ROOT_DIR, k)
        full_path = full_path.replace("\\", "/")
        if os.path.exists(full_path):
            new_dict.update({k: v})
        elif log_missed:
            with open("./logs/log_missed_paths.log", "a", encoding="utf-8") as writer:
                writer.write(f"{full_path}\n")
    return new_dict


def _return_paths_with_info(gloss, gloss_df):
    """
    Returns dict {path: (rank, token), ...}
    :param gloss: gloss name // str
    :param gloss_df: gloss table // pd.Dataframe
    :return: dict
    """
    paths_with_info_raw = {info[0]: (info[1], info[2]) for info in zip(gloss_df.path.tolist(),
                                                                       gloss_df.gloss_rank.tolist(),
                                                                       gloss_df.token.tolist())}
    paths_with_info = {}
    for path, info in paths_with_info_raw.items():
        if 'JSONS_ASL' in path:
            path = localise_asl_paths(gloss, path)
        paths_with_info.update({path: info})

    return paths_with_info


def get_full_local_paths(chosen_glosses, tokens,
                         mounted=ROOT_DIR,
                         all_checked=CHECKED_GLOSSES_DF,
                         all_added=TO_ADD,
                         all_glosses=ALL_GLOSSES_DF,
                         is_full=False,
                         verbose=VERBOSE):
    """
    Returns full local paths for glosses and a list of glosses
    :param verbose: bool // print info
    :param all_added: pd.Dataframe // all glosses that were added via API
    :param chosen_glosses: list // input glosses
    :param tokens: list // input tokens
    :param mounted: str, Path // root folder
    :param all_checked: pd.Dataframe
    :param all_glosses: pd.Dataframe
    :param is_full: bool // if path is full
    :return:
    """
    full_paths = []
    full_glosses = []
    missing_glosses = {}

    df = pd.read_csv(all_checked)
    df_all = pd.read_csv(all_glosses)

    if os.path.exists(all_added):
        df_new = pd.read_csv(all_added)
        df = pd.concat((df, df_new))

    chosen_glosses = [g.upper() for g in chosen_glosses]
    tokens = [None for _ in chosen_glosses] if tokens is None else tokens

    for gloss, token in zip(chosen_glosses, tokens):
        short_path = find_gloss(gloss, df=df, token=token)

        if short_path[0] == "#":
            missed_gloss = short_path[1:]

            if missed_gloss.isdigit() or missed_gloss in NUM_DICT.keys():
                missing_glosses[gloss] = "Number-Spelled"

                if missed_gloss in NUM_DICT.keys():
                    missed_gloss = NUM_DICT[missed_gloss]
                # elif short_path[0] == '&':

                number_glosses = num2glosses(missed_gloss)

                if verbose:
                    print(f"{SysColors.INFO}GLOSS {gloss} >> {SysColors.RANDOM}{number_glosses}{SysColors.RESET}")

                number_paths = get_full_paths_for_letters(number_glosses, df=df_all)

                for idx, num_path in enumerate(number_paths):
                    full_paths.append(num_path)
                    full_glosses.append(number_glosses[idx])
            # TODO: test numbers

            else:
                missed_gloss = ''.join([i for i in str(missed_gloss) if i.isalpha()])  # delete numbers TODO

                if verbose:
                    print(f"{SysColors.INFO}GLOSS {gloss} >> {SysColors.RANDOM}[\'{missed_gloss}\']{SysColors.RESET}")

                letter_paths = get_full_paths_for_letters(missed_gloss, df=df_all)
                missing_glosses[gloss] = True

                for idx, letter_path in enumerate(letter_paths):
                    full_paths.append(letter_path)
                    full_glosses.append(gloss.strip()[idx])
                # print(f"letter paths: {len(letter_paths)}")

        else:
            missing_glosses[gloss] = False
            full_path = os.path.join(mounted, short_path) if is_full else short_path
            full_paths.append(full_path)
            full_glosses.append(gloss)
            # print(f"after gloss {gloss}: {len(full_paths)}")

    if verbose and False:
        print(f"finally: {len(full_paths)} {missing_glosses}")

    return full_paths, full_glosses, missing_glosses


def localise_asl_paths(gloss, path, root=ROOT_DIR):
    """Adjusts local path for the file from the JSONS_ASL dataset"""
    local_path = os.path.join(root, """JSONS/JSONS_ASL/""")
    local_folder = gloss.replace("_", " ").lower()
    local_file = path_leaf(path)
    updated_file_path = os.path.join(local_path, local_folder, local_file)

    return updated_file_path


def find_gloss_old(gloss, df, best_quality=False):
    all_words = list(set(df.word.values))
    # print(f"{len(all_words)} words in vocabulary")
    if gloss in all_words:
        sample = df.loc[df.word == gloss]
        if best_quality:
            # base
            # sample = sample.loc[sample.gloss_error == sample.gloss_error.min()]
            # experimental
            sample["err_rate"] = sample.gloss_error - (sample.quality / 8)
            sample = sample.loc[sample.err_rate == sample.err_rate.min()]
        else:
            sample = sample.sample(4, replace=True)
    else:
        return
    return sample


def get_full_paths_old(chosen_glosses, df_glosses, all_glosses=None, lower=False):
    full_paths = []
    full_glosses = []
    all_glosses = df_glosses.word.unique() if all_glosses is None else all_glosses
    all_glosses = [gl.lower() for gl in all_glosses] if lower \
        else [gl.upper() for gl in all_glosses]

    for gloss in chosen_glosses:
        if gloss not in all_glosses:
            letter_paths = get_full_paths_for_letters(gloss.strip(), df_glosses)

            for idx, letter_path in enumerate(letter_paths):
                full_paths.append(letter_path)
                full_glosses.append(gloss.strip()[idx])
            # print(f"letter paths: {len(letter_paths)}")

        else:
            sample = find_gloss_old(gloss=gloss, df=df_glosses, best_quality=True)

            if sample is not None:
                info = sample.iloc[0]
                file_name = info.local_path
                full_paths.append(file_name)
                full_glosses.append(gloss)
                # print(f"after gloss {gloss}: {len(full_paths)}")

    # print(f"finally: {len(full_paths)}")
    return full_paths, full_glosses


def get_full_paths_for_letters(chosen_glosses, df):
    """
    The function returns full path for each letter
    :param chosen_glosses: iterable // list or tuple of letters
    :param df: pd.Dataframe // gloss df
    :return: list // list with full local paths
    """
    full_paths = []

    for gloss in chosen_glosses:
        sample = find_gloss_old(gloss=gloss, df=df, best_quality=True)

        if sample is not None:
            info = sample.iloc[0]
            file_name = info.local_path
            full_paths.append(file_name)

    return full_paths


# def get_full_paths_for_numbers(chosen_glosses, df):
#     """
#     The function returns full path for each letter
#     :param chosen_glosses: iterable // list or tuple of letters
#     :param df: pd.Dataframe // gloss df
#     :return: list // list with full local paths
#     """
#     full_paths = []
#
#     for gloss in chosen_glosses:
#         sample = find_gloss(gloss=gloss, df=df)
#
#         if sample is None:
#             gloss = NUM_DICT[gloss]
#             sample = find_gloss_old(gloss=gloss, df=df, best_quality=True)
#
#         if sample is not None:
#             info = sample.iloc[0]
#             file_name = info.local_path
#             full_paths.append(file_name)
#
#     return full_paths


def _update_path(path, gloss, mounted):
    if "JSONS_ASL" in path:
        path_updated = path if path[0] == "#" else localise_asl_paths(gloss, path, mounted)
    else:
        path_updated = path if path[0] == "#" else os.path.join(mounted, path)

    return path_updated


def localize_paths(chosen_glosses, df, all_glosses=None, mounted=ROOT_DIR):
    full_paths, full_glosses = get_full_paths_old(chosen_glosses, df, all_glosses)
    updated_paths = []

    if type(chosen_glosses) == str:
        full_glosses = [chosen_glosses for _ in range(len(full_paths))]
    for path, gloss in zip(full_paths, full_glosses):
        path_updated = _update_path(path, gloss, mounted)

        # if path[0] == "#":
        #     full_paths = get_full_paths_for_letters(path[1:])
        #     for letter in path[1:]:
        #         path_updated = _update_path(letter, gloss, mounted)

        updated_paths.append(path_updated)
    return updated_paths


def localize_paths_to_dict_old(chosen_glosses, df, all_glosses=None, mounted=ROOT_DIR):
    """
    Returns dictionary with gloss idx in the sentence, gloss name and local path
    :param chosen_glosses: list of glosses
    :param df: path to the dataframe with all glosses (all_glosses.csv)
    :param all_glosses: list of the all glosses
    :param mounted: root directory where JSONS folder is located
    :return: dict
    """
    full_paths, full_glosses = get_full_paths_old(chosen_glosses, df, all_glosses)

    if type(chosen_glosses) == str:
        full_glosses = [chosen_glosses for _ in range(len(full_paths))]

    updated_paths = {gp[0]: gp[1] for gp in enumerate(zip(full_glosses, full_paths))}
    for idx, (path, gloss) in enumerate(zip(full_paths, full_glosses)):
        path_updated = _update_path(path, gloss, mounted)
        updated_paths[idx] = (gloss, path_updated)

    return updated_paths


def localize_paths_to_dict(chosen_glosses, mounted=ROOT_DIR, tokens=None):
    full_paths, full_glosses, missed = get_full_local_paths(chosen_glosses=chosen_glosses, tokens=tokens)

    if type(chosen_glosses) == str:
        full_glosses = [chosen_glosses for _ in range(len(full_paths))]

    updated_paths = {gp[0]: gp[1] for gp in enumerate(zip(full_glosses, full_paths))}
    for idx, (path, gloss) in enumerate(zip(full_paths, full_glosses)):
        path_updated = _update_path(path, gloss, mounted)
        path_updated = path_updated.replace("\\\\", "/").replace("\\", "/")  # convert \\ for windows paths
        path_updated = path_updated.replace("/C:/", "/")  # fix bug with C:/ in the middle for windows paths
        updated_paths[idx] = (gloss, path_updated)

    return updated_paths, missed


def test_localize_paths_to_dict():
    glosses = "STUDENT SENTENCE YOU FINISH READ"

    # df = pd.read_csv("./data/all_glosses.csv")
    glosses = [k.upper() for k in glosses.split()]
    paths, _ = localize_paths_to_dict(chosen_glosses=glosses)
    for item in paths.items():
        print(item)

    c = get_unique_glosses_from_csv()
    print(c)


def merge_df_glosses(all_added=TO_ADD,
                     all_checked=CHECKED_GLOSSES_DF):
    df = pd.read_csv(all_checked)

    if os.path.exists(all_added):
        df_new = pd.read_csv(all_added)
        df = pd.concat((df, df_new))

    return df


def find_existing_gloss_paths(gloss_name, from_main=False):
    df_merged = merge_df_glosses()
    paths_and_ranks, sim = find_gloss(gloss=gloss_name, df=df_merged, return_list=True)
    paths_and_ranks = recombine_dict(paths_and_ranks)  # show only existing files

    if from_main:  # or only from the main dataset
        paths_and_ranks, sim = find_gloss(gloss=gloss_name, df_file=CHECKED_GLOSSES_DF, return_list=True)
    return paths_and_ranks


def test_adding(all_added=TO_ADD,
                all_checked=CHECKED_GLOSSES_DF):
    """
        Returns full local paths for glosses and a list of glosses
        :param all_added:
        :param all_checked:
        :return: None
        """
    df_all = pd.read_csv(all_checked)
    df_new = pd.read_csv(all_added)
    df_all = pd.concat((df_all, df_new))
    print(df_all.tail(5))


if __name__ == "__main__":
    # test_localize_paths_to_dict()
    test_adding()
