import os
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

samples_dir = Path("/Users/rnd/Program/Personal/AIMedical/samples")
samples_dir.mkdir(parents=True, exist_ok=True)

# Colors for PDF
emerald_primary = colors.HexColor("#065F46")
emerald_dark = colors.HexColor("#022C22")
emerald_light = colors.HexColor("#ECFDF5")
emerald_border = colors.HexColor("#A7F3D0")
slate_dark = colors.HexColor("#1E293B")
slate_muted = colors.HexColor("#64748B")

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    'DocTitle',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=17,
    leading=21,
    textColor=emerald_primary,
    spaceAfter=5
)

subtitle_style = ParagraphStyle(
    'DocSubTitle',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=10.5,
    leading=14,
    textColor=slate_muted,
    spaceAfter=12
)

h1_style = ParagraphStyle(
    'Header1',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=12,
    leading=16,
    textColor=emerald_dark,
    spaceBefore=10,
    spaceAfter=5
)

h2_style = ParagraphStyle(
    'Header2',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=10,
    leading=13,
    textColor=emerald_primary,
    spaceBefore=6,
    spaceAfter=3
)

body_style = ParagraphStyle(
    'BodyTextCustom',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=9,
    leading=13,
    textColor=slate_dark,
    spaceAfter=5
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
    fontSize=8,
    leading=10,
    textColor=emerald_primary
)

table_header_style = ParagraphStyle(
    'TableHeader',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=8.5,
    leading=11,
    textColor=colors.white
)

table_cell_style = ParagraphStyle(
    'TableCell',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=8,
    leading=11,
    textColor=slate_dark
)

# ==============================================================================
# 1. PDF: SINDROM KORONER AKUT (STEMI & NSTEMI)
# ==============================================================================
def create_stemi_pdf():
    pdf_path = samples_dir / "Panduan_Klinis_Sindrom_Koroner_Akut_STEMI.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []

    story.append(Paragraph("PANDUAN PRAKTIK KLINIS: SINDROM KORONER AKUT (STEMI & NSTEMI)", title_style))
    story.append(Paragraph("Protokol Revaskularisasi Koroner, Terapi Antiplatelet Ganda, & Terapi Reperfusi Primer", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=emerald_primary, spaceBefore=0, spaceAfter=8))

    meta_data = [[
        Paragraph("<b>Kategori:</b> Penyakit & Panduan", badge_style),
        Paragraph("<b>Spesialisasi:</b> Kardiologi & Vaskular", badge_style),
        Paragraph("<b>Kode ICD-10:</b> I21.0 - I21.9", badge_style),
        Paragraph("<b>Level Bukti:</b> ACC/AHA & ESC Level I-A", badge_style)
    ]]
    meta_table = Table(meta_data, colWidths=[130, 130, 120, 135])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), emerald_light),
        ('BOX', (0, 0), (-1, -1), 1, emerald_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, emerald_border),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("1. Definisi dan Kriteria Diagnostik", h1_style))
    story.append(Paragraph(
        "<b>Sindrom Koroner Akut (SKA)</b> merupakan kondisi kegawatdaruratan kardiovaskular yang disebabkan oleh oklusi trombotik akut pada arteri koroner akibat ruptur atau erosi plak aterosklerosis. "
        "SKA diklasifikasikan menjadi <b>STEMI (ST-Segment Elevation Myocardial Infarction)</b>, <b>NSTEMI (Non-ST-Segment Elevation Myocardial Infarction)</b>, dan <b>UAP (Unstable Angina Pectoris)</b>.",
        body_style
    ))
    story.append(Paragraph("<b>Kriteria Diagnosis:</b>", h2_style))
    story.append(Paragraph("• <b>Nyeri Dada Khas Angina:</b> Nyeri substernal menjalar ke lengan kiri, leher, atau rahang, sensasi tertekan berat berlangsung >20 menit, tidak berkurang dengan istirahat/nitrat.", bullet_style))
    story.append(Paragraph("• <b>EKG 12 Sandapan (Wajib dalam 10 menit pertama):</b> Elevasi segmen ST baru pada J-point di ≥2 sandapan berdekatan (≥2.5 mm pada pria <40 th di V2-V3, ≥2 mm pada pria ≥40 th, ≥1.5 mm pada wanita) atau Left Bundle Branch Block (LBBB) baru.", bullet_style))
    story.append(Paragraph("• <b>Biomarka Jantung:</b> Troponin I / T berkadar sensitivitas tinggi (hs-cTn) meningkat melebihi persentil ke-99 URL dengan kenaikan/penurunan serial signifikan.", bullet_style))

    story.append(Paragraph("2. Protokol Reperfusi dan Antiplatelet (Level I-A Evidence)", h1_style))
    story.append(Paragraph(
        "Waktu adalah miokardium (<i>Time is Muscle</i>). Target <b>Door-to-Balloon Time < 90 menit</b> untuk Intervensi Koroner Perkutan (PCI) Primer, atau <b>Door-to-Needle Time < 30 menit</b> untuk fibrinolisis jika PCI tidak dapat dilakukan dalam waktu 120 menit.",
        body_style
    ))

    t_data = [
        [Paragraph("Regimen Obat", table_header_style), Paragraph("Dosis Inisiasi (Loading)", table_header_style), Paragraph("Dosis Pemeliharaan", table_header_style), Paragraph("Tingkat Bukti", table_header_style)],
        [Paragraph("<b>Aspirin (Asam Asetilsalisilat)</b>", table_cell_style), Paragraph("160 - 320 mg kunyah (PO)", table_cell_style), Paragraph("80 - 100 mg 1x/hari seumur hidup", table_cell_style), Paragraph("Level I-A (ACC/AHA)", table_cell_style)],
        [Paragraph("<b>Ticagrelor</b> (Inhibitor P2Y12 pilihan)", table_cell_style), Paragraph("180 mg PO (2 tablet @ 90mg)", table_cell_style), Paragraph("90 mg 2x/hari selama 12 bulan", table_cell_style), Paragraph("Level I-B (PLATO Trial)", table_cell_style)],
        [Paragraph("<b>Clopidogrel</b> (Alternatif jika Ticagrelor kontraindikasi)", table_cell_style), Paragraph("300 - 600 mg PO", table_cell_style), Paragraph("75 mg 1x/hari selama 12 bulan", table_cell_style), Paragraph("Level I-A (CURE Trial)", table_cell_style)],
        [Paragraph("<b>Antikoagulan (Heparin / Enoxaparin)</b>", table_cell_style), Paragraph("UFH 60-70 U/kg IV bolus atau Enoxaparin 30 mg IV bolus", table_cell_style), Paragraph("Enoxaparin 1 mg/kg SC tiap 12 jam", table_cell_style), Paragraph("Level I-A", table_cell_style)],
        [Paragraph("<b>Statin Intensitas Tinggi (Atorvastatin)</b>", table_cell_style), Paragraph("Atorvastatin 80 mg PO / Rosuvastatin 40 mg", table_cell_style), Paragraph("40 - 80 mg PO 1x/hari malam", table_cell_style), Paragraph("Level I-A (PROVE-IT)", table_cell_style)]
    ]
    stemi_t = Table(t_data, colWidths=[120, 160, 140, 95])
    stemi_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), emerald_primary),
        ('GRID', (0, 0), (-1, -1), 0.5, emerald_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, emerald_light]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(stemi_t)
    story.append(Spacer(1, 6))

    story.append(Paragraph("3. Referensi Klinis", h1_style))
    story.append(Paragraph("1. <b>ACC/AHA Guidelines for the Management of Patients With STEMI / NSTEMI</b>. Circulation 2024.", bullet_style))
    story.append(Paragraph("2. <b>PERKI (Perhimpunan Dokter Spesialis Kardiovaskular Indonesia):</b> <i>Pedoman Tatalaksana Sindrom Koroner Akut Edisi V 2024</i>.", bullet_style))

    doc.build(story)
    print(f"Generated: {pdf_path}")

# ==============================================================================
# 2. PDF: FARMAKOLOGI SGLT2 INHIBITORS (EMPAGLIFLOZIN & DAPAGLIFLOZIN)
# ==============================================================================
def create_sglt2_pdf():
    pdf_path = samples_dir / "Monografi_Obat_SGLT2_Inhibitor_Empagliflozin_Dapagliflozin.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []

    story.append(Paragraph("MONOGRAFI KLINIS: INHIBITOR SGLT2 (EMPAGLIFLOZIN & DAPAGLIFLOZIN)", title_style))
    story.append(Paragraph("Profil Farmakologi, Manfaat Kardio-Renal, Penyesuaian eGFR, dan Protokol Keamanan", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=emerald_primary, spaceBefore=0, spaceAfter=8))

    meta_data = [[
        Paragraph("<b>Kategori:</b> Obat / Farmakologi", badge_style),
        Paragraph("<b>Spesialisasi:</b> Endokrin & Kardiologi", badge_style),
        Paragraph("<b>Kode RxNorm:</b> 1373458 / 1488564", badge_style),
        Paragraph("<b>Level Bukti:</b> ADA & KDIGO Level I-A", badge_style)
    ]]
    meta_table = Table(meta_data, colWidths=[130, 130, 120, 135])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), emerald_light),
        ('BOX', (0, 0), (-1, -1), 1, emerald_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, emerald_border),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("1. Mekanisme Kerja dan Profil Farmakodinamik", h1_style))
    story.append(Paragraph(
        "<b>Sodium-Glucose Cotransporter 2 (SGLT2) Inhibitor</b> bekerja dengan menghambat reabsorpsi glukosa dan natrium di tubulus proksimal ginjal, "
        "menyebabkan glukosuria terukur (~70-80 g glukosa/hari) serta natriuresis. "
        "Efek natriuresis memicu tubuloglomerular feedback melalui peningkatan hantaran natrium ke macula densa, menginduksi vasokonstriksi arteriol aferen dan menurunkan hiperfiltrasi intraglomerular (efek nefroprotektif langsung).",
        body_style
    ))

    story.append(Paragraph("2. Indikasi Klinis Berbasis Bukti (Level I-A)", h1_style))
    story.append(Paragraph("• <b>Diabetes Melitus Tipe 2 (DMT2):</b> Menurunkan HbA1c 0.7-1.0%, menurunkan berat badan 2-3 kg, dan menurunkan tekanan darah sistolik 3-5 mmHg tanpa risiko hipoglikemia intrinsik.", bullet_style))
    story.append(Paragraph("• <b>Gagal Jantung (Heart Failure - HFrEF & HFpEF):</b> Menurunkan risiko rawat inap gagal jantung dan kematian kardiovaskular sebesar 25-30% terlepas dari status diabetes (EMPEROR-Reduced, DAPA-HF, DELIVER trials).", bullet_style))
    story.append(Paragraph("• <b>Penyakit Ginjal Kronis (Chronic Kidney Disease - CKD):</b> Memperlambat progresi penurunan eGFR dan menurunkan risiko end-stage renal disease (DAPA-CKD, EMPA-KIDNEY trials).", bullet_style))

    story.append(Paragraph("3. Panduan Dosis dan Penyesuaian Fungsi Ginjal (eGFR)", h1_style))

    d_data = [
        [Paragraph("Nama Generik", table_header_style), Paragraph("Dosis Standar", table_header_style), Paragraph("Batas Minimum eGFR Inisiasi", table_header_style), Paragraph("Catatan Klinis", table_header_style)],
        [
            Paragraph("<b>Empagliflozin (Jardiance)</b>", table_cell_style),
            Paragraph("10 mg 1x/hari pagi (dapat ditingkatkan ke 25 mg pada DMT2)", table_cell_style),
            Paragraph("eGFR ≥ 20 mL/menit/1.73m² (untuk indikasi HF & CKD)", table_cell_style),
            Paragraph("Lanjutkan terapi hingga hemodialisis jika sudah dimulai.", table_cell_style)
        ],
        [
            Paragraph("<b>Dapagliflozin (Forxiga)</b>", table_cell_style),
            Paragraph("10 mg 1x/hari pagi", table_cell_style),
            Paragraph("eGFR ≥ 20 mL/menit/1.73m² (DAPA-CKD & DAPA-HF)", table_cell_style),
            Paragraph("Tidak direkomendasikan jika eGFR <20 untuk inisiasi baru.", table_cell_style)
        ]
    ]
    d_table = Table(d_data, colWidths=[120, 140, 130, 125])
    d_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), emerald_primary),
        ('GRID', (0, 0), (-1, -1), 0.5, emerald_border),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, emerald_light]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(d_table)
    story.append(Spacer(1, 6))

    story.append(Paragraph("4. Keamanan dan Kewaspadaan (Safety Warnings)", h1_style))
    story.append(Paragraph("• <b>Ketoasidosis Diabetik Euglikemik (euDKA):</b> Hentikan obat 3 hari sebelum operasi mayor atau saat kondisi sakit kritis/dehidrasi berat.", bullet_style))
    story.append(Paragraph("• <b>Infeksi Mikotik Genital:</b> Edukasi kebersihan perineal; umumnya responsif terhadap antijamur topikal tanpa perlu menghentikan obat.", bullet_style))
    story.append(Paragraph("• <b>Penurunan eGFR Awal (Initial Dip):</b> Penurunan eGFR hingga 30% pada 2-4 minggu pertama adalah efek fisiologis reversibel penurunan tekanan intraglomerular, BUKAN tanda kerusakan ginjal.", bullet_style))

    doc.build(story)
    print(f"Generated: {pdf_path}")

# ==============================================================================
# 3. PDF: STROKE ISKEMIK AKUT & PROTOKOL TROMBOLISIS
# ==============================================================================
def create_stroke_pdf():
    pdf_path = samples_dir / "Panduan_Klinis_Stroke_Iskemik_Akut_Trombolisis.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []

    story.append(Paragraph("PANDUAN PRAKTIK KLINIS: STROKE ISKEMIK AKUT & TROMBOLISIS IV", title_style))
    story.append(Paragraph("Protokol Reperfusi Hiperakut r-tPA (Alteplase / Tenecteplase) & Trombektomi Mekanik", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=emerald_primary, spaceBefore=0, spaceAfter=8))

    meta_data = [[
        Paragraph("<b>Kategori:</b> Penyakit & Panduan", badge_style),
        Paragraph("<b>Spesialisasi:</b> Neurologi & Stroke", badge_style),
        Paragraph("<b>Kode ICD-10:</b> I63.0 - I63.9", badge_style),
        Paragraph("<b>Level Bukti:</b> AHA/ASA & ESO Level I-A", badge_style)
    ]]
    meta_table = Table(meta_data, colWidths=[130, 130, 120, 135])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), emerald_light),
        ('BOX', (0, 0), (-1, -1), 1, emerald_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, emerald_border),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("1. Kriteria Golden Period & Skrining Hiperakut", h1_style))
    story.append(Paragraph(
        "Setiap menit penundaan terapi reperfusi stroke iskemik menyebabkan kematian ~1.9 juta neuron otak (<i>Time is Brain</i>). "
        "Jendela waktu terapi trombolisis intravena (IVT) menggunakan r-tPA adalah <b>dalam waktu 4.5 jam</b> sejak onset gejala defisit neurologis terakhir diketahui normal.",
        body_style
    ))
    story.append(Paragraph("<b>Evaluasi Segera di Unit Gawat Darurat:</b>", h2_style))
    story.append(Paragraph("• Skrining FAST (Face drooping, Arm weakness, Speech difficulty, Time to call).", bullet_style))
    story.append(Paragraph("• Penilaian Derajat Keparahan Stroke menggunakan <b>National Institutes of Health Stroke Scale (NIHSS)</b>.", bullet_style))
    story.append(Paragraph("• <b>CT Scan Kepala Non-Kontras Cepat (Door-to-CT <20 menit):</b> Menyingkirkan perdarahan intrakranial (ICH) dan menghitung skor ASPECTS.", bullet_style))
    story.append(Paragraph("• <b>Batas Tekanan Darah Sebelum Trombolisis:</b> Tekanan darah harus diturunkan hingga < 185/110 mmHg (menggunakan Nicardipine atau Labetalol IV).", bullet_style))

    story.append(Paragraph("2. Dosis dan Protokol Administrasi r-tPA (Alteplase)", h1_style))
    story.append(Paragraph(
        "<b>Dosis Total Alteplase:</b> 0.9 mg/kg berat badan (Dosis maksimum 90 mg).<br/>"
        "• <b>10% dari dosis total</b> diberikan sebagai Bolus Intravena dalam 1 menit.<br/>"
        "• <b>90% sisa dosis</b> diberikan melalui Infus Kontinu menggunakan Syringe Pump selama 60 menit.<br/>"
        "• <i>Alternatif Tenecteplase (TNK-tPA):</i> 0.25 mg/kg IV bolus tunggal (maksimum 25 mg) (Level I-A, AcT trial).",
        body_style
    ))

    story.append(Paragraph("3. Kontraindikasi Mutlak Trombolisis IV", h1_style))
    story.append(Paragraph("• Perdarahan intrakranial aktif pada CT scan.", bullet_style))
    story.append(Paragraph("• Riwayat trauma kepala berat atau bedah saraf dalam 3 bulan terakhir.", bullet_style))
    story.append(Paragraph("• Perdarahan internal aktif atau diastesis perdarahan (Trombosit < 100.000/uL, INR > 1.7, aPTT > 40 detik).", bullet_style))
    story.append(Paragraph("• Penggunaan antikoagulan oral langsung (DOAC) dalam 48 jam terakhir dengan kadar terapeutik.", bullet_style))

    doc.build(story)
    print(f"Generated: {pdf_path}")

# ==============================================================================
# 4. DOCX: PEDOMAN TUBERKULOSIS RESISTEN OBAT (TB-RO / MDR-TB)
# ==============================================================================
def create_tb_ro_docx():
    docx_path = samples_dir / "Pedoman_Tatalaksana_Tuberkulosis_Paru_Resisten_Obat.docx"
    doc = Document()

    # Title
    p_title = doc.add_heading("PEDOMAN TATALAKSANA TUBERKULOSIS RESISTEN OBAT (TB-RO / MDR-TB)", level=0)
    p_title.paragraph_format.space_after = Pt(4)

    # Subtitle
    p_sub = doc.add_paragraph("Panduan Regimen Paduan Baru BPaLM / BPaL Berdasarkan Rekomendasi WHO 2024 & Kemenkes RI")
    p_sub.style.font.color.rgb = RGBColor(100, 116, 139)
    p_sub.style.font.size = Pt(10)

    # Metadata Table
    meta_table = doc.add_table(rows=2, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.style = 'Light Shading Accent 1'
    meta_table.rows[0].cells[0].text = "Kategori: Penyakit & Panduan Klinis"
    meta_table.rows[0].cells[1].text = "Spesialisasi: Pulmonologi & Penyakit Tropis"
    meta_table.rows[1].cells[0].text = "Kode ICD-10: U07.0 / A15.0 (MDR-TB)"
    meta_table.rows[1].cells[1].text = "Level Bukti: WHO Consolidated Guidelines Level 1"

    doc.add_heading("1. Definisi dan Klasifikasi Resistensi OAT", level=1)
    doc.add_paragraph(
        "Tuberkulosis Resisten Obat (TB-RO) adalah penyakit infeksi paru akibat Mycobacterium tuberculosis yang telah resisten terhadap obat anti-tuberkulosis (OAT) lini pertama.\n"
        "• TB Resisten Rifampisin (TB-RR): Resisten terhadap Rifampisin dengan atau tanpa resistensi OAT lain.\n"
        "• TB Multidrug-Resistant (TB-MDR): Resisten minimal terhadap Isoniazid (H) dan Rifampisin (R) secara simultan.\n"
        "• TB Pre-Extensively Drug-Resistant (Pre-XDR): TB-MDR/RR yang juga resisten terhadap golongan Fluorokuinolon (Moxifloxacin atau Levofloxacin).\n"
        "• TB Extensively Drug-Resistant (TB-XDR): TB Pre-XDR yang juga resisten terhadap minimal satu obat Grup A tambahan (Bedaquiline atau Linezolid)."
    )

    doc.add_heading("2. Paduan Regimen Baru 6 Bulan: BPaLM (WHO 2024)", level=1)
    doc.add_paragraph(
        "Regimen paduan BPaLM (Bedaquiline + Pretomanid + Linezolid + Moxifloxacin) selama 6 bulan merupakan standar emas baru "
        "yang menggantikan paduan jangka panjang konvensional 18–24 bulan dengan tingkat kesembuhan klinis mencapai >89% (TB-PRACTICAL Trial)."
    )

    # Regimen Table
    reg_table = doc.add_table(rows=5, cols=4)
    reg_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    reg_table.style = 'Table Grid'
    headers = ["Nama Obat", "Dosis Harian", "Durasi Terapi", "Tingkat Bukti"]
    for i, h in enumerate(headers):
        reg_table.rows[0].cells[i].paragraphs[0].text = h
        reg_table.rows[0].cells[i].paragraphs[0].runs[0].font.bold = True

    data = [
        ("Bedaquiline (Bdq)", "400 mg 1x/hari (2 mgg pertama), lalu 200 mg 3x/mgg", "24 minggu (6 bulan)", "Level 1A (WHO)"),
        ("Pretomanid (Pa)", "200 mg PO 1x/hari setiap hari", "24 minggu (6 bulan)", "Level 1A (WHO)"),
        ("Linezolid (Lzd)", "600 mg PO 1x/hari (turunkan ke 300 mg jika neuropati)", "16–24 minggu", "Level 1A (WHO)"),
        ("Moxifloxacin (Mfx)", "400 mg PO 1x/hari (dihentikan jika resisten kuinolon)", "24 minggu (6 bulan)", "Level 1B (WHO)")
    ]

    for row_idx, (ob, dos, dur, buk) in enumerate(data, start=1):
        reg_table.rows[row_idx].cells[0].paragraphs[0].text = ob
        reg_table.rows[row_idx].cells[1].paragraphs[0].text = dos
        reg_table.rows[row_idx].cells[2].paragraphs[0].text = dur
        reg_table.rows[row_idx].cells[3].paragraphs[0].text = buk

    doc.add_heading("3. Pemantauan Keamanan & Efek Samping", level=1)
    doc.add_paragraph(
        "• Pemantauan EKG Berkala: Deteksi pemanjangan interval QTc akibat Bedaquiline dan Moxifloxacin (Stop jika QTc >500 ms).\n"
        "• Pemantauan Darah Lengkap: Deteksi mielosupresi / anemia / trombositopenia akibat Linezolid.\n"
        "• Skrining Neuropati Optik & Perifer: Evaluasi visus dan keluhan kesemutan/kebas ekstremitas."
    )

    doc.save(str(docx_path))
    print(f"Generated: {docx_path}")

# ==============================================================================
# 5. DOCX: MONOGRAFI OBAT ANTIKOAGULAN ORAL LANGSUNG (DOAC / NOAC)
# ==============================================================================
def create_doac_docx():
    docx_path = samples_dir / "Monografi_Obat_DOAC_Antikoagulan_Oral_Langsung.docx"
    doc = Document()

    # Title
    p_title = doc.add_heading("MONOGRAFI FARMAKOLOGI: DIRECT ORAL ANTICOAGULANTS (DOAC)", level=0)
    p_title.paragraph_format.space_after = Pt(4)

    p_sub = doc.add_paragraph("Perbandingan Klinis Rivaroxaban, Apixaban, dan Dabigatran pada Fibrilasi Atrium & DVT")
    p_sub.style.font.color.rgb = RGBColor(100, 116, 139)
    p_sub.style.font.size = Pt(10)

    meta_table = doc.add_table(rows=2, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.style = 'Light Shading Accent 1'
    meta_table.rows[0].cells[0].text = "Kategori: Obat / Farmakologi"
    meta_table.rows[0].cells[1].text = "Spesialisasi: Hematologi & Kardiologi"
    meta_table.rows[1].cells[0].text = "Kode RxNorm: 1114195 / 1364430 / 1037046"
    meta_table.rows[1].cells[1].text = "Level Bukti: ESC & ACC/AHA Level I-A"

    doc.add_heading("1. Pengantar dan Indikasi Klinis", level=1)
    doc.add_paragraph(
        "Direct Oral Anticoagulants (DOAC) merupakan antikoagulan lini pertama untuk prevensi stroke pada Fibrilasi Atrium Non-Valvular (NVAF) "
        "serta terapi dan pencegahan sekunder Deep Vein Thrombosis (DVT) dan Pulmonary Embolism (PE). "
        "DOAC memiliki keunggulan farmakokinetik yang terprediksi tanpa memerlukan pemantauan rutin INR (berbeda dari Warfarin)."
    )

    doc.add_heading("2. Tabel Komparasi Obat DOAC Terkemuka", level=1)
    comp_table = doc.add_table(rows=4, cols=5)
    comp_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    comp_table.style = 'Table Grid'
    headers = ["Nama Generik", "Target Faktor", "Dosis Standar NVAF", "Penyesuaian Ginjal", "Antidotum Spesifik"]
    for i, h in enumerate(headers):
        comp_table.rows[0].cells[i].paragraphs[0].text = h
        comp_table.rows[0].cells[i].paragraphs[0].runs[0].font.bold = True

    rows_data = [
        ("Apixaban (Eliquis)", "Faktor Xa", "5 mg PO 2x/hari", "2.5 mg 2x/hari jika ≥2 dari: Usia ≥80 th, BB ≤60 kg, Cr ≥1.5 mg/dL", "Andexanet Alfa"),
        ("Rivaroxaban (Xarelto)", "Faktor Xa", "20 mg PO 1x/hari (bersama makanan)", "15 mg 1x/hari jika CrCl 15–49 mL/menit", "Andexanet Alfa"),
        ("Dabigatran (Pradaxa)", "Faktor IIa (Trombin)", "150 mg PO 2x/hari", "110 mg 2x/hari jika usia ≥80 th / CrCl 30–50 mL/menit", "Idarucizumab (Praxbind)")
    ]

    for r_idx, row in enumerate(rows_data, start=1):
        for c_idx, val in enumerate(row):
            comp_table.rows[r_idx].cells[c_idx].paragraphs[0].text = val

    doc.add_heading("3. Manajemen Perdarahan Mayor dan Pembalikan Efek (Reversal)", level=1)
    doc.add_paragraph(
        "• Untuk Dabigatran: Berikan Idarucizumab 5 g IV (2 vial @ 2.5 g IV bolus).\n"
        "• Untuk Rivaroxaban & Apixaban: Berikan Andexanet alfa IV atau 4-Factor Prothrombin Complex Concentrate (4F-PCC) 25–50 U/kg IV.\n"
        "• Hentikan obat 24–48 jam sebelum prosedur bedah elektif tergantung klirens kreatinin pasien."
    )

    doc.save(str(docx_path))
    print(f"Generated: {docx_path}")

# ==============================================================================
# 6. DOCX: PROTOKOL DEMAM BERDARAH DENGUE (DBD / DHF)
# ==============================================================================
def create_dengue_docx():
    docx_path = samples_dir / "Protokol_Klinis_Demam_Berdarah_Dengue_DHF.docx"
    doc = Document()

    p_title = doc.add_heading("PROTOKOL TANGGAP DARURAT: DEMAM BERDARAH DENGUE (DBD / DHF)", level=0)
    p_title.paragraph_format.space_after = Pt(4)

    p_sub = doc.add_paragraph("Pedoman Manajemen Fase Kritis, Resusitasi Cairan, dan Pencegahan Dengue Shock Syndrome")
    p_sub.style.font.color.rgb = RGBColor(100, 116, 139)
    p_sub.style.font.size = Pt(10)

    meta_table = doc.add_table(rows=2, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.style = 'Light Shading Accent 1'
    meta_table.rows[0].cells[0].text = "Kategori: Penyakit & Panduan Klinis"
    meta_table.rows[0].cells[1].text = "Spesialisasi: Penyakit Dalam & Pediatri"
    meta_table.rows[1].cells[0].text = "Kode ICD-10: A91 / A90"
    meta_table.rows[1].cells[1].text = "Level Bukti: WHO Dengue Guidelines 2024"

    doc.add_heading("1. Perjalanan Penyakit: Fase Kritis (Hari ke 3 - 7)", level=1)
    doc.add_paragraph(
        "Fase kritis demam berdarah terjadi saat demam mulai turun (defervescence). "
        "Pada fase ini terjadi perembesan plasma (plasma leakage) sistemik yang ditandai dengan peningkatan hematokrit ≥20%, "
        "penurunan trombosit (<100.000/uL), efusi pleura, dan asites yang berisiko memicu Dengue Shock Syndrome (DSS)."
    )

    doc.add_heading("2. Protokol Resusitasi Cairan Berbasis Tingkat Keparahan", level=1)
    doc.add_paragraph(
        "• DBD Derajat I & II (Tanpa Syok):\n"
        "  - Berikan cairan kristaloid (Ringer Laktat / Asetat) 5-7 mL/kgBB/jam selama 1-2 jam.\n"
        "  - Turunkan bertahap ke 3-5 mL/kgBB/jam jika kondisi membaik, lalu 2-3 mL/kgBB/jam.\n"
        "• DBD Derajat III & IV (Dengue Shock Syndrome / DSS):\n"
        "  - Guyur kristaloid cepat 10–20 mL/kgBB dalam 10–15 menit.\n"
        "  - Evaluasi tanda vital dan hematokrit. Jika syok belum teratasi, ulangi bolus kristaloid atau berikan Koloid 10-20 mL/kgBB/jam.\n"
        "  - Waspadai kelebihan cairan (fluid overload) saat fase reabsorpsi (hari ke-6 hingga ke-7)."
    )

    doc.save(str(docx_path))
    print(f"Generated: {docx_path}")

# ==============================================================================
# 7. MARKDOWN: PROTOKOL PENGGUNAAN INSULIN INTENSIF ICU
# ==============================================================================
def create_insulin_md():
    md_path = samples_dir / "Protokol_Penggunaan_Insulin_Intensif_ICU.md"
    content = """# Protokol Klinis: Infus Insulin Kontinu dan Regulasi Glukosa Darah di ICU

### Metadata Dokumen
- **Kategori**: Obat / Farmakologi & Protokol Kritis
- **Spesialisasi**: Endokrinologi, Anestesiologi & Intensive Care
- **Kode RxNorm**: 5856 (Insulin Reguler)
- **Kode ICD-10**: E11.65 (Hyperglycemia in Type 2 Diabetes)
- **Level Bukti**: ADA Standards of Care in Hospitalized Patients Level A

---

### 1. Indikasi dan Target Terapi
Infus insulin intravena kontinu diindikasikan untuk:
1. Pasien kritis di ICU dengan hiperglikemia persisten (>180 mg/dL).
2. Ketoasidosis Diabetik (KAD / DKA) dan Status Hiperglikemik Hiperosmolar (HHS).
3. Pasien pasca-bedah jantung terbuka dan syok kardiogenik.

**Target Glukosa Darah ICU**: **140 – 180 mg/dL (7.8 – 10.0 mmol/L)**. Target ketat (<110 mg/dL) TIDAK direkomendasikan karena meningkatkan risiko mortalitas akibat hipoglikemia berat (NICE-SUGAR Study).

---

### 2. Formulasi dan Skema Dosis Awal
- **Sediaan Infus**: 50 Unit Insulin Regular (Actrapid / Humulin R) dilarutkan dalam 50 mL NaCl 0.9% (Konsentrasi: **1 Unit/mL**).
- **Bolus Awal**: 0.1 Unit/kgBB IV (opsional pada KAD, tidak diberikan jika K+ < 3.3 mEq/L).
- **Kecepatan Infus Awal**:
  - Glukosa Darah 180 - 240 mg/dL : 1 - 2 Unit/jam
  - Glukosa Darah 241 - 300 mg/dL : 2 - 3 Unit/jam
  - Glukosa Darah > 300 mg/dL : 3 - 4 Unit/jam

---

### 3. Penyesuaian Dosis Tiap Jam (Titration Algorithm)
- Periksa glukosa darah kapiler (POCT) setiap **1 jam** hingga stabil dalam target selama 3 jam berturut-turut, kemudian periksa setiap 2 jam.
- Jika glukosa darah turun >50 mg/dL/jam : Turunkan kecepatan infus sebesar 50%.
- Jika glukosa darah mencapai target (140-180 mg/dL) : Pertahankan kecepatan infus.
- Jika glukosa darah masih >180 mg/dL : Naikkan kecepatan infus 0.5 - 1.0 Unit/jam.

---

### 4. Protokol Tanggap Darurat Hipoglikemia
Jika glukosa darah **< 70 mg/dL**:
1. **Hentikan segera** infus insulin.
2. Berikan **Dextrose 40% (D40%) 25-50 mL IV bolus**.
3. Periksa ulang glukosa darah setiap 15 menit sampai ≥100 mg/dL.
4. Jika sudah stabil >140 mg/dL, mulai kembali infus insulin dengan kecepatan **50% dari dosis sebelumnya**.
"""
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated: {md_path}")

if __name__ == "__main__":
    create_stemi_pdf()
    create_sglt2_pdf()
    create_stroke_pdf()
    create_tb_ro_docx()
    create_doac_docx()
    create_dengue_docx()
    create_insulin_md()
    print("\n✅ All sample documents generated successfully in samples/ directory!")
