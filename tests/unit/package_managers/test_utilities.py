from rubrical.package_managers.utilities import git


def test_git_url_parse():
    assert (
        git.repository_from_url("https://github.com/xunleii/vector_jsonnet.git")
        == "xunleii/vector_jsonnet"
    )
    assert (
        git.repository_from_url("git@github.com:xunleii/vector_jsonnet.git")
        == "xunleii/vector_jsonnet"
    )
