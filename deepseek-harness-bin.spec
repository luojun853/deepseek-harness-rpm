# Unofficial community packaging for Fedora / COPR.
# Not affiliated with, endorsed by, or maintained by DeepSeek.

%global npm_name @deepseek-ai/dsh
%global npmver   0.2.1-rc.5

# Let COPR/rpmbuild fetch Source0 from the npm registry when it is not
# already present in the SOURCES directory.
%global _disable_source_fetch 0

# The upstream npm tarball contains prebuilt/native Node addons.
# Keep the same "!strip" behaviour as the Arch PKGBUILD.
%global debug_package %{nil}
%global __strip /bin/true

Name:           deepseek-harness-bin
Version:        0.2.1~rc.5
Release:        2%{?dist}
Summary:        DeepSeek Harness CLI and agent harness
License:        MIT AND Apache-2.0 AND ISC AND MPL-2.0 AND BSD-3-Clause AND LGPL-3.0-or-later AND BSD-2-Clause AND Python-2.0 AND Unlicense AND 0BSD AND (MIT OR CC0-1.0)
URL:            https://github.com/deepseek-ai/deepseek-harness
Source0:        https://registry.npmjs.org/@deepseek-ai/dsh/-/dsh-%{npmver}.tgz

# Fedora 44 ships Node.js 24 as nodejs24.  The -npm-bin package provides
# /usr/bin/npm (the plain nodejs24-npm package only provides npm-24).
# Native addons use their packaged prebuilt binaries; no compiler toolchain
# is needed.  patchelf is only used to fix the sherpa-onnx RUNPATH in %install.
BuildRequires:  nodejs24-npm-bin
BuildRequires:  /usr/bin/node
BuildRequires:  /usr/bin/npm
BuildRequires:  patchelf

Requires:       nodejs24-bin
Requires:       pnpm
Provides:       deepseek-harness = %{version}-%{release}
Conflicts:      deepseek-harness
Conflicts:      deepseek-harness-git

ExclusiveArch:  x86_64 aarch64

%description
DeepSeek Harness CLI and agent harness.

This package installs the npm distribution of DeepSeek Harness globally
under /usr/lib/node_modules and provides the dsh command.

%prep
%setup -q -n package

%build
export npm_config_foreground_scripts=true

mkdir -p npm-root/usr

# COPR: enable "Internet access during builds" for this dependency fetch.
npm install --global \
  --prefix "$PWD/npm-root/usr" \
  --cache "$PWD/.npm-cache" \
  --omit=dev \
  --no-audit \
  --no-fund \
  --allow-scripts=@deepseek-ai/dsh-subprocess-local,koffi,node-pty \
  "%{_sourcedir}/dsh-%{npmver}.tgz"

%install
install -d "%{buildroot}%{_prefix}"
cp -a npm-root/usr/. "%{buildroot}%{_prefix}/"

find "%{buildroot}%{_prefix}/lib/node_modules" -type d -exec chmod 0755 {} +

# The prebuilt sherpa-onnx binary carries a RUNPATH from its build machine.
# Replace it with $ORIGIN so the bundled shared libraries resolve correctly.
for d in %{buildroot}%{_prefix}/lib/node_modules/@deepseek-ai/dsh/node_modules/sherpa-onnx-linux-*; do
  [ -d "$d" ] || continue
  find "$d" -type f \( -name '*.node' -o -name '*.so' -o -name '*.so.*' \) \
    -exec patchelf --set-rpath '$ORIGIN' {} +
done

%check
HOME="$PWD" "%{buildroot}%{_bindir}/dsh" --version

%files
%{_bindir}/dsh
%dir %{_prefix}/lib/node_modules/@deepseek-ai
%{_prefix}/lib/node_modules/@deepseek-ai/dsh/
%license LICENSE
%doc README.md README.zh.md README.i18n.yaml

%changelog
* Sun Nov 01 2026 YG <yg@localhost> - 0.2.1~rc.5-2
- Trim build dependencies after switching to packaged native prebuilds.

* Sun Nov 01 2026 github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com> - 0.2.1~rc.5-1
- Update to upstream pre-release 0.2.1-rc.5.

* Sun Nov 01 2026 YG <yg@localhost> - 0.2.1~rc.4-2
- Patch sherpa-onnx RUNPATH for Fedora check-rpaths.

* Sun Nov 01 2026 YG <yg@localhost> - 0.2.1~rc.4-1
- Initial COPR package for Fedora 44, converted from PKGBUILD.
