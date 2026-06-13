"""Conversion logic for PDF and DOCX to Markdown with image extraction."""

import os
import re
import zipfile
from pathlib import Path

os.environ.setdefault("GRPC_VERBOSITY", "ERROR")
os.environ.setdefault("GLOG_minloglevel", "2")
os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")


def convert_pdf(input_path: str, output_path: str, extract_images: bool = True) -> None:
    """Convert a PDF file to Markdown using marker-pdf.

    Images are saved alongside the .md output with names like _page_0_Picture_1.jpeg.
    The markdown references them with relative paths.
    """
    from marker.config.parser import ConfigParser
    from marker.models import create_model_dict
    from marker.output import save_output

    output_dir = str(Path(output_path).parent)
    output_stem = Path(output_path).stem

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    models = create_model_dict()

    config_dict = {"output_format": "markdown"}
    if not extract_images:
        config_dict["extract_images"] = False

    config_parser = ConfigParser(config_dict)
    converter_cls = config_parser.get_converter_cls()
    converter = converter_cls(
        config=config_parser.generate_config_dict(),
        artifact_dict=models,
        processor_list=config_parser.get_processors(),
        renderer=config_parser.get_renderer(),
        llm_service=config_parser.get_llm_service(),
    )

    rendered = converter(input_path)
    save_output(rendered, output_dir, output_stem)


def _extract_docx_images(input_path: str, images_dir: Path) -> dict[str, str]:
    """Extract images from a DOCX file (ZIP archive).

    Returns a dict mapping original filenames to new sequential names.
    """
    images_dir.mkdir(parents=True, exist_ok=True)
    name_map: dict[str, str] = {}
    counter = 0

    with zipfile.ZipFile(input_path, "r") as zf:
        media_files = sorted(
            n for n in zf.namelist() if n.startswith("word/media/")
        )
        for media_path in media_files:
            original_name = Path(media_path).name
            ext = Path(media_path).suffix.lower()
            counter += 1
            new_name = f"image_{counter:03d}{ext}"
            data = zf.read(media_path)
            (images_dir / new_name).write_bytes(data)
            name_map[original_name] = new_name

    return name_map


def convert_docx(input_path: str, output_path: str, extract_images: bool = True) -> None:
    """Convert a DOCX file to Markdown using docling.

    When extract_images is True, images are extracted from the DOCX archive
    into a `<stem>_immagini/` folder and referenced in the markdown with
    relative paths, replacing any base64 inline data URIs.
    """
    from docling.document_converter import DocumentConverter

    output_path_obj = Path(output_path)
    output_dir = output_path_obj.parent
    output_stem = output_path_obj.stem

    output_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Extract images from DOCX archive
    name_map: dict[str, str] = {}
    images_dir = output_dir / f"{output_stem}_immagini"
    if extract_images:
        name_map = _extract_docx_images(input_path, images_dir)

    # Step 2: Convert to markdown with docling
    converter = DocumentConverter()
    result = converter.convert(input_path)
    markdown_text = result.document.export_to_markdown()

    # Step 3: Replace base64 image data URIs with file references
    if extract_images and name_map:
        markdown_text = _replace_base64_images(markdown_text, name_map, images_dir, output_dir)

    output_path_obj.write_text(markdown_text, encoding="utf-8")


def _replace_base64_images(
    markdown: str,
    name_map: dict[str, str],
    images_dir: Path,
    output_dir: Path,
) -> str:
    """Replace base64 data URIs for images found in the name_map.

    Matches patterns like ![...](data:image/...;base64,...) and replaces them
    with ![rel_path](rel_path) pointing to the extracted image file.
    """
    # Pattern to match markdown image references with base64 data URIs
    b64_pattern = re.compile(
        r'!\[([^\]]*)\]\(data:image/([^;]+);base64,[^)]+\)'
    )

    def _replacer(match: re.Match) -> str:
        _alt = match.group(1)
        # Use a deterministic name based on position — we use image_001, image_002, etc.
        # The name_map is ordered, so we assign sequentially.
        # We use a simple counter approach via a closure.
        idx = _replacer.counter
        _replacer.counter += 1
        # Get the idx-th value from the ordered name_map
        if idx < len(name_map):
            new_name = list(name_map.values())[idx]
            rel_path = os.path.relpath(images_dir / new_name, output_dir)
            # Normalize to forward slashes for markdown
            rel_path = rel_path.replace("\\", "/")
            return f"![{_alt}]({rel_path})"
        return match.group(0)
    _replacer.counter = 0

    return b64_pattern.sub(_replacer, markdown)


def convert_file(input_path: str, output_path: str, extract_images: bool = True) -> str:
    """Convert a single file to Markdown. Returns the output path."""
    ext = Path(input_path).suffix.lower()

    if ext == ".pdf":
        convert_pdf(input_path, output_path, extract_images)
    elif ext in (".docx", ".doc"):
        convert_docx(input_path, output_path, extract_images)
    else:
        raise ValueError(
            f"Unsupported format: {ext}. Use PDF or DOCX."
        )

    return output_path
