# Reproducible cumulative build

Run from `source/id-ID` with a TeX distribution providing pdfLaTeX, BibTeX,
MakeIndex, Xy-pic, and `latexmk`:

```powershell
$env:SOURCE_DATE_EPOCH = '1444126743'
latexmk -C -outdir='../../qa/build-through-ch05' 'functional-analysis-id-through-ch05.tex'
latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error `
  -outdir='../../qa/build-through-ch05' 'functional-analysis-id-through-ch05.tex'
```

The admitted Windows baseline used MiKTeX 26.5, pdfTeX 1.40.29, and latexmk
4.88. Repeated clean fixed-path runs produced byte-identical PDFs. The current
canonical Bab 1--5 reader artifact and its exact hash are recorded in
`provenance/CH05_BUILD_AND_QA_RECEIPT.md`. The frozen Bab 1--4, Bab 1--3, Bab 1--2, and Unit 1
masters and receipts remain available for replay of the earlier boundaries.

The build intentionally includes the unchanged `DIAGXY.TEX`; do not rename,
modify, or silently replace it. The wrapper excludes `TABLE.TEX`, badge art,
and uncleared quotations. Page reflow is acceptable, but mathematics, labels,
citations, references, exercises, and logical order are not.

The current wrapper also loads `cmap` and Latin Modern so that 38 of its 40
font resources carry Unicode mappings, fixes derivative PDF dates explicitly,
and uses one high-contrast link color. The two remaining non-Unicode fonts are
the legacy XY-pic arrow resources; semantic HTML remains the edition-level
accessibility surface.
