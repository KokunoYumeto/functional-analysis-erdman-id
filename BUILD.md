# Reproducible PDF and semantic HTML builds

## PDF

For the complete integrated edition, run the guarded repository-root script:

```powershell
./qa/run_final_companion_build.ps1
```

The script requires fresh exact output targets, validates all 52 exercise
solutions, ten selected reader-work solutions, and 13 bridge units, regenerates
`source/id-ID/functional-analysis-id-complete-with-companions.tex`, freezes all
36 inputs, and performs two clean fixed-path replays. The admitted result is
the 298-page reader in `output/pdf/`; exact identities are recorded in
`provenance/FINAL_EDITION_BUILD_AND_QA_RECEIPT.md`.

The following command remains the reproducible baseline for the source-text-
only historical boundary.

Run from `source/id-ID` with a TeX distribution providing pdfLaTeX, BibTeX,
MakeIndex, Xy-pic, and `latexmk`:

```powershell
$env:SOURCE_DATE_EPOCH = '1444126743'
latexmk -C -outdir='../../qa/build-complete-source-final' 'functional-analysis-id-complete-source.tex'
latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error `
  -outdir='../../qa/build-complete-source-final' 'functional-analysis-id-complete-source.tex'
```

The admitted Windows baseline used MiKTeX 26.5, pdfTeX 1.40.29, and latexmk
4.88. Repeated clean replays in the same fixed path produced byte-identical
PDFs. The current canonical source-text-complete reader artifact and its exact
hash are recorded in `provenance/PREFACE_BUILD_AND_QA_RECEIPT.md`. The frozen
Bab 1--17, Bab 1--16,
Bab 1--15,
Bab 1--14, Bab 1--13, Bab 1--12, Bab 1--11, Bab 1--10,
Bab 1--9, Bab 1--8, Bab 1--7, Bab
1--6, Bab 1--5, Bab 1--4, Bab 1--3, Bab 1--2, and Unit 1 masters and receipts
remain available for replay of the earlier boundaries.

The complete-source master inserts `preface-id.tex` after the table of contents,
then preserves all 17 chapter includes, bibliography, and index in order. It
loads `tabularx` for the two replacement front-matter tables. The build
intentionally includes the unchanged `DIAGXY.TEX`; do not rename,
modify, or silently replace it. The wrapper excludes `TABLE.TEX`, badge art,
and uncleared quotations. Page reflow is acceptable, but mathematics, labels,
citations, references, exercises, and logical order are not.

The current wrapper also loads `cmap` and Latin Modern so that all embedded
font resources carry Unicode mappings, fixes derivative PDF dates explicitly, and
uses one high-contrast link color. The PDF remains untagged; semantic HTML or a
later tagged-PDF derivative remains the edition-level accessibility surface.

## Semantic HTML

From the repository root, with Python 3, Pandoc, `lxml`, LaTeX, and `dvisvgm`
available:

```powershell
python html/build_reader.py `
  --site-root output/html `
  --build-root qa/html-final-build `
  --route-map backend/html_routes.jsonl `
  --report qa/HTML_BUILD_RESULT.json
python html/qa_reader.py output/html backend/html_routes.jsonl `
  --output qa/HTML_READER_QA.json
python backend/generate_backend.py
python backend/validate_backend.py
```

The admitted baseline used Python 3.13.9, Pandoc 3.9.0.2, `lxml` 6.1.1,
MiKTeX-pdfTeX 4.27, and `dvisvgm` 3.6. Two clean replays and the canonical
output produced the same 105 paths, byte counts, and SHA-256 values. The site
is static and works offline: open `output/html/index.html` after building or
downloading the repository. The exact admitted identities and all-route
responsive QA are recorded in
`provenance/HTML_READER_BUILD_AND_QA_RECEIPT.md`.

### Integrated companion reader and additive backend

From the repository root:

```powershell
python html/build_companion_reader.py
python html/qa_companion_reader.py
python backend/generate_companion_backend.py
python qa/validate_companion_backend.py
```

For the deterministic HTML receipt, build two additional clean sites with the
same builder and compare all three using
`html/verify_companion_replays.py`. The admitted companion has 15 HTML
documents, 2,288 MathML elements, 294 route records, and no machine-QA or
responsive-layout findings. The additive generator preserves all admitted base
JSONLs byte-identically and writes only the separately manifested companion
overlay.
