import re
import os
import rjsmin as _rjsmin
from pprint import pprint
py_jsmin = _rjsmin._make_jsmin(python_only=True)
import rjsmin as _rjsmin
py_jsmin = _rjsmin._make_jsmin(python_only=True)


class CypressCucumberPreprocessorPlugin:
    js_ext = ".js"
    keywords = {
        "Outcome": "Then",
        "Action": "When",
        "Context": "Given",
    }
    curly_braces_regex = r"\\\{.*?\}"
    any_value_regex = r"[^\n].*"

    def __init__(self):
        regexes = {}
        regexes_with_subs = {}
        for step_type in self.keywords:
            keyword = self.keywords[step_type]
            regexes[step_type] = []
            regexes_with_subs[step_type] = []
            regexes[step_type].extend(self.get_regexes(keyword))
            regexes_with_subs[step_type].extend(self.get_regexes_with_subs(keyword))
        self.regexes = regexes
        self.regexes_with_subs = regexes_with_subs

    @staticmethod
    def is_subdir(path, directory):
        path = os.path.realpath(path)
        directory = os.path.realpath(directory)
        relative = os.path.relpath(path, directory)
        if relative.startswith(os.pardir):
            return False
        else:
            return True

    def get_regexes(self, keyword):
        return [keyword + r"\(\'([^\n{}]*?)'", keyword + r'\(\"([^\n{}]*?)"']

    def get_regexes_with_subs(self, keyword):
        return [keyword + r"\(\'([^\n]*?{[^\n]*?}[^\n]*?)'", keyword + r'\(\"([^\n]*?{[^\n]*?}[^\n]*?)"']


    def fix_substitute(self, regex_with_sub):
        curly_braces_regex = r"\{.*?\}"
        any_value_regex = r"[^\n].*"

        return re.sub(curly_braces_regex, any_value_regex, regex_with_sub).strip(
                    """"'"""
                )

    def get_auto_test_steps_from_file(self, file_path):

        with open(file_path, "r") as f:
            file_text = f.read()

        regexes = self.regexes
        regexes_with_subs = self.regexes_with_subs
        auto_test_steps = []
        for step_type, regexes in regexes.items():
            for regex in regexes:
                steps = re.findall(regex, file_text)
                for step in steps:
                    auto_test_steps.append({"keyword": step_type,
                                            "step": step})

        for step_type, regexes in regexes_with_subs.items():
            for regex in regexes:
                steps = re.findall(regex, file_text)
                for step in steps:
                    regexed_step = self.fix_substitute(step)
                    auto_test_steps.append({"keyword": step_type,
                                            "step": regexed_step})

        return auto_test_steps

    def get_auto_test_steps_from_dir(self, dir_path):

        auto_test_steps = []
        if not os.path.isdir(dir_path):
            return auto_test_steps

        for dirname, dirnames, filenames in os.walk(dir_path):
            if ".git" in dirnames:
                dirnames.remove(".git")

            for full_filename in filenames:
                filename, file_extension = os.path.splitext(full_filename)

                if file_extension != self.js_ext:
                    continue

                file_path = os.path.join(dirname, full_filename)
                auto_test_steps.extend(self.get_auto_test_steps_from_file(file_path))

        return auto_test_steps

    def get_auto_test_steps_from_repo(self, repo_path, exclude_folders=[]):

        auto_test_steps = []
        if not os.path.isdir(repo_path):
            return auto_test_steps

        for dirname, dirnames, filenames in os.walk(repo_path):
            skip = False
            for exclude_folder in exclude_folders:
                if self.is_subdir(dirname, exclude_folder):
                    skip = True
                    break
            if skip:
                continue

            if ".git" in dirnames:
                dirnames.remove(".git")

            for full_filename in filenames:
                filename, file_extension = os.path.splitext(full_filename)

                if file_extension == self.js_ext:
                    steps_parent = os.path.basename(os.path.normpath(dirname))
                    auto_test_steps.append({"folder": steps_parent, "steps": self.get_auto_test_steps_from_dir(dirname)})
                    break

                file_path = os.path.join(dirname, full_filename)
                auto_test_steps.extend(self.get_auto_test_steps_from_file(file_path))

        return auto_test_steps
