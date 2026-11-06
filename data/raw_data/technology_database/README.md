# Technology database: source extractions

This folder is layer 1 of the EMRG industrial technology database: what each published
source reports about industrial technologies (costs, energy use, efficiencies, emissions,
lifetimes, and sizes), extracted as printed into long CSV files, with the manifest that
says where every figure comes from. It is deposited on FRDR as it is, and the build of the
database reads it from `data/raw_data/technology_database/` in the technology-database
repository (https://github.com/brad-griffin/technology-database) or in the CIMS
repository (https://github.com/EMRG-SFU/cims).

The source documents themselves are not part of this deposit. The manifest records each
one: its citation, DOI or URL, the date it was obtained, and its licence.

## What is here

| File or folder | What it holds |
| - | - |
| `source-details_sources.csv` | One row per source: `source_id`, author, institution, title, a description of what was extracted and how, year, `licence_type` (the licence or copyright terms the document prints, as recorded when it was extracted), update schedule, and download instructions. |
| `source-details_files.csv` | One row per file: the source document and every extraction file made from it. `file_path` is the publisher folder (the same in this deposit and in the local `primary-sources/` folder of documents), `file_on_disk` the file name, `csv_data_extract` the extraction a document feeds, and `file_source`, `doi`, and `date_accessed` where the file came from. |
| `source-details_reference.csv` | Sources behind conversion factors, prices, and currency tables, with what each one is used for. |
| `background-register.csv` | Documents read that yielded no usable figures, and why. Their `_meta.csv` files are in `background-no-data-extracted/`. |
| `to-get.csv`, `unavailable.csv` | Documents still to obtain, and those that could not be obtained, with the reason and any substitute. |
| `extraction-vocabulary.csv` | The controlled terms the extraction files use. |
| `gov-can/`, `gov-dk/`, `gov-eu/`, `gov-nl/`, `gov-nz/`, `gov-uk/`, `gov-usa/`, `iea/`, `other-reports/`, `peer-reviewed/` | The extractions, by publisher. |

## The extraction files

Each file is named `author_year_slug[_source]`, with `-` joining words within a part and
`_` separating the parts; the source document has the same stem. One source can have
several files:

| Suffix | What it holds |
| - | - |
| (none) | The figures, one row per technology, parameter, and value, with the unit, the year and currency of costs, and the page or table they came from. |
| `_meta` | The citation, licence, and extraction notes. |
| `_nodes` | The sector, end use, and service unit of each technology the source describes. |
| `_flows` | Material and energy inputs and outputs per unit of product. |
| `_constraints` | Market shares and other limits the source gives. |
| `_other-values` | Figures with no parameter in the database, kept but not loaded. |
| other suffixes | Source-specific tables (for example `_rows` for a workbook dumped as printed, or `_table-11-3`). |

Figures are as the source prints them. Where a source prints a figure wrongly, the
extraction keeps it, and the correction is a separate record in the database
(`data/technology_database/reference/source-correction.csv`).

## Licences

`licence_type` in `source-details_sources.csv` records each source's terms. A first sort
of the 602 sources (2026-11-06, by keyword; read the text before relying on it):

| Terms | Sources |
| - | - |
| Copyright, no open licence (journal articles, commercial reports) | 225 |
| Open licence: Creative Commons | 85 |
| Public domain (US government work) | 77 |
| Free to reproduce with acknowledgement, or freely available | 65 |
| Open licence: government open data (OGL, Alberta, BC) | 56 |
| No licence stated | 38 |
| Cited only, document not held | 45 |
| Other (read the text) | 11 |

The extractions hold figures and short labels from these documents, not their text.

## Adding a source

A new source is added in the technology-database repository: its document goes in
`primary-sources/`, its extraction in this folder, and its rows in the manifest (see
`src/technology_database/docs/pipeline.md`, *Add a source*). The folder is then deposited
on FRDR as a new version.
