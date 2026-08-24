# Task-local cleanup receipt — 2026-08-24

Scope: O008 Functional Analysis only. The cleanup inspected only the two exact
Chapter 16 preflight build trees already known to this lane. No workspace scan,
repository-wide scan, credential access, or other task's files were involved.

## Verified archives and deleted originals

1. The superseded initial preflight tree at
   `qa/build-through-ch16-preflight/` was archived as
   `old stuff/o008-functional-analysis-ch16-obsolete-preflight-20260824-072228.zip`
   in the workspace's external archive directory.
   The archive contains 32 entries representing 3,231,984 expanded bytes; its
   ZIP size is 1,657,700 bytes and its SHA-256 is
   `dc19a332fd8e1a9a7916541e8cfe14c1537732b57e836ead681315cb33ae32c5`.
   Entry inventory, entry sizes, entry hashes, archive reopen, and full stream
   reads passed before the exact loose tree was deleted.

2. The later superseded final-preflight tree, recreated at the same exact path
   `qa/build-through-ch16-preflight/`, was archived as
   `old stuff/o008-functional-analysis-ch16-superseded-final-preflight-20260824-074252.zip`
   in the workspace's external archive directory.
   The archive contains 30 entries representing 3,026,164 expanded bytes; its
   ZIP size is 1,631,070 bytes and its SHA-256 is
   `190ce8cb30a36f269e2f07f184ae7766b81d5f764fa00f051940cb4cd7be114d`.
   Entry inventory, entry sizes, entry hashes, archive reopen, and full stream
   reads passed before the exact loose tree was deleted.

Post-cleanup verification on 2026-08-24 reopened and fully streamed both ZIPs,
reconfirmed their entry counts, expanded sizes, ZIP byte counts, and SHA-256
hashes, and confirmed that `qa/build-through-ch16-preflight/` is absent.

## Deliberately retained

Canonical upstream and Indonesian sources, the final Chapter 16 build and
all-page render evidence, admission and publication receipts, backend records,
release payloads, public reader PDFs, durable controls, authority witnesses,
and Chapter 17 production inputs were retained because they remain canonical,
evidentiary, reusable, or required for continuation. No uncertain or shared
material was archived or deleted.

## Preface preflight follow-up

After preface reflow produced a corrected 238-page layout, the superseded
initial preface build and render became unambiguously disposable. The exact
trees `qa/build-complete-source-preflight/` (31 files / 3,021,225 bytes) and
`tmp/pdfs/preface-preflight-render/` (14 files / 2,484,976 bytes) were archived
as `old stuff/o008-functional-analysis-preface-obsolete-initial-preflight-20260824-100739.zip`.
The ZIP contains 45 entries representing 5,506,201 expanded bytes; its size is
4,068,492 bytes and its SHA-256 is
`bd965b3c56d769f991bf08ae6a7349620f65add2fe1bf87f9212ee92104875b8`.
Archive reopen, entry-name equality, entry sizes, entry SHA-256 hashes, and full
stream reads all passed before those two exact loose trees were deleted. Both
loose paths are absent.

The corrected `qa/build-complete-source-layout2/` build and
`tmp/pdfs/preface-layout2-render/` render were deliberately retained, along
with every translation fragment, source ledger, checker, and active master,
because they remain current evidence or production inputs.

## Source-text admission cleanup

After the source-text-complete final build, all-page render, PDF audit, and
admission receipt passed, the corrected layout-2 preflight witnesses were
superseded by the retained final evidence and became unambiguously disposable.
The exact trees `qa/build-complete-source-layout2/` (31 files / 3,018,651
bytes) and `tmp/pdfs/preface-layout2-render/` (2 files / 778,454 bytes) were
archived as
`old stuff/o008-functional-analysis-superseded-preface-layout2-build-render-20260824-141834.zip`.
The ZIP contains 33 entries representing 3,797,105 expanded bytes; its size is
2,484,208 bytes and its SHA-256 is
`3b57b2337a9758427a66c7c2218a8d8d26d99f83756b8094167f9f6bb185866b`.
Entry-name equality, uncompressed sizes, per-entry SHA-256 hashes, archive
reopen, and complete stream reads passed before the two exact loose trees were
deleted. Both loose paths are absent. The retained final build and render are
`qa/build-complete-source-final/` and `qa/render-complete-source-final/`.

At the start of this continuation, the designated `old stuff/` directory and
the three ZIPs recorded in the two earlier sections were no longer present,
although their exact loose originals remained absent. This receipt does not
speculate about that external-state change and does not claim those earlier
archives are currently recoverable. The directory was recreated for the new
verified archive above; no current, reusable, uncertain, shared, canonical,
evidentiary, credential-bearing, or cross-task material was moved or deleted.

The subsequent narrow publication inventory exposed one further superseded
preface build tree plus its two detached console logs. The exact targets
`qa/build-complete-source-preface-c014/` (31 files / 3,020,101 bytes),
`qa/build-complete-source-layout2-console.txt` (295,488 bytes), and
`qa/build-complete-source-preface-c014-console.txt` (296,781 bytes) were
archived as
`old stuff/o008-functional-analysis-obsolete-preface-c014-build-consoles-20260824-142245.zip`.
The ZIP contains 33 entries representing 3,612,370 expanded bytes; its size is
1,807,845 bytes and its SHA-256 is
`f7f603056ee99cc35f7bab9df9dc2d9e870a5b852592d17003411dbce638f1bf`.
Entry names, uncompressed sizes, per-entry SHA-256 hashes, archive reopen, and
full stream reads passed before the three exact loose targets were deleted;
all three are absent. This did not alter the retained final build or render.
