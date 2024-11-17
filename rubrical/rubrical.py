from pathlib import Path
from typing import Dict, List, Tuple

from rubrical.comparisons import check_package
from rubrical.enum import PackageCheck, SupportedPackageManagers
from rubrical.package_managers.base_package_manager import BasePackageManager
from rubrical.package_managers.go import Go
from rubrical.package_managers.jsonnet import Jsonnet
from rubrical.package_managers.nodejs import NodeJS
from rubrical.package_managers.python import Python
from rubrical.reporters import terminal
from rubrical.schemas.configuration import RubricalConfig
from rubrical.schemas.results import PackageCheckResult
from rubrical.utilities import console

PACKAGE_MANAGER_MAPPING = {
    SupportedPackageManagers.JSONNET.value: Jsonnet,
    SupportedPackageManagers.PYTHON.value: Python,
    SupportedPackageManagers.GO.value: Go,
    SupportedPackageManagers.NODEJS.value: NodeJS,
}


class Rubrical:
    configuration: RubricalConfig
    package_managers: List[BasePackageManager]
    repository_path: Path
    debug: bool

    def __init__(
        self, configuration: RubricalConfig, repository_path: Path, debug: bool = False
    ) -> None:
        self.configuration = configuration
        self.repository_path = repository_path
        self.debug = debug
        self.package_managers = []

        for package_manager in self.configuration.package_managers:
            self.package_managers.append(
                PACKAGE_MANAGER_MAPPING[package_manager.name]()  #  type:  ignore
            )

    def check_package_managers(
        self,
    ) -> Tuple[bool, bool, Dict[str, List[PackageCheckResult]]]:
        warnings_found = False
        blocks_found = False
        results: Dict[str, List[PackageCheckResult]] = {}

        for package_manager in self.package_managers:
            check_results = self.check_package_manager(package_manager)
            terminal.terminal_report(package_manager.name, check_results)

            if (
                any([x.check == PackageCheck.BLOCK for x in check_results])
                and not blocks_found
            ):
                blocks_found = True

            if (
                any([x.check == PackageCheck.WARN for x in check_results])
                and not warnings_found
            ):
                warnings_found = True

            results[package_manager.name] = check_results

        return (warnings_found, blocks_found, results)

    def check_package_manager(
        self, package_manager: BasePackageManager
    ) -> List[PackageCheckResult]:
        console.print_header(f"Grading {package_manager.name}", "🈴")
        check_results: List[PackageCheckResult] = []

        package_manager.read_package_manager_files(self.repository_path)
        package_manager.parse_package_manager_files()

        [configuration] = [
            x
            for x in self.configuration.package_managers
            if x.name == package_manager.name
        ]

        for file in package_manager.packages.keys():
            if self.debug:
                console.print_debug(f"Processing {file}.")

            for package in package_manager.packages[file]:
                for package_requirements in configuration.packages:
                    if self.debug:
                        console.print_debug(
                            f"Checking {package.name} @ {package.raw_constraint}."
                        )

                    if package_requirements.name == package.name:
                        check_results.append(
                            PackageCheckResult(
                                name=package.name,
                                file=file,
                                check=check_package(package_requirements, package),
                                version_package=package.raw_constraint,
                                version_warn=package_requirements.warn,
                                version_block=package_requirements.block,
                            )
                        )
                        if self.debug:
                            console.print_debug(
                                f"Check result for {package.name} @ {package.raw_constraint} is {check_results[-1].check.value}."
                            )

        return check_results


"⚙️  Rubrical starting!\n📃 Loading configuration.\n🈴 Grading jsonnet\nDebug: Processing files/jsonnet/jsonnetfile.json.\nDebug: Checking jsonnet-libs/k8s-libsonnet @ jsonnet-libs/k8s-libsonnet main.\nDebug: Checking jsonnet-libs/k8s-libsonnet @ jsonnet-libs/k8s-libsonnet main.\nDebug: Checking xunleii/vector_jsonnet @ xunleii/vector_jsonnet v0.1.2.\nDebug: Check result for xunleii/vector_jsonnet @ xunleii/vector_jsonnet v0.1.2 \nis ok.\nDebug: Checking xunleii/vector_jsonnet @ xunleii/vector_jsonnet v0.1.2.\nDebug: Checking jsonnet-libs/argo-workflows-libsonnet @ \njsonnet-libs/argo-workflows-libsonnet v1.1.1.\nDebug: Checking jsonnet-libs/argo-workflows-libsonnet @ \njsonnet-libs/argo-workflows-libsonnet v1.1.1.\nDebug: Check result for jsonnet-libs/argo-workflows-libsonnet @ \njsonnet-libs/argo-workflows-libsonnet v1.1.1 is block.\nDebug: Checking jsonnet-libs/argo-workflows-libsonAWESOME @ \njsonnet-libs/argo-workflows-libsonAWESOME random-branch.\nDebug: Checking jsonnet-libs/argo-workflows-libsonAWESOME @ \njsonnet-libs/argo-workflows-libsonAWESOME random-branch.\n jsonnet checks completed with violations!\n┏━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┓\n┃ File                    ┃ Dependency               ┃ Result                  ┃\n┡━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━┩\n│ files/jsonnet/jsonnetf… │ jsonnet-libs/argo-workf… │ ❌                      │\n│                         │                          │ jsonnet-libs/argo-work… │\n│                         │                          │ v1.1.1 < v1.1.2, update │\n│                         │                          │ to >= v1.1.3            │\n└─────────────────────────┴──────────────────────────┴─────────────────────────┘\n🈴 Grading python\nDebug: Processing files/python/requirements.txt.\nDebug: Checking docopt @ docopt == 0.6.1             # Version Matching. Must be\nversion 0.6.1.\nDebug: Checking docopt @ docopt == 0.6.1             # Version Matching. Must be\nversion 0.6.1.\nDebug: Checking docopt @ docopt == 0.6.1             # Version Matching. Must be\nversion 0.6.1.\nDebug: Checking docopt @ docopt == 0.6.1             # Version Matching. Must be\nversion 0.6.1.\nDebug: Checking keyring @ keyring >= 4.1.1            # Minimum version 4.1.1.\nDebug: Checking keyring @ keyring >= 4.1.1            # Minimum version 4.1.1.\nDebug: Checking keyring @ keyring >= 4.1.1            # Minimum version 4.1.1.\nDebug: Checking keyring @ keyring >= 4.1.1            # Minimum version 4.1.1.\nDebug: Checking coverage @ coverage != 3.5             # Version Exclusion. \nAnything except version 3.5.\nDebug: Checking coverage @ coverage != 3.5             # Version Exclusion. \nAnything except version 3.5.\nDebug: Checking coverage @ coverage != 3.5             # Version Exclusion. \nAnything except version 3.5.\nDebug: Checking coverage @ coverage != 3.5             # Version Exclusion. \nAnything except version 3.5.\nDebug: Checking Mopidy-Dirble @ Mopidy-Dirble ~= 1.1        # Compatible \nrelease. Same as >= 1.1, == 1.*.\nDebug: Check result for Mopidy-Dirble @ Mopidy-Dirble ~= 1.1        # Compatible\nrelease. Same as >= 1.1, == 1.* is block.\nDebug: Checking Mopidy-Dirble @ Mopidy-Dirble ~= 1.1        # Compatible \nrelease. Same as >= 1.1, == 1.*.\nDebug: Checking Mopidy-Dirble @ Mopidy-Dirble ~= 1.1        # Compatible \nrelease. Same as >= 1.1, == 1.*.\nDebug: Checking Mopidy-Dirble @ Mopidy-Dirble ~= 1.1        # Compatible \nrelease. Same as >= 1.1, == 1.*.\nDebug: Checking something-something @ something-something <1.6,>1.5.\nDebug: Checking something-something @ something-something <1.6,>1.5.\nDebug: Checking something-something @ something-something <1.6,>1.5.\nDebug: Checking something-something @ something-something <1.6,>1.5.\nDebug: Checking flake8 @ flake8~=4.0,<5.\nDebug: Checking flake8 @ flake8~=4.0,<5.\nDebug: Checking flake8 @ flake8~=4.0,<5.\nDebug: Check result for flake8 @ flake8~=4.0,<5 is block.\nDebug: Checking flake8 @ flake8~=4.0,<5.\nDebug: Processing files/poetry/pyproject.toml.\nDebug: Checking dom-toml @ dom-toml<3.0.0,>=2.0.0.\nDebug: Checking dom-toml @ dom-toml<3.0.0,>=2.0.0.\nDebug: Checking dom-toml @ dom-toml<3.0.0,>=2.0.0.\nDebug: Checking dom-toml @ dom-toml<3.0.0,>=2.0.0.\nDebug: Checking pydantic @ pydantic<3.0.0,>=2.5.2.\nDebug: Checking pydantic @ pydantic<3.0.0,>=2.5.2.\nDebug: Checking pydantic @ pydantic<3.0.0,>=2.5.2.\nDebug: Checking pydantic @ pydantic<3.0.0,>=2.5.2.\nDebug: Check result for pydantic @ pydantic<3.0.0,>=2.5.2 is ok.\nDebug: Checking pygithub @ pygithub<3.0.0,>=2.0.0.\nDebug: Checking pygithub @ pygithub<3.0.0,>=2.0.0.\nDebug: Checking pygithub @ pygithub<3.0.0,>=2.0.0.\nDebug: Checking pygithub @ pygithub<3.0.0,>=2.0.0.\nDebug: Checking pyproject-parser @ pyproject-parser>=0.11.0,<0.12.0.\nDebug: Checking pyproject-parser @ pyproject-parser>=0.11.0,<0.12.0.\nDebug: Checking pyproject-parser @ pyproject-parser>=0.11.0,<0.12.0.\nDebug: Checking pyproject-parser @ pyproject-parser>=0.11.0,<0.12.0.\nDebug: Checking python-benedict @ python-benedict>=0.34.0,<0.35.0.\nDebug: Checking python-benedict @ python-benedict>=0.34.0,<0.35.0.\nDebug: Checking python-benedict @ python-benedict>=0.34.0,<0.35.0.\nDebug: Checking python-benedict @ python-benedict>=0.34.0,<0.35.0.\nDebug: Checking pyyaml @ pyyaml>=6.0,<7.0.\nDebug: Checking pyyaml @ pyyaml>=6.0,<7.0.\nDebug: Checking pyyaml @ pyyaml>=6.0,<7.0.\nDebug: Checking pyyaml @ pyyaml>=6.0,<7.0.\nDebug: Checking requirements-detector @ requirements-detector<2.0.0,>=1.3.2.\nDebug: Checking requirements-detector @ requirements-detector<2.0.0,>=1.3.2.\nDebug: Checking requirements-detector @ requirements-detector<2.0.0,>=1.3.2.\nDebug: Checking requirements-detector @ requirements-detector<2.0.0,>=1.3.2.\nDebug: Checking requirements-parser @ requirements-parser>=0.11.0,<0.12.0.\nDebug: Checking requirements-parser @ requirements-parser>=0.11.0,<0.12.0.\nDebug: Checking requirements-parser @ requirements-parser>=0.11.0,<0.12.0.\nDebug: Checking requirements-parser @ requirements-parser>=0.11.0,<0.12.0.\nDebug: Checking semver @ semver>=3.0.2,<4.0.0.\nDebug: Checking semver @ semver>=3.0.2,<4.0.0.\nDebug: Checking semver @ semver>=3.0.2,<4.0.0.\nDebug: Checking semver @ semver>=3.0.2,<4.0.0.\nDebug: Checking setuptools @ setuptools>=75.0.0,<76.0.0.\nDebug: Checking setuptools @ setuptools>=75.0.0,<76.0.0.\nDebug: Checking setuptools @ setuptools>=75.0.0,<76.0.0.\nDebug: Checking setuptools @ setuptools>=75.0.0,<76.0.0.\nDebug: Checking toml @ toml>=0.10.2,<0.11.0.\nDebug: Checking toml @ toml>=0.10.2,<0.11.0.\nDebug: Checking toml @ toml>=0.10.2,<0.11.0.\nDebug: Checking toml @ toml>=0.10.2,<0.11.0.\nDebug: Checking typer @ typer<0.13.0,>=0.12.0.\nDebug: Checking typer @ typer<0.13.0,>=0.12.0.\nDebug: Checking typer @ typer<0.13.0,>=0.12.0.\nDebug: Checking typer @ typer<0.13.0,>=0.12.0.\nDebug: Processing files/python/pyproject.toml.\nDebug: Checking apscheduler @ apscheduler < 4.0.0.\nDebug: Checking apscheduler @ apscheduler < 4.0.0.\nDebug: Check result for apscheduler @ apscheduler < 4.0.0 is block.\nDebug: Checking apscheduler @ apscheduler < 4.0.0.\nDebug: Checking apscheduler @ apscheduler < 4.0.0.\nDebug: Checking semver @ semver < 3.0.0.\nDebug: Checking semver @ semver < 3.0.0.\nDebug: Checking semver @ semver < 3.0.0.\nDebug: Checking semver @ semver < 3.0.0.\n python checks completed with violations!\n┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n┃ File                          ┃ Dependency    ┃ Result                       ┃\n┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩\n│ files/python/requirements.txt │ Mopidy-Dirble │ ❌ Mopidy-Dirble ~= 1.1    … │\n│                               │               │ # Compatible release. Same   │\n│                               │               │ as >= 1.1, == 1.* < v1.2.1,  │\n│                               │               │ update to >= v1.2.2          │\n│ files/python/requirements.txt │ flake8        │ ❌ flake8~=4.0,<5 < v6.0.0,  │\n│                               │               │ update to >= v7.0.0          │\n│ files/python/pyproject.toml   │ apscheduler   │ ❌ apscheduler < 4.0.0 <     │\n│                               │               │ v4.0.1, update to >= v4.0.2  │\n└───────────────────────────────┴───────────────┴──────────────────────────────┘\n🈴 Grading go\nDebug: Processing files/go/go.mod.\nDebug: Checking github.com/adrg/xdg @ github.com/adrg/xdg v0.4.0.\nDebug: Check result for github.com/adrg/xdg @ github.com/adrg/xdg v0.4.0 is \nblock.\nDebug: Checking github.com/atotto/clipboard @ github.com/atotto/clipboard \nv0.1.4.\nDebug: Checking github.com/cenkalti/backoff/v4 @ github.com/cenkalti/backoff/v4 \nv4.2.0.\nDebug: Checking github.com/derailed/popeye @ github.com/derailed/popeye v0.11.1.\nDebug: Checking github.com/derailed/tcell/v2 @ github.com/derailed/tcell/v2 \nv2.3.1-rc.3.\nDebug: Checking github.com/derailed/tview @ github.com/derailed/tview v0.8.1.\nDebug: Checking github.com/fatih/color @ github.com/fatih/color v1.15.0.\nDebug: Checking github.com/fsnotify/fsnotify @ github.com/fsnotify/fsnotify \nv1.6.0.\nDebug: Checking github.com/fvbommel/sortorder @ github.com/fvbommel/sortorder \nv1.0.2.\nDebug: Checking github.com/ghodss/yaml @ github.com/ghodss/yaml v1.0.0.\nDebug: Checking github.com/mattn/go-colorable @ github.com/mattn/go-colorable \nv0.1.13.\nDebug: Checking github.com/mattn/go-runewidth @ github.com/mattn/go-runewidth \nv0.0.14.\nDebug: Checking github.com/petergtz/pegomock @ github.com/petergtz/pegomock \nv2.9.0+incompatible.\nDebug: Checking github.com/rakyll/hey @ github.com/rakyll/hey v0.1.4.\nDebug: Checking github.com/rs/zerolog @ github.com/rs/zerolog v1.29.0.\nDebug: Checking github.com/sahilm/fuzzy @ github.com/sahilm/fuzzy v0.1.0.\nDebug: Checking github.com/spf13/cobra @ github.com/spf13/cobra v1.6.1.\nDebug: Checking github.com/stretchr/testify @ github.com/stretchr/testify \nv1.8.2.\nDebug: Checking golang.org/x/text @ golang.org/x/text v0.7.0.\nDebug: Checking gopkg.in/yaml.v2 @ gopkg.in/yaml.v2 v2.4.0.\nDebug: Checking helm.sh/helm/v3 @ helm.sh/helm/v3 v3.11.1.\nDebug: Checking k8s.io/api @ k8s.io/api v0.26.2.\nDebug: Checking k8s.io/apiextensions-apiserver @ k8s.io/apiextensions-apiserver \nv0.26.1.\nDebug: Checking k8s.io/apimachinery @ k8s.io/apimachinery v0.26.2.\nDebug: Checking k8s.io/cli-runtime @ k8s.io/cli-runtime v0.26.1.\nDebug: Checking k8s.io/client-go @ k8s.io/client-go v0.26.2.\nDebug: Checking k8s.io/klog/v2 @ k8s.io/klog/v2 v2.90.0.\nDebug: Checking k8s.io/kubectl @ k8s.io/kubectl v0.26.1.\nDebug: Checking k8s.io/metrics @ k8s.io/metrics v0.26.2.\nDebug: Checking sigs.k8s.io/yaml @ sigs.k8s.io/yaml v1.3.0.\n go checks completed with violations!\n┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n┃ File            ┃ Dependency          ┃ Result                               ┃\n┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩\n│ files/go/go.mod │ github.com/adrg/xdg │ ❌ github.com/adrg/xdg v0.4.0 <      │\n│                 │                     │ v0.5.0, update to >= v0.6.0          │\n└─────────────────┴─────────────────────┴──────────────────────────────────────┘\n🈴 Grading nodejs\nDebug: Processing files/nodejs/package.json.\nDebug: Checking @electron/remote @ @electron/remote 2.0.9.\nDebug: Checking @react-icons/all-files @ @react-icons/all-files 4.1.0.\nDebug: Checking args @ args 5.0.3.\nDebug: Checking chalk @ chalk 5.2.0.\nDebug: Checking clsx @ clsx 1.2.1.\nDebug: Checking color @ color 4.2.3.\nDebug: Checking columnify @ columnify 1.6.0.\nDebug: Checking css-loader @ css-loader 6.7.3.\nDebug: Checking got @ got 12.4.1.\nDebug: Checking json-loader @ json-loader 0.5.7.\nDebug: Checking mousetrap @ mousetrap chabou/mousetrap#useCapture.\nDebug: Checking ms @ ms 2.1.3.\nDebug: Checking open @ open 8.4.2.\nDebug: Checking ora @ ora 5.4.1.\nDebug: Checking parse-url @ parse-url 8.1.0.\nDebug: Checking php-escape-shell @ php-escape-shell 1.0.0.\nDebug: Checking react @ react 17.0.2.\nDebug: Check result for react @ react 17.0.2 is block.\nDebug: Checking react-deep-force-update @ react-deep-force-update 2.1.3.\nDebug: Checking react-dom @ react-dom 17.0.2.\nDebug: Checking react-redux @ react-redux 7.2.8.\nDebug: Checking redux @ redux 4.2.1.\nDebug: Checking redux-thunk @ redux-thunk 2.4.2.\nDebug: Checking registry-url @ registry-url ^6.0.1.\nDebug: Checking reselect @ reselect 4.1.7.\nDebug: Checking seamless-immutable @ seamless-immutable 7.1.4.\nDebug: Checking semver @ semver 7.3.8.\nDebug: Checking shebang-loader @ shebang-loader 0.0.1.\nDebug: Checking styled-jsx @ styled-jsx 5.1.2.\nDebug: Checking stylis @ stylis 3.5.4.\nDebug: Checking typescript-json-schema @ typescript-json-schema 0.56.0.\nDebug: Checking uuid @ uuid 9.0.0.\nDebug: Checking webpack-cli @ webpack-cli 5.0.1.\nDebug: Checking xterm @ xterm 4.19.0.\nDebug: Checking xterm-addon-fit @ xterm-addon-fit ^0.5.0.\nDebug: Checking xterm-addon-ligatures @ xterm-addon-ligatures 0.6.0-beta.19.\nDebug: Checking xterm-addon-search @ xterm-addon-search ^0.9.0.\nDebug: Checking xterm-addon-unicode11 @ xterm-addon-unicode11 ^0.3.0.\nDebug: Checking xterm-addon-web-links @ xterm-addon-web-links ^0.6.0.\nDebug: Checking xterm-addon-webgl @ xterm-addon-webgl 0.12.0.\nDebug: Checking @ava/babel @ @ava/babel 2.0.0.\nDebug: Checking @ava/typescript @ @ava/typescript ^4.0.0.\nDebug: Checking @babel/cli @ @babel/cli 7.21.0.\nDebug: Checking @babel/core @ @babel/core 7.21.4.\nDebug: Checking @babel/plugin-proposal-class-properties @ \n@babel/plugin-proposal-class-properties ^7.18.6.\nDebug: Checking @babel/plugin-proposal-numeric-separator @ \n@babel/plugin-proposal-numeric-separator ^7.18.6.\nDebug: Checking @babel/plugin-proposal-object-rest-spread @ \n@babel/plugin-proposal-object-rest-spread ^7.20.7.\nDebug: Checking @babel/plugin-proposal-optional-chaining @ \n@babel/plugin-proposal-optional-chaining 7.21.0.\nDebug: Checking @babel/preset-react @ @babel/preset-react 7.18.6.\nDebug: Checking @babel/preset-typescript @ @babel/preset-typescript 7.21.4.\nDebug: Checking @types/args @ @types/args 5.0.0.\nDebug: Checking @types/async-retry @ @types/async-retry 1.4.3.\nDebug: Checking @types/color @ @types/color 3.0.3.\nDebug: Checking @types/columnify @ @types/columnify ^1.5.1.\nDebug: Checking @types/fs-extra @ @types/fs-extra 11.0.1.\nDebug: Checking @types/lodash @ @types/lodash ^4.14.192.\nDebug: Checking @types/mousetrap @ @types/mousetrap 1.6.11.\nDebug: Checking @types/ms @ @types/ms 0.7.31.\nDebug: Checking @types/node @ @types/node 16.18.23.\nDebug: Checking @types/plist @ @types/plist 3.0.2.\nDebug: Checking @types/react @ @types/react ^17.0.43.\nDebug: Checking @types/react-dom @ @types/react-dom ^17.0.14.\nDebug: Checking @types/react-redux @ @types/react-redux ^7.1.22.\nDebug: Checking @types/seamless-immutable @ @types/seamless-immutable 7.1.16.\nDebug: Checking @types/styled-jsx @ @types/styled-jsx 2.2.9.\nDebug: Checking @types/terser-webpack-plugin @ @types/terser-webpack-plugin \n5.2.0.\nDebug: Checking @types/uuid @ @types/uuid 9.0.1.\nDebug: Checking @typescript-eslint/eslint-plugin @ \n@typescript-eslint/eslint-plugin 4.33.0.\nDebug: Checking @typescript-eslint/parser @ @typescript-eslint/parser 4.33.0.\nDebug: Checking ava @ ava 5.2.0.\nDebug: Checking babel-loader @ babel-loader 9.1.2.\nDebug: Checking concurrently @ concurrently 8.0.1.\nDebug: Checking copy-webpack-plugin @ copy-webpack-plugin 11.0.0.\nDebug: Checking cpy-cli @ cpy-cli ^4.2.0.\nDebug: Checking cross-env @ cross-env 7.0.3.\nDebug: Checking electron @ electron 24.0.0.\nDebug: Checking electron-builder @ electron-builder ^23.3.3.\nDebug: Checking electron-devtools-installer @ electron-devtools-installer 3.2.0.\nDebug: Checking electron-link @ electron-link ^0.6.0.\nDebug: Checking electron-mksnapshot @ electron-mksnapshot 24.0.0.\nDebug: Checking electron-notarize @ electron-notarize 1.2.2.\nDebug: Checking electron-rebuild @ electron-rebuild 3.2.9.\nDebug: Checking electronmon @ electronmon ^2.0.2.\nDebug: Checking eslint @ eslint 7.32.0.\nDebug: Checking eslint-config-prettier @ eslint-config-prettier 8.8.0.\nDebug: Checking eslint-plugin-eslint-comments @ eslint-plugin-eslint-comments \n^3.2.0.\nDebug: Checking eslint-plugin-json-schema-validator @ \neslint-plugin-json-schema-validator ^4.4.0.\nDebug: Checking eslint-plugin-jsonc @ eslint-plugin-jsonc ^2.7.0.\nDebug: Checking eslint-plugin-prettier @ eslint-plugin-prettier 4.2.1.\nDebug: Checking eslint-plugin-react @ eslint-plugin-react 7.32.2.\nDebug: Checking husky @ husky 8.0.3.\nDebug: Checking inquirer @ inquirer 9.1.5.\nDebug: Checking node-addon-api @ node-addon-api 6.0.0.\nDebug: Checking node-gyp @ node-gyp 9.3.1.\nDebug: Checking null-loader @ null-loader 4.0.1.\nDebug: Checking playwright @ playwright 1.32.2.\nDebug: Checking plist @ plist 3.0.6.\nDebug: Checking prettier @ prettier 2.8.7.\nDebug: Checking proxyquire @ proxyquire 2.1.3.\nDebug: Checking redux-devtools-extension @ redux-devtools-extension 2.13.9.\nDebug: Checking style-loader @ style-loader 3.3.2.\nDebug: Checking terser @ terser 5.16.8.\nDebug: Checking ts-node @ ts-node 10.9.1.\nDebug: Checking typescript @ typescript 5.0.4.\nDebug: Checking webpack @ webpack 5.78.0.\nDebug: Processing files/nodejs/complex/package.json.\nDebug: Checking foo @ foo 1.0.0 - 2.9999.9999.\nDebug: Checking bar @ bar >=1.0.2 <2.1.2.\nDebug: Checking baz @ baz >1.0.2 <=2.3.4.\nDebug: Checking boo @ boo 2.0.1.\nDebug: Checking asd @ asd http://asdf.com/asdf.tar.gz.\nDebug: Checking til @ til ~1.2.\nDebug: Checking elf @ elf ~1.2.3.\nDebug: Checking two @ two 2.x.\nDebug: Checking thr @ thr 3.3.x.\nDebug: Checking lat @ lat latest.\nDebug: Checking dyl @ dyl file:../dyl.\n nodejs checks completed with violations!\n┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n┃ File                      ┃ Dependency ┃ Result                              ┃\n┡━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩\n│ files/nodejs/package.json │ react      │ ❌ react 17.0.2 < v17.0.3, update   │\n│                           │            │ to >= v17.0.4                       │\n└───────────────────────────┴────────────┴─────────────────────────────────────┘\n🛑 Blocked dependencies found!\n"
