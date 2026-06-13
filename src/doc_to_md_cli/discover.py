"""Recursive discovery of PDF/DOCX files for batch conversion."""

from pathlib import Path

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".doc"}


def discover_inputs(input_path: str, output_path: str) -> list[tuple[str, str]]:
    """Discover all convertible files and compute their output paths.

    Returns a list of (input_file, output_file) tuples.
    Output paths preserve the relative directory structure of the input.
    """
    input_p = Path(input_path).resolve()
    output_p = Path(output_path).resolve()

    if input_p.is_file():
        if input_p.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported format: {input_p.suffix}. "
                f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
            )
        return [(str(input_p), str(output_p.with_suffix(".md")))]

    if input_p.is_dir():
        files = []
        for ext in sorted(SUPPORTED_EXTENSIONS):
            for f in sorted(input_p.rglob(f"*{ext}")):
                rel = f.relative_to(input_p)
                out = output_p / rel.with_suffix(".md")
                files.append((str(f), str(out)))
        if not files:
            raise ValueError(
                f"No PDF/DOCX files found in: {input_path}"
            )
        return files

    raise FileNotFoundError(f"Path does not exist: {input_path}")
