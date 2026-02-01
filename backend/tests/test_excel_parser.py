"""
Unit tests for Excel template parser.

Tests cover:
- Valid Excel parsing
- Missing required fields
- Invalid result types
- Dropdown without options
- Empty files
- Invalid file format
"""

import pytest
from io import BytesIO
from openpyxl import Workbook

from app.services.excel_parser import parse_template_excel, ParseResult


def create_test_excel(rows: list[list]) -> bytes:
    """Helper to create Excel file bytes from row data."""
    wb = Workbook()
    ws = wb.active

    # Add header
    ws.append(["Section", "Script Step", "Result Type", "Step Result Values"])

    # Add data rows
    for row in rows:
        ws.append(row)

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer.read()


class TestExcelParser:
    def test_valid_excel_with_dropdown_and_text(self):
        """Test parsing valid Excel with mixed field types."""
        rows = [
            ["General", "Check power", "Drop Down", "Yes/No/NA"],
            ["General", "Serial number", "Text", ""],
            ["Electrical", "Voltage reading", "Text", ""],
        ]
        excel_bytes = create_test_excel(rows)

        result = parse_template_excel(excel_bytes)

        assert result.valid is True
        assert result.errors is None
        assert len(result.sections) == 2
        assert result.summary["section_count"] == 2
        assert result.summary["field_count"] == 3

        # Check first section
        general = result.sections[0]
        assert general.name == "General"
        assert len(general.fields) == 2
        assert general.fields[0].field_type == "dropdown"
        assert general.fields[0].options == ["Yes", "No", "NA"]
        assert general.fields[1].field_type == "text"

    def test_missing_section_column(self):
        """Test error when Section is empty."""
        rows = [
            ["", "Check power", "Drop Down", "Yes/No"],
        ]
        excel_bytes = create_test_excel(rows)

        result = parse_template_excel(excel_bytes)

        assert result.valid is False
        assert any("Section" in e and "obrigatoria" in e for e in result.errors)

    def test_missing_script_step(self):
        """Test error when Script Step is empty."""
        rows = [
            ["General", "", "Drop Down", "Yes/No"],
        ]
        excel_bytes = create_test_excel(rows)

        result = parse_template_excel(excel_bytes)

        assert result.valid is False
        assert any("Script Step" in e and "obrigatoria" in e for e in result.errors)

    def test_invalid_result_type(self):
        """Test error for invalid Result Type."""
        rows = [
            ["General", "Check", "Checkbox", "Yes/No"],
        ]
        excel_bytes = create_test_excel(rows)

        result = parse_template_excel(excel_bytes)

        assert result.valid is False
        assert any("Result Type" in e and "invalido" in e for e in result.errors)

    def test_dropdown_without_options(self):
        """Test error when Drop Down has no options."""
        rows = [
            ["General", "Check", "Drop Down", ""],
        ]
        excel_bytes = create_test_excel(rows)

        result = parse_template_excel(excel_bytes)

        assert result.valid is False
        assert any("Step Result Values" in e and "obrigatorio" in e for e in result.errors)

    def test_dropdown_with_single_option(self):
        """Test error when Drop Down has only one option."""
        rows = [
            ["General", "Check", "Drop Down", "Yes"],
        ]
        excel_bytes = create_test_excel(rows)

        result = parse_template_excel(excel_bytes)

        assert result.valid is False
        assert any("2 opcoes" in e for e in result.errors)

    def test_collects_all_errors(self):
        """Test that parser collects ALL errors, not just first."""
        rows = [
            ["", "Check", "Drop Down", ""],  # Missing section + missing options
            ["General", "", "InvalidType", ""],  # Missing step + invalid type
        ]
        excel_bytes = create_test_excel(rows)

        result = parse_template_excel(excel_bytes)

        assert result.valid is False
        # Should have at least 4 errors (not fail on first)
        assert len(result.errors) >= 4

    def test_comma_separated_options(self):
        """Test parsing comma-separated options."""
        rows = [
            ["General", "Status", "Drop Down", "Active, Inactive, Pending"],
        ]
        excel_bytes = create_test_excel(rows)

        result = parse_template_excel(excel_bytes)

        assert result.valid is True
        assert result.sections[0].fields[0].options == ["Active", "Inactive", "Pending"]

    def test_empty_excel(self):
        """Test error for Excel with only header."""
        excel_bytes = create_test_excel([])

        result = parse_template_excel(excel_bytes)

        assert result.valid is False
        assert any("Nenhum dado" in e for e in result.errors)

    def test_skips_empty_rows(self):
        """Test that completely empty rows are skipped."""
        rows = [
            ["General", "Check 1", "Text", ""],
            ["", "", "", ""],  # Empty row - should be skipped
            ["General", "Check 2", "Text", ""],
        ]
        excel_bytes = create_test_excel(rows)

        result = parse_template_excel(excel_bytes)

        assert result.valid is True
        assert result.summary["field_count"] == 2

    def test_invalid_file_format(self):
        """Test error for non-Excel file."""
        result = parse_template_excel(b"not an excel file")

        assert result.valid is False
        assert any("invalido" in e or "corrompido" in e or "Erro ao abrir arquivo" in e for e in result.errors)
