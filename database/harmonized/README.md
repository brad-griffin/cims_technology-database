# database/harmonized

The database. The rules are in [database/docs/design.md](../docs/design.md) and the build
in [database/docs/pipeline.md](../docs/pipeline.md).

```
python database/harmonized/build.py
```

| Folder | Edited by | Contents |
| - | - | - |
| `records/` | hand | `archetype.csv`, `archetype-service.csv`, `source-example.csv`, `family.csv`, `hierarchy-annotation.csv`, the CIMS hierarchy snapshot, `vocabulary/` and `reference/` |
| `pipeline/`, `build.py` | hand | the build |
| `output/` | the build | the example and archetype tables, the wide views, the reviews and the workbook. Never edit these: the build rewrites them. |

To change what an example is an example of, edit its row in
`records/source-example.csv`. For everything else, see the *How to* section of the
pipeline doc.
