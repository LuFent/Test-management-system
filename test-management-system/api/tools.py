from git import Repo
from gherkin.parser import Parser
from os import listdir, path
from gherkin.token_scanner import TokenScanner
import re
from copy import deepcopy
from .models import *
from shutil import rmtree, copyfile
from django.conf import settings

parser = Parser()
RESERVED_FILES_POSTFIX = "_res"
PUSHING_DIR_POSTFIX = "_push"
NOTHING_TO_COMMIT_MESSAGE = "nothing to commit, working tree clean"

def covered_in_single_quotes(text):
    return "'" + text + "'"


def covered_in_double_quotes(text):
    return '"' + text + '"'


def get_reserve_repo_name(repo_path):
    return repo_path + RESERVED_FILES_POSTFIX


def get_unreserved_repo_path(repo_path):
    return repo_path[:len(repo_path)-len(RESERVED_FILES_POSTFIX)]


def get_pushing_repo_path(repo_path):
    return repo_path + PUSHING_DIR_POSTFIX


def reserve_repo(repo_path):
    reserved_repo_path = get_reserve_repo_name(repo_path)
    if os.path.isdir(reserved_repo_path):
        rmtree(reserved_repo_path)
    os.rename(repo_path, reserved_repo_path)


def unreserve_repo(repo_path):
    reserved_repo_path = get_reserve_repo_name(repo_path)
    if os.path.isdir(repo_path):
        rmtree(repo_path)
    if os.path.isdir(reserved_repo_path):
        os.rename(reserved_repo_path, repo_path)


def get_repo_path(project_id, version_id):
    return os.path.join(
        settings.DOT_FEATURE_FILES_DIR, str(project_id), str(version_id)
    )

def remove_repo(repo_path):
    if os.path.isdir(repo_path):
        rmtree(repo_path)

def get_version_creation_error(error_message):
    message = f"""
    Couldn't create version due to:
    {error_message}
    """
    return message


def get_version_update_error(error_message):
    message = f"""
    Couldn't update version due to:
    {error_message}
    """
    return message


def get_files_push_error(error_message):
    message = f"""
    Couldn't push files due to:
    {error_message}
    """
    return message


def copy_files_to_dir(files, directory):
    for file in files:
        new_file_path = path.join(directory, path.basename(file.file_path))
        if path.isfile(new_file_path):
            os.remove(new_file_path)
        copyfile(file.file_path, new_file_path)


def get_common_folder_path(repo_path, particular_dir, common_autotests_folder):
    return os.path.join(
            repo_path,
            particular_dir,
            common_autotests_folder
        )


def get_commit_message(test_files):
    commit_message = "Added Files: "
    file_names = [file.file_name for file in test_files]
    commit_message += ", ".join(file_names)
    return commit_message




def get_substances_regexes(text):
    strings_with_subs = []

    single_quoted_strings_with_substances_regex = (
        r"""[A-Z]{1}[a-z]*?\(\'([^\n]*?{[^\n]*?}[^\n]*?)\'"""
    )
    double_quoted_strings_with_substances_regex = (
        r"""[A-Z]{1}[a-z]*?\(\"([^\n]*?{[^\n]*?}[^\n]*?)\""""
    )
    strings_with_subs.extend(
        re.findall(single_quoted_strings_with_substances_regex, text)
    )
    strings_with_subs.extend(
        re.findall(double_quoted_strings_with_substances_regex, text)
    )

    steps_check_regexes = []
    curly_braces_regex = r"\\\{.*?\}"
    any_value_regex = r"[^\n].*"
    for string in strings_with_subs:
        steps_check_regexes.append(
            re.sub(curly_braces_regex, any_value_regex, re.escape(string)).strip(
                """"'"""
            )
        )

    return steps_check_regexes


def fetch_with_common_autotests_check(features, common_js_dir):
    js_ext = ".js"

    if not os.path.isdir(common_js_dir):
        return features

    for dirname, dirnames, filenames in os.walk(common_js_dir):
        for full_filename in filenames:
            filename, file_extension = os.path.splitext(full_filename)

            if file_extension != js_ext:
                continue

            file_path = os.path.join(dirname, full_filename)
            with open(file_path, "r") as f:
                file_text = f.read()

            substances_regexes = get_substances_regexes(file_text)
            for feature in features:
                for scenario in feature["scenarios"]:
                    for step in scenario["steps"]:
                        if step["has_auto_test"]:
                            continue
                        step_text = step["text"]
                        step_text = step_text.strip()
                        if covered_in_single_quotes(step_text) in file_text:
                            step["has_auto_test"] = True
                        elif covered_in_double_quotes(step_text) in file_text:
                            step["has_auto_test"] = True
                        else:
                            for regex in substances_regexes:
                                if re.match(regex, step_text):
                                    step["has_auto_test"] = True
                                    break
        return features


def fetch_with_autotests_check(feature_data, js_dir):
    js_files = listdir(js_dir)
    if not js_files:
        return False

    for file_name in js_files:
        file_path = os.path.join(js_dir, file_name)
        with open(file_path, "r") as f:
            file_text = f.read()

        substances_regexes = get_substances_regexes(file_text)
        for scenario in feature_data["scenarios"]:
            for step in scenario["steps"]:
                if step["has_auto_test"]:
                    continue
                step_text = step["text"]
                step_text = step_text.strip()
                if step_text in file_text:
                    step["has_auto_test"] = True
                else:
                    for regex in substances_regexes:
                        if re.match(regex, step_text):
                            step["has_auto_test"] = True
                            break
    return feature_data


def parse_feature_file(file_path):
    with open(file_path, "r") as f:
        gherkin_document = parser.parse(TokenScanner(f.read()))

    feature_name = gherkin_document["feature"]["name"]
    file_scenarios = gherkin_document["feature"]["children"]

    data = {"feature": feature_name, "scenarios": []}
    for scenario in file_scenarios:
        scenario = scenario.get("scenario")
        if not scenario:
            continue

        scenario_name, scenario_type, steps = (
            scenario.get("name"),
            scenario.get("keyword"),
            scenario.get("steps"),
        )

        if not scenario_name or not scenario_type or not steps:
            continue

        scenario_steps = [
            {
                "text": step["text"],
                "has_auto_test": False,
                "keyword": step["keyword"],
                "keywordType": step["keywordType"],
            }
            for step in steps
        ]

        data["scenarios"].append(
            {
                "name": scenario_name,
                "type": scenario_type,
                "steps": scenario_steps,
                "has_auto_test": False,
            }
        )

    return data


def paste_token_into_url(repo_url, username, token):
    user_data = f"{username}:{token}@"
    protocol_end = "://"
    protocol_end_index = repo_url.index(protocol_end) + len(protocol_end)
    return repo_url[:protocol_end_index] + user_data + repo_url[protocol_end_index:]


def clone_features(
    repo_url,
    username,
    token,
    repo_path,
    branch=None,
    commit=None,
    particular_dir=None,
    smart_mode=False,
):
    dot_feature_files_mask = "*.feature"
    url = paste_token_into_url(repo_url, username, token)
    params = ["--filter=blob:none", "--no-checkout", "--depth", "1", "--sparse"]
    if branch:
        params.extend(["-b", branch])

    try:
        repo = Repo.clone_from(url=url, to_path=repo_path, multi_options=params)
    except Exception as e:
        return False, str(e.stderr)

    git_ = repo.git

    if not smart_mode and not particular_dir:
        git_.sparse_checkout("set", dot_feature_files_mask)

    elif not smart_mode and particular_dir:
        mask = particular_dir + "/" + dot_feature_files_mask
        git_.sparse_checkout("set", mask)

    elif smart_mode and particular_dir:
        git_.sparse_checkout("set", particular_dir)

    else:
        return False, "Cant be smart mode without dir"

    try:
        if commit:
            git_.checkout(commit)
        else:
            git_.checkout()

        cur_commit = git_.rev_parse("HEAD")

    except Exception as e:
        return False, str(e.stderr)

    return True, cur_commit


def push_files(
    repo_path,
    commit_message
):
    repo = Repo(repo_path)
    git_ = repo.git
    try:
        git_.add(".")
        if NOTHING_TO_COMMIT_MESSAGE == git_.status().split("\n")[-1]:
            return True, True
        git_.commit("-m", commit_message)
        git_.push()
    except Exception as e:
       return False, str(e.stderr)

    return True, True


def get_features(path, smart_mode, common_autotests_folder):
    features = []
    feature_ext = ".feature"

    for dirname, dirnames, filenames in os.walk(path):
        if ".git" in dirnames:
            dirnames.remove(".git")

        for full_filename in filenames:
            filename, file_extension = os.path.splitext(full_filename)

            if file_extension != feature_ext:
                continue

            file_path = os.path.join(dirname, full_filename)
            try:
                feature_data = parse_feature_file(file_path)
                feature_data["file_path"] = file_path
                feature_data["file_name"] = filename
                if smart_mode and filename in dirnames:
                    js_dir = os.path.join(dirname, filename)
                    feature_data = fetch_with_autotests_check(feature_data, js_dir)
                features.append(feature_data)

            except Exception:
                continue

    features_ = deepcopy(features)
    if smart_mode and common_autotests_folder:
        try:
            features = fetch_with_common_autotests_check(
                features, common_autotests_folder
            )
        except Exception:
            return features_

    return features


def get_features_from_file(path, file_name, smart_mode, common_autotests_folder):
    features = []
    feature_ext = ".feature"
    dirname = None
    full_filename = None
    dirnames = None
    for dirname_, dirnames_, filenames in os.walk(path):
        if dirname:
            break

        if ".git" in dirnames_:
            dirnames_.remove(".git")

        for full_filename_ in filenames:
            if full_filename_ == file_name:
                dirname = dirname_
                full_filename = full_filename_
                dirnames = dirnames_
                break

    filename, file_extension = os.path.splitext(full_filename)
    file_path = os.path.join(dirname, full_filename)

    try:
        feature_data = parse_feature_file(file_path)
        feature_data["file_path"] = file_path
        feature_data["file_name"] = filename
        if smart_mode and filename in dirnames:
            js_dir = os.path.join(dirname, filename)
            feature_data = fetch_with_autotests_check(feature_data, js_dir)
        features.append(feature_data)

    except Exception:
        return []

    features_ = deepcopy(features)
    if smart_mode and common_autotests_folder:
        try:
            features = fetch_with_common_autotests_check(
                features, common_autotests_folder
            )
        except Exception:
            return features_

    return features


def get_updated_tests_objcts(features, version):
    updated_test_files = []
    updated_project_tests = []
    updated_test_steps = []

    keywords = {
        "Outcome": "1",
        "Conjunction": "2",
        "Unknown": "3",
        "Action": "4",
        "Context": "5",
    }

    for feature in features:
        test_file = version.test_files.filter(file_path=feature["file_path"])
        if not test_file.exists():
            test_file = TestFile(
                file_path=feature["file_path"], project_version=version
            )
            updated_test_files.append(test_file)
        else:
            test_file = test_file.first()

        for scenario in feature["scenarios"]:
            project_test = test_file.tests.filter(test_name=scenario["name"])
            if not project_test.exists():
                project_test = ProjectTest(test_name=scenario["name"], file=test_file)
                updated_project_tests.append(project_test)
            else:
                project_test = project_test.first()
            for step in scenario["steps"]:
                keyword = keywords.get(step["keywordType"], "2")
                full_text = step["keyword"] + step["text"]
                step_ = project_test.steps.filter(keyword=keyword, text=full_text)
                if not step_.exists():
                    step_ = TestStep(
                        keyword=keyword,
                        project_test=project_test,
                        text=full_text,
                        has_auto_test=step.get("has_auto_test", False),
                    )
                    updated_test_steps.append(step_)
                else:
                    step_ = step_.first()
                    step_.has_auto_test = step.get("has_auto_test", False)
                    step_.save()

    return updated_test_files, updated_project_tests, updated_test_steps


def get_new_tests_objcts(features, version):
    new_test_files = []
    new_project_tests = []
    new_test_steps = []

    keywords = {
        "Outcome": "1",
        "Conjunction": "2",
        "Unknown": "3",
        "Action": "4",
        "Context": "5",
    }

    for feature in features:
        test_file = TestFile(file_path=feature["file_path"], project_version=version)
        new_test_files.append(test_file)

        for scenario in feature["scenarios"]:
            project_test = ProjectTest(test_name=scenario["name"], file=test_file)
            new_project_tests.append(project_test)

            for step in scenario["steps"]:
                keyword = keywords.get(step["keywordType"], "2")
                full_text = step["keyword"] + step["text"]
                step = TestStep(
                    keyword=keyword,
                    project_test=project_test,
                    text=full_text,
                    has_auto_test=step.get("has_auto_test", False),
                )
                new_test_steps.append(step)

    return new_test_files, new_project_tests, new_test_steps
