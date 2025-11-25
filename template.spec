# vim: filetype=spec

%define version @@@Version@@@
%define builddir %{_builddir}/python%{python3_pkgversion}-fb-vmware-%{version}

Name:           python%{python3_pkgversion}-fb-vmware
Version:        %{version}
Release:        @@@Release@@@%{?dist}
Summary:        Python wrapper module around the pyvmomi module to simplify work and handling.

Group:          Development/Languages/Python
License:        LGPL-3
Distribution:   Frank Brehm
URL:            https://github.com/fbrehm/fb-vmware
Source0:        fb-vmware.%{version}.tar.gz

BuildRequires:  gettext
BuildRequires:  python%{python3_pkgversion}
BuildRequires:  python%{python3_pkgversion}-babel
BuildRequires:  python%{python3_pkgversion}-chardet
BuildRequires:  python%{python3_pkgversion}-devel
BuildRequires:  python%{python3_pkgversion}-fb-logging >= 1.0.0
BuildRequires:  python%{python3_pkgversion}-fb-tools >= 2.6.2
BuildRequires:  python%{python3_pkgversion}-libs
BuildRequires:  python%{python3_pkgversion}-pytz
BuildRequires:  python%{python3_pkgversion}-pyvmomi
BuildRequires:  python%{python3_pkgversion}-pyyaml
BuildRequires:  python%{python3_pkgversion}-semver
BuildRequires:  python%{python3_pkgversion}-six
BuildRequires:  pyproject-rpm-macros
Requires:       python%{python3_pkgversion}
Requires:       python%{python3_pkgversion}-babel
Requires:       python%{python3_pkgversion}-chardet
Requires:       python%{python3_pkgversion}-fb-logging >= 1.0.0
Requires:       python%{python3_pkgversion}-fb-tools >= 2.6.2
Requires:       python%{python3_pkgversion}-libs
Requires:       python%{python3_pkgversion}-pytz
Requires:       python%{python3_pkgversion}-pyvmomi
Requires:       python%{python3_pkgversion}-pyyaml
Requires:       python%{python3_pkgversion}-requests
Requires:       python%{python3_pkgversion}-semver
Requires:       python%{python3_pkgversion}-six
BuildArch:      noarch

%description
Python wrapper module around the pyvmomi module to simplify work and handling.

This is the Python@@@py_version_nodot@@@ version.

In this package are contained the following scripts:
 * get-vsphere-host-list
 * get-vsphere-network-list
 * get-vsphere-storage-cluster-list
 * get-vsphere-vm-info
 * get-vsphere-vm-list

%prep
echo "Preparing '${builddir}-' ..."
echo "Pwd: $( pwd )"
%autosetup -p1 -v

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files fb_vmware

echo "Whats in '%{builddir}':"
ls -lA '%{builddir}'

echo "Whats in '%{buildroot}':"
ls -lA '%{buildroot}'

%files -f %{pyproject_files}
%defattr(-,root,root,-)
%license LICENSE
%doc CHANGELOG.md LICENSE README.md pyproject.toml debian/changelog
%{_bindir}/*
%{_datadir}/*

%changelog
