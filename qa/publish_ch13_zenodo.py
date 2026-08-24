#!/usr/bin/env python3
"""Publish the admitted Chapter 13 checkpoint in the existing Zenodo concept."""

from __future__ import annotations

from typing import Any

import publish_ch11_zenodo as release


release.EXPECTED_PREVIOUS_VERSION = "2026.08.23-ch12"
release.VERSION = "2026.08.24-ch13"
release.PDF_NAME = "analisis-fungsional-dan-aljabar-operator-id-bab-1-13.pdf"
release.ZIP_NAME = "functional-analysis-erdman-id-2026.08.24-ch13-source-backend.zip"
_base_writable_metadata = release.writable_metadata


def description(github_commit: str) -> str:
    return (
        "<p><strong>Status: edisi dalam pengerjaan, Bab 1–13 dari 17 bab.</strong> "
        "Versi ini menambahkan Bab 13, <em>Konstruksi Gelfand–Naimark–Segal</em>, "
        "kepada reader Bahasa Indonesia yang telah diverifikasi. Bab 14–17, "
        "reader HTML semantik/aksesibel, lapisan solusi O001, dan jembatan "
        "spektral-kompak/SVD masih dalam pengerjaan.</p>"
        "<p>Adaptasi dari John M. Erdman, <em>Functional Analysis and Operator "
        "Algebras: An Introduction</em>, versi 4 Oktober 2015. Karya sumber dan "
        "adaptasi ini berlisensi CC BY-SA 4.0. Perubahan mencakup terjemahan "
        "Bahasa Indonesia, build modern, navigasi, indeks, backend modular, dan "
        "koreksi sumber yang dicatat secara transparan. Tidak ada dukungan atau "
        "persetujuan tersirat dari John M. Erdman maupun Portland State "
        "University.</p>"
        "<p>Terjemahan dan penyuntingan teknis dibantu oleh "
        "<strong>OpenAI Codex gpt-5.6-sol, Ultra</strong>, atas arahan pengguna "
        "manusia. Kredit penulis sumber dan kontributor komponen tetap "
        "dipertahankan.</p>"
        "<p>PDF 183 halaman dapat ditelusuri dan dinavigasi; seluruh halaman "
        "telah dirender dan diperiksa secara visual, dan semua font tertanam "
        "memiliki pemetaan Unicode. PDF belum bertag; klaim aksesibilitas "
        "semantik tidak dibuat. Arsip sumber/backend mengikat commit publik "
        f"GitHub <code>{github_commit}</code> dan menyertakan manifest serta "
        "rekaman QA yang diperlukan untuk melanjutkan edisi.</p>"
        "<p>Mirror GitHub: "
        "<a href=\"https://github.com/KokunoYumeto/functional-analysis-erdman-id\">"
        "functional-analysis-erdman-id</a>.</p>"
    )


def writable_metadata(existing: dict[str, Any], github_commit: str) -> dict[str, Any]:
    metadata = _base_writable_metadata(existing, github_commit)
    metadata["publication_date"] = "2026-08-24"
    return metadata


release.description = description
release.writable_metadata = writable_metadata


if __name__ == "__main__":
    release.main()
