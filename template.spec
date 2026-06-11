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
BuildRequires:  python%{python3_pkgversion}-devel
BuildRequires:  python%{python3_pkgversion}-fb-logging >= 1.4.0
BuildRequires:  python%{python3_pkgversion}-fb-tools >= 3.0.0
BuildRequires:  python%{python3_pkgversion}-libs
BuildRequires:  python%{python3_pkgversion}-pytz
BuildRequires:  python%{python3_pkgversion}-pyvmomi
BuildRequires:  python%{python3_pkgversion}-pyyaml
BuildRequires:  python%{python3_pkgversion}-rich
BuildRequires:  python%{python3_pkgversion}-semver
BuildRequires:  python%{python3_pkgversion}-six
BuildRequires:  pyproject-rpm-macros

Requires:       python%{python3_pkgversion}
Requires:       python%{python3_pkgversion}-babel
Requires:       python%{python3_pkgversion}-fb-logging >= 1.4.0
Requires:       python%{python3_pkgversion}-fb-tools >= 3.0.0
Requires:       python%{python3_pkgversion}-libs
Requires:       python%{python3_pkgversion}-pytz
Requires:       python%{python3_pkgversion}-pyvmomi
Requires:       python%{python3_pkgversion}-pyyaml
Requires:       python%{python3_pkgversion}-rich
Requires:       python%{python3_pkgversion}-semver
Requires:       python%{python3_pkgversion}-six
BuildArch:      noarch

%description
Python wrapper module around the pyvmomi module to simplify work and handling.

This is the Python%{python3_pkgversion} version.

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

%files
%defattr(-,root,root,-)
%license LICENSE
%doc CHANGELOG.md README.md pyproject.toml debian/changelog
%{python3_sitelib}/*
%{_datadir}/locale/*

%package -n fb-vmware

Summary:  Python wrapper module around the pyvmomi module to simplify work and handling.
Group:    Applications/System

Requires: python%{python3_pkgversion}-fb-vmware = %{version}

%description -n fb-vmware
Python wrapper module around the pyvmomi module to simplify work and handling.

In this package are contained the following scripts:
 * get-vsphere-cluster-list
 * get-vsphere-host-list
 * get-vsphere-network-list
 * get-vsphere-storage-cluster-info
 * get-vsphere-storage-cluster-list
 * get-vsphere-storage-list
 * get-vsphere-vm-info
 * get-vsphere-vm-list
 * search-vsphere-storage

This is the Python%{python3_pkgversion} version.

%files -n fb-vmware
%{_bindir}/*
%{_mandir}/*

%changelog
