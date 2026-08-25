#!/usr/bin/env python3
"""Anonymously verify the published O008 GitHub Pages reader byte-for-byte.

This verifier intentionally uses only Python's standard library and sends no
credentials.  It binds the public Pages deployment to an exact ``main``
commit/tree, successful workflow run and GitHub deployment, a tracked public
manifest, every byte named by that manifest, and independently captured
desktop/mobile browser evidence.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import time
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urljoin, urlsplit, urlunsplit
from urllib.request import HTTPHandler, HTTPSHandler, ProxyHandler, Request, build_opener


ROOT = Path(__file__).resolve().parents[1]
TRACKED_MANIFEST = ROOT / "qa" / "GITHUB_PAGES_PUBLIC_MANIFEST.csv"
TRACKED_MANIFEST_PATH = "qa/GITHUB_PAGES_PUBLIC_MANIFEST.csv"
MANIFEST_NAME = "PAGES_DEPLOYMENT_MANIFEST.csv"
MANIFEST_FIELDS = ["public_path", "role", "source_path", "bytes", "sha256"]
REQUIRED_PUBLIC_PATHS = (
    "output/html/index.html",
    "output/html-companion/index.html",
    "output/html-companion/jembatan-spektral-kompak-svd/index.html",
)
HEX_OBJECT_ID = re.compile(r"[0-9a-f]{40}")
HEX_SHA256 = re.compile(r"[0-9a-f]{64}")


class VerificationError(RuntimeError):
    """Raised when public evidence does not match the declared deployment."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_root(value: str) -> str:
    parts = urlsplit(value.strip())
    if (
        parts.scheme != "https"
        or not parts.netloc
        or parts.username is not None
        or parts.password is not None
        or parts.query
        or parts.fragment
    ):
        raise VerificationError("--pages-root must be a credential-free HTTPS URL")
    path = parts.path.rstrip("/") + "/"
    return urlunsplit((parts.scheme, parts.netloc.lower(), path, "", ""))


def comparable_url(value: str) -> str:
    parts = urlsplit(value.strip())
    if parts.scheme != "https" or not parts.netloc:
        return ""
    path = parts.path.rstrip("/") + "/"
    return urlunsplit((parts.scheme, parts.netloc.lower(), path, "", ""))


def safe_relative_path(value: str, label: str) -> str:
    if not value or "\\" in value or value.startswith("/"):
        raise VerificationError(f"invalid {label}: {value!r}")
    if any(character in value for character in ("?", "#", "\x00")):
        raise VerificationError(f"invalid {label}: {value!r}")
    path = PurePosixPath(value)
    if any(part in {"", ".", ".."} for part in path.parts):
        raise VerificationError(f"unsafe {label}: {value!r}")
    return path.as_posix()


class AnonymousHTTP:
    """Small credential-free HTTP client with bounded propagation retries."""

    def __init__(self) -> None:
        self.opener = build_opener(ProxyHandler({}), HTTPHandler(), HTTPSHandler())

    def get(
        self,
        url: str,
        *,
        accept: str = "*/*",
        attempts: int = 1,
        retry_statuses: frozenset[int] = frozenset({404, 429, 500, 502, 503, 504}),
    ) -> tuple[int, bytes, dict[str, str], str]:
        last: tuple[int, bytes, dict[str, str], str] | None = None
        for attempt in range(attempts):
            request = Request(
                url,
                headers={
                    "Accept": accept,
                    "Cache-Control": "no-cache",
                    "User-Agent": "O008-GitHub-Pages-public-verifier/1.0",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
                method="GET",
            )
            try:
                with self.opener.open(request, timeout=90) as response:
                    result = (
                        int(response.status),
                        response.read(),
                        {key.lower(): value for key, value in response.headers.items()},
                        response.geturl(),
                    )
            except HTTPError as error:
                result = (
                    int(error.code),
                    error.read(),
                    {key.lower(): value for key, value in error.headers.items()},
                    error.geturl(),
                )
            except (TimeoutError, URLError) as error:
                if attempt + 1 == attempts:
                    raise VerificationError(f"anonymous HTTP read failed: {url}: {error}") from error
                time.sleep(2)
                continue
            last = result
            if result[0] not in retry_statuses or attempt + 1 == attempts:
                return result
            time.sleep(2)
        if last is None:  # pragma: no cover - defensive invariant
            raise VerificationError(f"anonymous HTTP read produced no response: {url}")
        return last

    def json_object(
        self, url: str, *, allowed_statuses: frozenset[int] = frozenset({200})
    ) -> tuple[int, dict[str, Any] | None, dict[str, str]]:
        status, body, headers, _ = self.get(
            url, accept="application/vnd.github+json", attempts=3
        )
        if status not in allowed_statuses:
            raise VerificationError(f"anonymous GitHub API returned HTTP {status}: {url}")
        if status != 200:
            return status, None, headers
        try:
            payload = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise VerificationError(f"GitHub API response is not UTF-8 JSON: {url}") from error
        if not isinstance(payload, dict):
            raise VerificationError(f"GitHub API response is not an object: {url}")
        return status, payload, headers


def raw_url(repo: str, commit: str, path: str) -> str:
    return (
        f"https://raw.githubusercontent.com/{repo}/{commit}/"
        f"{quote(path, safe='/')}"
    )


def api_url(repo: str, suffix: str) -> str:
    return f"https://api.github.com/repos/{repo}/{suffix.lstrip('/')}"


def require_dict(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise VerificationError(f"{label} must be an object")
    return value


def parse_manifest(data: bytes) -> list[dict[str, Any]]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise VerificationError("Pages deployment manifest is not UTF-8") from error
    reader = csv.DictReader(io.StringIO(text, newline=""))
    if reader.fieldnames != MANIFEST_FIELDS:
        raise VerificationError(
            f"manifest schema differs: expected {MANIFEST_FIELDS}, got {reader.fieldnames}"
        )
    records: list[dict[str, Any]] = []
    seen_public: set[str] = set()
    seen_source: set[str] = set()
    for line_number, row in enumerate(reader, start=2):
        if None in row or any(value is None for value in row.values()):
            raise VerificationError(f"malformed manifest row {line_number}")
        public_path = safe_relative_path(row["public_path"].strip(), "public_path")
        source_path = safe_relative_path(row["source_path"].strip(), "source_path")
        role = row["role"].strip()
        byte_text = row["bytes"].strip()
        digest = row["sha256"].strip()
        if not role:
            raise VerificationError(f"empty role in manifest row {line_number}")
        if not byte_text.isascii() or not byte_text.isdecimal():
            raise VerificationError(f"invalid byte count in manifest row {line_number}")
        byte_count = int(byte_text)
        if str(byte_count) != byte_text:
            raise VerificationError(f"non-canonical byte count in manifest row {line_number}")
        if not HEX_SHA256.fullmatch(digest):
            raise VerificationError(f"invalid SHA-256 in manifest row {line_number}")
        if public_path in seen_public:
            raise VerificationError(f"duplicate public_path in manifest: {public_path}")
        if source_path in seen_source:
            raise VerificationError(f"duplicate source_path in manifest: {source_path}")
        seen_public.add(public_path)
        seen_source.add(source_path)
        records.append(
            {
                "public_path": public_path,
                "role": role,
                "source_path": source_path,
                "bytes": byte_count,
                "sha256": digest,
            }
        )
    if not records:
        raise VerificationError("Pages deployment manifest has no file records")
    if [record["public_path"] for record in records] != sorted(seen_public):
        raise VerificationError("manifest rows are not sorted by public_path")
    return records


def validate_browser_evidence(
    path: Path, pages_root: str, required_urls: list[str]
) -> dict[str, Any]:
    data = path.read_bytes()
    try:
        payload = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise VerificationError("browser evidence is not valid UTF-8 JSON") from error
    evidence = require_dict(payload, "browser evidence")
    if not isinstance(evidence.get("schema"), str) or not evidence["schema"].strip():
        raise VerificationError("browser evidence has no schema identifier")
    if evidence.get("status") != "pass":
        raise VerificationError("browser evidence status is not pass")
    if comparable_url(str(evidence.get("base_url", ""))) != pages_root:
        raise VerificationError("browser evidence base_url differs from --pages-root")
    if evidence.get("console_errors") != [] or evidence.get("failed_requests") != []:
        raise VerificationError("browser evidence contains console errors or failed requests")

    viewports = evidence.get("viewports")
    if not isinstance(viewports, list) or not viewports:
        raise VerificationError("browser evidence viewports must be a nonempty list")
    has_desktop = False
    has_mobile = False
    viewport_summary: list[dict[str, Any]] = []
    for index, raw_viewport in enumerate(viewports):
        viewport = require_dict(raw_viewport, f"browser viewport {index}")
        if viewport.get("status") != "pass":
            raise VerificationError(f"browser viewport {index} did not pass")
        label = " ".join(
            str(viewport.get(key, "")) for key in ("name", "kind", "label")
        ).lower()
        width = viewport.get("width")
        if isinstance(width, bool):
            width = None
        if isinstance(width, str) and width.isdecimal():
            width = int(width)
        if "desktop" in label or (isinstance(width, int) and width >= 1000):
            has_desktop = True
        if "mobile" in label or (isinstance(width, int) and 240 <= width <= 800):
            has_mobile = True
        viewport_summary.append(
            {
                key: viewport[key]
                for key in ("name", "kind", "label", "width", "height", "status")
                if key in viewport
            }
        )
    if not has_desktop or not has_mobile:
        raise VerificationError("browser evidence lacks passing desktop and mobile viewports")

    inspected = evidence.get("inspected_urls")
    if not isinstance(inspected, list) or not all(isinstance(item, str) for item in inspected):
        raise VerificationError("browser evidence inspected_urls must be a list of URLs")
    inspected_set = {item.rstrip("/") for item in inspected}
    missing = [url for url in required_urls if url.rstrip("/") not in inspected_set]
    if missing:
        raise VerificationError(f"browser evidence did not inspect required URLs: {missing}")
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": len(data),
        "sha256": sha256(data),
        "schema": evidence["schema"],
        "status": "pass",
        "base_url": pages_root,
        "viewports": viewport_summary,
        "desktop_passed": True,
        "mobile_passed": True,
        "console_error_count": 0,
        "failed_request_count": 0,
        "inspected_urls": sorted(inspected),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Anonymously verify the deployed O008 GitHub Pages reader."
    )
    parser.add_argument("--repo", default="KokunoYumeto/functional-analysis-erdman-id")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--commit", required=True)
    parser.add_argument("--tree", required=True)
    parser.add_argument("--pages-root", required=True)
    parser.add_argument("--workflow-run-id", required=True, type=int)
    parser.add_argument("--deployment-id", required=True, type=int)
    parser.add_argument("--browser-evidence", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()

    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", args.repo):
        raise SystemExit("--repo must be an exact owner/repository name")
    if not re.fullmatch(r"[A-Za-z0-9._/-]+", args.branch) or ".." in args.branch:
        raise SystemExit("--branch is invalid")
    commit = args.commit.lower()
    tree = args.tree.lower()
    if not HEX_OBJECT_ID.fullmatch(commit) or args.commit != commit:
        raise SystemExit("--commit must be an exact lowercase 40-character object ID")
    if not HEX_OBJECT_ID.fullmatch(tree) or args.tree != tree:
        raise SystemExit("--tree must be an exact lowercase 40-character object ID")
    if args.workflow_run_id <= 0 or args.deployment_id <= 0:
        raise SystemExit("workflow run and deployment IDs must be positive integers")
    pages_root = canonical_root(args.pages_root)
    report_path = args.report.resolve()
    browser_path = args.browser_evidence.resolve()
    if report_path == Path(__file__).resolve():
        raise SystemExit("--report may not overwrite this verifier")
    try:
        report_path.relative_to(ROOT)
        browser_path.relative_to(ROOT)
    except ValueError as error:
        raise SystemExit(
            "--report and --browser-evidence must resolve inside this repository"
        ) from error
    if not TRACKED_MANIFEST.is_file():
        raise SystemExit(f"tracked manifest is missing: {TRACKED_MANIFEST_PATH}")
    if not browser_path.is_file():
        raise SystemExit("the supplied browser-evidence file is missing")

    client = AnonymousHTTP()
    _, repository, _ = client.json_object(client_url := api_url(args.repo, ""))
    assert repository is not None
    if repository.get("full_name") != args.repo:
        raise VerificationError("repository API identity differs from --repo")
    if repository.get("default_branch") != args.branch:
        raise VerificationError("repository default branch differs from --branch")
    if repository.get("has_pages") is not True:
        raise VerificationError("repository API does not report has_pages=true")
    homepage = str(repository.get("homepage") or "")
    if comparable_url(homepage) != pages_root:
        raise VerificationError("repository homepage does not lead to the Pages root")

    _, ref, _ = client.json_object(
        api_url(args.repo, f"git/ref/heads/{quote(args.branch, safe='/')}")
    )
    assert ref is not None
    ref_object = require_dict(ref.get("object"), "branch ref object")
    if ref_object.get("type") != "commit" or ref_object.get("sha") != commit:
        raise VerificationError("public branch head differs from --commit")
    _, commit_payload, _ = client.json_object(api_url(args.repo, f"git/commits/{commit}"))
    assert commit_payload is not None
    commit_tree = require_dict(commit_payload.get("tree"), "commit tree")
    if commit_payload.get("sha") != commit or commit_tree.get("sha") != tree:
        raise VerificationError("public commit/tree differs from supplied identities")

    pages_status, pages, _ = client.json_object(
        api_url(args.repo, "pages"), allowed_statuses=frozenset({200, 404})
    )
    if pages_status == 200:
        assert pages is not None
        pages_html_url = canonical_root(str(pages.get("html_url", "")))
        if pages_html_url != pages_root:
            raise VerificationError("Pages API html_url differs from --pages-root")
        build_type = pages.get("build_type")
        if build_type != "workflow":
            raise VerificationError(f"Pages build_type is not workflow: {build_type!r}")
        pages_evidence: dict[str, Any] = {
            "anonymous_api_visible": True,
            "http_status": 200,
            "html_url": pages_html_url,
            "build_type": build_type,
            "status": pages.get("status"),
            "protected_domain_state": pages.get("protected_domain_state"),
        }
    else:
        pages_evidence = {
            "anonymous_api_visible": False,
            "http_status": 404,
            "note": "Pages settings are not anonymously exposed; live bytes remain authoritative.",
        }

    _, workflow, _ = client.json_object(
        api_url(args.repo, f"actions/runs/{args.workflow_run_id}")
    )
    assert workflow is not None
    workflow_repository = require_dict(workflow.get("repository"), "workflow repository")
    if (
        workflow.get("id") != args.workflow_run_id
        or workflow_repository.get("full_name") != args.repo
        or workflow.get("head_branch") != args.branch
        or workflow.get("head_sha") != commit
        or workflow.get("path") != ".github/workflows/pages.yml"
        or workflow.get("event") not in {"push", "workflow_dispatch"}
        or workflow.get("status") != "completed"
        or workflow.get("conclusion") != "success"
    ):
        raise VerificationError("workflow run identity or success state differs")

    _, deployment, _ = client.json_object(
        api_url(args.repo, f"deployments/{args.deployment_id}")
    )
    assert deployment is not None
    if (
        deployment.get("id") != args.deployment_id
        or deployment.get("sha") != commit
        or deployment.get("ref") != args.branch
        or deployment.get("environment") != "github-pages"
    ):
        raise VerificationError("GitHub Pages deployment identity differs")
    status_code, status_body, _, _ = client.get(
        api_url(args.repo, f"deployments/{args.deployment_id}/statuses"),
        accept="application/vnd.github+json",
        attempts=3,
    )
    if status_code != 200:
        raise VerificationError(f"deployment statuses API returned HTTP {status_code}")
    try:
        deployment_statuses = json.loads(status_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise VerificationError("deployment statuses response is not UTF-8 JSON") from error
    if not isinstance(deployment_statuses, list) or not deployment_statuses:
        raise VerificationError("deployment has no public status records")
    if not all(isinstance(item, dict) for item in deployment_statuses):
        raise VerificationError("deployment status response contains a non-object")
    newest_status = max(
        deployment_statuses,
        key=lambda item: (str(item.get("created_at", "")), int(item.get("id", 0))),
    )
    if newest_status.get("state") != "success":
        raise VerificationError("latest deployment status is not success")
    environment_url = str(newest_status.get("environment_url") or "")
    if comparable_url(environment_url) != pages_root:
        raise VerificationError("deployment environment_url differs from --pages-root")

    local_manifest = TRACKED_MANIFEST.read_bytes()
    tracked_status, tracked_public, _, _ = client.get(
        raw_url(args.repo, commit, TRACKED_MANIFEST_PATH), attempts=3
    )
    if tracked_status != 200 or tracked_public != local_manifest:
        raise VerificationError("tracked manifest differs from the exact public commit")
    manifest_url = urljoin(pages_root, MANIFEST_NAME)
    manifest_status, deployed_manifest, manifest_headers, manifest_final_url = client.get(
        manifest_url, attempts=8
    )
    if manifest_status != 200:
        raise VerificationError(f"public Pages manifest returned HTTP {manifest_status}")
    if deployed_manifest != local_manifest:
        raise VerificationError(
            "public PAGES_DEPLOYMENT_MANIFEST.csv differs byte-for-byte from the tracked manifest"
        )
    records = parse_manifest(local_manifest)

    public_files: list[dict[str, Any]] = []
    total_bytes = 0
    for record in records:
        public_path = str(record["public_path"])
        source_path = str(record["source_path"])
        expected_bytes = int(record["bytes"])
        expected_sha256 = str(record["sha256"])
        source_status, source_bytes, _, _ = client.get(
            raw_url(args.repo, commit, source_path), attempts=3
        )
        if source_status != 200:
            raise VerificationError(f"tracked source returned HTTP {source_status}: {source_path}")
        public_url = urljoin(pages_root, quote(public_path, safe="/"))
        public_status, public_bytes, headers, final_url = client.get(
            public_url, attempts=8
        )
        if public_status != 200:
            raise VerificationError(f"public file returned HTTP {public_status}: {public_path}")
        if (
            public_bytes != source_bytes
            or len(public_bytes) != expected_bytes
            or sha256(public_bytes) != expected_sha256
        ):
            raise VerificationError(f"public byte/SHA-256 mismatch: {public_path}")
        total_bytes += len(public_bytes)
        public_files.append(
            {
                **record,
                "url": public_url,
                "final_url": final_url,
                "http_status": 200,
                "content_type": headers.get("content-type"),
                "matches_tracked_source": True,
            }
        )

    records_by_path = {str(record["public_path"]): record for record in records}
    required_urls = [pages_root] + [
        urljoin(pages_root, quote(path, safe="/")) for path in REQUIRED_PUBLIC_PATHS
    ]
    required_results: list[dict[str, Any]] = []
    for index, url in enumerate(required_urls):
        status, body, headers, final_url = client.get(url, attempts=8)
        if status != 200:
            raise VerificationError(f"required Pages URL returned HTTP {status}: {url}")
        manifest_path = "index.html" if index == 0 else REQUIRED_PUBLIC_PATHS[index - 1]
        record = records_by_path.get(manifest_path)
        if record is None:
            raise VerificationError(f"required URL is absent from the manifest: {manifest_path}")
        if len(body) != record["bytes"] or sha256(body) != record["sha256"]:
            raise VerificationError(f"required URL bytes differ from the manifest: {url}")
        required_results.append(
            {
                "url": url,
                "final_url": final_url,
                "http_status": 200,
                "bytes": len(body),
                "sha256": sha256(body),
                "content_type": headers.get("content-type"),
            }
        )

    browser_evidence = validate_browser_evidence(browser_path, pages_root, required_urls)

    result = {
        "schema_version": "1.0.0",
        "receipt_id": "FAOA-2015-ID-GITHUB-PAGES-PUBLICATION",
        "verification_event_utc": newest_status.get("updated_at")
        or newest_status.get("created_at")
        or workflow.get("updated_at"),
        "repository": {
            "api_url": client_url,
            "html_url": repository.get("html_url"),
            "full_name": args.repo,
            "branch": args.branch,
            "commit": commit,
            "tree": tree,
            "remote_head_matches": True,
            "remote_tree_matches": True,
            "has_pages": True,
            "homepage": homepage,
            "homepage_matches_pages_root": True,
        },
        "pages": {"root": pages_root, "api": pages_evidence},
        "workflow_run": {
            key: workflow.get(key)
            for key in (
                "id",
                "workflow_id",
                "run_number",
                "run_attempt",
                "event",
                "status",
                "conclusion",
                "head_branch",
                "head_sha",
                "created_at",
                "updated_at",
                "html_url",
            )
        },
        "deployment": {
            "id": deployment.get("id"),
            "ref": deployment.get("ref"),
            "sha": deployment.get("sha"),
            "task": deployment.get("task"),
            "environment": deployment.get("environment"),
            "created_at": deployment.get("created_at"),
            "updated_at": deployment.get("updated_at"),
            "latest_status_id": newest_status.get("id"),
            "latest_status": newest_status.get("state"),
            "latest_status_created_at": newest_status.get("created_at"),
            "latest_status_updated_at": newest_status.get("updated_at"),
            "environment_url": environment_url,
        },
        "manifest": {
            "tracked_path": TRACKED_MANIFEST_PATH,
            "public_url": manifest_url,
            "final_url": manifest_final_url,
            "http_status": 200,
            "content_type": manifest_headers.get("content-type"),
            "bytes": len(local_manifest),
            "sha256": sha256(local_manifest),
            "row_count": len(records),
            "matches_exact_public_commit": True,
            "matches_public_pages_bytes": True,
        },
        "public_file_readback": {
            "file_count": len(public_files),
            "total_bytes": total_bytes,
            "all_files_match_manifest_and_tracked_sources": True,
            "files": public_files,
        },
        "required_url_readback": required_results,
        "browser_evidence": browser_evidence,
        "authentication_used": False,
        "credential_material_recorded": False,
        "result": "pass",
    }
    serialized = json.dumps(
        result, ensure_ascii=False, indent=2, sort_keys=True
    ).encode("utf-8") + b"\n"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_bytes(serialized)
    print(serialized.decode("utf-8"), end="")


if __name__ == "__main__":
    main()
