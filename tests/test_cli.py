"""Tests for the CLI module."""

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from doc_to_md_cli.cli import build_parser, main


class TestParser:
    def test_basic_args(self):
        parser = build_parser()
        args = parser.parse_args(["document.pdf"])
        assert args.input == "document.pdf"
        assert args.output is None
        assert args.no_images is False
        assert args.dry_run is False
        assert args.verbose is False

    def test_output_flag(self):
        parser = build_parser()
        args = parser.parse_args(["doc.pdf", "-o", "out.md"])
        assert args.output == "out.md"

    def test_no_images_flag(self):
        parser = build_parser()
        args = parser.parse_args(["doc.pdf", "--no-images"])
        assert args.no_images is True

    def test_dry_run_flag(self):
        parser = build_parser()
        args = parser.parse_args(["docs/", "--dry-run"])
        assert args.dry_run is True

    def test_verbose_flag(self):
        parser = build_parser()
        args = parser.parse_args(["doc.pdf", "-v"])
        assert args.verbose is True


class TestMainDryRun:
    def test_dry_run_single_file(self, tmp_path, capsys):
        pdf = tmp_path / "test.pdf"
        pdf.write_text("fake")

        with patch.object(sys, "argv", ["doc-to-md-cli", str(pdf), "--dry-run"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "Dry run" in captured.out
        assert "1 file" in captured.out

    def test_dry_run_directory(self, tmp_path, capsys):
        (tmp_path / "a.pdf").write_text("fake")
        (tmp_path / "b.docx").write_text("fake")

        with patch.object(sys, "argv", ["doc-to-md-cli", str(tmp_path), "--dry-run"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "2 file" in captured.out


class TestMainErrors:
    def test_missing_file(self, capsys):
        with patch.object(sys, "argv", ["doc-to-md-cli", "/nonexistent/file.pdf"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
        assert exc_info.value.code == 1

    def test_unsupported_extension(self, tmp_path, capsys):
        txt = tmp_path / "readme.txt"
        txt.write_text("not a doc")

        with patch.object(sys, "argv", ["doc-to-md-cli", str(txt)]):
            with pytest.raises(SystemExit) as exc_info:
                main()
        assert exc_info.value.code == 1
