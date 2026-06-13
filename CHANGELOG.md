# Changelog

## [0.1.0] — 2026-06-13

### Added

- Initial release.
- CLI entry point: `doc-to-md-cli`
- PDF → Markdown via marker-pdf with image extraction
- DOCX → Markdown via docling with image extraction from DOCX archive
- Recursive directory conversion preserving folder structure
- `--no-images` flag to disable image extraction
- `--dry-run` flag to preview conversions
- `-v/--verbose` flag for detailed logging
- `python -m doc_to_md_cli` support
- Tests: `test_discover.py`, `test_cli.py`
- `Makefile` with install, test, clean, dry-run targets
