#!/usr/bin/env python3
"""Build the deterministic Chapter 12 release with the established packager."""

from __future__ import annotations

import package_ch11_release as release


release.RELEASE = "2026.08.23-ch12"
release.PREFIX = f"functional-analysis-erdman-id-{release.RELEASE}"
release.PDF_NAME = "analisis-fungsional-dan-aljabar-operator-id-bab-1-12.pdf"
release.ZIP_NAME = f"{release.PREFIX}-source-backend.zip"
release.SCOPE = "in progress; Chapters 1--12 of 17"


if __name__ == "__main__":
    release.main()
