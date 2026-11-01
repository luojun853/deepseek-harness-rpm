# deepseek-harness-rpm

> **Unofficial project / 非官方项目**
>
> This repository is an unofficial community packaging project. It is not affiliated with, endorsed by, sponsored by, or maintained by DeepSeek.
>
> 本仓库是非官方社区打包项目，与 DeepSeek 无隶属、认可、赞助或维护关系。

Fedora 44 / COPR RPM spec for **DeepSeek Harness**.

## Contents

- `deepseek-harness-bin.spec` — RPM spec for the npm distribution of `@deepseek-ai/dsh`
- Supported architectures: `x86_64`, `aarch64`

## Requirements

- Fedora 44 build environment
- COPR project with **Enable internet access during builds** enabled
- Node.js 24 packages from Fedora 44
- Native build tooling: `gcc-c++`, `make`, `cmake`, `patchelf`, `python3` (node-gyp is bundled with npm)

## Build an SRPM

```bash
mkdir -p ~/rpmbuild/{SOURCES,SPECS}
cp deepseek-harness-bin.spec ~/rpmbuild/SPECS/

curl -L -o ~/rpmbuild/SOURCES/dsh-0.2.1-rc.4.tgz \
  https://registry.npmjs.org/@deepseek-ai/dsh/-/dsh-0.2.1-rc.4.tgz

rpmbuild -bs ~/rpmbuild/SPECS/deepseek-harness-bin.spec
```

Then submit the generated SRPM to COPR:

```bash
copr-cli build <your-copr-project> \
  ~/rpmbuild/SRPMS/deepseek-harness-bin-0.2.1~rc.4-1.fc44.src.rpm
```

## Automation

The `Update spec from upstream pre-release` workflow runs daily and on manual dispatch. It fetches the latest upstream pre-release, updates the spec version, release number, and changelog, then commits the change.

## Notes

- The spec runs `npm install --global` during `%build`, so the COPR project must allow network access during builds.
- The npm tarball SHA256 matches the source referenced by the original PKGBUILD:
  `1fddead34d3c943b7a4eed1d614e14fa19925803455e28c5141645caf4b02d13`
- Native dependencies `koffi` and `node-pty` are built during the package build.

## Disclaimer

This project is provided for convenience and testing. The upstream software, trademarks, and release artifacts belong to their respective owners. Use at your own risk.
