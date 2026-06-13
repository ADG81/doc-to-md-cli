# doc-to-md-cli

Convert PDF and DOCX files to Markdown from the command line — no AI agent needed.

## Features

- **PDF** → Markdown via [marker-pdf](https://github.com/datalab-to/marker) (tables, formulas, layouts)
- **DOCX** → Markdown via [docling](https://github.com/docling-project/docling)
- **Image extraction** — saves images as separate files, referenced in the markdown
- **Batch mode** — convert entire folders recursively, preserving directory structure
- **Dry-run** — preview what would be converted

## Requirements

- Python 3.9+

## Install

```bash
git clone https://github.com/adg81/doc-to-md-cli.git
cd doc-to-md-cli
pip install -e .
```

Or install directly from GitHub:

```bash
pip install git+https://github.com/adg81/doc-to-md-cli.git
```

### Development install

```bash
pip install -e ".[dev]"
```

## Usage

### Single file

```bash
# Output defaults to same name with .md extension
doc-to-md-cli document.pdf

# Specify output path
doc-to-md-cli report.docx -o output/report.md
```

### Batch (recursive folder)

```bash
# Converts all PDF/DOCX in docs/, output in out/ with same structure
doc-to-md-cli ./docs/ -o ./out/

# Example: docs/2024/annual.pdf → out/2024/annual.md
```

### Options

```bash
doc-to-md-cli docs/ -o out/ [OPTIONS]

  -o, --output PATH    Output file or directory
  --no-images          Disable image extraction
  --dry-run            Show what would be converted without converting
  -v, --verbose        Detailed output
  --version            Show version
```

### Examples

```bash
# Preview what will be converted
doc-to-md-cli ./my-folder/ --dry-run

# Convert without extracting images
doc-to-md-cli document.pdf --no-images

# Verbose batch conversion
doc-to-md-cli ./library/ -o ./markdown/ --verbose
```

## How images work

- **PDF**: marker-pdf saves images as `_page_0_Picture_1.jpeg` alongside the `.md` file
- **DOCX**: images are extracted from the DOCX archive into a `<name>_immagini/` folder

In both cases, the markdown contains relative references like `![alt](_page_0_Picture_1.jpeg)`.

## Project structure

```
doc-to-md-cli/
├── pyproject.toml
├── Makefile
├── README.md
├── CHANGELOG.md
├── LICENSE
├── src/doc_to_md_cli/
│   ├── __init__.py
│   ├── __main__.py        # python -m doc_to_md_cli
│   ├── cli.py             # Argument parsing
│   ├── converter.py       # PDF (marker) + DOCX (docling) conversion
│   └── discover.py        # Recursive file discovery
└── tests/
    ├── test_discover.py
    └── test_cli.py
```

## Run tests

```bash
make test
```

## License

[MIT](LICENSE)
