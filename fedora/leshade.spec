Name: leshade
Version: 2.3.7
Release: 1%{?dist}
Summary: Official build for LeShade. An ReShade Manager for Linux.

License: MIT
URL: https://github.com/Ishidawg/LeShade
Source0: LeShade-%{version}.tar.gz

BuildArch: noarch
BuildRequires: git
BuildRequires: meson
BuildRequires: ninja-build
Requires: python
Requires: python3-pyside6
Requires: python3-requests
Requires: python3-certifi

%description
%{summary}

%prep
%autosetup -n LeShade-%{version}

sed -i "s/^VERSION = .*/VERSION = \"%{version}\"/" main.py
sed -i "s/^BUILD_TYPE = .*/BUILD_TYPE = \"Release\"/" main.py

%build
%meson
%meson_build

%install
%meson_install

%files
%{_bindir}/%{name}
%{_datadir}/%{name}/
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/256x256/apps/%{name}.png
%{_datadir}/licenses/%{name}/LICENSE
%doc README.md

%changelog
* Thu Feb 26 2026 Ishidaw <willianscagol@gmail.com> - 2.3.7-1
- Trying to build with github actions, LeShade Stable Release 2.3.7
