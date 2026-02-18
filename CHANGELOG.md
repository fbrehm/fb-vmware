# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2026-02-06

### Changed

* Updated CHANGELOG.md.
* Extending valid search chains of classes VsphereDatastoreDict and VsphereDsClusterDict.
* Added classmethod `valid_search_chains()` to classes VsphereDatastoreDict
  and VsphereDsClusterDict.

## [1.8.4] - 2026-02-06

### Changed

* Non change release for triggering build pipelines.

## [1.8.3] - 2026-01-22

### Fixed

* Fixed debug output errors in classes `VsphereDatastoreDict` and `VsphereDsClusterDict`.

## [1.8.2] - 2026-01-19

### Added

* Adding parameter `as_pyvmomi_obj` to method `get_vm_direct()` of class `VsphereConnection`.

### Fixed

* Fixing the `get_pyvmomi_obj()` methods of different classes.

## [1.8.1] - 2026-01-16

### Added

* Adding script `get-vsphere-cluster-list`.

### Changed

* Trying to get name of the resource pool of a computing cluster from UI.
* Some minor fixes.

## [1.8.0] - 2026-01-15

### Added

* Adding methods `get_all_objects()` and `get_parents()` to class BaseVsphereHandler.
* Adding method `get_vm_direct()` to class VsphereConnection.
* Adding method `get_pyvmomi_obj()` to different classes.
* Adding script `get-vsphere-storage-cluster-info`
* Adding method `search_space` to classes VsphereDatastoreDict and VsphereDsClusterDict.
* Adding script `search-vsphere-storage`.

### Changed

* Implementingmethod `get_vm_list()` to class VsphereConnection and using it in scripts
  `get-vsphere-vm-list` and `get-vsphere-vm-info`.
* Changing command line arguments for `get-vsphere-vm-list`.
* Collect connected hosts to a datastore.
* Refactoring all info scripts to use Python-Rich tables.
* Applying black to all Python scripts.

## [1.7.1] - 2025-11-28

### Fixed

* Removing pointless data/.gitkeep.

## [1.7.0] - 2025-11-28

### Changed

* Collecting different objects now in all available data centers.
* Extending classes VsphereDatastoreand VsphereDsCluster by new
  properties `vsphere` and `dc_name`.
* Extending class VsphereVm by ne property `dc_name`.
* Output of DC name in Query scripts.
* Adding property 'name' to VsphereConnection.

## [1.6.0] - 2025-11-25

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
* Fixed typo of VMware and vSphere.

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


[Unreleased]: https://github.com/fbrehm/fb-vmware/compare/1.8.4...develop
[1.8.4]: https://github.com/fbrehm/fb-vmware/compare/1.8.3...1.8.4
[1.8.3]: https://github.com/fbrehm/fb-vmware/compare/1.8.2...1.8.3
[1.8.2]: https://github.com/fbrehm/fb-vmware/compare/1.8.1...1.8.2
[1.8.1]: https://github.com/fbrehm/fb-vmware/compare/1.8.0...1.8.1
[1.8.0]: https://github.com/fbrehm/fb-vmware/compare/1.7.1...1.8.0
[1.7.1]: https://github.com/fbrehm/fb-vmware/compare/1.7.0...1.7.1
[1.7.0]: https://github.com/fbrehm/fb-vmware/compare/1.6.0...1.7.0
[1.6.0]: https://github.com/fbrehm/fb-vmware/compare/1.5.3...1.6.0
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
