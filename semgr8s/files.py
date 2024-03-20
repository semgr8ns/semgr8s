"""
File handler for all k8s yaml, results files.
"""

import json
import os
import random
import string

import yaml
from werkzeug.utils import secure_filename

DATA_FOLDER = "/app/data"
RANDOM = random.SystemRandom()


class S8sFiles:
    """
    Files class for handling file management for semgr8s.
    """

    postfix: str

    def __init__(self) -> None:
        self.postfix = self.get_random_string(length=20)

    @property
    def k8s_yaml_file(self) -> str:
        "Full file path of the the kubernetes yaml file."
        return self.generate_filename(prefix="k8s", filetype="yml")

    @property
    def results_file(self) -> str:
        "Full path semgrep results file."
        return self.generate_filename(prefix="results", filetype="json")

    @property
    def results(self) -> dict:
        "Get semgrep results from results file."
        return self.read_results()

    @staticmethod
    def get_random_string(length: int = 1) -> str:
        "Get random string of ascii letters and digits of length 'k'."
        return "".join(RANDOM.choices(string.ascii_letters + string.digits, k=length))

    @staticmethod
    def read_json(filename: str) -> dict:
        "Get data from json file."
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(fp=file)
        return data

    @staticmethod
    def read_yaml(filename: str) -> dict:
        "Get data from yaml file."
        with open(filename, "r", encoding="utf-8") as file:
            data = yaml.safe_load(stream=file)
        return data

    @staticmethod
    def write_yaml(filename: str, data: dict) -> None:
        "Write data to yaml file."
        with open(filename, "w", encoding="utf-8") as file:
            yaml.safe_dump(data=data, stream=file, default_flow_style=False)

    def generate_filename(self, prefix: str = "", filetype: str = "") -> str:
        "Generate filename from prefix, postfix, and file type."
        return os.path.join(
            DATA_FOLDER,
            secure_filename(f"{prefix}_{self.postfix}.{filetype}"),
        )

    def read_k8s_yaml(self) -> dict:
        "Get k8s resource data from k8s_yaml_file."
        return self.read_yaml(self.k8s_yaml_file)

    def write_k8s_yaml(self, data: dict) -> None:
        "Write yaml data to k8s_yaml_file."
        self.write_yaml(self.k8s_yaml_file, data=data)

    def read_results(self) -> dict:
        "Get results data from results_file."
        return self.read_json(self.results_file)

    def remove_files(self) -> None:
        "Remove temporary files files."
        try:
            os.remove(self.k8s_yaml_file)
            os.remove(self.results_file)
        except (FileNotFoundError, UnboundLocalError):
            pass
