# Reproducible Unit 1 build

Run from `source/id-ID` with a TeX distribution providing pdfLaTeX, BibTeX,
MakeIndex, Xy-pic, and `latexmk`:

```powershell
$env:SOURCE_DATE_EPOCH = '1444126743'
latexmk -C -outdir='../../qa/build-unit1' 'functional-analysis-id-unit1.tex'
latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error `
  -outdir='../../qa/build-unit1' 'functional-analysis-id-unit1.tex'
```

The admitted Windows baseline used MiKTeX 26.5, pdfTeX 1.40.29, and latexmk
4.88. Two clean fixed-path runs produced byte-identical PDFs. The canonical
reader artifact and its exact hash are recorded in
`provenance/CH01_BUILD_AND_QA_RECEIPT.md`.

The build intentionally includes the unchanged `DIAGXY.TEX`; do not rename,
modify, or silently replace it. The wrapper excludes `TABLE.TEX`, badge art,
and uncleared quotations. Page reflow is acceptable, but mathematics, labels,
citations, references, exercises, and logical order are not.
