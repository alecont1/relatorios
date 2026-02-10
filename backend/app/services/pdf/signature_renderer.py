"""Signature grid renderer."""

from .base_renderer import BaseRenderer


class SignatureRenderer(BaseRenderer):
    """Renders the signature grid."""

    def render(self, signatures):
        """Add signatures grid with text wrapping."""
        if not signatures:
            return

        pdf = self.pdf
        sc = self.config.signatures

        pdf.ln(2)

        x_start = self.config.margins.left
        y_start = pdf.get_y()
        sig_width = sc.box_width_mm
        sig_height = sc.box_height_mm
        sigs_per_row = sc.columns
        margin = 5

        for i, sig in enumerate(signatures):
            col = i % sigs_per_row
            row = i // sigs_per_row

            x = x_start + col * (sig_width + margin)
            y = y_start + row * (sig_height + 25)

            if y + sig_height + 25 > pdf.h - 25:
                pdf.add_page()
                y_start = pdf.get_y()
                y = y_start

            pdf.set_draw_color(200, 200, 200)
            pdf.rect(x, y, sig_width, sig_height)

            if hasattr(sig, 'file_key') and sig.file_key:
                try:
                    sig_url = self.resolve_image_url(sig.file_key)
                    self.add_image_from_url(sig_url, x + 2, y + 2, sig_width - 4)
                except Exception:
                    pass

            # Role name - wrapping
            pdf.set_xy(x, y + sig_height + 1)
            pdf.set_font("Helvetica", "B", 8)
            pdf.set_text_color(0, 0, 0)
            pdf.multi_cell(sig_width, 3.5, sig.role_name or "", align="C")

            # Signer name - wrapping
            if sig.signer_name:
                pdf.set_xy(x, y + sig_height + 6)
                pdf.set_font("Helvetica", "", 7)
                pdf.set_text_color(100, 100, 100)
                pdf.multi_cell(sig_width, 3, sig.signer_name, align="C")

            # Date
            pdf.set_xy(x, y + sig_height + 11)
            pdf.set_font("Helvetica", "", 7)
            pdf.set_text_color(100, 100, 100)
            signed_date = sig.signed_at.strftime("%d/%m/%Y %H:%M") if sig.signed_at else ""
            pdf.cell(sig_width, 4, signed_date, align="C")

        if signatures:
            last_row = (len(signatures) - 1) // sigs_per_row
            pdf.set_y(y_start + (last_row + 1) * (sig_height + 28))
