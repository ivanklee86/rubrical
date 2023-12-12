from pathlib import Path

from rubrical.package_managers.jsonnet import Jsonnet
from tests.constants import FILES_FOLDER_PATH


def test_jsonnet():
    jsonnet = Jsonnet()

    jsonnet.read_package_manager_files(Path(FILES_FOLDER_PATH, "jsonnet"))
    jsonnet.parse_package_manager_files()

    assert jsonnet.packages
    assert len(jsonnet.packages["jsonnetfile.json"]) == 4
    assert jsonnet.packages["jsonnetfile.json"][1].name == "xunleii/vector_jsonnet"
    assert (
        jsonnet.packages["jsonnetfile.json"][1].version_constraints[0].version
        == "v0.1.2"
    )
