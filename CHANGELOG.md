# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2025-11-25

### Added

* Adding `pyproject.toml`.
* Adding `CHANGELOG.md`.

### Changed

* Renaming directory lib => src and updating references to it.
* Updating update-env.sh for pyproject.toml and flit.
* Improving `src/fb_vmware/app/__init__.py`.
* Transforming the modules `src/fb_vmware/app/get_storage_cluster_list.py`, `src/fb_vmware/app/get_host_list.py`,
  `src/fb_vmware/app/get_network_list.py`, `src/fb_vmware/app/get_vm_info.py` and
  `src/fb_vmware/app/get_vm_list.py` into entrypoints.
* Applying `black` to all Python scripts.

### Fixed

* Fixing `src/fb_vmware/xlate.py`.

### Removed

* Removed all scripts in `bin/` - they are substitited by entrypoints.

## [1.5.3] - 2025-04-09

### Fixed

* Fixing Github workflows.

## [1.5.2] - 2025-04-09

### Fixed

* Fixing `lib/fb_vmware/network.py`.

## [1.5.1] - 2025-04-08

### Added

* Adding class VSphereNoNetFoundError to `lib/fb_vmware/errors.py`.

### Fixed

* Fixing method `get_network_for_ip()` of class VsphereNetworkDict.

## [1.5.0] - 2025-04-07

### Added

* Adding `lib/fb_vmware/typed_dict.py` for class TypedDict.
* Adding script `bin/get-vsphere-network-list` and its application class
  module `lib/fb_vmware/app/get_network_list.py`.
* Adding module `lib/fb_vmware/app/get_network_list.py` for classes VsphereDVS and VsphereDvPortGroup.

## [1.4.1] - 2025-02-06

### Changed

* Changing debug behaviour in `lib/fb_vmware/ether.py`.

## [1.4.0] - 2025-02-05

### Added

* Extending .gitignore.
* Adding debug output to `lib/fb_vmware/connect.py`.

### Changed

* Workaround for unusual backing devices for Ethernet devices.
* Setting copyright year to 2025.

## [1.3.1] - 2024-07-25

### Fixed

* Fixing search for locales dir in `lib/fb_vmware/xlate.py`.

## [1.3.0] - 2024-07-24

### Changed

* Changing the used spinner by this from `pp_tools` and removing the no more used spinner module.
* Making username and password in VSphere configuration optional.

## [1.2.0] - 2024-07-10

### Added

* Adding `bin/get-vsphere-storage-cluster-list` with application class module
  `lib/fb_vmware/app/get_storage_cluster_list.py`.
* Adding error class VSphereDiskCtrlrTypeNotFoudError.
* Adding classmethod `VSphereDiskCtrlrTypeNotFoudError.get_disk_controller_class()`.
* Adding possibility to use another SCSI controller type for a VM to create.

## [1.1.2] - 2024-07-01

### Changed

* Updating dependencies to `fb_tools`.
* Setting shared Github workflow to branch main.

## [1.1.1] - 2024-06-20

### Changed

* Changing version of package builder in .gitlab-ci.yml to v2.0.

## [1.1.0] - 2024-06-19

### Added

* Adding GitHub workflow build-packages for using a shared workflow.

### Changed

* Deactivating GitHub workflow packages.
* Refactoring setup.py.
* Applying flake8 rules to all Python sources.

## [1.0.1] - 2024-05-29

### Changed

* Using shared GitHub action.

### Fixed

* Fixing search for locales dir in `lib/fb_vmware/xlate.py`.
* Fixing `.github/workflows/packages.yaml`.

## [1.0.0] - 2024-05-29

### Changed

* Updating `.gitlab-ci.yml` o the latest version of Digitas packaging tools.
* Reworking `.github/workflows/packages.yaml`.
* Updating setup.cfg and setup.py.
* Increasing copyright year to 2024.

## [0.6.2] - 2023-10-17

### Fixed

* Fixing GitHub workflow for creating packages for EL-8.

## [0.6.1] - 2023-10-17

### Added

* Adding option to enable UUID for VM disks on creation a VM.

## [0.6.0] - 2023-07-13

### Changed

* Extending flake8 rules.
* Applying flake8 rules to all python scripts and modules.

### Fixed

* Fixing translations.

## [0.5.7] - 2023-01-02

## Fixed

* Fixing `.gitlab-ci.yml`.

## [0.5.6] - 2022-12-30

### Added

* Adding signing of all Debian packages in Github workflow.
* Adding Python 3.11 to test matrix in Github workflow.

### Changed

* Updating package dependencies in template.spec and debian/control.
* Using shared pipelines in `.gitlab-ci.yml`.


## [0.5.5] - 2022-11-24

### Added

* Adding `rpm-addsign-wrapper.expect`.

## [0.5.4] - 2022-11-24

### Added

* Adding `.gitlab-ci.yml`.

## [0.5.3] - 2022-06-13

### Fixed

* Fixing typo in `locale/de_DE/LC_MESSAGES/fb_vmware.po`.

## [0.5.2] - 2022-06-10

### Changed

* Applying linting rules to Python modules.

### Fixed

* Fixing tests for current status.

## [0.5.1] - 2022-06-09

### Added

* Adding Github workflow and actions.

## [0.5.0] - 2022-06-09

### Added

* Initial release.


[Unreleased]: https://github.com/fbrehm/fb-vmware/compare/1.5.3...HEAD
[1.5.3]: https://github.com/fbrehm/fb-vmware/compare/1.5.2...1.5.3
[1.5.2]: https://github.com/fbrehm/fb-vmware/compare/1.5.1...1.5.2
[1.5.1]: https://github.com/fbrehm/fb-vmware/compare/1.5.0...1.5.1
[1.5.0]: https://github.com/fbrehm/fb-vmware/compare/1.4.1...1.5.0
[1.4.1]: https://github.com/fbrehm/fb-vmware/compare/1.4.0...1.4.1
[1.4.0]: https://github.com/fbrehm/fb-vmware/compare/1.3.1...1.4.0
[1.3.1]: https://github.com/fbrehm/fb-vmware/compare/1.3.0...1.3.1
[1.3.0]: https://github.com/fbrehm/fb-vmware/compare/1.2.0...1.3.0
[1.2.0]: https://github.com/fbrehm/fb-vmware/compare/1.1.1...1.2.0
[1.1.1]: https://github.com/fbrehm/fb-vmware/compare/1.1.0...1.1.1
[1.1.0]: https://github.com/fbrehm/fb-vmware/compare/1.0.1...1.1.0
[1.0.1]: https://github.com/fbrehm/fb-vmware/compare/1.0.0...1.0.1
[1.0.0]: https://github.com/fbrehm/fb-vmware/compare/0.6.2...1.0.0
[0.6.2]: https://github.com/fbrehm/fb-vmware/compare/0.6.1...0.6.2
[0.6.1]: https://github.com/fbrehm/fb-vmware/compare/0.6.0...0.6.1
[0.6.0]: https://github.com/fbrehm/fb-vmware/compare/0.5.7...0.6.0
[0.5.7]: https://github.com/fbrehm/fb-vmware/compare/0.5.6...0.5.7
[0.5.6]: https://github.com/fbrehm/fb-vmware/compare/0.5.5...0.5.6
[0.5.5]: https://github.com/fbrehm/fb-vmware/compare/0.5.4...0.5.5
[0.5.4]: https://github.com/fbrehm/fb-vmware/compare/0.5.3...0.5.4
[0.5.3]: https://github.com/fbrehm/fb-vmware/compare/0.5.2...0.5.3
[0.5.2]: https://github.com/fbrehm/fb-vmware/compare/0.5.1...0.5.2
[0.5.1]: https://github.com/fbrehm/fb-vmware/compare/0.5.0...0.5.1
[0.5.0]: https://github.com/fbrehm/fb-vmware/releases/tag/0.5.0
