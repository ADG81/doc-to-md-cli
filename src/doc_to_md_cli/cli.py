"""CLI entry point for doc-to-md-cli."""

import argparse
import logging
import sys
from pathlib import Path

from doc_to_md_cli import __version__
from doc_to_md_cli.converter import convert_file
from doc_to_md_cli.discover import discover_inputs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="doc-to-md-cli",
        description="Convert PDF and DOCX files to Markdown.",
        epilog="Examples:\n"
               "  doc-to-md-cli document.pdf\n"
               "  doc-to-md-cli report.md -o output/\n"
               "  doc-to-md-cli ./docs/ -o ./out/ --verbose\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "input",
        help="Input file or directory (PDF/DOCX, or folder containing them)",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output file path (for single input) or directory (for batch). "
             "Default: same name as input with .md extension.",
    )
    parser.add_argument(
        "--no-images",
        action="store_true",
        default=False,
        help="Disable image extraction",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Show what would be converted without converting",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        default=False,
        help="Enable verbose output",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="[doc-to-md] %(message)s",
    )
    log = logging.getLogger(__name__)

    input_path = args.input
    output_path = args.output
    extract_images = not args.no_images

    # Determine output path default for single file
    if output_path is None:
        if Path(input_path).is_file() or (
            not Path(input_path).exists() and Path(input_path).suffix
        ):
            output_path = str(Path(input_path).with_suffix(".md"))
        else:
            output_path = str(Path(input_path).parent / (Path(input_path).name + "_md"))

    # Ensure output_path is a string (handles Path input from tests)
    output_path = str(output_path)

    # Discover files
    try:
        tasks = discover_inputs(input_path, output_path)
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print(f"[doc-to-md] Dry run — {len(tasks)} file(s) would be converted:")
        for inp, out in tasks:
            print(f"  {inp}  →  {out}")
        sys.exit(0)

    # Convert
    ok, fail = 0, 0
    for inp, out in tasks:
        try:
            log.info(f"Converting: {inp}")
            log.info(f"Output:     {out}")
            convert_file(inp, out, extract_images=extract_images)
            log.info(f"Done: {out}")
            ok += 1
        except Exception as e:
            log.error(f"Failed: {inp} — {e}")
            fail += 1

    # Summary
    total = len(tasks)
    if total > 1:
        print(f"\n[doc-to-md] Converted {ok}/{total} files ({fail} failed).")
    if fail > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
