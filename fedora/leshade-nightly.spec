Name: leshade-nightly
Version: 2.3.7
Release: 1%{?dist}
Summary: Official build for LeShade Nightly. An ReShade Manager for Linux.

License: MIT
URL: https://github.com/Ishidawg/LeShade
Source0: LeShade-%{version}.tar.gz

Conflicts: leshade
Provides: leshade = %{version}

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

%build
%meson
%meson_build

%install
%meson_install

# Need to pass leshade instead of name cuz mason give leshade but the package name is leshade-nightly
%files
%{_bindir}/leshade
%{_datadir}/leshade
%{_datadir}/applications/leshade.desktop
%{_datadir}/icons/hicolor/256x256/apps/leshade.png
%{_datadir}/licenses/leshade/LICENSE
%doc README.md

%changelog
* Thu Feb 26 2026 Ishidaw <willianscagol@gmail.com> - 2.3.7-1
- Trying to build with github actions, LeShade Nightly Release 2.3.7
