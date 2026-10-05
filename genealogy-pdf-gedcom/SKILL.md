---
name: genealogy-pdf-gedcom
description: Convert scanned genealogy PDFs into traceable Markdown and GEDCOM files, especially Norwegian lineage registers with custom numbering, ancestor prefixes, spouse lines, source codes, and OCR ambiguity.
---

# Genealogy PDF to GEDCOM

Use this skill when a user asks to inspect a scanned genealogy PDF, convert it to Markdown, interpret its register structure, or create a GEDCOM from the documented people and relationships.

## Workflow

1. Identify the exact PDF and inspect its page count, whether it has an extractable text layer, and whether it is image-based.
2. If the PDF is scanned, use local rendering plus OCR. Prefer Poppler (`pdftoppm`) and Tesseract with Norwegian plus English language data when available. Keep one Markdown page heading per source page.
3. Read the introductory/instruction pages before interpreting rows. Extract the register's numbering rules, date conventions, spouse markers, source-code legend, and any caveats about incomplete or approximate data.
4. Separate the main structured register pages from alphabetical indexes, diagrams, and prose. State clearly which pages contribute genealogical records to the GEDCOM.
5. Model each numbered register person with a stable GEDCOM ID derived from the complete lineage number, not only the final four-digit person number. Preserve the original lineage number in a NOTE.
6. Model unnumbered spouse/partner rows as separate individuals when their identity is readable. Link them to the numbered person's family; do not invent parentage for them.
7. Infer parent-child links only from explicit lineage-number structure. If the source does not provide a parent link, leave `FAMC` absent. Do not infer a place, date, surname, or relationship from surrounding context alone.
8. Convert dates conservatively: exact `dd.mm.yyyy` to GEDCOM `dd MON yyyy`; year-only values to year-only dates; `ca.` to `ABT`. Preserve uncertain, missing, or source-qualified values in notes.
9. Preserve source traceability with page notes and, when OCR is imperfect, the raw register line. Avoid silently correcting names; lightly normalized display names are acceptable only when the original line is retained.
10. Validate the generated GEDCOM: one `HEAD` and `TRLR`, unique record IDs, every `FAMC`/`HUSB`/`WIFE`/`CHIL` reference resolves, and no generated placeholder is presented as a sourced person.

## Output expectations

- Create a Markdown transcription with a short structure-interpretation section and page headings.
- Create a GEDCOM 5.5.1 file with source-derived notes and explicit import limitations.
- Report record counts, source-page scope, validation results, and any OCR or relationship limitations.
- Treat OCR-derived GEDCOM as a reviewable import, not as independently verified genealogy.

For the Norwegian register conventions used in the Follese material, read [references/norwegian-register-structure.md](references/norwegian-register-structure.md).
