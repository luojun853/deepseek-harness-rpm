#!/usr/bin/env python3
"""Update the RPM spec to an upstream npm pre-release.

This script is intentionally self-contained so the GitHub Actions workflow can
run without installing a separate Python package.
"""

from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone
from pathlib import Path

PACKAGER = "github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com>"


def npm_to_rpm_version(version: str) -> str:
    return version.replace("-", "~", 1)


def update_spec(spec_path: Path, npm_version: str) -> str:
    rpm_version = npm_to_rpm_version(npm_version)
    with spec_path.open("r", encoding="utf-8", newline="") as f:
        text = f.read()

    text, npm_count = re.subn(
        r"(?m)^%global\s+npmver\s+.*$",
        f"%global npmver   {npm_version}",
        text,
        count=1,
    )
    text, version_count = re.subn(
        r"(?m)^Version:\s+.*$",
        f"Version:        {rpm_version}",
        text,
        count=1,
    )
    text, release_count = re.subn(
        r"(?m)^Release:\s+.*$",
        "Release:        1%{?dist}",
        text,
        count=1,
    )
    if not (npm_count and version_count and release_count):
        raise RuntimeError("spec is missing npmver, Version, or Release fields")

    today = datetime.now(timezone.utc).strftime("%a %b %d %Y")
    entry = (
        f"* {today} {PACKAGER} - {rpm_version}-1\n"
        f"- Update to upstream pre-release {npm_version}.\n"
    )
    marker = "%changelog\n"
    if marker not in text:
        raise RuntimeError("spec has no %changelog section")

    # Avoid inserting a duplicate entry if the workflow is re-run.
    if f"- Update to upstream pre-release {npm_version}." not in text:
        text = text.replace(marker, marker + entry + "\n", 1)

    with spec_path.open("w", encoding="utf-8", newline="") as f:
        f.write(text)
    return rpm_version


def update_readme(readme_path: Path, rpm_version: str) -> None:
    if not readme_path.exists():
        return
    with readme_path.open("r", encoding="utf-8", newline="") as f:
        text = f.read()
    text, count = re.subn(
        r"(?m)^- Package version: `[^`]+`$",
        f"- Package version: `{rpm_version}`",
        text,
        count=1,
    )
    if count:
        with readme_path.open("w", encoding="utf-8", newline="") as f:
            f.write(text)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument("--readme", type=Path)
    parser.add_argument("--version", required=True)
    args = parser.parse_args()

    if "-" not in args.version:
        raise SystemExit(f"not a pre-release version: {args.version}")

    rpm_version = update_spec(args.spec, args.version)
    if args.readme:
        update_readme(args.readme, rpm_version)
    print(f"updated to npm={args.version} rpm={rpm_version}")


if __name__ == "__main__":
    main()
