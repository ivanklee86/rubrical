from rubrical.configuration.dependency_requirement import DependencyRequirement
from rubrical.dependency import Dependency
from rubrical.enum import DependencyCheck

SEMVER_DEPENDENCY_REQUIREMENT = DependencyRequirement(
    **{"name": "dep1", "type": "semver", "warn": "v1.0.1", "block": "v1.0.0"}
)

SEMVER_DEPENDENCY = Dependency(**{"name": "dep1", "version": "v1.0.0"})
SEMVER_OLD_DEPENDENCY = Dependency(**{"name": "dep1", "version": "v0.9.0"})
SEMVER_NEWER_DEPENDENCY = Dependency(**{"name": "dep1", "version": "v1.0.1"})
SEMVER_NEWEST_DEPENDENCY = Dependency(**{"name": "dep2", "version": "v1.0.2"})


def test_dependency_semver():
    assert DependencyCheck.BLOCK == SEMVER_DEPENDENCY_REQUIREMENT.check_dependency(
        SEMVER_OLD_DEPENDENCY
    )
    assert DependencyCheck.BLOCK == SEMVER_DEPENDENCY_REQUIREMENT.check_dependency(
        SEMVER_DEPENDENCY
    )
    assert DependencyCheck.WARN == SEMVER_DEPENDENCY_REQUIREMENT.check_dependency(
        SEMVER_NEWER_DEPENDENCY
    )
    assert DependencyCheck.OK == SEMVER_DEPENDENCY_REQUIREMENT.check_dependency(
        SEMVER_NEWEST_DEPENDENCY
    )
