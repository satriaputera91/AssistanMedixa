import os
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)

def build_pdf():
    samples_dir = Path("/Users/rnd/Program/Personal/AIMedical/samples")
    samples_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = samples_dir / "Panduan_Klinis_Infeksi_Ginjal_Pielonefritis.pdf"

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    emerald_primary = colors.HexColor("#065F46")
    emerald_dark = colors.HexColor("#022C22")
    emerald_light = colors.HexColor("#ECFDF5")
    emerald_border = colors.HexColor("#A7F3D0")
    slate_dark = colors.HexColor("#1E293B")
    slate_muted = colors.HexColor("#64748B")

    # Custom typography styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=emerald_primary,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=slate_muted,
        spaceAfter=14
    )

    h1_style = ParagraphStyle(
        'Header1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=emerald_dark,
        spaceBefore=12,
        spaceAfter=6
    )

    h2_style = ParagraphStyle(
        'Header2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=emerald_primary,
        spaceBefore=8,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=slate_dark,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=3
    )

    badge_style = ParagraphStyle(
        'Badge',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=emerald_primary
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=slate_dark
    )

    story = []

    # Title & Header
    story.append(Paragraph("PANDUAN PRAKTIK KLINIS: INFEKSI GINJAL (PIELONEFRITIS AKUT)", title_style))
    story.append(Paragraph("Protokol Standar Diagnosis, Manajemen Terapi Antibiotik, dan Tingkat Bukti Klinis Terkini", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=emerald_primary, spaceBefore=0, spaceAfter=10))

    # Metadata Box
    meta_data = [
        [
            Paragraph("<b>Kategori:</b> Penyakit & Panduan Klinis", badge_style),
            Paragraph("<b>Spesialisasi:</b> Nefrologi & Urologi", badge_style),
            Paragraph("<b>Kode ICD-10:</b> N10 / N11.9", badge_style),
            Paragraph("<b>Level Bukti:</b> IDSA/EAU Level I-A", badge_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[130, 130, 120, 135])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), emerald_light),
        ('BOX', (0, 0), (-1, -1), 1, emerald_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, emerald_border),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # Section 1: Definisi & Etiologi
    story.append(Paragraph("1. Definisi dan Etiologi", h1_style))
    story.append(Paragraph(
        "<b>Pielonefritis Akut</b> adalah infeksi bakteri invasif akut yang mengenai parenkim ginjal dan sistem pelviokalises. "
        "Sebagian besar kasus merupakan infeksi asendens dari saluran kemih bawah (uretritis/sistitis) yang menyebar menuju traktus urinarius atas. "
        "Patogen penyebab tersering meliputi <i>Escherichia coli</i> (75%–90%), diikuti oleh <i>Klebsiella pneumoniae</i>, <i>Proteus mirabilis</i>, <i>Enterobacter spp.</i>, "
        "dan <i>Enterococcus faecalis</i> pada kasus komplikasi atau terpasang kateter.",
        body_style
    ))

    # Section 2: Kriteria Diagnosis Klinis & Laboratorium
    story.append(Paragraph("2. Kriteria Diagnosis Klinis dan Pemeriksaan Penunjang", h1_style))
    story.append(Paragraph("<b>Gejala Klinis Khas (Trias Pielonefritis):</b>", h2_style))
    story.append(Paragraph("• <b>Demam Tinggi Akut</b> (>38.5°C) disertai menggigil dan takikardia.", bullet_style))
    story.append(Paragraph("• <b>Nyeri Sudut Kostovertebra (Costovertebral Angle / CVA tenderness)</b> unilateral atau bilateral.", bullet_style))
    story.append(Paragraph("• <b>Gejala Iritasi Saluran Kemih Bawah:</b> Disuria, frekuensi berkemih meningkat, nokturia, dan urgensi.", bullet_style))
    story.append(Paragraph("• <b>Gejala Gastrointestinal Sistemik:</b> Mual, muntah berat, anoreksia, dan nyeri abdomen difus.", bullet_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Pemeriksaan Laboratorium & Pencitraan:</b>", h2_style))
    story.append(Paragraph("• <b>Urinalisis:</b> Piuria (>10 leukosit per LPB), silinder leukosit (leukocyte casts - patognomonik infeksi tubulus), hematuria mikroskopik, tes esterase leukosit dan nitrit positif.", bullet_style))
    story.append(Paragraph("• <b>Kultur Urin & Uji Resistensi:</b> Baku emas diagnosis; bakteriuria bermakna didefinisikan sebagai ≥ 10^5 CFU/mL dari spesimen urin porsi tengah (midstream urine).", bullet_style))
    story.append(Paragraph("• <b>Darah Lengkap & Fungsi Ginjal:</b> Leukositosis dengan pergeseran ke kiri (neutrofilia), peningkatan CRP/LED, serta pemantauan ureum dan kreatinin serum untuk deteksi dini <i>Acute Kidney Injury (AKI)</i>.", bullet_style))
    story.append(Paragraph("• <b>Ultrasonografi (USG) / CT Urografi Abdomen:</b> Indikasi utama bila tidak ada perbaikan klinis dalam 48–72 jam terapi antibiotik empiris, suspek urolitiasis obstruktif, urosepsis berat, atau dugaan abses ginjal/perirenal.", bullet_style))

    story.append(Spacer(1, 8))

    # Section 3: Terapi & Protokol Antibiotik
    story.append(Paragraph("3. Protokol Terapi Antibiotik Berbasis Bukti (Evidence-Based)", h1_style))
    story.append(Paragraph(
        "Pemilihan antibiotik empiris didasarkan pada tingkat keparahan klinis, pola resistensi lokal patogen uropatogen, serta ada/tidaknya komplikasi.",
        body_style
    ))

    antibiotic_table_data = [
        [
            Paragraph("Kategori Kasus", table_header_style),
            Paragraph("Pilihan Obat & Dosis", table_header_style),
            Paragraph("Rute & Durasi", table_header_style),
            Paragraph("Tingkat Bukti (Level)", table_header_style)
        ],
        [
            Paragraph("<b>Pielonefritis Tanpa Komplikasi (Rawat Jalan)</b>", table_cell_style),
            Paragraph("• Ciprofloxacin 500 mg PO tiap 12 jam<br/>• Levofloxacin 750 mg PO tiap 24 jam<br/>• <i>Opsi alternatif:</i> Cefixime 400 mg 1x/hari / Cefpodoxime 200 mg 2x/hari", table_cell_style),
            Paragraph("Oral (PO)<br/>7 hari (Cipro)<br/>5 hari (Levo)<br/>10–14 hari (Sefalosporin)", table_cell_style),
            Paragraph("<b>Level I-A</b><br/>(IDSA / EAU)", table_cell_style)
        ],
        [
            Paragraph("<b>Pielonefritis Berat / Dirawat (Rawat Inap)</b>", table_cell_style),
            Paragraph("• Ceftriaxone 1–2 g IV tiap 24 jam<br/>• Cefotaxime 2 g IV tiap 8 jam<br/>• Piperacillin-Tazobactam 4.5 g IV tiap 8 jam<br/>• Gentamicin / Amikacin dosis tunggal IV", table_cell_style),
            Paragraph("Intravena (IV)<br/>Transisi ke oral setelah 48 jam bebas demam (total 10–14 hari)", table_cell_style),
            Paragraph("<b>Level I-A</b><br/>(IDSA Guidelines)", table_cell_style)
        ],
        [
            Paragraph("<b>Kasus Khusus / Suspek Kuman ESBL</b>", table_cell_style),
            Paragraph("• Meropenem 1 g IV tiap 8 jam<br/>• Ertapenem 1 g IV tiap 24 jam", table_cell_style),
            Paragraph("Intravena (IV)<br/>10–14 hari", table_cell_style),
            Paragraph("<b>Level I-B</b><br/>(ESCMID)", table_cell_style)
        ]
    ]

    ab_table = Table(antibiotic_table_data, colWidths=[130, 180, 115, 90])
    ab_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), emerald_primary),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, emerald_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, emerald_light]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(ab_table)
    story.append(Spacer(1, 10))

    # Section 4: Komplikasi & Tanda Bahaya (Red Flags)
    story.append(Paragraph("4. Komplikasi dan Tanda Bahaya (Red Flags)", h1_style))
    story.append(Paragraph("Segera lakukan eskalasi perawatan intensif / konsultasi bedah urologi jika ditemukan:", body_style))
    story.append(Paragraph("• <b>Urosepsis & Syok Septik:</b> Hipotensi (MAP <65 mmHg), oliguria, laktat serum >2 mmol/L.", bullet_style))
    story.append(Paragraph("• <b>Pielonefritis Emfisematosa:</b> Terbentuknya gas di parenkim ginjal pada pasien diabetes mellitus (indikasi darurat urologi).", bullet_style))
    story.append(Paragraph("• <b>Abses Ginjal / Abses Perinefrik:</b> Nyeri menetap dan demam resisten antibiotik >72 jam.", bullet_style))
    story.append(Paragraph("• <b>Obstruksi Saluran Kemih:</b> Pielonefritis dengan hidronefrosis memerlukan dekompresi segera (kateterisasi DJ stent / nefrostomi perkutan).", bullet_style))

    # Section 5: Bukti Literatur & Referensi
    story.append(Spacer(1, 6))
    story.append(Paragraph("5. Bukti Literatur dan Referensi Klinis", h1_style))
    story.append(Paragraph("1. <b>Infectious Diseases Society of America (IDSA):</b> <i>International Clinical Practice Guidelines for the Treatment of Acute Uncomplicated Cystitis and Pyelonephritis in Women</i>. Clinical Infectious Diseases, Level I, Grade A.", bullet_style))
    story.append(Paragraph("2. <b>European Association of Urology (EAU):</b> <i>Guidelines on Urological Infections 2024</i>. Update on Management of Upper Urinary Tract Infections, Level 1a Evidence.", bullet_style))
    story.append(Paragraph("3. <b>Perhimpunan Nefrologi Indonesia (PERNEFRI) & Ikatan Ahli Urologi Indonesia (IAUI):</b> <i>Konsensus Nasional Penatalaksanaan Infeksi Saluran Kemih dan Ginjal 2025</i>.", bullet_style))

    doc.build(story)
    print(f"PDF successfully generated at: {pdf_path}")
    print(f"File size: {os.path.getsize(pdf_path)} bytes")

if __name__ == "__main__":
    build_pdf()
