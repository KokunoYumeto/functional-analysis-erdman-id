# Figshare Chapter 13 operational failure

Observed: 2026-08-24T02:05:18Z  
Scope: existing O008 Figshare concept only; no replacement item created

## Result

The Chapter 13 GitHub and Zenodo checkpoint is public and verified, but the
existing Figshare work-level item could not be updated. This is a concrete
authentication and destination-state failure, not a human-review hold and not
a reason to stop corpus production.

## Exact evidence

- Historical task identity: article `33314709`, last locally verified as
  version 4 / DOI `10.6084/m9.figshare.33314709.v4`, CC0 metadata and external
  link pointers only. Substantive release bytes remain CC BY-SA 4.0 on Zenodo.
- Anonymous `GET /v2/articles/33314709` returned HTTP 404; the public versions
  endpoint returned an empty list.
- Public project `280296` exposed one unrelated article and did not expose
  article `33314709`.
- Public collection `8668413` was at version 43 and exposed no articles.
- The historical DOI remained DataCite-findable and its old linked-file ID
  continued to redirect to the Chapter 10 Zenodo reader. This proves historical
  DOI continuity, not a current public Figshare record.
- The task's saved 128-character Figshare credential returned HTTP 403 for
  token introspection, account article, account project, and account-article
  listing endpoints with both documented authentication header forms. No
  credential material was printed, copied, logged, or persisted.
- The in-app browser had no authenticated Figshare account session; no other
  connected browser session was available.

## Safety disposition and next executable remedy

No write was attempted and no duplicate article or concept was created. When
authenticated Figshare access becomes operational, first probe the exact
account article `33314709`, its file inventory, project membership, and
collection membership. If it exists, update that same article to a reader-first
Chapter 13 link-only CC0 metadata version pointing to Zenodo record 22074101,
preserve project/collection members additively, publish, and anonymously read
back the linked PDF and metadata. If the account article is absent, do not
create a competing replacement without an explicit concept-recovery decision.

The active reader remains publicly preserved at GitHub and at Zenodo DOI
`10.5281/zenodo.22074101`; Chapter 14 production proceeds.
