from pathlib import Path

from rubrical.package_managers.jsonnet import Jsonnet
from tests.constants import FILES_FOLDER_PATH


def test_jsonnet():
    jsonnet = Jsonnet()

    jsonnet.read_dependency_files(Path(FILES_FOLDER_PATH, "jsonnet"))
    jsonnet.parse_dependency_files()

    assert jsonnet.dependencies
    assert len(jsonnet.dependencies["jsonnetfile.json"]) == 2
    assert jsonnet.dependencies["jsonnetfile.json"][1].name == "xunleii/vector_jsonnet"
    assert jsonnet.dependencies["jsonnetfile.json"][1].version == "v0.1.2"
