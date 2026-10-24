from rubrical.enum import VersionDialect
from rubrical.languages.nodejs import NodeJS
from tests.constants import FILES_FOLDER_PATH


def test_nodejs_engines():
    nodejs = NodeJS()
    nodejs.read_files(FILES_FOLDER_PATH)
    nodejs.parse_files()

    assert {file: x.version for file, x in nodejs.declarations.items()} == {
        "nodejs/engines/minimum/package.json": ">=18.0.0",
        "nodejs/engines/caret/package.json": "^20.11.0",
        "nodejs/engines/range/package.json": ">=18.17.0 <23",
        "nodejs/engines/or-range/package.json": "^18.18.0 || ^20.9.0 || >=21.1.0",
        "nodejs/engines/wildcard/package.json": "20.x",
        "nodejs/engines/partial-gt/package.json": ">18",
        "nodejs/engines/spaced/package.json": ">= 18.17.0",
        "nodejs/engines/any/package.json": "*",
        "version-files/node/.node-version": "v18.17.1",
        "version-files/nvmrc/.nvmrc": "20",
        "version-files/nvmrc-lts/.nvmrc": "lts/*",
    }
    assert {
        file: x.dialect
        for file, x in nodejs.declarations.items()
        if x.dialect != VersionDialect.NPM
    } == {
        "version-files/node/.node-version": VersionDialect.VERSION_FILE,
        "version-files/nvmrc/.nvmrc": VersionDialect.VERSION_FILE,
        "version-files/nvmrc-lts/.nvmrc": VersionDialect.VERSION_FILE,
    }
    # Files without `engines.node` aren't graded, and node_modules is skipped.
    assert "nodejs/engines/none/package.json" in nodejs.found_files
    assert not any("node_modules" in x for x in nodejs.found_files)
