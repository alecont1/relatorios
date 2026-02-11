"""
GENSEP-style PDF renderer.

Generates PDFs matching the GENSEP commissioning protocol layout:
- Page 1: Cover with logo top-left, title centered, footer with address
- Page 2: Dense data page (info fields, technical chars, instrument data,
          measured values, general condition, signatures)
- Pages 3+: Equipment photos with instrument data repeated above
"""

from io import BytesIO
from pathlib import Path
import urllib.request

from fpdf import FPDF

from app.core.config import settings
from app.models.report import Report
from app.models.tenant import Tenant
from .layout_config import LayoutConfig


class GensepPDF(FPDF):
    """Custom FPDF subclass for GENSEP style with header/footer."""

    # Unicode chars outside Latin-1 → ASCII replacements
    _CHAR_MAP = {
        "\u03a9": "Ohm", "\u2126": "Ohm",  # Ω
        "\u03bc": "u",    # μ (micro)
        "\u03b1": "a", "\u03b2": "b", "\u03b3": "g", "\u03b4": "d",
        "\u2103": "C", "\u2109": "F",  # ℃ ℉
        "\u221e": "inf",  # ∞
        "\u2264": "<=", "\u2265": ">=", "\u2260": "!=",
    }

    def __init__(self, tenant_info: dict, template_name: str, primary_color: tuple):
        super().__init__()
        self._tenant_info = tenant_info
        self._template_name = template_name
        self._primary_color = primary_color
        self._is_cover = False

    def normalize_text(self, text):
        """Override to sanitize Unicode chars unsupported by Helvetica/Latin-1."""
        if text:
            for char, repl in self._CHAR_MAP.items():
                text = text.replace(char, repl)
            # Replace any remaining non-Latin-1 chars with '?'
            text = text.encode("latin-1", errors="replace").decode("latin-1")
        return super().normalize_text(text)

    def header(self):
        if self._is_cover:
            return
        # Logo left
        logo_url = self._tenant_info.get("logo_primary_url")
        if logo_url:
            try:
                self._add_image(logo_url, 10, 5, 30)
            except Exception:
                pass

        # Title right-aligned in primary color
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(*self._primary_color)
        self.set_xy(45, 8)
        self.cell(155, 4, "COMMISSIONING TEST PROTOCOL - LOW VOLTAGE CABLES", align="R")
        self.set_xy(45, 13)
        self.set_font("Helvetica", "", 7)
        self.cell(155, 4, self._template_name, align="R")

        # Line under header
        self.set_draw_color(*self._primary_color)
        self.set_line_width(0.3)
        self.line(10, 20, 200, 20)
        self.set_y(22)

    def footer(self):
        if self._is_cover:
            return
        self.set_y(-15)
        self.set_draw_color(180, 180, 180)
        self.set_line_width(0.2)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(1)

        self.set_font("Helvetica", "", 6)
        self.set_text_color(100, 100, 100)

        # Address + phone + website on left
        parts = []
        if self._tenant_info.get("address"):
            parts.append(self._tenant_info["address"])
        if self._tenant_info.get("phone"):
            parts.append(self._tenant_info["phone"])
        if self._tenant_info.get("website"):
            parts.append(self._tenant_info["website"])
        info_text = " | ".join(parts)
        self.cell(170, 3, info_text)

        # Page number right
        self.cell(0, 3, f"{self.page_no()}/{{nb}}", align="R")

    def _add_image(self, url: str, x: float, y: float, w: float):
        """Add image from URL or local path."""
        if url.startswith(("http://", "https://")):
            with urllib.request.urlopen(url, timeout=5) as response:
                img_data = response.read()
                img_io = BytesIO(img_data)
                self.image(img_io, x, y, w)
        else:
            local_path = Path(url)
            if local_path.exists():
                self.image(str(local_path), x, y, w)


class GensepPDFRenderer:
    """
    Complete PDF renderer for GENSEP commissioning protocol style.

    Renders the entire PDF in a single class, matching the GENSEP
    CPQ11 protocol layout exactly.
    """

    def __init__(self, report: Report, tenant: Tenant, certificates: list | None,
                 config: LayoutConfig):
        self.report = report
        self.tenant = tenant
        self.certificates = certificates or []
        self.config = config
        self.snapshot = report.template_snapshot

        # Build tenant info dict
        self.tenant_info = {
            "name": tenant.name,
            "logo_primary_url": self._resolve_logo(tenant.logo_primary_key),
            "logo_secondary_url": self._resolve_logo(tenant.logo_secondary_key),
            "primary_color": tenant.brand_color_primary or "#003B7A",
            "secondary_color": tenant.brand_color_secondary or "#005BAA",
            "accent_color": tenant.brand_color_accent or "#00A651",
            "phone": tenant.contact_phone,
            "email": tenant.contact_email,
            "address": tenant.contact_address,
            "website": tenant.contact_website,
        }
        self.primary = self._hex_to_rgb(self.tenant_info["primary_color"])
        self.secondary = self._hex_to_rgb(self.tenant_info["secondary_color"])
        self.accent = self._hex_to_rgb(self.tenant_info["accent_color"])

    @staticmethod
    def _clean_value(val: str) -> str:
        """Clean response_value from possible JSON array artifacts.

        Dropdown values may be stored as '["OK"' or '["APPROVED"]' instead
        of plain strings. This extracts the actual value.
        """
        if not val:
            return ""
        val = val.strip()
        # Handle truncated JSON arrays like '["OK"' or full '["OK"]'
        if val.startswith('["') or val.startswith("['"):
            import json
            try:
                parsed = json.loads(val if val.endswith("]") else val + '"]')
                if isinstance(parsed, list) and parsed:
                    return str(parsed[0])
            except (json.JSONDecodeError, IndexError):
                # Strip brackets and quotes manually
                val = val.lstrip("[").rstrip("]").strip("'\"")
        return val

    def generate(self) -> bytes:
        """Generate the complete PDF and return bytes."""
        template_name = self.snapshot.get("name", "Report")

        self.pdf = GensepPDF(self.tenant_info, template_name, self.primary)
        self.pdf.alias_nb_pages()
        self.pdf.set_auto_page_break(auto=True, margin=18)

        # Group data
        self.info_map = self._build_info_map()
        self.sections = self._group_responses_by_section()

        # Render pages
        self._render_cover_page()
        self._render_data_page()
        self._render_photo_pages()

        return bytes(self.pdf.output())

    # ── Cover Page ────────────────────────────────────────────────

    def _render_cover_page(self):
        """Page 1: Cover with logo, title, footer."""
        pdf = self.pdf
        pdf._is_cover = True
        pdf.add_page()
        pdf.set_auto_page_break(auto=False)

        # Logo top-left
        logo_url = self.tenant_info.get("logo_primary_url")
        if logo_url:
            try:
                pdf._add_image(logo_url, 10, 10, 40)
            except Exception:
                pass

        # Header text right-aligned
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*self.primary)
        pdf.set_xy(60, 12)
        pdf.cell(140, 5, "COMMISSIONING TEST PROTOCOL - LOW VOLTAGE CABLES", align="R")

        # Line under header
        pdf.set_draw_color(*self.primary)
        pdf.set_line_width(0.4)
        pdf.line(10, 25, 200, 25)

        # Central title box
        box_y = 100
        box_h = 50
        pdf.set_draw_color(0, 0, 0)
        pdf.set_line_width(0.5)
        pdf.rect(30, box_y, 150, box_h)

        # Title inside box
        template_name = self.snapshot.get("name", "ELECTRICAL TESTS")
        pdf.set_font("Helvetica", "B", 16)
        pdf.set_text_color(0, 0, 0)
        pdf.set_xy(35, box_y + 10)
        pdf.multi_cell(140, 8, template_name.upper(), align="C")

        # Subtitle
        code = self.snapshot.get("code", "")
        version = self.snapshot.get("version", "1")
        if code:
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(80, 80, 80)
            pdf.set_xy(35, box_y + box_h - 15)
            pdf.cell(140, 6, f"{code} - v{version}", align="C")

        # Footer - address, phone, website
        pdf.set_y(-30)
        pdf.set_draw_color(180, 180, 180)
        pdf.set_line_width(0.2)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(2)

        pdf.set_font("Helvetica", "", 7)
        pdf.set_text_color(100, 100, 100)

        if self.tenant_info.get("address"):
            pdf.cell(0, 3, self.tenant_info["address"], align="C",
                     new_x="LMARGIN", new_y="NEXT")

        contact_parts = []
        if self.tenant_info.get("phone"):
            contact_parts.append(self.tenant_info["phone"])
        if self.tenant_info.get("website"):
            contact_parts.append(self.tenant_info["website"])
        if contact_parts:
            pdf.cell(0, 3, " | ".join(contact_parts), align="C",
                     new_x="LMARGIN", new_y="NEXT")

        # Page number
        pdf.cell(0, 3, f"{pdf.page_no()}/{{nb}}", align="R")

        pdf._is_cover = False

    # ── Data Page ─────────────────────────────────────────────────

    def _render_data_page(self):
        """Page 2+: Dense data with all sections."""
        pdf = self.pdf
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=18)

        # Title bar
        self._section_header("TEST PROTOCOL - LOW VOLTAGE CABLES")

        # Info fields (paired layout)
        self._render_info_table()

        # Render each section based on its position/name
        for idx, section in enumerate(self.sections):
            name = section["name"].upper() if section.get("name") else f"SECTION {idx+1}"
            fields = section.get("fields", [])

            self._section_header(name)

            if "TECHNICAL CHARACTERISTICS" in name:
                self._render_paired_fields(fields)
            elif "AMBIENT TEMPERATURE" in name or "OHMIC" in name or "INSTRUMENT" in name:
                self._render_instrument_data(fields)
            elif "MEASURED VALUES" in name:
                self._render_measured_values(fields)
            elif "GENERAL CONDITION" in name:
                self._render_general_condition(fields)
            elif "PHOTO" in name or "EQUIPMENT" in name:
                # Photos rendered separately
                continue
            else:
                # Default: render as instrument-style 3-column
                self._render_instrument_data(fields)

        # Signatures inline
        if self.report.signatures:
            self._render_signatures()

    # ── Section Header ────────────────────────────────────────────

    def _section_header(self, title: str):
        """Render a section title bar."""
        pdf = self.pdf

        # Check if we need a new page
        if pdf.get_y() > pdf.h - 30:
            pdf.add_page()

        pdf.set_fill_color(*self.primary)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 7)
        pdf.cell(0, 5, f"  {title}", fill=True, new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)

    # ── Info Table (paired columns) ──────────────────────────────

    def _render_info_table(self):
        """Render info fields as paired columns like the GENSEP layout."""
        pdf = self.pdf
        info_values = self.report.info_values
        if not info_values:
            return

        pdf.set_font("Helvetica", "", 7)
        row_h = 5

        # Build label:value map
        iv_map = {iv.field_label: (iv.value or "") for iv in info_values}

        # Define row layout: each row is a list of (label, width_pct) pairs
        # GENSEP layout: Customer full width, then pairs
        rows = [
            [("Customer", 0.5), ("O.S.", 0.25), ("Date", 0.25)],
            [("Plant", 0.5), ("City-State", 0.5)],
            [("Location", 0.5), ("Circuit", 0.5)],
            [("Source", 0.5), ("Load", 0.5)],
        ]

        total_w = 190  # page width minus margins

        for row_def in rows:
            y_start = pdf.get_y()
            x = 10

            for label, width_pct in row_def:
                w = total_w * width_pct
                value = iv_map.get(label, "")

                # If no exact match, try case-insensitive
                if not value:
                    for k, v in iv_map.items():
                        if k.lower() == label.lower():
                            value = v
                            break

                # Label cell
                label_w = min(w * 0.4, 35)
                val_w = w - label_w

                pdf.set_xy(x, y_start)
                pdf.set_font("Helvetica", "B", 7)
                pdf.set_fill_color(230, 235, 245)
                pdf.cell(label_w, row_h, f" {label}:", border=1, fill=True)

                pdf.set_font("Helvetica", "", 7)
                pdf.set_fill_color(255, 255, 255)
                pdf.cell(val_w, row_h, f" {value}", border=1)

                x += w

            pdf.set_y(y_start + row_h)

        pdf.ln(1)

    # ── Paired Fields (Technical Characteristics) ─────────────────

    def _render_paired_fields(self, fields: list):
        """Render fields as 2 columns side by side: label:value | label:value."""
        pdf = self.pdf
        row_h = 5
        total_w = 190
        col_w = total_w / 2

        # Process fields in pairs
        for i in range(0, len(fields), 2):
            y_start = pdf.get_y()

            if y_start + row_h > pdf.h - 20:
                pdf.add_page()
                y_start = pdf.get_y()

            # Left field
            f1 = fields[i]
            label1 = f1.get("label", "")
            resp1 = f1.get("response", {})
            val1 = self._clean_value(resp1.get("response_value", ""))

            pdf.set_xy(10, y_start)
            label_w = 40
            val_w = col_w - label_w

            pdf.set_font("Helvetica", "B", 7)
            bg = (245, 247, 250) if (i // 2) % 2 == 0 else (255, 255, 255)
            pdf.set_fill_color(*bg)
            pdf.cell(label_w, row_h, f" {label1}:", border=1, fill=True)
            pdf.set_font("Helvetica", "", 7)
            pdf.cell(val_w, row_h, f" {val1}", border=1, fill=True)

            # Right field (if exists)
            if i + 1 < len(fields):
                f2 = fields[i + 1]
                label2 = f2.get("label", "")
                resp2 = f2.get("response", {})
                val2 = self._clean_value(resp2.get("response_value", ""))

                pdf.set_font("Helvetica", "B", 7)
                pdf.cell(label_w, row_h, f" {label2}:", border=1, fill=True)
                pdf.set_font("Helvetica", "", 7)
                pdf.cell(val_w, row_h, f" {val2}", border=1, fill=True)
            else:
                # Empty right half
                pdf.cell(col_w, row_h, "", border=1, fill=True)

            pdf.set_y(y_start + row_h)

        pdf.ln(1)

    # ── Instrument Data (3-column) ────────────────────────────────

    def _render_instrument_data(self, fields: list):
        """Render fields in 3 columns: Instrument | Serial Number | Calibration."""
        pdf = self.pdf
        row_h = 5
        total_w = 190

        # Render as label:value pairs, 3 per row
        for i in range(0, len(fields), 3):
            y_start = pdf.get_y()

            if y_start + row_h > pdf.h - 20:
                pdf.add_page()
                y_start = pdf.get_y()

            x = 10
            cols_in_row = min(3, len(fields) - i)
            col_w = total_w / 3

            for j in range(cols_in_row):
                field = fields[i + j]
                label = field.get("label", "")
                resp = field.get("response", {})
                value = self._clean_value(resp.get("response_value", ""))

                label_w = min(col_w * 0.45, 30)
                val_w = col_w - label_w

                pdf.set_xy(x, y_start)
                bg = (245, 247, 250) if (i // 3) % 2 == 0 else (255, 255, 255)
                pdf.set_fill_color(*bg)
                pdf.set_font("Helvetica", "B", 6.5)
                pdf.cell(label_w, row_h, f" {label}:", border=1, fill=True)
                pdf.set_font("Helvetica", "", 6.5)
                pdf.cell(val_w, row_h, f" {value}", border=1, fill=True)

                x += col_w

            # Fill remaining empty cols
            for j in range(cols_in_row, 3):
                pdf.set_xy(x, y_start)
                pdf.cell(total_w / 3, row_h, "", border=1)
                x += total_w / 3

            pdf.set_y(y_start + row_h)

        pdf.ln(1)

    # ── Measured Values (6-column table) ──────────────────────────

    def _render_measured_values(self, fields: list):
        """Render measured values as a table: Connection | 30s | 1min | Unit | IA | STATUS.

        Fields follow the pattern: "{ROW_NAME} - {COLUMN_NAME}", e.g.:
        "POSITIVE X NEGATIVE - 30s", "POSITIVE X NEGATIVE - 1min", etc.
        """
        pdf = self.pdf
        row_h = 5
        font_sz = 6.5

        if not fields:
            return

        # Parse fields into rows by detecting "ROW - COLUMN" pattern
        from collections import OrderedDict
        rows: OrderedDict[str, list] = OrderedDict()
        columns: list[str] = []

        for field in fields:
            label = field.get("label", "")
            if " - " in label:
                row_name, col_name = label.rsplit(" - ", 1)
                if row_name not in rows:
                    rows[row_name] = []
                if col_name not in columns:
                    columns.append(col_name)
                rows[row_name].append(field)
            else:
                # Fallback: field without pattern
                if "_ungrouped" not in rows:
                    rows["_ungrouped"] = []
                rows["_ungrouped"].append(field)

        # If pattern not detected, fall back to instrument layout
        if not columns or len(rows) == 0:
            self._render_instrument_data(fields)
            return

        # Remove ungrouped if present
        ungrouped = rows.pop("_ungrouped", [])

        # Build table: header = ["Connection", col1, col2, ...]
        num_cols = len(columns) + 1  # +1 for row name column
        conn_w = 50  # Connection/row name column
        remaining_w = 140  # remaining width for data columns
        col_w = remaining_w / max(len(columns), 1)

        # Header row
        pdf.set_fill_color(*self.primary)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", font_sz)

        x = 10
        pdf.set_xy(x, pdf.get_y())
        pdf.cell(conn_w, row_h, "Connection", border=1, fill=True, align="C")
        x += conn_w
        for col_name in columns:
            pdf.set_xy(x, pdf.get_y())
            # Shorten column headers
            short = col_name
            if len(short) > 10:
                short = short[:9] + "."
            pdf.cell(col_w, row_h, short, border=1, fill=True, align="C")
            x += col_w
        pdf.set_y(pdf.get_y() + row_h)

        # Data rows
        pdf.set_font("Helvetica", "", font_sz)
        for row_idx, (row_name, row_fields) in enumerate(rows.items()):
            y_start = pdf.get_y()
            if y_start + row_h > pdf.h - 20:
                pdf.add_page()
                y_start = pdf.get_y()

            bg = (245, 247, 250) if row_idx % 2 == 0 else (255, 255, 255)
            pdf.set_fill_color(*bg)

            # Build a lookup from column name to field
            field_by_col = {}
            for f in row_fields:
                lbl = f.get("label", "")
                if " - " in lbl:
                    _, cn = lbl.rsplit(" - ", 1)
                    field_by_col[cn] = f

            x = 10
            pdf.set_xy(x, y_start)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Helvetica", "B", font_sz)
            # Abbreviate row name if too long
            display_name = row_name
            if len(display_name) > 25:
                display_name = display_name[:24] + "."
            pdf.cell(conn_w, row_h, display_name, border=1, fill=True, align="L")
            x += conn_w

            pdf.set_font("Helvetica", "", font_sz)
            for col_name in columns:
                f = field_by_col.get(col_name)
                resp = f.get("response", {}) if f else {}
                value = self._clean_value(resp.get("response_value", ""))

                pdf.set_xy(x, y_start)

                # Color STATUS column
                if col_name.lower() == "status" and value:
                    upper_val = value.upper()
                    if upper_val in ("OK", "APPROVED", "PASS", "CONFORME"):
                        pdf.set_text_color(*self.accent)
                        pdf.set_font("Helvetica", "B", font_sz)
                    elif upper_val in ("NOK", "REPROVED", "FAIL", "REJECTED", "NAO CONFORME"):
                        pdf.set_text_color(220, 38, 38)
                        pdf.set_font("Helvetica", "B", font_sz)

                pdf.cell(col_w, row_h, value, border=1, fill=True, align="C")
                pdf.set_text_color(0, 0, 0)
                pdf.set_font("Helvetica", "", font_sz)
                x += col_w

            pdf.set_y(y_start + row_h)

        # Render any ungrouped fields below
        if ungrouped:
            self._render_instrument_data(ungrouped)

        pdf.ln(1)

    # ── General Condition (OK/NOK/NA table) ───────────────────────

    def _render_general_condition(self, fields: list):
        """Render general condition as ITEM | OK | NOK | NA | OBSERVATION."""
        pdf = self.pdf
        row_h = 5
        total_w = 190

        # Column widths
        item_w = 80
        ok_w = 15
        nok_w = 15
        na_w = 15
        obs_w = total_w - item_w - ok_w - nok_w - na_w

        # Header
        pdf.set_fill_color(*self.primary)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 6.5)

        y = pdf.get_y()
        pdf.set_xy(10, y)
        pdf.cell(item_w, row_h, "  ITEM", border=1, fill=True)
        pdf.cell(ok_w, row_h, "OK", border=1, fill=True, align="C")
        pdf.cell(nok_w, row_h, "NOK", border=1, fill=True, align="C")
        pdf.cell(na_w, row_h, "N/A", border=1, fill=True, align="C")
        pdf.cell(obs_w, row_h, "  OBSERVATION", border=1, fill=True,
                 new_x="LMARGIN", new_y="NEXT")

        # Data rows
        pdf.set_text_color(0, 0, 0)

        status_value = None
        notes_value = None
        test_condition_value = None

        for i, field in enumerate(fields):
            label = field.get("label", "")
            resp = field.get("response", {})
            value = (self._clean_value(resp.get("response_value", ""))).strip()
            comment = (resp.get("comment", "") or "").strip()

            # Detect special fields
            label_upper = label.upper()
            if "STATUS" in label_upper and "GENERAL" not in label_upper:
                status_value = value
                continue
            if "NOTE" in label_upper or "OBSERVATION" in label_upper.replace(" ", ""):
                if not any(x in label_upper for x in ["ITEM", "CABLE"]):
                    notes_value = value or comment
                    continue
            if "TEST CONDITION" in label_upper or "CONDITION OF TEST" in label_upper:
                test_condition_value = value
                continue

            y = pdf.get_y()
            if y + row_h > pdf.h - 20:
                pdf.add_page()
                y = pdf.get_y()

            bg = (245, 247, 250) if i % 2 == 0 else (255, 255, 255)
            pdf.set_fill_color(*bg)
            pdf.set_font("Helvetica", "", 6.5)

            # Item label
            pdf.set_xy(10, y)
            pdf.cell(item_w, row_h, f"  {label}", border=1, fill=True)

            # OK / NOK / N/A checkboxes
            is_ok = value.upper() in ("OK", "SIM", "CONFORME", "YES")
            is_nok = value.upper() in ("NOK", "NAO", "NAO CONFORME", "NO")
            is_na = value.upper() in ("N/A", "NA", "N.A.")

            pdf.set_font("Helvetica", "B", 7)

            # OK column
            if is_ok:
                pdf.set_text_color(*self.accent)
                pdf.cell(ok_w, row_h, "X", border=1, fill=True, align="C")
            else:
                pdf.cell(ok_w, row_h, "", border=1, fill=True, align="C")

            # NOK column
            if is_nok:
                pdf.set_text_color(220, 38, 38)
                pdf.cell(nok_w, row_h, "X", border=1, fill=True, align="C")
            else:
                pdf.cell(nok_w, row_h, "", border=1, fill=True, align="C")

            # N/A column
            pdf.set_text_color(107, 114, 128)
            if is_na:
                pdf.cell(na_w, row_h, "X", border=1, fill=True, align="C")
            else:
                pdf.cell(na_w, row_h, "", border=1, fill=True, align="C")

            # Observation
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Helvetica", "", 6.5)
            pdf.cell(obs_w, row_h, f"  {comment}", border=1, fill=True,
                     new_x="LMARGIN", new_y="NEXT")

        # Test condition row (full width)
        if test_condition_value:
            y = pdf.get_y()
            pdf.set_xy(10, y)
            pdf.set_fill_color(240, 240, 240)
            pdf.set_font("Helvetica", "B", 6.5)
            pdf.cell(50, row_h, "  Test Condition:", border=1, fill=True)
            pdf.set_font("Helvetica", "", 6.5)
            pdf.cell(total_w - 50, row_h, f"  {test_condition_value}", border=1, fill=True,
                     new_x="LMARGIN", new_y="NEXT")

        # STATUS row (full width, colored)
        if status_value:
            y = pdf.get_y()
            pdf.set_xy(10, y)

            upper_status = status_value.upper()
            if upper_status in ("APPROVED", "OK", "PASS", "APROVADO"):
                pdf.set_fill_color(200, 240, 200)
                pdf.set_text_color(0, 128, 0)
            elif upper_status in ("REJECTED", "NOK", "FAIL", "REPROVADO"):
                pdf.set_fill_color(255, 220, 220)
                pdf.set_text_color(200, 0, 0)
            else:
                pdf.set_fill_color(255, 255, 200)
                pdf.set_text_color(0, 0, 0)

            pdf.set_font("Helvetica", "B", 7)
            pdf.cell(50, row_h + 1, "  STATUS:", border=1, fill=True)
            pdf.cell(total_w - 50, row_h + 1, f"  {status_value}", border=1, fill=True,
                     new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(0, 0, 0)

        # Notes row
        if notes_value:
            y = pdf.get_y()
            pdf.set_xy(10, y)
            pdf.set_fill_color(255, 255, 240)
            pdf.set_font("Helvetica", "B", 6.5)
            pdf.cell(50, row_h, "  Notes:", border=1, fill=True)
            pdf.set_font("Helvetica", "I", 6.5)
            pdf.cell(total_w - 50, row_h, f"  {notes_value}", border=1, fill=True,
                     new_x="LMARGIN", new_y="NEXT")

        pdf.ln(1)

    # ── Signatures (inline) ───────────────────────────────────────

    def _render_signatures(self):
        """Render signatures inline: Performed By: [name] SIGN: [box]."""
        pdf = self.pdf
        signatures = self.report.signatures

        if pdf.get_y() > pdf.h - 35:
            pdf.add_page()

        self._section_header("SIGNATURES")

        row_h = 6
        total_w = 190

        # Execution date
        pdf.set_font("Helvetica", "B", 7)
        pdf.set_fill_color(240, 240, 240)
        pdf.set_xy(10, pdf.get_y())
        pdf.cell(40, row_h, "  Execution Date:", border=1, fill=True)
        pdf.set_font("Helvetica", "", 7)
        date_str = self.report.created_at.strftime("%d/%m/%Y") if self.report.created_at else ""
        pdf.cell(total_w - 40, row_h, f"  {date_str}", border=1, fill=True,
                 new_x="LMARGIN", new_y="NEXT")

        # Signatures in pairs on same row
        y_start = pdf.get_y()
        sig_count = len(signatures)

        if sig_count >= 2:
            half_w = total_w / 2

            for pair_idx in range(0, sig_count, 2):
                y = pdf.get_y()
                if y + 20 > pdf.h - 20:
                    pdf.add_page()
                    y = pdf.get_y()

                # Left signature
                sig1 = signatures[pair_idx]
                pdf.set_xy(10, y)
                pdf.set_font("Helvetica", "B", 7)
                pdf.set_fill_color(230, 235, 245)
                pdf.cell(25, row_h, f"  {sig1.role_name}:", border=1, fill=True)
                pdf.set_font("Helvetica", "", 7)
                pdf.cell(half_w - 25 - 30, row_h, f"  {sig1.signer_name or ''}", border=1)

                # Signature box
                sig_box_w = 30
                sig_box_h = 15
                x_box = 10 + half_w - sig_box_w
                pdf.set_xy(x_box, y)
                pdf.cell(sig_box_w, row_h, "  SIGN:", border=1,
                         fill=True)

                # Right signature
                if pair_idx + 1 < sig_count:
                    sig2 = signatures[pair_idx + 1]
                    x2 = 10 + half_w
                    pdf.set_xy(x2, y)
                    pdf.set_font("Helvetica", "B", 7)
                    pdf.set_fill_color(230, 235, 245)
                    pdf.cell(25, row_h, f"  {sig2.role_name}:", border=1, fill=True)
                    pdf.set_font("Helvetica", "", 7)
                    pdf.cell(half_w - 25 - sig_box_w, row_h,
                             f"  {sig2.signer_name or ''}", border=1)
                    pdf.cell(sig_box_w, row_h, "  SIGN:", border=1, fill=True)

                pdf.set_y(y + row_h)

                # Signature image boxes
                y_img = pdf.get_y()
                pdf.set_draw_color(180, 180, 180)
                pdf.rect(10 + half_w - sig_box_w, y_img, sig_box_w, sig_box_h)

                if sig1.file_key:
                    try:
                        sig_url = self._resolve_image_url(sig1.file_key)
                        pdf._add_image(sig_url, 10 + half_w - sig_box_w + 2, y_img + 1,
                                       sig_box_w - 4)
                    except Exception:
                        pass

                if pair_idx + 1 < sig_count:
                    pdf.rect(10 + total_w - sig_box_w, y_img, sig_box_w, sig_box_h)
                    sig2 = signatures[pair_idx + 1]
                    if sig2.file_key:
                        try:
                            sig_url = self._resolve_image_url(sig2.file_key)
                            pdf._add_image(sig_url, 10 + total_w - sig_box_w + 2,
                                           y_img + 1, sig_box_w - 4)
                        except Exception:
                            pass

                pdf.set_y(y_img + sig_box_h + 2)

        elif sig_count == 1:
            sig = signatures[0]
            y = pdf.get_y()
            pdf.set_xy(10, y)
            pdf.set_font("Helvetica", "B", 7)
            pdf.set_fill_color(230, 235, 245)
            pdf.cell(30, row_h, f"  {sig.role_name}:", border=1, fill=True)
            pdf.set_font("Helvetica", "", 7)
            pdf.cell(total_w - 30, row_h, f"  {sig.signer_name or ''}", border=1,
                     new_x="LMARGIN", new_y="NEXT")

            if sig.file_key:
                y_img = pdf.get_y()
                pdf.set_draw_color(180, 180, 180)
                pdf.rect(10, y_img, 50, 15)
                try:
                    sig_url = self._resolve_image_url(sig.file_key)
                    pdf._add_image(sig_url, 12, y_img + 1, 46)
                except Exception:
                    pass
                pdf.set_y(y_img + 17)

        pdf.ln(2)

    # ── Photo Pages ───────────────────────────────────────────────

    def _render_photo_pages(self):
        """Render equipment photos with instrument data above each group."""
        pdf = self.pdf

        # Collect photos from all sections
        photo_groups = []
        instrument_sections = {}

        for idx, section in enumerate(self.sections):
            name = section.get("name", "")
            name_upper = name.upper()
            fields = section.get("fields", [])

            # Save instrument data sections for reference
            if "AMBIENT TEMPERATURE" in name_upper or "OHMIC" in name_upper:
                instrument_sections[name] = fields

            # Collect photos from responses
            section_photos = []
            for field in fields:
                resp = field.get("response", {})
                for photo in (resp.get("photos") or []):
                    section_photos.append({
                        **photo,
                        "field": field.get("label", ""),
                        "section": name,
                    })

            if section_photos:
                # Try to find associated instrument data
                associated_instrument = None
                if "PHOTO" in name_upper or "EQUIPMENT" in name_upper:
                    # Match by keywords
                    for inst_name, inst_fields in instrument_sections.items():
                        if any(kw in name_upper for kw in
                               inst_name.upper().split()[:2]):
                            associated_instrument = {
                                "name": inst_name,
                                "fields": inst_fields,
                            }
                            break

                photo_groups.append({
                    "section_name": name,
                    "photos": section_photos,
                    "instrument_data": associated_instrument,
                })

        if not photo_groups:
            return

        for group in photo_groups:
            pdf.add_page()

            # Section title
            self._section_header(f"EQUIPMENT USED IN THIS MEASUREMENT")
            pdf.ln(1)

            # Sub-header with equipment name
            pdf.set_font("Helvetica", "B", 8)
            pdf.set_text_color(*self.primary)
            pdf.cell(0, 5, group["section_name"].upper(), new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(0, 0, 0)
            pdf.ln(1)

            # Instrument data table (if available)
            if group.get("instrument_data"):
                inst = group["instrument_data"]
                pdf.set_font("Helvetica", "B", 7)
                pdf.set_fill_color(*self.secondary)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(0, 4, f"  {inst['name']}", fill=True,
                         new_x="LMARGIN", new_y="NEXT")
                pdf.set_text_color(0, 0, 0)

                self._render_instrument_data(inst["fields"])
                pdf.ln(1)

            # Photo grid
            photos = group["photos"]
            photo_w = 85
            photo_h = 65
            margin = 10
            x_start = 10
            cols = 2

            for i, photo_data in enumerate(photos):
                col = i % cols
                row_offset = (i // cols) * (photo_h + 18)

                x = x_start + col * (photo_w + margin)
                y = pdf.get_y() + row_offset

                if y + photo_h + 18 > pdf.h - 20:
                    pdf.add_page()
                    pdf.set_y(pdf.get_y())
                    y = pdf.get_y()
                    # Reset row counting for new page
                    remaining_photos = photos[i:]
                    for ri, rp in enumerate(remaining_photos):
                        rc = ri % cols
                        rr = (ri // cols) * (photo_h + 18)
                        rx = x_start + rc * (photo_w + margin)
                        ry = pdf.get_y() + rr

                        if ry + photo_h + 18 > pdf.h - 20:
                            pdf.add_page()
                            ry = pdf.get_y()

                        photo_url = rp.get("url", "")
                        if photo_url:
                            try:
                                resolved = self._resolve_image_url(photo_url)
                                pdf._add_image(resolved, rx, ry, photo_w)
                            except Exception:
                                pass

                        # Caption
                        pdf.set_xy(rx, ry + photo_h)
                        pdf.set_font("Helvetica", "", 6)
                        pdf.set_text_color(100, 100, 100)
                        caption = rp.get("field", "")
                        if rp.get("captured_at"):
                            captured = rp["captured_at"][:16].replace("T", " ")
                            caption += f" - {captured}"
                        pdf.multi_cell(photo_w, 3, caption, align="C")
                        pdf.set_text_color(0, 0, 0)

                    break  # Already rendered all remaining

                photo_url = photo_data.get("url", "")
                if photo_url:
                    try:
                        resolved = self._resolve_image_url(photo_url)
                        pdf._add_image(resolved, x, y, photo_w)
                    except Exception:
                        pass

                # Caption
                pdf.set_xy(x, y + photo_h)
                pdf.set_font("Helvetica", "", 6)
                pdf.set_text_color(100, 100, 100)
                caption = photo_data.get("field", "")
                if photo_data.get("captured_at"):
                    captured = photo_data["captured_at"][:16].replace("T", " ")
                    caption += f" - {captured}"
                pdf.multi_cell(photo_w, 3, caption, align="C")
                pdf.set_text_color(0, 0, 0)

            # Move Y past the last row of photos
            if photos:
                last_row = (len(photos) - 1) // cols
                new_y = pdf.get_y() + (last_row) * (photo_h + 18) + photo_h + 20
                if new_y < pdf.h:
                    pdf.set_y(new_y)

    # ── Helpers ───────────────────────────────────────────────────

    def _build_info_map(self) -> dict:
        """Build a dict of info field label -> value."""
        return {
            iv.field_label: iv.value or ""
            for iv in (self.report.info_values or [])
        }

    def _group_responses_by_section(self) -> list:
        """Group checklist responses by section."""
        responses_by_field = {
            (r.section_name, r.field_label): r
            for r in self.report.checklist_responses
        }
        sections = []
        for section_data in self.snapshot.get("sections", []):
            fields = []
            for field_data in section_data.get("fields", []):
                response = responses_by_field.get(
                    (section_data["name"], field_data["label"])
                )
                fields.append({
                    "label": field_data.get("label"),
                    "response": {
                        "response_value": response.response_value if response else None,
                        "comment": response.comment if response else None,
                        "photos": response.photos if response else [],
                    } if response else {},
                })
            sections.append({
                "name": section_data.get("name"),
                "fields": fields,
            })
        return sections

    @staticmethod
    def _hex_to_rgb(hex_color: str) -> tuple:
        """Convert hex color to RGB tuple."""
        hex_color = (hex_color or "").lstrip("#")
        if len(hex_color) != 6:
            return (0, 59, 122)
        try:
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except ValueError:
            return (0, 59, 122)

    def _resolve_logo(self, key: str | None) -> str | None:
        """Resolve logo key to URL."""
        if not key:
            return None
        if key.startswith(("http://", "https://")):
            return key
        if settings.r2_public_url:
            return f"{settings.r2_public_url}/{key}"
        return f"uploads/{key}"

    def _resolve_image_url(self, key_or_url: str) -> str:
        """Resolve an R2 object key or URL to a fetchable URL."""
        if not key_or_url:
            return ""
        if key_or_url.startswith(("http://", "https://")):
            return key_or_url
        if key_or_url.startswith("/uploads/"):
            return key_or_url[1:]
        if settings.r2_public_url:
            return f"{settings.r2_public_url}/{key_or_url}"
        return f"uploads/{key_or_url}"
