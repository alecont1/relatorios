"""
PDF merger service using PyPDF2.

Merges the main report PDF with calibration certificate PDF attachments.
"""
from io import BytesIO

from PyPDF2 import PdfMerger, PdfReader


def merge_report_with_certificates(
    report_pdf: bytes,
    cert_files: list[bytes],
) -> bytes:
    """
    Merge the report PDF with certificate PDF attachments.

    Args:
        report_pdf: The main report PDF as bytes
        cert_files: List of certificate PDF files as bytes

    Returns:
        Merged PDF as bytes
    """
    if not cert_files:
        return report_pdf

    merger = PdfMerger()

    # Add the main report
    merger.append(PdfReader(BytesIO(report_pdf)))

    # Add each certificate PDF
    for cert_bytes in cert_files:
        try:
            reader = PdfReader(BytesIO(cert_bytes))
            merger.append(reader)
        except Exception:
            # Skip invalid PDFs silently
            continue

    # Write merged result
    output = BytesIO()
    merger.write(output)
    merger.close()
    output.seek(0)
    return output.read()
