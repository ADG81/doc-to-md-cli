"""Tests for the discover module."""

import os
import tempfile
from pathlib import Path

import pytest

from doc_to_md_cli.discover import discover_inputs, SUPPORTED_EXTENSIONS


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


class TestSupportedExtensions:
    def test_includes_pdf(self):
        assert ".pdf" in SUPPORTED_EXTENSIONS

    def test_includes_docx(self):
        assert ".docx" in SUPPORTED_EXTENSIONS

    def test_includes_doc(self):
        assert ".doc" in SUPPORTED_EXTENSIONS


class TestSingleFile:
    def test_single_pdf(self, tmp_dir):
        f = tmp_dir / "doc.pdf"
        f.write_text("fake pdf")
        result = discover_inputs(str(f), str(tmp_dir / "out.md"))
        assert len(result) == 1
        assert result[0][0] == str(f)
        assert result[0][1].endswith(".md")

    def test_single_docx(self, tmp_dir):
        f = tmp_dir / "report.docx"
        f.write_text("fake docx")
        result = discover_inputs(str(f), str(tmp_dir / "out.md"))
        assert len(result) == 1
        assert result[0][0] == str(f)

    def test_unsupported_extension(self, tmp_dir):
        f = tmp_dir / "file.txt"
        f.write_text("not convertible")
        with pytest.raises(ValueError, match="Unsupported"):
            discover_inputs(str(f), str(tmp_dir / "out.md"))

    def test_missing_file(self, tmp_dir):
        with pytest.raises(FileNotFoundError):
            discover_inputs(str(tmp_dir / "nonexistent.pdf"), str(tmp_dir / "out.md"))


class TestDirectoryRecursive:
    def test_finds_nested_files(self, tmp_dir):
        (tmp_dir / "sub" / "deep").mkdir(parents=True)
        (tmp_dir / "a.pdf").write_text("fake")
        (tmp_dir / "sub" / "b.pdf").write_text("fake")
        (tmp_dir / "sub" / "deep" / "c.docx").write_text("fake")

        result = discover_inputs(str(tmp_dir), str(tmp_dir / "out"))

        assert len(result) == 3
        # Verify structure is preserved
        out_paths = [r[1] for r in result]
        assert any("a.md" in p for p in out_paths)
        assert any(p.endswith(os.path.join("sub", "b.md")) for p in out_paths)
        assert any(p.endswith(os.path.join("sub", "deep", "c.md")) for p in out_paths)

    def test_ignores_unsupported_files(self, tmp_dir):
        (tmp_dir / "doc.pdf").write_text("fake")
        (tmp_dir / "readme.txt").write_text("skip me")
        (tmp_dir / "data.json").write_text("{}")

        result = discover_inputs(str(tmp_dir), str(tmp_dir / "out"))
        assert len(result) == 1

    def test_empty_directory(self, tmp_dir):
        with pytest.raises(ValueError, match="No PDF/DOCX"):
            discover_inputs(str(tmp_dir), str(tmp_dir / "out"))

    def test_mixed_extensions(self, tmp_dir):
        (tmp_dir / "a.pdf").write_text("fake")
        (tmp_dir / "b.docx").write_text("fake")
        (tmp_dir / "c.doc").write_text("fake")

        result = discover_inputs(str(tmp_dir), str(tmp_dir / "out"))
        assert len(result) == 3

    def test_preserves_relative_structure(self, tmp_dir):
        (tmp_dir / "2024" / "reports").mkdir(parents=True)
        (tmp_dir / "2024" / "reports" / "annual.pdf").write_text("fake")

        result = discover_inputs(str(tmp_dir), str(tmp_dir / "converted"))

        out = result[0][1]
        assert "converted" in out
        assert "2024" in out
        assert "reports" in out
        assert out.endswith("annual.md")
