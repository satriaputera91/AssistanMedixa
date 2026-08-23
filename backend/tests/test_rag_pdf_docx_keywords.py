import io
import sys
from pathlib import Path
from docx import Document
from pypdf import PdfWriter

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.modules.rag.rag_service import (
    extract_text_from_file_bytes,
    extract_keywords_with_gemini,
    qdrant_rag_service
)


def test_docx_text_extraction():
    doc = Document()
    doc.add_heading("Pedoman Terapi Gagal Jantung Kongestif (CHF)", level=1)
    doc.add_paragraph("Pemberian ACE Inhibitor atau ARB dikombinasikan dengan Beta Blocker terbukti menurunkan mortalitas pada pasien gagal jantung dengan fraksi ejeksi rendah (HFrEF).")
    doc.add_paragraph("Pemberian Spironolakton (MRA) dan SGLT2 Inhibitor seperti Dapagliflozin direkomendasikan sebagai pilar keempat terapi.")
    
    # Add table
    table = doc.add_table(rows=1, cols=2)
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Golongan Obat'
    hdr_cells[1].text = 'Dosis Awal'
    row_cells = table.add_row().cells
    row_cells[0].text = 'Bisoprolol'
    row_cells[1].text = '1.25 mg 1x/hari'

    buf = io.BytesIO()
    doc.save(buf)
    docx_bytes = buf.getvalue()

    extracted = extract_text_from_file_bytes("chf_guidelines.docx", docx_bytes)
    assert "Pedoman Terapi Gagal Jantung" in extracted
    assert "ACE Inhibitor" in extracted
    assert "Bisoprolol" in extracted
    assert "1.25 mg" in extracted


def test_pdf_text_extraction():
    # Test valid PDF binary structure
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    buf = io.BytesIO()
    writer.write(buf)
    pdf_bytes = buf.getvalue()

    extracted = extract_text_from_file_bytes("blank_sample.pdf", pdf_bytes)
    assert isinstance(extracted, str)


def test_gemini_keyword_extraction():
    medical_text = (
        "Pasien dengan diagnosis diabetes melitus tipe 2 tidak terkontrol (HbA1c 9.5%) "
        "diberikan terapi kombinasi Metformin 1000mg dua kali sehari dan Empagliflozin 10mg. "
        "Evaluasi komplikasi nefropati diabetik dan retinopati dilakukan secara berkala."
    )
    keywords = extract_keywords_with_gemini(medical_text, title="Tatalaksana DMT2", max_keywords=6)
    assert isinstance(keywords, list)
    assert len(keywords) > 0
    # Verify keywords contain relevant medical terms
    kw_str = " ".join(keywords).lower()
    assert any(term in kw_str for term in ["diabetes", "metformin", "hba1c", "empagliflozin", "nefropati", "dmt2"])


def test_qdrant_ingest_uploaded_docx():
    doc = Document()
    doc.add_heading("Protokol Penanganan Stroke Iskemik Akut", level=1)
    doc.add_paragraph("Golden period trombolisis menggunakan r-tPA (Alteplase) adalah dalam 4.5 jam pertama sejak onset gejala defisit neurologis.")
    buf = io.BytesIO()
    doc.save(buf)
    docx_bytes = buf.getvalue()

    raw_text = extract_text_from_file_bytes("stroke_iskemik.docx", docx_bytes)
    ingested = qdrant_rag_service.ingest_uploaded_file(
        filename="stroke_iskemik.docx",
        raw_content=raw_text,
        category="guideline",
        specialty="Neurology"
    )
    assert ingested is not None
    assert ingested["title"] == "Stroke Iskemik"
    assert len(ingested["keywords"]) > 0
    assert ingested["chunks_count"] >= 1


if __name__ == "__main__":
    test_docx_text_extraction()
    test_pdf_text_extraction()
    test_gemini_keyword_extraction()
    test_qdrant_ingest_uploaded_docx()
    print("✅ All PDF, DOCX, and Gemini keyword extraction tests passed successfully!")
