from git import Repo
from gherkin.parser import Parser
from os import listdir, path
from gherkin.token_scanner import TokenScanner
import re
from copy import deepcopy
from .models import *
from shutil import rmtree, copyfile
from django.conf import settings
from django.db import connection
from pprint import pprint
from .auto_test_plugins import CypressCucumberPreprocessorPlugin
from django.db.models import Prefetch
from pathlib import Path
from django.db.models import Q
from gherkin.errors import CompositeParserException


ccp_plugin = CypressCucumberPreprocessorPlugin()

parser = Parser()

RESERVED_FILES_POSTFIX = "_res"
PUSHING_DIR_POSTFIX = "_push"
NOTHING_TO_COMMIT_MESSAGE = "nothing to commit, working tree clean"
CONJUNCTION_STEP_TYPE = "Conjunction"
UNKNOWN_STEP_TYPE = "Unknown"
CONJUNCTION_STEP_KEYWORD = "*"

STEP_TYPES_CODES = {
    "Outcome": "1",
    "Conjunction": "2",
    "Unknown": "3",
    "Action": "4",
    "Context": "5"
}




def covered_in_single_quotes(text):
    return "'" + text + "'"


def covered_in_double_quotes(text):
    return '"' + text + '"'


def get_reserve_repo_name(repo_path):
    return repo_path + RESERVED_FILES_POSTFIX


def get_unreserved_repo_path(repo_path):
    return repo_path[: len(repo_path) - len(RESERVED_FILES_POSTFIX)]


def get_pushing_repo_path(repo_path):
    return repo_path + PUSHING_DIR_POSTFIX


def rename_file_hard(old_path, new_path):
    if os.path.isdir(new_path):
        os.remove(new_path)

    os.rename(old_path, new_path)


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


def del_reserve_repo(repo_path):
    reserved_repo_path = get_reserve_repo_name(repo_path)
    if os.path.isdir(reserved_repo_path):
        rmtree(reserved_repo_path)



def get_repo_path(project_id, version_id):
    return os.path.join(
        settings.DOT_FEATURE_FILES_DIR, str(project_id), str(version_id)
    )


def remove_repo(repo_path):
    if os.path.isdir(repo_path):
        rmtree(repo_path)


def shift(seq, n):
    if not seq:
        return []
    n = n % len(seq)
    return seq[n:] + seq[:n]


def split_common_autotests_folder_filed(field_value):
    separator = ","
    folders = [x.strip() for x in field_value.split(separator)]
    return folders



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


def bulk_delete(model, ids, cursor):
    if not ids:
        return
    table_name = model.objects.model._meta.db_table
    ids = ",".join([str(id_) for id_ in ids])
    query = f"DELETE FROM {table_name} WHERE id IN ({ids})"
    cursor.execute(query)


def copy_files_to_dir(files, directory):
    for file in files:
        new_file_path = path.join(directory, path.basename(file.file_path))
        if path.isfile(new_file_path):
            os.remove(new_file_path)
        copyfile(file.file_path, new_file_path)


def get_common_folder_path(repo_path, particular_dir, common_autotests_folder):
    return os.path.join(repo_path, particular_dir, common_autotests_folder)


def get_commit_message(test_files):
    commit_message = "Added Files: "
    file_names = [file.file_name for file in test_files]
    commit_message += ", ".join(file_names)
    return commit_message


def check_for_similar_test_names(features):
    features = [scenario["name"] for scenario in features["scenarios"]]
    duplicates = []
    seen = set()
    for f in features:
        if f in seen:
            duplicates.append(f)
        else:
            seen.add(f)

    return duplicates


def get_parse_error_message(file_name, error):
    return f"Error in file {file_name}: {error}"

def fetch_file_with_autotests(file):
    file_name = Path(file.file_path).stem
    autotests = file.project_version.auto_test_steps.filter(Q(autotests_folder_name=file_name) | Q(is_common=True))
    file.auto_test_steps.set(autotests)


def get_autotest_updated_steps(file):
    auto_steps = file.auto_test_steps.all()
    tests = file.tests.all()
    steps_to_update = []
    for test in tests:
        steps = test.steps.all()
        for step in steps:
            for auto_step in auto_steps:
                if re.fullmatch(auto_step.text, step.text_without_keyword) and step.keyword == auto_step.keyword:
                    if not step.has_auto_test:
                        step.has_auto_test = True
                        steps_to_update.append(step)
                    break
            else:
                if step.has_auto_test:
                    step.has_auto_test = False
                    steps_to_update.append(step)
                    break

    return steps_to_update


def fetch_version_files_with_auto_test(version_id):
    version = (
        ProjectVersion.objects.filter(id=version_id)
        .prefetch_related(
            Prefetch(
                "test_files",
                queryset=TestFile.objects.prefetch_related(
                    Prefetch(
                        "tests",
                        queryset=ProjectTest.objects.prefetch_related(
                            Prefetch("steps", queryset=TestStep.objects.all())
                        ),
                    )
                ).prefetch_related("auto_test_steps"),
            )
        )
        .first()
    )
    steps = []
    for file in version.test_files.all():
        steps.extend(get_autotest_updated_steps(file))

    TestStep.objects.bulk_update(steps, ["has_auto_test"])


def get_test_text_position(scenario):
    last_line = -1

    for step in scenario["steps"]:
        if step["location"]["line"] > last_line:
            last_line = step["location"]["line"]

    examples = scenario.get("examples", None)
    if examples:
        for example in examples:
            table = example.get("tableBody", None)
            if not table:
                continue
            for cells in table:
                if cells["location"]["line"] > last_line:
                    last_line = cells["location"]["line"]
    return scenario["location"]["line"], last_line


def filter_queryset(queryset, **kwargs):
    res = []
    for instance in queryset:
        if all((instance.__getattribute__(field)==value for field, value in kwargs.items())):
            res.append(instance)
    return res


def fetch_with_autotests(common_autotests_folders, files, repo_path, version):
    auto_tests_steps_objects = []
    exclude_dirs = []
    if common_autotests_folders:
        common_autotests_steps_objects_ = []
        for common_autotests_folder in common_autotests_folders:
            exclude_dirs.append(common_autotests_folder)
            common_autotests_steps = ccp_plugin.get_auto_test_steps_from_dir(common_autotests_folder)

            for step in common_autotests_steps:
                auto_step = AutoTestStep(keyword=STEP_TYPES_CODES[step["keyword"]],
                                         text=step["step"],
                                         is_common=True,
                                         version=version)
                common_autotests_steps_objects_.append(auto_step)

        common_autotests_steps_objects = AutoTestStep.objects.bulk_create(common_autotests_steps_objects_)
        for common_autotests_steps_object in common_autotests_steps_objects:
            common_autotests_steps_object.project_files.set(files)

    auto_tests_folders = ccp_plugin.get_auto_test_steps_from_repo(repo_path, exclude_dirs)

    for auto_tests_folder in auto_tests_folders:
        files_objects = []
        autotests_folder_name = None
        for file in files:
            if Path(file.file_path).stem == auto_tests_folder["folder"]:
                files_objects.append(file)
                autotests_folder_name = auto_tests_folder["folder"]

        for auto_tests_step in auto_tests_folder["steps"]:
            auto_tests_steps_object = AutoTestStep(keyword=STEP_TYPES_CODES[auto_tests_step["keyword"]],
                                                   text=auto_tests_step["step"],
                                                   version=version,
                                                   autotests_folder_name=autotests_folder_name)
            auto_tests_steps_object.project_files_ = files_objects
            auto_tests_steps_objects.append(auto_tests_steps_object)

    auto_tests_steps_objects = AutoTestStep.objects.bulk_create(auto_tests_steps_objects)
    for auto_tests_steps_object in auto_tests_steps_objects:
        auto_tests_steps_object.project_files.add(*auto_tests_steps_object.project_files_)
    fetch_version_files_with_auto_test(version.id)


def parse_feature_file(file_path):
    with open(file_path, "r") as f:
        gherkin_document = parser.parse(TokenScanner(f.read()))
    feature_name = gherkin_document["feature"]["name"]
    file_scenarios = gherkin_document["feature"]["children"]

    data = {"feature": feature_name, "scenarios": []}

    for scenario in file_scenarios:
        scenario = scenario.get("scenario", None)
        if not scenario:
            continue

        start_line, last_line = get_test_text_position(scenario)

        scenario_name, scenario_type, steps = (
            scenario.get("name"),
            scenario.get("keyword"),
            scenario.get("steps"),
        )

        if not scenario_name or not scenario_type or not steps:
            continue

        scenario_steps = []
        last_step_type = UNKNOWN_STEP_TYPE
        for step in steps:
            if step["keywordType"] != CONJUNCTION_STEP_TYPE and step["keyword"].strip() != CONJUNCTION_STEP_KEYWORD:
                last_step_type = step["keywordType"]

            scenario_steps.append(
                {
                    "text": step["text"],
                    "has_auto_test": False,
                    "keyword": step["keyword"],
                    "keywordType": last_step_type,
                    "number": step["id"]
                }
            )

        data["scenarios"].append(
            {
                "name": scenario_name,
                "type": scenario_type,
                "steps": scenario_steps,
                "has_auto_test": False,
                "start_line": start_line,
                "last_line": last_line
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

        git_ = repo.git

        if not smart_mode and not particular_dir:
            git_.sparse_checkout("set", dot_feature_files_mask, "--no-cone")

        elif not smart_mode and particular_dir:
            mask = particular_dir + "/" + dot_feature_files_mask
            git_.sparse_checkout("set", mask, "--no-cone")

        elif smart_mode and particular_dir:
            git_.sparse_checkout("set", particular_dir)

        else:
            return False, "Cant be smart mode without dir"

        if commit:
            git_.checkout(commit)
        else:
            git_.checkout()

        cur_commit = git_.rev_parse("HEAD")

    except Exception as e:
        return False, str(e.stderr)

    return True, cur_commit


def push_files(repo_path, commit_message, commit_email, commit_username):
    repo = Repo(repo_path)
    git_ = repo.git
    try:
        git_.add(".")
        if NOTHING_TO_COMMIT_MESSAGE == git_.status().split("\n")[-1]:
            return True, True

        repo.config_writer().set_value("user", "name", commit_username).release()
        repo.config_writer().set_value("user", "email", commit_email).release()
        git_.commit("-m", commit_message)
        git_.push()
    except Exception as e:
        return False, str(e.stderr)

    return True, True


def get_features(path):
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
                features.append(feature_data)
            except CompositeParserException as e:
                raise Exception(get_parse_error_message(full_filename, e.errors[0]))

    return features


def get_features_from_file(path, file_name):
    dirname = None
    full_filename = None

    for dirname_, dirnames_, filenames in os.walk(path):
        if dirname:
            break

        if ".git" in dirnames_:
            dirnames_.remove(".git")

        for full_filename_ in filenames:
            if full_filename_ == file_name:
                dirname = dirname_
                full_filename = full_filename_
                break

    filename, file_extension = os.path.splitext(full_filename)
    file_path = os.path.join(dirname, full_filename)
    feature_data = parse_feature_file(file_path)
    feature_data["file_path"] = file_path
    feature_data["file_name"] = filename
    return feature_data


def sync_features_with_file(features, version_id, cursor=None):
    new_tests = []
    new_steps = []
    updated_tests = []
    updated_steps = []
    deleted_tests_ids = []
    deleted_steps_ids = []

    file = TestFile.objects.filter(file_path=features["file_path"]).prefetch_related(
                    Prefetch(
                        "tests",
                        queryset=ProjectTest.objects.prefetch_related(
                            Prefetch("steps", queryset=TestStep.objects.all())
                        ),
                    )
                ).prefetch_related("auto_test_steps")

    if file.exists():
        file = file.first()
    else:
        version = ProjectVersion.objects.get(id=version_id)
        file = TestFile(file_path=features["file_path"],
                        project_version=version)
        file.save()


    for test in file.tests.all():
        deleted_tests_ids.append(test.id)
        for step in test.steps.all():
            deleted_steps_ids.append(step.id)

    for scenario in features["scenarios"]:
        test_exists = True
        test = file.tests.filter_locally(test_name=scenario["name"])
        if test:
            test = test[0]
            deleted_tests_ids.remove(test.id)
            if test.last_line != scenario["last_line"] or test.start_line != scenario["start_line"]:
                test.last_line = scenario["last_line"]
                test.start_line = scenario["start_line"]
                updated_tests.append(test)
        else:
            test = ProjectTest(test_name=scenario["name"],
                               last_line=scenario["last_line"],
                               start_line=scenario["start_line"],
                               file=file,
                               )
            new_tests.append(test)
            test_exists = False

        for step in scenario["steps"]:
            keyword = STEP_TYPES_CODES.get(step["keywordType"], "2")
            full_text = step["keyword"] + step["text"]
            number = step["number"]
            text_without_keyword = step["text"].strip()
            has_auto_test = step.get("has_auto_test", False)
            if test_exists:
                steps = test.steps.filter_locally(keyword=keyword,
                                                  text=full_text,
                                                  text_without_keyword=text_without_keyword)

                if steps:
                    for step_ in steps:
                        try:
                            deleted_steps_ids.remove(step_.id)
                            break
                        except ValueError:
                            pass

                    if step_.number != number or step_.has_auto_test != has_auto_test:
                        step_.number = number
                        step_.has_auto_test = has_auto_test
                        updated_steps.append(step_)
                else:
                    step_ = TestStep(
                        keyword=keyword,
                        project_test=test,
                        text=full_text,
                        has_auto_test=step.get("has_auto_test", False),
                        text_without_keyword=text_without_keyword,
                        number=number,
                    )
                    new_steps.append(step_)
            else:
                step_ = TestStep(
                    keyword=keyword,
                    project_test=test,
                    text=full_text,
                    has_auto_test=step.get("has_auto_test", False),
                    text_without_keyword=text_without_keyword,
                    number=number,
                )
                new_steps.append(step_)

    if not cursor:
        cursor = connection.cursor()
    bulk_delete(ProjectTest, deleted_tests_ids, cursor)
    bulk_delete(TestStep, deleted_steps_ids, cursor)
    ProjectTest.objects.bulk_update(updated_tests, ["last_line", "start_line"])
    TestStep.objects.bulk_update(updated_steps, ["number", "has_auto_test"])
    ProjectTest.objects.bulk_create(new_tests)
    TestStep.objects.bulk_create(new_steps)

    return file





def get_updated_tests_objects(features, version):
    new_test_files = []
    updated_project_tests = []
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
        for test_file_ in version.test_files.all():
            if test_file_.file_path == feature["file_path"]:
                test_file = test_file_
                break
        else:
            test_file = TestFile(
                file_path=feature["file_path"], project_version=version
            )
            new_test_files.append(test_file)

        for scenario in feature["scenarios"]:
            project_test = test_file.tests.filter(test_name=scenario["name"])

            if project_test.exists():
                project_test = project_test.first()
                if project_test.start_line != scenario["start_line"] or project_test.last_line != scenario["last_line"]:
                    project_test.start_line = scenario["start_line"]
                    project_test.last_line = scenario["last_line"]
                    updated_project_tests.append(project_test)

            else:
                project_test = ProjectTest(test_name=scenario["name"],
                                           file=test_file,
                                           start_line=scenario["start_line"],
                                           last_line=scenario["last_line"])
                new_project_tests.append(project_test)

            for step in scenario["steps"]:
                keyword = keywords.get(step["keywordType"], "2")
                full_text = step["keyword"] + step["text"]
                step_ = project_test.steps.filter(keyword=keyword, text=full_text)
                number = step["number"]
                text_without_keyword = step["text"].strip()
                if not step_.exists():
                    step_ = TestStep(
                        keyword=keyword,
                        project_test=project_test,
                        text=full_text,
                        has_auto_test=step.get("has_auto_test", False),
                        text_without_keyword=text_without_keyword,
                        number=number,
                    )
                    new_test_steps.append(step_)
                else:
                    step_ = step_.first()
                    step_.number = number
                    step_.has_auto_test = step.get("has_auto_test", False)
                    step_.save()

    return new_test_files, new_project_tests, updated_project_tests, new_test_steps


def get_new_tests_objects(features, version):
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
            project_test = ProjectTest(test_name=scenario["name"],
                                       file=test_file,
                                       start_line=scenario["start_line"],
                                       last_line=scenario["last_line"])
            new_project_tests.append(project_test)

            for step in scenario["steps"]:
                keyword = keywords.get(step["keywordType"], "2")
                full_text = step["keyword"] + step["text"]
                number = step["number"]
                text_without_keyword = step["text"].strip()
                step = TestStep(
                    keyword=keyword,
                    project_test=project_test,
                    text=full_text,
                    text_without_keyword=text_without_keyword,
                    has_auto_test=step.get("has_auto_test", False),
                    number=number
                )
                new_test_steps.append(step)

    return new_test_files, new_project_tests, new_test_steps


def get_deleted_tests_objects(features, version):
    deleted_test_files = []
    deleted_project_tests = []
    deleted_test_steps = []

    keywords = {
        "Outcome": "1",
        "Conjunction": "2",
        "Unknown": "3",
        "Action": "4",
        "Context": "5",
    }

    for file in version.test_files.all():
        deleted_test_files.append(file.id)
        for test in file.tests.all():
            deleted_project_tests.append(test.id)
            for step in test.steps.all():
                deleted_test_steps.append(step.id)

    for feature in features:
        test_file = version.test_files.filter_locally(file_path=feature["file_path"])
        if test_file:
            test_file = test_file.first()
            deleted_test_files.remove(test_file.id)
        else:
            continue
        for scenario in feature["scenarios"]:
            project_test = test_file.tests.filter_locally(test_name=scenario["name"])

            if project_test:
                project_test = project_test.first()
                deleted_project_tests.remove(project_test.id)
            else:
                continue

            for step in scenario["steps"]:
                keyword = keywords.get(step["keywordType"], "2")
                full_text = step["keyword"] + step["text"]
                step_ = project_test.steps.filter_locally(keyword=keyword, text=full_text)
                if step_:
                    step_ = step_.first()
                    deleted_test_steps.remove(step_.id)
                else:
                    continue

    return deleted_test_files, deleted_project_tests, deleted_test_steps


def get_deleted_tests_objects_from_file(features, test_file):
    if not features:
        return None, None

    deleted_project_tests = []
    deleted_test_steps = []

    keywords = {
        "Outcome": "1",
        "Conjunction": "2",
        "Unknown": "3",
        "Action": "4",
        "Context": "5",
    }

    for test in test_file.tests.all():
        deleted_project_tests.append(test.id)
        for step in test.steps.all():
            deleted_test_steps.append(step.id)

    feature = features[0]

    for scenario in feature["scenarios"]:
        project_test = test_file.tests.filter(test_name=scenario["name"])
        if project_test.exists():
            project_test = project_test.first()
            try:
                deleted_project_tests.remove(project_test.id)
            except ValueError:
                continue
        else:
            continue

        for step in scenario["steps"]:
            keyword = keywords.get(step["keywordType"], "2")
            full_text = step["keyword"] + step["text"]
            steps = project_test.steps.filter(keyword=keyword, text=full_text)
            if steps.exists():
                for step_ in steps:
                    try:
                        deleted_test_steps.remove(step_.id)
                        break
                    except ValueError:
                        pass
            else:
                continue

    return deleted_project_tests, deleted_test_steps
