#!/usr/bin/env python3
"""Build the deterministic Chapter 15 release with the established packager."""

from __future__ import annotations

import zipfile

import package_ch11_release as release


release.RELEASE = "2026.08.24-ch15"
release.PREFIX = f"functional-analysis-erdman-id-{release.RELEASE}"
release.PDF_NAME = "analisis-fungsional-dan-aljabar-operator-id-bab-1-15.pdf"
release.ZIP_NAME = f"{release.PREFIX}-source-backend.zip"
release.SCOPE = "in progress; Chapters 1--15 of 17"


def zip_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=(2026, 8, 24, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    info.create_system = 3
    return info


release.zip_info = zip_info


if __name__ == "__main__":
    release.main()
