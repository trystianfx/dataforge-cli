# dataforge documentation

Per-stage reference docs: options, the underlying Python API, and working
examples for every part of the pipeline. Start here if you know which
stage you need; otherwise see the main [README](../README.md) for the
end-to-end quick start.

| Stage | Doc | CLI command(s) |
|---|---|---|
| Ingest | [ingest.md](ingest.md) | `dataforge ingest` |
| Schema | [schema.md](schema.md) | `dataforge schema` |
| Profile | [profile.md](profile.md) | `dataforge profile` |
| Export | [export.md](export.md) | (used internally by `build`; also usable as a library) |
| Charts | [charts.md](charts.md) | `dataforge chart` |
| Render | [render.md](render.md) | (used internally by `build`; also usable as a library) |
| Publish (WordPress) | [wp_publish.md](wp_publish.md) | `dataforge wp-push` |

The full pipeline (`dataforge build`) chains Ingest -> Schema -> Profile ->
Export -> Render in one command; each doc below also shows how to call
that stage standalone, either from the CLI or as a Python import, if you
only need one piece.

Every page ends with a "See also" pointer to the upstream library's own
documentation for anything beyond what dataforge exposes.
