'use client';

import React, { useState, useEffect } from 'react';
import { AgentService, type PatientRecord } from '@/services/agent.service';
import { ICD10_DATABASE } from './DiagnosisEditor';

export interface CPPTContent {
  subjective: string;
  objective: string;
  assessment: string;
  plan: string;
  instructions?: string;
}

interface CPPTEditorModalProps {
  isOpen: boolean;
  onClose: () => void;
  patient?: PatientRecord | null;
  messages?: Array<{ role: string; content: string; metadata?: Record<string, any> | null }>;
  initialContent?: Partial<CPPTContent>;
  onConfirmSend: (content: CPPTContent) => void;
  isSubmitting?: boolean;
}

// Helper to clean Markdown syntax for plaintext editing in modal
function cleanMarkdown(raw: string): string {
  if (!raw) return '';
  return raw
    .replace(/^\|\s*/gm, '')
    .replace(/\s*\|$/gm, '')
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/\*\*/g, '')
    .replace(/`/g, '')
    .replace(/^[\s\-\*]+/gm, '- ')
    .trim();
}

// Function to dynamically parse SOAP components from AI generated recommendation markdown and structured outputs
export function parseSOAPFromAIText(
  content: string,
  allMessages?: Array<{ role: string; content: string; metadata?: Record<string, any> | null; structured_output?: any }>,
  patient?: PatientRecord | null
): CPPTContent {
  let s = '';
  let o = '';
  let a = '';
  let p = '';
  let i_inst = '';

  const extractTableRow = (text: string, keyRegex: RegExp): string => {
    const lines = text.split('\n');
    for (const line of lines) {
      if (keyRegex.test(line) && line.includes('|')) {
        const parts = line.split('|').map(x => x.trim()).filter(Boolean);
        if (parts.length >= 2) {
          return cleanMarkdown(parts.slice(1).join(' - '));
        }
      }
    }
    return '';
  };

  // 1. Priority pass: Extract from structured Pydantic Output if available in allMessages
  if (allMessages && allMessages.length > 0) {
    for (let idx = allMessages.length - 1; idx >= 0; idx--) {
      const msg = allMessages[idx];
      const struct = (msg as any).structured_output || msg.metadata?.structured_output;
      if (!struct) continue;

      const soapObj = struct.soap || (struct.assessment && struct.subjective ? struct : null);

      if (soapObj) {
        // Subjective
        if (!s && soapObj.subjective) {
          const subj = soapObj.subjective;
          const sLines: string[] = [];
          if (subj.chief_complaint) sLines.push(`- Keluhan Utama: ${subj.chief_complaint}`);
          if (subj.history_present_illness) sLines.push(`- Riwayat Penyakit Sekarang (RPS): ${subj.history_present_illness}`);
          if (subj.past_medical_history) sLines.push(`- Riwayat Penyakit Dahulu (RPD): ${subj.past_medical_history}`);
          if (subj.allergy_history) sLines.push(`- Riwayat Alergi: ${subj.allergy_history}`);
          if (subj.medication_history) sLines.push(`- Riwayat Obat Rutin: ${subj.medication_history}`);
          if (sLines.length > 0) s = sLines.join('\n');
        }

        // Objective
        if (!o && soapObj.objective) {
          const obj = soapObj.objective;
          const oLines: string[] = [];
          if (obj.vital_signs) {
            const vs = obj.vital_signs;
            const vsParts: string[] = [];
            if (vs.blood_pressure) vsParts.push(`TD ${vs.blood_pressure}`);
            if (vs.heart_rate) vsParts.push(`HR ${vs.heart_rate}`);
            if (vs.respiratory_rate) vsParts.push(`RR ${vs.respiratory_rate}`);
            if (vs.temperature) vsParts.push(`Suhu ${vs.temperature}`);
            if (vs.spo2) vsParts.push(`SpO2 ${vs.spo2}`);
            if (vsParts.length > 0) oLines.push(`- Tanda-Tanda Vital: ${vsParts.join(', ')}`);
          }
          if (obj.physical_examination) oLines.push(`- Pemeriksaan Fisik: ${obj.physical_examination}`);
          if (Array.isArray(obj.laboratory_results) && obj.laboratory_results.length > 0) {
            oLines.push(`- Evaluasi Laboratorium:`);
            obj.laboratory_results.forEach((l: any) => {
              const ref = l.reference_range ? ` [Rujukan: ${l.reference_range}]` : '';
              oLines.push(`  • ${l.test_name}: ${l.value} ${l.unit || ''} (${l.status || 'Normal'})${ref}`);
            });
          }
          if (oLines.length > 0) o = oLines.join('\n');
        }

        // Assessment
        if (!a && soapObj.assessment) {
          const ass = soapObj.assessment;
          const aLines: string[] = [];
          if (ass.primary_diagnosis) {
            const pd = ass.primary_diagnosis;
            const icd = pd.icd10 ? ` (ICD-10: ${pd.icd10})` : '';
            const conf = pd.confidence ? ` [Keyakinan AI: ${Math.round(Number(pd.confidence) * (Number(pd.confidence) <= 1 ? 100 : 1))}%]` : '';
            const note = pd.notes ? ` — ${pd.notes}` : '';
            aLines.push(`- Diagnosis Primer (Kerja): ${pd.diagnosis}${icd}${conf}${note}`);
          }
          if (Array.isArray(ass.differential_diagnoses)) {
            ass.differential_diagnoses.forEach((dd: any) => {
              const icd = dd.icd10 ? ` (ICD-10: ${dd.icd10})` : '';
              const conf = dd.confidence ? ` [Keyakinan AI: ${Math.round(Number(dd.confidence) * (Number(dd.confidence) <= 1 ? 100 : 1))}%]` : '';
              const note = dd.notes || dd.clinical_clues ? ` — ${dd.notes || dd.clinical_clues}` : '';
              aLines.push(`- Diagnosis Banding: ${dd.diagnosis}${icd}${conf}${note}`);
            });
          }
          if (ass.clinical_reasoning) aLines.push(`- Penalaran Klinis: ${ass.clinical_reasoning}`);
          if (aLines.length > 0) a = aLines.join('\n');
        }

        // Plan
        if (!p && soapObj.plan) {
          const pl = soapObj.plan;
          const pLines: string[] = [];
          if (Array.isArray(pl.medications) && pl.medications.length > 0) {
            pLines.push(`- Rekomendasi Terapi Obat:`);
            pl.medications.forEach((m: any) => {
              const note = m.notes ? ` (${m.notes})` : '';
              pLines.push(`  • ${m.drug_name} ${m.dosage || ''} ${m.frequency || ''} ${m.route || 'Oral'}${note}`);
            });
          }
          if (Array.isArray(pl.diagnostic_workup) && pl.diagnostic_workup.length > 0) {
            pLines.push(`- Pemeriksaan Penunjang: ${pl.diagnostic_workup.join(', ')}`);
          }
          if (Array.isArray(pl.clinical_procedures) && pl.clinical_procedures.length > 0) {
            pLines.push(`- Prosedur / Tindakan Klinis: ${pl.clinical_procedures.join(', ')}`);
          }
          if (pl.follow_up) pLines.push(`- Rencana Kontrol / Tindak Lanjut: ${pl.follow_up}`);
          if (pLines.length > 0) p = pLines.join('\n');
        }

        // Instructions
        if (!i_inst) {
          const iLines: string[] = [];
          if (soapObj.plan?.patient_education && Array.isArray(soapObj.plan.patient_education)) {
            soapObj.plan.patient_education.forEach((e: string) => iLines.push(`- Edukasi Pasien: ${e}`));
          }
          if (soapObj.red_flags && Array.isArray(soapObj.red_flags)) {
            soapObj.red_flags.forEach((r: any) => {
              iLines.push(`- Tanda Bahaya (Red Flag) [${r.severity || 'Peringatan'}]: ${r.title} — ${r.action_required}`);
            });
          }
          if (iLines.length > 0) i_inst = iLines.join('\n');
        }

        if (s && o && a && p) break;
      }
    }
  }

  // 2. Parse from Content string
  if (content) {
    // A. Table row format (| **Subjective (S)** | ... |)
    const sTable = extractTableRow(content, /Subjective|👤\s*S\b|\bS\s*\(Subjective\)/i);
    const oTable = extractTableRow(content, /Objective|🔬\s*O\b|\bO\s*\(Objective\)/i);
    const aTable = extractTableRow(content, /Assessment|🎯\s*A\b|\bA\s*\(Assessment\)/i);
    const pTable = extractTableRow(content, /Plan|💊\s*P\b|\bP\s*\(Plan\)/i);
    const iTable = extractTableRow(content, /Instruksi|Instruction|📝\s*I\b|\bI\s*\(Instruksi\)/i);

    if (sTable && !s) s = sTable;
    if (oTable && !o) o = oTable;
    if (aTable && !a) a = aTable;
    if (pTable && !p) p = pTable;
    if (iTable && !i_inst) i_inst = iTable;

    // B. Section headers format (### 👤 S — Subjective, ### S — Subjective, etc.)
    if (!s) {
      const sSec = content.match(/(?:###|\*\*|##)\s*(?:👤\s*)?(?:S\s*[—\-:\.]\s*Subjective|Subjective|Hasil Anamnesis)[\s\S]*?(?=(?:###|\*\*|##)\s*(?:🔬\s*)?(?:O\s*[—\-:\.]\s*Objective|Objective|Evaluasi Hasil Lab|Tanda Vital|🎯|💊|📋)|$)/i);
      if (sSec && sSec[0]) {
        s = cleanMarkdown(sSec[0].replace(/^(?:###|\*\*|##).*?\n/i, ''));
      }
    }

    if (!o) {
      const oSec = content.match(/(?:###|\*\*|##)\s*(?:🔬\s*)?(?:O\s*[—\-:\.]\s*Objective|Objective|Evaluasi Hasil Lab|Tanda Vital)[\s\S]*?(?=(?:###|\*\*|##)\s*(?:🎯\s*)?(?:A\s*[—\-:\.]\s*Assessment|Assessment|Rekomendasi Diagnosis|💊|📋)|$)/i);
      if (oSec && oSec[0]) {
        o = cleanMarkdown(oSec[0].replace(/^(?:###|\*\*|##).*?\n/i, ''));
      }
    }

    if (!a) {
      const aSec = content.match(/(?:###|\*\*|##)\s*(?:🎯\s*)?(?:A\s*[—\-:\.]\s*Assessment|Assessment|Rekomendasi Diagnosis|Diagnosis Kerja)[\s\S]*?(?=(?:###|\*\*|##)\s*(?:💊\s*)?(?:P\s*[—\-:\.]\s*Plan|Plan|Rekomendasi Terapi Obat|Rejimen|📋)|$)/i);
      if (aSec && aSec[0]) {
        a = cleanMarkdown(aSec[0].replace(/^(?:###|\*\*|##).*?\n/i, ''));
      }
    }

    if (!p) {
      const pSec = content.match(/(?:###|\*\*|##)\s*(?:💊\s*)?(?:P\s*[—\-:\.]\s*Plan.*?|Plan|Rekomendasi Terapi Obat|Rejimen Farmakoterapi)[\s\S]*?(?=(?:###|\*\*|##)\s*(?:📝\s*)?(?:I\s*[—\-:\.]\s*Instruksi|Instruksi|Instruksi PPA|Instruksi Klinis|Edukasi Pasien|Tanda Bahaya|🛡️|📋)|---\n|\*\(⚠️|$)/i);
      if (pSec && pSec[0]) {
        p = cleanMarkdown(pSec[0].replace(/^(?:###|\*\*|##).*?\n/i, ''));
      }
    }

    if (!i_inst) {
      const iSec = content.match(/(?:###|\*\*|##)\s*(?:📝\s*)?(?:I\s*[—\-:\.]\s*Instruksi|Instruksi.*?|Instruksi PPA|Instruksi Klinis|Edukasi Pasien|Tanda Bahaya)[\s\S]*?(?=(?:###\s*🛡️|---\n|\*\(⚠️|##\s*📋|$))/i);
      if (iSec && iSec[0]) {
        i_inst = cleanMarkdown(iSec[0].replace(/^(?:###|\*\*|##).*?\n/i, ''));
      }
    }
  }

  // 3. Scan previous assistant messages in the conversation (prioritize audio recordings / diarized summaries!)
  if (allMessages && allMessages.length > 0 && (!s || !o || !a || !p)) {
    for (let i = allMessages.length - 1; i >= 0; i--) {
      const msg = allMessages[i];
      if (msg.role !== 'assistant') continue;
      const t = msg.content;

      if (
        t.includes('Resume Klinis (S-O-A-P)') ||
        t.includes('Transkrip Percakapan Medis') ||
        (t.includes('S — Subjective') && t.includes('O — Objective')) ||
        t.includes('CPPT')
      ) {
        const audioS = t.match(/(?:###|\*\*|##)\s*(?:👤\s*)?(?:S\s*[—\-:\.]\s*Subjective|Subjective)[\s\S]*?(?=(?:###|\*\*|##)\s*(?:🔬\s*)?(?:O\s*[—\-:\.]\s*Objective|Objective|🎯|💊|📋)|$)/i);
        const audioO = t.match(/(?:###|\*\*|##)\s*(?:🔬\s*)?(?:O\s*[—\-:\.]\s*Objective|Objective)[\s\S]*?(?=(?:###|\*\*|##)\s*(?:🎯\s*)?(?:A\s*[—\-:\.]\s*Assessment|Assessment|💊|📋)|$)/i);
        const audioA = t.match(/(?:###|\*\*|##)\s*(?:🎯\s*)?(?:A\s*[—\-:\.]\s*Assessment|Assessment)[\s\S]*?(?=(?:###|\*\*|##)\s*(?:💊\s*)?(?:P\s*[—\-:\.]\s*Plan|Plan|📋)|$)/i);
        const audioP = t.match(/(?:###|\*\*|##)\s*(?:💊\s*)?(?:P\s*[—\-:\.]\s*Plan.*?|Plan)[\s\S]*?(?=(?:###|\*\*|##)\s*(?:📝\s*)?(?:I\s*[—\-:\.]\s*Instruksi|Instruksi|🛡️)|---\n|\*\(⚠️|##\s*📋|$)/i);
        const audioI = t.match(/(?:###|\*\*|##)\s*(?:📝\s*)?(?:I\s*[—\-:\.]\s*Instruksi|Instruksi)[\s\S]*?(?=(?:###\s*🛡️|---\n|\*\(⚠️|##\s*📋|$))/i);

        if (!s && audioS && audioS[0]) s = cleanMarkdown(audioS[0].replace(/^(?:###|\*\*|##).*?\n/i, ''));
        if (!o && audioO && audioO[0]) o = cleanMarkdown(audioO[0].replace(/^(?:###|\*\*|##).*?\n/i, ''));
        if (!a && audioA && audioA[0]) a = cleanMarkdown(audioA[0].replace(/^(?:###|\*\*|##).*?\n/i, ''));
        if (!p && audioP && audioP[0]) p = cleanMarkdown(audioP[0].replace(/^(?:###|\*\*|##).*?\n/i, ''));
        if (!i_inst && audioI && audioI[0]) i_inst = cleanMarkdown(audioI[0].replace(/^(?:###|\*\*|##).*?\n/i, ''));

        if (s && o && a && p) break;
      }
    }
  }

  // 4. Fallback from patient record if still missing
  if (!s && patient) {
    const sParts: string[] = [];
    if (patient.allergies && patient.allergies.length > 0) sParts.push(`- Riwayat Alergi: ${patient.allergies.join(', ')}`);
    if (patient.current_medications && patient.current_medications.length > 0) {
      sParts.push(`- Riwayat Obat Rutin: ${patient.current_medications.map(m => `${m.name} ${m.dosage || ''}`).join(', ')}`);
    }
    if (patient.diagnoses && patient.diagnoses.length > 0) sParts.push(`- Riwayat Penyakit Dahulu: ${patient.diagnoses.join(', ')}`);
    if (sParts.length > 0) s = sParts.join('\n');
  }

  if (!o && patient?.vitals && Object.keys(patient.vitals).length > 0) {
    const v = patient.vitals as Record<string, string>;
    const vitalsStr = [
      v.bp || v.blood_pressure ? `TD ${v.bp || v.blood_pressure}` : '',
      v.hr || v.heart_rate ? `HR ${v.hr || v.heart_rate}` : '',
      v.rr || v.respiratory_rate ? `RR ${v.rr || v.respiratory_rate}` : '',
      v.temp || v.temperature ? `Suhu ${v.temp || v.temperature}` : '',
      v.spo2 ? `SpO2 ${v.spo2}` : ''
    ].filter(Boolean).join(', ');
    if (vitalsStr) o = `- Tanda Vital Pasien (SIMRS): ${vitalsStr}`;
  }

  if (!a && patient?.diagnoses && patient.diagnoses.length > 0) {
    a = `- Diagnosis Primer (SIMRS): ${patient.diagnoses[0]}\n${patient.diagnoses.slice(1).map(d => `- Diagnosis Banding: ${d}`).join('\n')}`;
  }

  if (!p && patient?.current_medications && patient.current_medications.length > 0) {
    p = `- Lanjutkan Terapi Rutin SIMRS:\n${patient.current_medications.map(m => `  • ${m.name} ${m.dosage || ''}`).join('\n')}\n- Kontrol poliklinik berkala.`;
  }

  return {
    subjective: s || '- Keluhan Utama: Pasien datang untuk kontrol berkala.\n- Riwayat Penyakit Sekarang: Evaluasi keluhan klinis.',
    objective: o || '- Tanda-Tanda Vital: Dalam batas evaluasi klinis.\n- Hasil Pemeriksaan Penunjang: Evaluasi laboratorium terlampir.',
    assessment: a || '- Diagnosis Kerja: Evaluasi klinis dan kodefikasi ICD-10.',
    plan: p || '- Terapi Farmakoterapi & Rencana Penatalaksanaan Lanjutan.',
    instructions: i_inst || '- Edukasi kepatuhan minum obat teratur.\n- Kontrol poliklinik berkala dalam 2-4 minggu.\n- Segera ke IGD bila timbul tanda bahaya (red flags).'
  };
}

// Preset clinical instructions data items for quick insertion
const INSTRUCTION_CATEGORIES = [
  {
    category: 'Instruksi Pemantauan & TTV',
    icon: '🩺',
    items: [
      { label: 'Monitoring TTV per 8 Jam', text: '- Monitoring tanda-tanda vital (TD, HR, RR, Suhu, SpO2) berkala setiap 8 jam.' },
      { label: 'Pantau Diuresis & Keseimbangan Cairan', text: '- Pantau ketat diuresis urin dan keseimbangan cairan masuk/keluar (fluid balance) per 24 jam.' },
      { label: 'Pemantauan Gula Darah Mandiri (SMBG)', text: '- Pemantauan glukosa darah mandiri (SMBG): periksa GDP pagi hari dan 2 jam pasca makan 3x seminggu.' },
      { label: 'Awasi Tanda Bahaya Hipoglikemia', text: '- Edukasi pasien dan keluarga: bila muncul keringat dingin, gemetar, atau pusing (hipoglikemia), segera konsumsi air gula 1-2 sendok.' },
    ],
  },
  {
    category: 'Instruksi Terapi & Tindakan',
    icon: '💉',
    items: [
      { label: 'Edukasi Kepatuhan Minum Obat Rutin', text: '- Minum obat antihipertensi dan antidiabetes secara teratur sesuai jadwal, jangan menghentikan obat tanpa instruksi dokter.' },
      { label: 'Minum PPI 30 Menit Sebelum Makan', text: '- Obat penekan asam lambung (PPI/Omeprazole) diminum 30 menit sebelum makan pagi.' },
      { label: 'Pemberian Oksigen Kanul Nasal 3 lpm jika Sesak', text: '- Berikan Oksigen kanul nasal 2-3 lpm bila pasien mengeluh sesak napas atau SpO2 < 95%.' },
      { label: 'Tirah Baring (Bed Rest) Semi-Fowler', text: '- Pasien dianjurkan istirahat tirah baring (bed rest) dengan posisi kepala ditinggikan (semi-Fowler 30-45 derajat).' },
    ],
  },
  {
    category: 'Diet, Edukasi & Jadwal Kontrol',
    icon: '🥗',
    items: [
      { label: 'Diet Rendah Garam (RG < 2g/hari)', text: '- Diet Rendah Garam: Batasi asupan natrium/garam maksimal 2 gram (1 sendok teh) per hari.' },
      { label: 'Diet DM Rendah Karbohidrat Olahan', text: '- Diet Diabetes Melitus: Kurangi makanan tinggi indeks glikemik, batasi gula murni, dan perbanyak serat sayuran.' },
      { label: 'Jadwal Kontrol Poli Rawat Jalan 2-4 Minggu', text: '- Jadwal kontrol ulang ke Poli Rawat Jalan dalam 2-4 minggu dengan membawa hasil evaluasi lab terbaru.' },
      { label: 'Segera ke IGD Jika Tanda Bahaya Akut', text: '- Segera bawa pasien ke IGD terdekat bila mengalami nyeri dada memberat, sesak napas akut, atau penurunan kesadaran.' },
    ],
  },
];

// Preset clinical anamnesis data items for quick insertion
const ANAMNESIS_CATEGORIES = [
  {
    category: 'Keluhan & RPS',
    icon: '💬',
    items: [
      { label: 'Nyeri Ulu Hati Terbakar (1 Minggu)', text: '- Keluhan Utama: Nyeri ulu hati terasa perih terbakar sejak 1 minggu terakhir, bertambah saat perut kosong dan malam hari.' },
      { label: 'Pusing, Lemas & Nokturia (3 Hari)', text: '- Riwayat Sekarang: Pusing berputar, badan lemas sejak 3 hari, sering kencing malam hari (nokturia 3-4x).' },
      { label: 'Sesak Napas Saat Aktivitas / Tidur', text: '- Riwayat Sekarang: Sesak napas bertambah saat beraktivitas berat dan posisi tidur terlentang (ortopnea ringan).' },
      { label: 'Nyeri Dada Kiri Tertindih Beban', text: '- Keluhan Utama: Rasa tidak nyaman/dada kiri seperti tertindih beban berat menjalar ke punggung saat lelah.' },
      { label: 'Demam Naik Turun & Batuk Berdahak', text: '- Keluhan Sekarang: Demam menggigil naik turun sejak 4 hari disertai batuk berdahak kekuningan.' },
    ],
  },
  {
    category: 'Riwayat Penyakit (RPD & RPK)',
    icon: '📋',
    items: [
      { label: 'Gastritis Kronis / Dispepsia Berulang', text: '- RPD: Riwayat Gastritis Kronis / Dispepsia fungsional berulang sejak 2 tahun lalu.' },
      { label: 'Diabetes Melitus Tipe 2 (5 Tahun)', text: '- RPD: Riwayat Diabetes Melitus Tipe 2 terdiagnosis 5 tahun, kontrol rutin berkala.' },
      { label: 'Hipertensi Grade 1 (3 Tahun)', text: '- RPD: Riwayat Hipertensi Grade 1 sejak 3 tahun lalu.' },
      { label: 'PJK CAD Post-PCI Stent (1 Tahun)', text: '- RPD: Riwayat Penyakit Jantung Koroner (CAD post-PCI stent LAD 1 tahun lalu).' },
      { label: 'RPK: Riwayat DM & Hipertensi Keluarga', text: '- RPK: Riwayat Diabetes Melitus pada Ibu dan Hipertensi/Stroke pada Ayah.' },
      { label: 'Tidak Ada Riwayat Penyakit Kronis', text: '- RPD/RPK: Tidak ada riwayat penyakit kronis terdahulu atau penyakit herediter dalam keluarga.' },
    ],
  },
  {
    category: 'Alergi, Obat & Gaya Hidup',
    icon: '🛡️',
    items: [
      { label: 'Tidak Ada Riwayat Alergi (NKDA)', text: '- Riwayat Alergi: Tidak ada riwayat alergi obat atau makanan (No Known Drug Allergies - NKDA).' },
      { label: 'Alergi Golongan Penisilin / Amoxicillin', text: '- Riwayat Alergi: Alergi Antibiotik Golongan Penisilin / Amoxicillin (reaksi gatal dan biduran).' },
      { label: 'Alergi Obat NSAID (Aspirin/Ibuprofen)', text: '- Riwayat Alergi: Alergi Obat Golongan NSAID (Aspirin/Ibuprofen - reaksi sesak napas / bronkospasme).' },
      { label: 'Obat Rutin: Metformin & Lisinopril', text: '- Riwayat Pengobatan: Metformin 500mg 2x1 tablet p.c., Lisinopril 10mg 1x1 tablet pagi.' },
      { label: 'Obat Rutin: Antasida / PPI Mandiri', text: '- Riwayat Pengobatan: Antasida sirup 3x1 sendok makan dan Omeprazole 20mg kapsul minum mandiri.' },
      { label: 'Gaya Hidup: Pola Makan & Kafein Kopi', text: '- Faktor Gaya Hidup: Pola makan sering terlambat, konsumsi kopi 2-3 cangkir/hari, stres kerja (+), merokok (-).' },
      { label: 'Gaya Hidup: Merokok Aktif 1 Bungkus/Hari', text: '- Faktor Gaya Hidup: Riwayat merokok aktif 1 bungkus/hari selama 10 tahun, alkohol (-).' },
    ],
  },
];

// Preset clinical observation data items for quick insertion
const OBSERVATION_CATEGORIES = [
  {
    category: 'Tanda Vital (TTV)',
    icon: '🩺',
    items: [
      { label: 'TD Normal (120/80 mmHg)', text: '- Tekanan Darah: 120/80 mmHg (Normotensi)' },
      { label: 'TD Hipertensi Tk. 1 (140/90 mmHg)', text: '- Tekanan Darah: 140/90 mmHg (Stage 1 HT)' },
      { label: 'Frekuensi Nadi 78 bpm (Reguler)', text: '- Frekuensi Nadi (HR): 78 x/menit, reguler, kuat angkat' },
      { label: 'Laju Napas 18 x/menit', text: '- Laju Pernapasan (RR): 18 x/menit, pola napas spontan' },
      { label: 'Suhu 36.5 °C (Afebris)', text: '- Suhu Tubuh (T): 36.5 °C (Afebris)' },
      { label: 'Saturasi SpO2 98% Room Air', text: '- Saturasi Oksigen (SpO2): 98% room air' },
      { label: 'Kesadaran Compos Mentis (GCS 15)', text: '- Tingkat Kesadaran: Compos Mentis (GCS 15 E4M6V5)' },
    ],
  },
  {
    category: 'Pemeriksaan Fisik Klinis',
    icon: '🔬',
    items: [
      { label: 'Mata: Konjungtiva Anemis (-/-), Sklera Ikterik (-/-)', text: '- Mata: Konjungtiva anemis (-/-), sklera ikterik (-/-), pupil isokor 3mm/3mm' },
      { label: 'Thoraks: Cor/Pulmo Normal Vesikuler', text: '- Thoraks: Cor BJ I-II reguler murni, Pulmo suara napas vesikuler (+/+), Rh (-/-), Wh (-/-)' },
      { label: 'Abdomen: Supel, BU (+), Nyeri Epigastrium (+)', text: '- Abdomen: Dinding perut supel, bising usus normal (8-10x/m), nyeri tekan epigastrium (+)' },
      { label: 'Abdomen: Nyeri Tekan (-), Hepatosplenomegali (-)', text: '- Abdomen: Supel, nyeri tekan (-), hepar dan lien tidak teraba membesar' },
      { label: 'Ekstremitas: Akral Hangat, Edema (-/-), CRT <2s', text: '- Ekstremitas: Akral hangat, CRT < 2 detik, edema pretibial (-/-)' },
    ],
  },
  {
    category: 'Hasil Laboratorium Serial',
    icon: '🧪',
    items: [
      { label: 'Hemoglobin (Hb) 12.8 g/dL', text: '- Hemoglobin (Hb): 12.8 g/dL (Nilai Rujukan: 12.0 - 16.0 g/dL)' },
      { label: 'Leukosit 7.400 /µL (Normal)', text: '- Leukosit: 7.400 /µL (Nilai Rujukan: 4.000 - 10.000 /µL)' },
      { label: 'Gula Darah Sewaktu (GDS) 115 mg/dL', text: '- Gula Darah Sewaktu (GDS): 115 mg/dL' },
      { label: 'GDP 138 mg/dL & HbA1c 7.2%', text: '- Kontrol Glikemik: GDP 138 mg/dL, HbA1c 7.2% (Suboptimal Control)' },
      { label: 'eGFR 58 mL/min (CKD 3a) & Cr 1.30 mg/dL', text: '- Fungsi Ginjal: eGFR 58.0 mL/min/1.73m² (CKD Stadium 3a), Kreatinin 1.30 mg/dL' },
      { label: 'Elektrolit: Na 140, K 4.2, Cl 101 mEq/L', text: '- Elektrolit: Natrium 140 mEq/L, Kalium 4.2 mEq/L, Klorida 101 mEq/L (Normal)' },
      { label: 'Rasio Albumin-Kreatinin Urin (uACR) 42 mg/g', text: '- Urinalisis: Rasio uACR 42.0 mg/g (Mikroalbuminuria Positif)' },
    ],
  },
];

// Helper to extract actual patient anamnesis items dynamically from patient records & chat history
export function extractPatientAnamnesisCategories(
  patient?: PatientRecord | null,
  allMessages?: Array<{ role: string; content: string }>
) {
  const patientItems: Array<{ label: string; text: string }> = [];

  // 1. Extract from allMessages (look for Anamnesis tables / messages)
  if (allMessages && allMessages.length > 0) {
    for (let i = allMessages.length - 1; i >= 0; i--) {
      const t = allMessages[i].content;
      if (allMessages[i].role !== 'assistant') continue;

      const extractRow = (regex: RegExp) => {
        const lines = t.split('\n');
        for (const line of lines) {
          if (regex.test(line) && line.includes('|')) {
            const parts = line.split('|').map(x => x.trim()).filter(Boolean);
            if (parts.length >= 2) return cleanMarkdown(parts.slice(1).join(' '));
          }
        }
        return '';
      };

      const cc = extractRow(/Keluhan Utama|Chief Complaint/i);
      const rps = extractRow(/Riwayat Penyakit Sekarang|RPS|HPI/i);
      const rpd = extractRow(/Riwayat Penyakit Dahulu|RPD/i);
      const rpk = extractRow(/Riwayat Penyakit Keluarga|RPK/i);
      const med = extractRow(/Riwayat Pengobatan|Pengobatan Terkini/i);
      const alg = extractRow(/Riwayat Alergi|Alergi/i);
      const life = extractRow(/Faktor Gaya Hidup|Gaya Hidup/i);

      if (cc && !patientItems.some(item => item.label.includes('Keluhan Utama'))) {
        patientItems.push({ label: `Keluhan Utama: ${cc.slice(0, 30)}…`, text: `- Keluhan Utama: ${cc}` });
      }
      if (rps && !patientItems.some(item => item.label.includes('RPS'))) {
        patientItems.push({ label: `RPS: ${rps.slice(0, 30)}…`, text: `- Riwayat Penyakit Sekarang (RPS): ${rps}` });
      }
      if (rpd && !patientItems.some(item => item.label.includes('RPD'))) {
        patientItems.push({ label: `RPD: ${rpd.slice(0, 30)}…`, text: `- Riwayat Penyakit Dahulu (RPD): ${rpd}` });
      }
      if (rpk && !patientItems.some(item => item.label.includes('RPK'))) {
        patientItems.push({ label: `RPK: ${rpk.slice(0, 30)}…`, text: `- Riwayat Penyakit Keluarga (RPK): ${rpk}` });
      }
      if (alg && !patientItems.some(item => item.label.includes('Alergi'))) {
        patientItems.push({ label: `Alergi: ${alg.slice(0, 30)}…`, text: `- Riwayat Alergi: ${alg}` });
      }
      if (med && !patientItems.some(item => item.label.includes('Pengobatan'))) {
        patientItems.push({ label: `Obat: ${med.slice(0, 30)}…`, text: `- Riwayat Pengobatan: ${med}` });
      }
      if (life && !patientItems.some(item => item.label.includes('Gaya Hidup'))) {
        patientItems.push({ label: `Gaya Hidup: ${life.slice(0, 30)}…`, text: `- Faktor Gaya Hidup: ${life}` });
      }
    }
  }

  // 2. Extract from Patient Record object if present
  if (patient) {
    if (patient.allergies && patient.allergies.length > 0 && !patientItems.some(item => item.label.includes('Alergi'))) {
      const algStr = patient.allergies.join(', ');
      patientItems.push({ label: `Alergi Pasien (${algStr})`, text: `- Riwayat Alergi (SIMRS): ${algStr}` });
    }
    if (patient.current_medications && patient.current_medications.length > 0 && !patientItems.some(item => item.label.includes('Pengobatan') || item.label.includes('Obat'))) {
      const medStr = patient.current_medications.map(m => `${m.name} ${m.dosage}`).join(', ');
      patientItems.push({ label: `Obat Pasien (${medStr.slice(0, 26)}…)`, text: `- Riwayat Pengobatan Rutin (SIMRS): ${medStr}` });
    }
    if (patient.diagnoses && patient.diagnoses.length > 0 && !patientItems.some(item => item.label.includes('RPD'))) {
      const diagStr = patient.diagnoses.join(', ');
      patientItems.push({ label: `RPD Pasien (${diagStr.slice(0, 26)}…)`, text: `- Riwayat Penyakit Dahulu (SIMRS): ${diagStr}` });
    }
  }

  const result = [];
  if (patientItems.length > 0) {
    result.push({
      category: 'Data Anamnesis Pasien Ini (SIMRS RME)',
      icon: '🌟',
      items: patientItems,
    });
  }

  result.push(...ANAMNESIS_CATEGORIES);
  return result;
}

// Helper to extract actual patient observation & lab items dynamically
export function extractPatientObservationCategories(
  patient?: PatientRecord | null,
  allMessages?: Array<{ role: string; content: string }>
) {
  const patientItems: Array<{ label: string; text: string }> = [];

  // 1. Extract vitals from patient record
  if (patient?.vitals && Object.keys(patient.vitals).length > 0) {
    const v = patient.vitals as Record<string, string>;
    const bp = v.blood_pressure || v.bp || v.BP;
    const hr = v.heart_rate || v.hr || v.pulse || v.Pulse;
    const rr = v.respiratory_rate || v.rr || v.RR;
    const temp = v.temperature || v.temp || v.Temp;
    const spo2 = v.spo2 || v.SpO2 || v.oxygen_saturation;

    const vitalsSummaryParts = [];
    if (bp) vitalsSummaryParts.push(`TD ${bp} mmHg`);
    if (hr) vitalsSummaryParts.push(`HR ${hr} bpm`);
    if (rr) vitalsSummaryParts.push(`RR ${rr} x/m`);
    if (temp) vitalsSummaryParts.push(`Suhu ${temp}`);
    if (spo2) vitalsSummaryParts.push(`SpO2 ${spo2}`);

    if (vitalsSummaryParts.length > 0) {
      patientItems.push({
        label: `TTV Pasien: ${vitalsSummaryParts.slice(0, 3).join(', ')}`,
        text: `- Tanda Vital Pasien (SIMRS): ${vitalsSummaryParts.join(', ')}`,
      });
    }
  }

  // 2. Extract recent labs from patient record
  if (patient?.recent_labs && Object.keys(patient.recent_labs).length > 0) {
    const labsList = Object.entries(patient.recent_labs).map(([k, val]) => `${k}: ${val}`);
    patientItems.push({
      label: `Lab Pasien: ${labsList.slice(0, 3).join(', ')}`,
      text: `- Hasil Laboratorium Pasien (SIMRS): ${labsList.join(', ')}`,
    });
  }

  // 3. Extract from messages (look for Lab evaluation tables)
  if (allMessages && allMessages.length > 0) {
    for (let i = allMessages.length - 1; i >= 0; i--) {
      const t = allMessages[i].content;
      if (allMessages[i].role !== 'assistant') continue;

      if (t.includes('Hasil Laboratorium') || t.includes('Pemeriksaan Penunjang') || t.includes('eGFR') || t.includes('uACR')) {
        const labLines = t.split('\n').filter(l => l.includes('|') && !l.includes('---') && !l.includes('Parameter') && !l.includes('Pemeriksaan'));
        const labItems = labLines.slice(0, 6).map(l => {
          const parts = l.split('|').map(x => x.trim()).filter(Boolean);
          if (parts.length >= 2) return `${parts[0]}: ${parts[1]}`;
          return '';
        }).filter(Boolean);

        if (labItems.length > 0 && !patientItems.some(p => p.label.includes('Lab Evaluasi'))) {
          patientItems.push({
            label: `Lab Evaluasi: ${labItems.slice(0, 3).join(', ')}`,
            text: `- Evaluasi Laboratorium Terkini: ${labItems.join('; ')}`,
          });
        }
      }
    }
  }

  const result = [];
  if (patientItems.length > 0) {
    result.push({
      category: 'Data Observasi & Lab Pasien Ini (SIMRS RME)',
      icon: '🌟',
      items: patientItems,
    });
  }

  result.push(...OBSERVATION_CATEGORIES);
  return result;
}

// Preset clinical plan data items for quick insertion
const PLAN_CATEGORIES = [
  {
    category: 'Terapi Farmakologi Lini Pertama & Standar',
    icon: '💊',
    items: [
      { label: 'Omeprazole 20 mg PO 2x1 (30m ac)', text: '- Omeprazole 20 mg PO 2x sehari (30-60 menit ac)' },
      { label: 'Lansoprazole 30 mg PO 1x1 ac', text: '- Lansoprazole 30 mg PO 1x sehari (pagi ac)' },
      { label: 'Sucralfate suspensi 500mg/5mL 3x10mL ac', text: '- Sucralfate suspensi 500 mg/5 mL 3x10 mL PO (1 jam ac)' },
      { label: 'Metformin 500 mg PO 2x1 dc', text: '- Metformin 500 mg PO 2x sehari (bersama/sesudah makan)' },
      { label: 'Lisinopril 10 mg PO 1x1 pagi', text: '- Lisinopril 10 mg PO 1x sehari (pagi hari pc)' },
      { label: 'Amlodipine 5 mg PO 1x1 pagi', text: '- Amlodipine 5 mg PO 1x sehari (pagi hari pc)' },
      { label: 'Clopidogrel 75 mg PO 1x1 pc', text: '- Clopidogrel 75 mg PO 1x sehari (sesudah makan)' },
      { label: 'Rosuvastatin 20 mg PO 1x1 malam', text: '- Rosuvastatin 20 mg PO 1x sehari (malam hari)' },
      { label: 'Atorvastatin 20 mg PO 1x1 malam', text: '- Atorvastatin 20 mg PO 1x sehari (malam hari)' },
      { label: 'Paracetamol 500 mg PO 3x1 PRN', text: '- Paracetamol 500 mg PO 3x sehari PRN (bila demam/nyeri)' },
      { label: 'Cetirizine 10 mg PO 1x1 malam', text: '- Cetirizine 10 mg PO 1x sehari malam PRN' },
      { label: 'Salbutamol Inhaler 100 mcg 2 puff PRN', text: '- Salbutamol Inhaler 100 mcg 2 semprot PRN bila sesak napas' },
    ],
  },
  {
    category: 'Rencana Pemeriksaan Penunjang (Workup)',
    icon: '🔬',
    items: [
      { label: 'Darah Lengkap (CBC) & LFT/RFT serial', text: '- Rencana Lab: Pemeriksaan Darah Lengkap (CBC), Ureum, Kreatinin, SGOT/SGPT serial' },
      { label: 'HbA1c & Glukosa Puasa/2JPP', text: '- Rencana Lab: Evaluasi profil glikemik HbA1c & Glukosa Darah Puasa / 2JPP' },
      { label: 'Urinalisis & Rasio uACR', text: '- Rencana Lab: Urinalisis lengkap dan evaluasi rasio albumin-kreatinin urin (uACR)' },
      { label: 'Profil Lipid Lengkap (Puasa 10-12 jam)', text: '- Rencana Lab: Profil lipid lengkap (Kolesterol Total, LDL, HDL, Trigliserida)' },
      { label: 'Elektrokardiogram (EKG) 12-Lead ulang', text: '- Rencana Penunjang: Rekam EKG 12-lead berkala evaluasi iskemia/aritmia' },
      { label: 'USG Abdomen / Endoskopi SCBA (EGD)', text: '- Rencana Penunjang: Evaluasi USG Abdomen / Endoskopi Saluran Cerna Atas (EGD)' },
    ],
  },
  {
    category: 'Rencana Monitoring & Evaluasi Klinis',
    icon: '🩺',
    items: [
      { label: 'Monitoring TTV Tiap Kunjungan / Shift', text: '- Monitoring ketat Tanda-Tanda Vital (TD, HR, RR, Suhu, SpO2) tiap shift/kunjungan' },
      { label: 'Monitoring Gejala & Toleransi Terapi', text: '- Evaluasi klinis kepatuhan minum obat, toleransi saluran cerna, dan efek samping' },
      { label: 'Pemantauan Glukosa Mandiri (SMBG)', text: '- Pemantauan Gula Darah Mandiri (SMBG) pagi puasa dan 2 jam pasca makan' },
      { label: 'Monitoring Balance Cairan & Diuresis', text: '- Evaluasi keseimbangan cairan masuk-keluar dan tanda-tanda dehidrasi / edema' },
    ],
  },
  {
    category: 'Edukasi & Rencana Non-Farmakologi',
    icon: '🥗',
    items: [
      { label: 'Diet Rendah Garam & Rendah Gula', text: '- Edukasi Nutrisi: Pembatasan asupan natrium (<2g/hari) dan pengurangan karbohidrat sederhana' },
      { label: 'Diet Lambung Porsi Kecil Sering', text: '- Edukasi Nutrisi: Hindari makanan pedas, asam, kafein, bersoda; makan teratur porsi kecil sering' },
      { label: 'Aktivitas Fisik Aerobik 150m/minggu', text: '- Gaya Hidup: Olahraga aerobik intensitas sedang 150 menit/minggu secara bertahap' },
      { label: 'Kontrol Poliklinik 7-14 Hari', text: '- Rencana Kontrol: Jadwal kunjungan ulang poliklinik dalam 7-14 hari untuk evaluasi berkala' },
    ],
  },
];

// Helper to extract actual patient plan & AI therapy recommendations dynamically
export function extractPatientPlanCategories(
  patient?: PatientRecord | null,
  allMessages?: Array<{ role: string; content: string }>
) {
  const patientItems: Array<{ label: string; text: string }> = [];

  // 1. Extract from AI recommendations in messages (Therapy tables, medication lists, renal dosing)
  if (allMessages && allMessages.length > 0) {
    for (let i = allMessages.length - 1; i >= 0; i--) {
      const msg = allMessages[i];
      if (msg.role !== 'assistant') continue;
      const t = msg.content;

      // Extract medication table rows
      if (
        t.includes('Rekomendasi Terapi Obat') ||
        t.includes('Rejimen Farmakoterapi') ||
        t.includes('Nama Obat') ||
        t.includes('Dosis') ||
        t.includes('Terapi Lini Pertama')
      ) {
        const lines = t.split('\n').filter(l => l.includes('|') && !l.includes('---') && !l.includes('Nama Obat') && !l.includes('Parameter'));
        for (const line of lines.slice(0, 8)) {
          const parts = line.split('|').map(x => x.trim()).filter(Boolean);
          if (parts.length >= 2) {
            const drug = parts[0].replace(/\*\*/g, '');
            const dose = parts[1] || '';
            const freq = parts[2] || '';
            const timing = parts[3] || '';
            const fullText = `- ${drug} ${dose} ${freq} ${timing}`.trim();
            const labelText = `${drug} ${dose} ${freq}`.trim();
            if (labelText.length > 3 && !patientItems.some(p => p.label === labelText)) {
              patientItems.push({
                label: labelText.slice(0, 38),
                text: fullText,
              });
            }
          }
        }
      }

      // Extract bullet points from Plan section in AI output
      if (t.includes('### 💊 P') || t.includes('### P — Plan') || t.includes('### P - Plan')) {
        const pBlock = t.match(/(?:###|\*\*)\s*(?:💊\s*)?(?:P\s*[—\-\(:\.]\s*Plan.*?|Plan)[\s\S]*?(?=(?:###|\*\*)\s*(?:📝\s*)?(?:I\s*[—\-\(:\.]\s*Instruksi\)?|Instruksi|###\s*🛡️|---\n|\*\(⚠️|##\s*📋|$))/i);
        if (pBlock && pBlock[0]) {
          const pLines = pBlock[0].split('\n').filter(l => l.trim().startsWith('-') || l.trim().startsWith('*') || /^\d+\./.test(l.trim()));
          for (const l of pLines.slice(0, 6)) {
            const cleaned = l.replace(/^[\-\*\d\.\s]+/, '').replace(/\*\*/g, '').trim();
            if (cleaned.length > 5 && !patientItems.some(p => p.label.includes(cleaned.slice(0, 20)))) {
              patientItems.push({
                label: `AI Plan: ${cleaned.slice(0, 32)}…`,
                text: `- ${cleaned}`,
              });
            }
          }
        }
      }
    }
  }

  // 2. Extract active medications from patient record (SIMRS)
  if (patient?.current_medications && patient.current_medications.length > 0) {
    for (const med of patient.current_medications) {
      const medLabel = `SIMRS: ${med.name} ${med.dosage || ''}`.trim();
      const extraFreq = (med as any).frequency ? ` ${(med as any).frequency}` : '';
      const extraInd = (med as any).indication ? ` (Indikasi: ${(med as any).indication})` : '';
      if (!patientItems.some(p => p.label.includes(med.name))) {
        patientItems.push({
          label: medLabel.slice(0, 38),
          text: `- Lanjutkan Terapi Rutin SIMRS: ${med.name} ${med.dosage || ''}${extraFreq}${extraInd}`.trim(),
        });
      }
    }
  }

  const result = [];
  if (patientItems.length > 0) {
    result.push({
      category: 'Rekomendasi Terapi & Plan AI Pasien Ini',
      icon: '🌟',
      items: patientItems,
    });
  }

  result.push(...PLAN_CATEGORIES);
  return result;
}

export const DIAG_CATEGORIES = [
  'Semua',
  'Endokrin',
  'Metabolik',
  'Kardiovaskular',
  'Gastrointestinal',
  'Infeksi/GI',
  'Hepatologi',
  'Nefrologi',
  'Hematologi',
  'Respirasi',
  'Neurologi',
  'Muskuloskeletal',
];

export function extractPatientDiagnosisCategories(
  patient?: PatientRecord | null,
  allMessages?: Array<{ role: string; content: string }>
) {
  const primaryItems: Array<{ label: string; diagnosis: string; icd10: string; justification?: string }> = [];
  const diffItems: Array<{ label: string; diagnosis: string; icd10: string; clues?: string }> = [];

  // 1. Extract from AI recommendations in messages
  if (allMessages && allMessages.length > 0) {
    for (let i = allMessages.length - 1; i >= 0; i--) {
      const msg = allMessages[i];
      if (msg.role !== 'assistant') continue;
      const t = msg.content;

      if (t.includes('Diagnosis Kerja') || t.includes('Rekomendasi Diagnosis') || t.includes('Diagnosis Banding') || t.includes('ICD-10')) {
        const lines = t.split('\n');
        for (const line of lines) {
          if (line.includes('|') && !line.includes('---') && !line.includes('Diagnosis') && !line.includes('Parameter')) {
            const parts = line.split('|').map(x => x.trim()).filter(Boolean);
            if (parts.length >= 2) {
              const diagName = parts[0].replace(/\*\*/g, '').replace(/`/g, '');
              const icd = parts[1].replace(/`/g, '').replace(/\*\*/g, '');
              const justOrClues = parts[3] || parts[2] || '';

              if (diagName.length > 3 && !diagName.includes('Profil') && !diagName.includes('Kolom')) {
                if (line.toLowerCase().includes('primer') || line.toLowerCase().includes('kerja') || !primaryItems.length) {
                  if (!primaryItems.some(p => p.icd10 === icd || p.diagnosis === diagName)) {
                    primaryItems.push({
                      label: `${diagName} (${icd})`,
                      diagnosis: diagName,
                      icd10: icd,
                      justification: justOrClues.length > 5 ? justOrClues : undefined,
                    });
                  }
                } else {
                  if (!diffItems.some(d => d.icd10 === icd || d.diagnosis === diagName)) {
                    diffItems.push({
                      label: `${diagName} (${icd})`,
                      diagnosis: diagName,
                      icd10: icd,
                      clues: justOrClues.length > 5 ? justOrClues : undefined,
                    });
                  }
                }
              }
            }
          }
        }
      }
    }
  }

  // 2. Extract from patient EHR chronic diagnoses
  if (patient?.diagnoses && patient.diagnoses.length > 0) {
    for (const d of patient.diagnoses) {
      const match = d.match(/^(.*?)\s*(?:\(ICD-10\s*([^\)]+)\))?$/i);
      const name = match ? match[1].trim() : d;
      const code = match && match[2] ? match[2].trim() : 'Unspecified';
      if (!primaryItems.some(p => p.diagnosis === name || p.icd10 === code)) {
        primaryItems.push({
          label: `${name} (${code})`,
          diagnosis: name,
          icd10: code,
          justification: 'Riwayat diagnosis terdokumentasi di RME SIMRS',
        });
      }
    }
  }

  return { primaryItems, diffItems };
}

export default function CPPTEditorModal({
  isOpen,
  onClose,
  patient,
  messages,
  initialContent,
  onConfirmSend,
  isSubmitting = false,
}: CPPTEditorModalProps) {
  const [activeTab, setActiveTab] = useState<'all' | 'S' | 'O' | 'A' | 'P' | 'I'>('all');

  // Default CPPT values derived strictly from AI generated recommendations
  const [subjective, setSubjective] = useState('');
  const [objective, setObjective] = useState('');
  const [assessment, setAssessment] = useState('');
  const [plan, setPlan] = useState('');
  const [instructions, setInstructions] = useState('');

  // Anamnesis Picker State
  const [showAnamnesisPicker, setShowAnamnesisPicker] = useState(false);
  const [selectedAnamCategory, setSelectedAnamCategory] = useState<string>('all');
  const [customAnamLabel, setCustomAnamLabel] = useState('');
  const [customAnamValue, setCustomAnamValue] = useState('');

  // Observation Picker State
  const [showObservationPicker, setShowObservationPicker] = useState(false);
  const [selectedObsCategory, setSelectedObsCategory] = useState<string>('all');
  const [customObsLabel, setCustomObsLabel] = useState('');
  const [customObsValue, setCustomObsValue] = useState('');

  // Diagnosis Modal & Selection State
  const [showDiagnosisModal, setShowDiagnosisModal] = useState(false);
  const [diagSearchQuery, setDiagSearchQuery] = useState('');
  const [diagCategoryFilter, setDiagCategoryFilter] = useState('Semua');
  const [diagType, setDiagType] = useState<'primary' | 'differential'>('primary');
  const [selectedDiagName, setSelectedDiagName] = useState('');
  const [selectedDiagCode, setSelectedDiagCode] = useState('');
  const [diagJustification, setDiagJustification] = useState('');

  // Plan Picker State
  const [showPlanPicker, setShowPlanPicker] = useState(false);
  const [selectedPlanCategory, setSelectedPlanCategory] = useState<string>('all');
  const [customPlanLabel, setCustomPlanLabel] = useState('');
  const [customPlanValue, setCustomPlanValue] = useState('');

  // Instruction Picker State
  const [showInstructionPicker, setShowInstructionPicker] = useState(false);
  const [selectedInstCategory, setSelectedInstCategory] = useState<string>('all');
  const [customInstText, setCustomInstText] = useState('');

  // Dynamically compute categorized items from actual patient and messages
  const anamnesisCategories = React.useMemo(
    () => extractPatientAnamnesisCategories(patient, messages?.map(m => ({ role: m.role, content: m.content }))),
    [patient, messages]
  );

  const observationCategories = React.useMemo(
    () => extractPatientObservationCategories(patient, messages?.map(m => ({ role: m.role, content: m.content }))),
    [patient, messages]
  );

  const diagnosisCategories = React.useMemo(
    () => extractPatientDiagnosisCategories(patient, messages?.map(m => ({ role: m.role, content: m.content }))),
    [patient, messages]
  );

  const filteredIcd10List = React.useMemo(() => {
    const q = diagSearchQuery.toLowerCase().trim();
    return ICD10_DATABASE.filter((item) => {
      const matchesCat = diagCategoryFilter === 'Semua' || item.category === diagCategoryFilter;
      if (!matchesCat) return false;
      if (!q) return true;
      return (
        item.code.toLowerCase().includes(q) ||
        item.name.toLowerCase().includes(q) ||
        item.indonesian.toLowerCase().includes(q) ||
        item.category.toLowerCase().includes(q)
      );
    });
  }, [diagSearchQuery, diagCategoryFilter]);

  const handleSelectIcd10Item = (
    item: { code: string; name: string; indonesian: string },
    type: 'primary' | 'differential' = 'primary',
    justification?: string
  ) => {
    setSelectedDiagName(item.indonesian || item.name);
    setSelectedDiagCode(item.code);
    setDiagType(type);
    if (justification) {
      setDiagJustification(justification);
    }
  };

  // AI Diagnosis Workflow Generation State
  const [isGeneratingDiagnosis, setIsGeneratingDiagnosis] = useState(false);
  const [aiGeneratedDiagnoses, setAiGeneratedDiagnoses] = useState<Array<{
    id: string;
    type: 'primary' | 'differential';
    diagnosis: string;
    icd10: string;
    confidence?: string | number;
    justification?: string;
    selected: boolean;
  }>>([]);
  const [aiGenError, setAiGenError] = useState<string | null>(null);
  const [showAiDiagPanel, setShowAiDiagPanel] = useState(false);

  const handleGenerateAIDiagnosis = async () => {
    setIsGeneratingDiagnosis(true);
    setAiGenError(null);
    setShowAiDiagPanel(true);
    try {
      const pId = patient?.patient_id || 'P-001';
      const res = await AgentService.executeChat({
        user_query: 'Rekomendasi diagnosis kerja, diagnosis banding, dan kodefikasi ICD-10 pasien ini berdasarkan hasil pemeriksaan klinis, anamnesis, dan laboratorium SIMRS',
        patient_id: pId,
      });

      const items: Array<{
        id: string;
        type: 'primary' | 'differential';
        diagnosis: string;
        icd10: string;
        confidence?: string | number;
        justification?: string;
        selected: boolean;
      }> = [];

      const struct = res.structured_output as any;

      // 1. Parse structured Pydantic output if available
      if (struct?.assessment) {
        if (struct.assessment.primary_diagnosis) {
          const pd = struct.assessment.primary_diagnosis;
          items.push({
            id: `gen-prim-${Date.now()}-0`,
            type: 'primary',
            diagnosis: pd.diagnosis || 'Diagnosis Primer',
            icd10: pd.icd10 || 'Unspecified',
            confidence: pd.confidence ? `${Math.round(Number(pd.confidence) * (Number(pd.confidence) <= 1 ? 100 : 1))}%` : undefined,
            justification: pd.notes || pd.justification,
            selected: true,
          });
        }
        if (Array.isArray(struct.assessment.differential_diagnoses)) {
          struct.assessment.differential_diagnoses.forEach((dd: any, idx: number) => {
            items.push({
              id: `gen-diff-${Date.now()}-${idx + 1}`,
              type: 'differential',
              diagnosis: dd.diagnosis || 'Diagnosis Banding',
              icd10: dd.icd10 || 'Unspecified',
              confidence: dd.confidence ? `${Math.round(Number(dd.confidence) * (Number(dd.confidence) <= 1 ? 100 : 1))}%` : undefined,
              justification: dd.notes || dd.clinical_clues || dd.justification,
              selected: true,
            });
          });
        }
      }

      // 2. Fallback: Parse from Markdown table synthesis
      if (items.length === 0 && res.final_synthesis) {
        const parsedCat = extractPatientDiagnosisCategories(patient, [
          { role: 'assistant', content: res.final_synthesis }
        ]);
        parsedCat.primaryItems.forEach((p, idx) => {
          items.push({
            id: `gen-prim-${Date.now()}-${idx}`,
            type: 'primary',
            diagnosis: p.diagnosis,
            icd10: p.icd10,
            justification: p.justification,
            selected: true,
          });
        });
        parsedCat.diffItems.forEach((d, idx) => {
          items.push({
            id: `gen-diff-${Date.now()}-${idx}`,
            type: 'differential',
            diagnosis: d.diagnosis,
            icd10: d.icd10,
            justification: d.clues,
            selected: true,
          });
        });
      }

      if (items.length === 0) {
        setAiGenError('Tidak ada diagnosis spesifik yang diekstraksi dari respons AI.');
      } else {
        setAiGeneratedDiagnoses(items);
      }
    } catch (err: any) {
      setAiGenError(err?.message || 'Gagal memanggil workflow rekomendasi diagnosis AI.');
    } finally {
      setIsGeneratingDiagnosis(false);
    }
  };

  const handleToggleSelectAIDiag = (id: string) => {
    setAiGeneratedDiagnoses(prev =>
      prev.map(item => item.id === id ? { ...item, selected: !item.selected } : item)
    );
  };

  const handleSelectAllAIDiag = (selectAll: boolean) => {
    setAiGeneratedDiagnoses(prev =>
      prev.map(item => ({ ...item, selected: selectAll }))
    );
  };

  const handleInsertSelectedAIDiagnoses = () => {
    const selectedItems = aiGeneratedDiagnoses.filter(d => d.selected);
    if (selectedItems.length === 0) return;

    const formattedLines = selectedItems.map(item => {
      const isPrim = item.type === 'primary';
      const typeLabel = isPrim ? 'Diagnosis Primer (Kerja)' : 'Diagnosis Banding';
      const codePart = item.icd10 && item.icd10 !== 'Unspecified' ? ` (ICD-10: ${item.icd10})` : '';
      const confPart = item.confidence ? ` [Keyakinan AI: ${item.confidence}]` : '';
      const notePart = item.justification ? ` — ${isPrim ? 'Justifikasi' : 'Petunjuk'}: ${item.justification}` : '';
      return `- ${typeLabel}: ${item.diagnosis}${codePart}${confPart}${notePart}`;
    });

    const newText = formattedLines.join('\n');
    setAssessment(prev => {
      const trimmed = prev.trim();
      if (!trimmed) return newText;
      return `${trimmed}\n${newText}`;
    });
  };

  const handleInsertSingleAIDiag = (item: { type: string; diagnosis: string; icd10: string; confidence?: string | number; justification?: string }) => {
    const isPrim = item.type === 'primary';
    const typeLabel = isPrim ? 'Diagnosis Primer (Kerja)' : 'Diagnosis Banding';
    const codePart = item.icd10 && item.icd10 !== 'Unspecified' ? ` (ICD-10: ${item.icd10})` : '';
    const confPart = item.confidence ? ` [Keyakinan AI: ${item.confidence}]` : '';
    const notePart = item.justification ? ` — ${isPrim ? 'Justifikasi' : 'Petunjuk'}: ${item.justification}` : '';
    const itemText = `- ${typeLabel}: ${item.diagnosis}${codePart}${confPart}${notePart}`;

    setAssessment(prev => {
      const trimmed = prev.trim();
      if (!trimmed) return itemText;
      if (trimmed.includes(item.diagnosis)) return prev;
      return `${trimmed}\n${itemText}`;
    });
  };

  const handleAppendDiagnosis = () => {
    if (!selectedDiagName.trim() && !selectedDiagCode.trim()) return;
    const isPrim = diagType === 'primary';
    const typeLabel = isPrim ? 'Diagnosis Primer (Kerja)' : 'Diagnosis Banding';
    const codePart = selectedDiagCode.trim() ? ` (ICD-10: ${selectedDiagCode.trim()})` : '';
    const notePart = diagJustification.trim()
      ? isPrim
        ? ` — Justifikasi Klinis: ${diagJustification.trim()}`
        : ` — Petunjuk Klinis: ${diagJustification.trim()}`
      : '';
    const formatted = `- ${typeLabel}: ${selectedDiagName.trim()}${codePart}${notePart}`;

    setAssessment((prev) => {
      const trimmed = prev.trim();
      if (!trimmed) return formatted;
      if (trimmed.includes(formatted.trim())) return prev;
      return `${trimmed}\n${formatted}`;
    });

    // Reset selection and close modal
    setSelectedDiagName('');
    setSelectedDiagCode('');
    setDiagJustification('');
    setShowDiagnosisModal(false);
  };


  const planCategories = React.useMemo(
    () => extractPatientPlanCategories(patient, messages?.map(m => ({ role: m.role, content: m.content }))),
    [patient, messages]
  );

  const appendSubjectiveAnamnesis = (anamText: string) => {
    setSubjective((prev) => {
      const trimmed = prev.trim();
      if (!trimmed) return anamText;
      if (trimmed.includes(anamText.trim())) return prev;
      return `${trimmed}\n${anamText}`;
    });
  };

  const handleAddCustomAnamnesis = () => {
    if (!customAnamLabel.trim() && !customAnamValue.trim()) return;
    const formatted = `- ${customAnamLabel.trim() ? `${customAnamLabel.trim()}: ` : ''}${customAnamValue.trim()}`;
    appendSubjectiveAnamnesis(formatted);
    setCustomAnamLabel('');
    setCustomAnamValue('');
  };

  const appendObjectiveObservation = (obsText: string) => {
    setObjective((prev) => {
      const trimmed = prev.trim();
      if (!trimmed) return obsText;
      if (trimmed.includes(obsText.trim())) return prev;
      return `${trimmed}\n${obsText}`;
    });
  };

  const handleAddCustomObservation = () => {
    if (!customObsLabel.trim() && !customObsValue.trim()) return;
    const formatted = `- ${customObsLabel.trim() ? `${customObsLabel.trim()}: ` : ''}${customObsValue.trim()}`;
    appendObjectiveObservation(formatted);
    setCustomObsLabel('');
    setCustomObsValue('');
  };

  const appendPlanItem = (planText: string) => {
    setPlan((prev) => {
      const trimmed = prev.trim();
      if (!trimmed) return planText;
      if (trimmed.includes(planText.trim())) return prev;
      return `${trimmed}\n${planText}`;
    });
  };

  const handleAddCustomPlan = () => {
    if (!customPlanLabel.trim() && !customPlanValue.trim()) return;
    const formatted = `- ${customPlanLabel.trim() ? `${customPlanLabel.trim()}: ` : ''}${customPlanValue.trim()}`;
    appendPlanItem(formatted);
    setCustomPlanLabel('');
    setCustomPlanValue('');
  };

  const appendInstruction = (instText: string) => {
    setInstructions((prev) => {
      const trimmed = prev.trim();
      if (!trimmed) return instText;
      if (trimmed.includes(instText.trim())) return prev;
      return `${trimmed}\n${instText}`;
    });
  };

  const handleAddCustomInstruction = () => {
    if (!customInstText.trim()) return;
    const formatted = `- ${customInstText.trim()}`;
    appendInstruction(formatted);
    setCustomInstText('');
  };

  useEffect(() => {
    if (!isOpen) return;

    let s = initialContent?.subjective || '';
    let o = initialContent?.objective || '';
    let a = initialContent?.assessment || '';
    let p = initialContent?.plan || '';
    let inst = initialContent?.instructions || '';

    // If any section is missing or empty, extract from messages/patient
    if (!s || !o || !a || !p) {
      const parsed = parseSOAPFromAIText('', messages, patient);
      if (!s) s = parsed.subjective;
      if (!o) o = parsed.objective;
      if (!a) a = parsed.assessment;
      if (!p) p = parsed.plan;
      if (!inst) inst = parsed.instructions || '';
    }

    setSubjective(s);
    setObjective(o);
    setAssessment(a);
    setPlan(p);
    setInstructions(inst);
  }, [isOpen, initialContent, messages, patient]);

  if (!isOpen) return null;

  const handleConfirm = () => {
    onConfirmSend({
      subjective,
      objective,
      assessment,
      plan,
      instructions,
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-xs animate-in fade-in duration-200">
      <div className="bg-white dark:bg-slate-900 border border-emerald-500/30 rounded-3xl shadow-2xl w-full max-w-4xl max-h-[92vh] flex flex-col overflow-hidden transition-all">

        {/* Header Modal */}
        <div className="px-6 py-4 border-b border-emerald-100 dark:border-slate-800 bg-gradient-to-r from-emerald-50 via-teal-50 to-emerald-50/50 dark:from-slate-900 dark:via-slate-850 dark:to-slate-900 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-emerald-600 text-white flex items-center justify-center text-lg font-bold shadow-md shadow-emerald-600/20">
              📝
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-bold text-emerald-950 dark:text-slate-100">
                  Review & Konfirmasi CPPT (S/O/A/P + Instruksi) Pasien
                </h3>
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300 border border-amber-300 dark:border-amber-700">
                  ✏️ Mode Edit & Validasi DPJP
                </span>
              </div>
              <p className="text-xs text-emerald-700 dark:text-slate-400">
                Verifikasi dan sesuaikan isi catatan perkembangan terintegrasi sebelum ditransmisikan permanen ke RME SIMRS
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="w-8 h-8 rounded-xl flex items-center justify-center text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Patient Identity Strip */}
        <div className="px-6 py-2.5 bg-emerald-500/10 dark:bg-emerald-950/30 border-b border-emerald-100 dark:border-slate-800 flex items-center justify-between text-xs flex-wrap gap-2">
          <div className="flex items-center gap-4">
            <div>
              <span className="text-slate-500 dark:text-slate-400">Pasien: </span>
              <span className="font-bold text-emerald-900 dark:text-emerald-300">{patient?.name || 'Eleanor Vance'}</span>
            </div>
            <div>
              <span className="text-slate-500 dark:text-slate-400">MRN: </span>
              <span className="font-mono font-semibold text-emerald-800 dark:text-emerald-400">
                {patient?.patient_id ? `MRN-SIMRS-${patient.patient_id.replace('P-', '')}` : 'MRN-SIMRS-10492'}
              </span>
            </div>
            <div>
              <span className="text-slate-500 dark:text-slate-400">Usia/JK: </span>
              <span className="font-semibold text-slate-700 dark:text-slate-300">{patient?.age || 64} Th / {patient?.gender || 'Perempuan'}</span>
            </div>
          </div>
          <div className="text-[11px] font-semibold text-emerald-700 dark:text-emerald-400 bg-white dark:bg-slate-800 px-2.5 py-1 rounded-lg border border-emerald-200 dark:border-slate-700">
            🏥 DPJP: Dr. Sarah Jenkins, Sp.PD
          </div>
        </div>

        {/* Tabs Filter */}
        <div className="px-6 pt-3 pb-1 border-b border-emerald-100 dark:border-slate-800 bg-white dark:bg-slate-900 flex items-center gap-2">
          <span className="text-xs font-bold text-slate-500 dark:text-slate-400 mr-2">Tampilan:</span>
          {(['all', 'S', 'O', 'A', 'P', 'I'] as const).map((tab) => (
            <button
              key={tab}
              type="button"
              onClick={() => setActiveTab(tab)}
              className={`px-3 py-1 rounded-xl text-xs font-bold transition-all ${activeTab === tab
                ? 'bg-emerald-600 text-white shadow-xs'
                : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
                }`}
            >
              {tab === 'all' ? '📄 Semua (S-O-A-P-I)' : tab === 'I' ? 'Komponen I (Instruksi)' : `Komponen ${tab}`}
            </button>
          ))}
        </div>

        {/* Modal Body / Editable Form */}
        <div className="p-6 overflow-y-auto space-y-4 flex-1">
          {/* S - Subjective */}
          {(activeTab === 'all' || activeTab === 'S') && (
            <div className="rounded-2xl border border-emerald-200 dark:border-slate-700 bg-emerald-50/40 dark:bg-slate-850/60 p-4 transition-colors space-y-3">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <label className="text-xs font-bold text-emerald-900 dark:text-emerald-300 flex items-center gap-2">
                  <span className="w-5 h-5 rounded-md bg-emerald-600 text-white flex items-center justify-center text-[10px] font-black">S</span>
                  <span>Subjective (Data Anamnesis & Riwayat Keluhan Pasien)</span>
                </label>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => setShowAnamnesisPicker(!showAnamnesisPicker)}
                    className="px-2.5 py-1 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-[11px] font-bold flex items-center gap-1.5 transition-all shadow-xs"
                  >
                    <span>{showAnamnesisPicker ? '✕' : '➕'}</span>
                    <span>{showAnamnesisPicker ? 'Tutup Panel Anamnesis' : 'Tambah Anamnesis'}</span>
                  </button>
                </div>
              </div>

              {/* Interactive Anamnesis Data Inserter Panel */}
              {showAnamnesisPicker && (
                <div className="p-3.5 rounded-2xl bg-white dark:bg-slate-900 border border-emerald-300 dark:border-slate-700 shadow-sm space-y-3 animate-in fade-in zoom-in-95 duration-150">
                  <div className="flex items-center justify-between border-b border-emerald-100 dark:border-slate-800 pb-2">
                    <span className="text-xs font-bold text-emerald-950 dark:text-emerald-300 flex items-center gap-1.5">
                      <span>💬</span>
                      <span>Katalog Data Anamnesis Pasien (Klik untuk Menyisipkan ke Subjective)</span>
                    </span>
                    <div className="flex items-center gap-1 overflow-x-auto max-w-[65%] py-0.5">
                      <button
                        type="button"
                        onClick={() => setSelectedAnamCategory('all')}
                        className={`px-2 py-0.5 rounded-lg text-[10px] font-bold transition-all shrink-0 ${selectedAnamCategory === 'all'
                          ? 'bg-emerald-600 text-white shadow-2xs'
                          : 'bg-emerald-50 dark:bg-slate-800 text-emerald-800 dark:text-slate-300 hover:bg-emerald-100 dark:hover:bg-slate-700'
                          }`}
                      >
                        Semua
                      </button>
                      {anamnesisCategories.map((c) => (
                        <button
                          key={c.category}
                          type="button"
                          onClick={() => setSelectedAnamCategory(c.category)}
                          className={`px-2 py-0.5 rounded-lg text-[10px] font-bold transition-all shrink-0 flex items-center gap-1 ${selectedAnamCategory === c.category
                            ? 'bg-emerald-600 text-white shadow-2xs'
                            : c.category.includes('Pasien Ini')
                              ? 'bg-amber-100 dark:bg-amber-950 text-amber-900 dark:text-amber-300 border border-amber-300 dark:border-amber-700 font-bold'
                              : 'bg-emerald-50 dark:bg-slate-800 text-emerald-800 dark:text-slate-300 hover:bg-emerald-100 dark:hover:bg-slate-700'
                            }`}
                        >
                          <span>{c.icon}</span>
                          <span>{c.category.includes('Pasien Ini') ? 'Data Pasien (SIMRS)' : c.category.split(' ')[0]}</span>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Preset Items Grid */}
                  <div className="space-y-2.5 max-h-52 overflow-y-auto pr-1">
                    {anamnesisCategories.filter(c => selectedAnamCategory === 'all' || c.category === selectedAnamCategory).map((cat) => (
                      <div key={cat.category} className="space-y-1.5">
                        <div className="text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider flex items-center gap-1">
                          <span>{cat.icon}</span>
                          <span>{cat.category}</span>
                        </div>
                        <div className="flex flex-wrap gap-1.5">
                          {cat.items.map((item, idx) => {
                            const isAlreadyIncluded = subjective.includes(item.text.replace(/^- /, ''));
                            return (
                              <button
                                key={idx}
                                type="button"
                                onClick={() => appendSubjectiveAnamnesis(item.text)}
                                className={`px-2.5 py-1 rounded-xl text-[11px] font-medium border text-left flex items-center gap-1.5 transition-all ${isAlreadyIncluded
                                  ? 'bg-emerald-100 dark:bg-emerald-950/60 border-emerald-400 dark:border-emerald-700 text-emerald-900 dark:text-emerald-200 font-semibold'
                                  : cat.category.includes('Pasien Ini')
                                    ? 'bg-amber-50/80 dark:bg-amber-950/40 hover:bg-amber-100 dark:hover:bg-amber-900 border-amber-300 dark:border-amber-700 text-amber-950 dark:text-amber-200 hover:scale-[1.01]'
                                    : 'bg-emerald-50/70 dark:bg-slate-800/80 hover:bg-emerald-100 dark:hover:bg-slate-700 border-emerald-200 dark:border-slate-700 text-emerald-950 dark:text-slate-200 hover:scale-[1.01]'
                                  }`}
                              >
                                <span>{isAlreadyIncluded ? '✓' : '+'}</span>
                                <span>{item.label}</span>
                              </button>
                            );
                          })}
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Custom Anamnesis Value Adder */}
                  <div className="pt-2 border-t border-emerald-100 dark:border-slate-800 flex items-center gap-2 flex-wrap">
                    <span className="text-[10px] font-bold text-emerald-800 dark:text-emerald-400 shrink-0">
                      Anamnesis Kustom:
                    </span>
                    <input
                      type="text"
                      value={customAnamLabel}
                      onChange={(e) => setCustomAnamLabel(e.target.value)}
                      placeholder="Komponen (cth: RPS / RPD / Alergi)"
                      className="px-2.5 py-1 text-xs rounded-lg border border-emerald-200 dark:border-slate-700 bg-emerald-50/40 dark:bg-slate-800 text-slate-900 dark:text-slate-100 flex-1 min-w-[140px] focus:outline-none focus:border-emerald-500"
                    />
                    <input
                      type="text"
                      value={customAnamValue}
                      onChange={(e) => setCustomAnamValue(e.target.value)}
                      placeholder="Uraian Keluhan / Riwayat Pasien..."
                      className="px-2.5 py-1 text-xs rounded-lg border border-emerald-200 dark:border-slate-700 bg-emerald-50/40 dark:bg-slate-800 text-slate-900 dark:text-slate-100 flex-1 min-w-[160px] focus:outline-none focus:border-emerald-500"
                    />
                    <button
                      type="button"
                      onClick={handleAddCustomAnamnesis}
                      disabled={!customAnamLabel.trim() && !customAnamValue.trim()}
                      className="px-3 py-1 rounded-lg bg-emerald-700 hover:bg-emerald-600 disabled:opacity-40 text-white text-xs font-bold transition-all shadow-2xs shrink-0"
                    >
                      + Sisipkan
                    </button>
                  </div>
                </div>
              )}

              <textarea
                value={subjective}
                onChange={(e) => setSubjective(e.target.value)}
                rows={4}
                className="w-full rounded-xl border border-emerald-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-3.5 py-2.5 text-xs leading-relaxed text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500/50"
                placeholder="Masukkan data anamnesis: keluhan utama, riwayat penyakit sekarang (RPS), riwayat penyakit dahulu (RPD), riwayat alergi dan pengobatan..."
              />
            </div>
          )}

          {/* O - Objective */}
          {(activeTab === 'all' || activeTab === 'O') && (
            <div className="rounded-2xl border border-teal-200 dark:border-slate-700 bg-teal-50/40 dark:bg-slate-850/60 p-4 transition-colors space-y-3">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <label className="text-xs font-bold text-teal-900 dark:text-teal-300 flex items-center gap-2">
                  <span className="w-5 h-5 rounded-md bg-teal-600 text-white flex items-center justify-center text-[10px] font-black">O</span>
                  <span>Objective (Data Observasi Klinis, Tanda Vital & Pemeriksaan Penunjang/Lab)</span>
                </label>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => setShowObservationPicker(!showObservationPicker)}
                    className="px-2.5 py-1 rounded-xl bg-teal-600 hover:bg-teal-500 text-white text-[11px] font-bold flex items-center gap-1.5 transition-all shadow-xs"
                  >
                    <span>{showObservationPicker ? '✕' : '➕'}</span>
                    <span>{showObservationPicker ? 'Tutup Panel Observasi' : 'Tambah Observasi'}</span>
                  </button>
                </div>
              </div>

              {/* Interactive Observation Data Inserter Panel */}
              {showObservationPicker && (
                <div className="p-3.5 rounded-2xl bg-white dark:bg-slate-900 border border-teal-300 dark:border-slate-700 shadow-sm space-y-3 animate-in fade-in zoom-in-95 duration-150">
                  <div className="flex items-center justify-between border-b border-teal-100 dark:border-slate-800 pb-2">
                    <span className="text-xs font-bold text-teal-950 dark:text-teal-300 flex items-center gap-1.5">
                      <span>🩺</span>
                      <span>Katalog Data Observasi Klinis & Lab (Klik untuk Menyisipkan ke Catatan)</span>
                    </span>
                    <div className="flex items-center gap-1 overflow-x-auto max-w-[65%] py-0.5">
                      <button
                        type="button"
                        onClick={() => setSelectedObsCategory('all')}
                        className={`px-2 py-0.5 rounded-lg text-[10px] font-bold transition-all shrink-0 ${selectedObsCategory === 'all'
                          ? 'bg-teal-600 text-white shadow-2xs'
                          : 'bg-teal-50 dark:bg-slate-800 text-teal-800 dark:text-slate-300 hover:bg-teal-100 dark:hover:bg-slate-700'
                          }`}
                      >
                        Semua
                      </button>
                      {observationCategories.map((c) => (
                        <button
                          key={c.category}
                          type="button"
                          onClick={() => setSelectedObsCategory(c.category)}
                          className={`px-2 py-0.5 rounded-lg text-[10px] font-bold transition-all shrink-0 flex items-center gap-1 ${selectedObsCategory === c.category
                            ? 'bg-teal-600 text-white shadow-2xs'
                            : c.category.includes('Pasien Ini')
                              ? 'bg-amber-100 dark:bg-amber-950 text-amber-900 dark:text-amber-300 border border-amber-300 dark:border-amber-700 font-bold'
                              : 'bg-teal-50 dark:bg-slate-800 text-teal-800 dark:text-slate-300 hover:bg-teal-100 dark:hover:bg-slate-700'
                            }`}
                        >
                          <span>{c.icon}</span>
                          <span>{c.category.includes('Pasien Ini') ? 'Data Pasien (SIMRS)' : c.category.split(' ')[0]}</span>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Preset Items Grid */}
                  <div className="space-y-2.5 max-h-52 overflow-y-auto pr-1">
                    {observationCategories.filter(c => selectedObsCategory === 'all' || c.category === selectedObsCategory).map((cat) => (
                      <div key={cat.category} className="space-y-1.5">
                        <div className="text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider flex items-center gap-1">
                          <span>{cat.icon}</span>
                          <span>{cat.category}</span>
                        </div>
                        <div className="flex flex-wrap gap-1.5">
                          {cat.items.map((item, idx) => {
                            const isAlreadyIncluded = objective.includes(item.text.replace(/^- /, ''));
                            return (
                              <button
                                key={idx}
                                type="button"
                                onClick={() => appendObjectiveObservation(item.text)}
                                className={`px-2.5 py-1 rounded-xl text-[11px] font-medium border text-left flex items-center gap-1.5 transition-all ${isAlreadyIncluded
                                  ? 'bg-emerald-50 dark:bg-emerald-950/40 border-emerald-300 dark:border-emerald-700 text-emerald-800 dark:text-emerald-300 font-semibold'
                                  : cat.category.includes('Pasien Ini')
                                    ? 'bg-amber-50/80 dark:bg-amber-950/40 hover:bg-amber-100 dark:hover:bg-amber-900 border-amber-300 dark:border-amber-700 text-amber-950 dark:text-amber-200 hover:scale-[1.01]'
                                    : 'bg-teal-50/70 dark:bg-slate-800/80 hover:bg-teal-100 dark:hover:bg-slate-700 border-teal-200 dark:border-slate-700 text-teal-950 dark:text-slate-200 hover:scale-[1.01]'
                                  }`}
                              >
                                <span>{isAlreadyIncluded ? '✓' : '+'}</span>
                                <span>{item.label}</span>
                              </button>
                            );
                          })}
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Custom Observation Value Adder */}
                  <div className="pt-2 border-t border-teal-100 dark:border-slate-800 flex items-center gap-2 flex-wrap">
                    <span className="text-[10px] font-bold text-teal-800 dark:text-teal-400 shrink-0">
                      Observasi Kustom:
                    </span>
                    <input
                      type="text"
                      value={customObsLabel}
                      onChange={(e) => setCustomObsLabel(e.target.value)}
                      placeholder="Nama Parameter (cth: GDS / USG Abdomen)"
                      className="px-2.5 py-1 text-xs rounded-lg border border-teal-200 dark:border-slate-700 bg-teal-50/40 dark:bg-slate-800 text-slate-900 dark:text-slate-100 flex-1 min-w-[140px] focus:outline-none focus:border-teal-500"
                    />
                    <input
                      type="text"
                      value={customObsValue}
                      onChange={(e) => setCustomObsValue(e.target.value)}
                      placeholder="Nilai Temuan Observasi (cth: 125 mg/dL Normal)"
                      className="px-2.5 py-1 text-xs rounded-lg border border-teal-200 dark:border-slate-700 bg-teal-50/40 dark:bg-slate-800 text-slate-900 dark:text-slate-100 flex-1 min-w-[160px] focus:outline-none focus:border-teal-500"
                    />
                    <button
                      type="button"
                      onClick={handleAddCustomObservation}
                      disabled={!customObsLabel.trim() && !customObsValue.trim()}
                      className="px-3 py-1 rounded-lg bg-teal-700 hover:bg-teal-600 disabled:opacity-40 text-white text-xs font-bold transition-all shadow-2xs shrink-0"
                    >
                      + Sisipkan
                    </button>
                  </div>
                </div>
              )}

              <textarea
                value={objective}
                onChange={(e) => setObjective(e.target.value)}
                rows={5}
                className="w-full rounded-xl border border-teal-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-3.5 py-2.5 text-xs leading-relaxed text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-teal-500/50 font-mono"
                placeholder="Masukkan data observasi klinis, pemeriksaan fisik, tanda-tanda vital (TTV: TD, HR, RR, Suhu, SpO2), dan hasil laboratorium serial..."
              />
            </div>
          )}

          {/* A - Assessment */}
          {(activeTab === 'all' || activeTab === 'A') && (
            <div className="rounded-2xl border border-blue-200 dark:border-slate-700 bg-blue-50/40 dark:bg-slate-850/60 p-4 transition-colors space-y-3">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <label className="text-xs font-bold text-blue-900 dark:text-blue-300 flex items-center gap-2">
                  <span className="w-5 h-5 rounded-md bg-blue-600 text-white flex items-center justify-center text-[10px] font-black">A</span>
                  <span>Assessment (Diagnosis Primer & Banding + Kodefikasi ICD-10)</span>
                </label>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={handleGenerateAIDiagnosis}
                    disabled={isGeneratingDiagnosis}
                    className="px-3 py-1 rounded-xl bg-linear-to-r from-teal-600 via-blue-600 to-indigo-600 hover:from-teal-500 hover:to-indigo-500 text-white text-[11px] font-bold flex items-center gap-1.5 transition-all shadow-xs active:scale-95 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isGeneratingDiagnosis ? (
                      <>
                        <span className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                        <span>Menganalisis Klinis...</span>
                      </>
                    ) : (
                      <>
                        <span>✨</span>
                        <span>Generate Rekomendasi Diagnosis (AI)</span>
                      </>
                    )}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setDiagType('primary');
                      setShowDiagnosisModal(true);
                    }}
                    className="px-2.5 py-1 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-[11px] font-bold flex items-center gap-1.5 transition-all shadow-xs active:scale-95 cursor-pointer"
                  >
                    <span>➕</span>
                    <span>Tambah Manual (ICD-10)</span>
                  </button>
                </div>
              </div>

              {/* AI Diagnosis Generated Workflow Results Panel */}
              {showAiDiagPanel && (
                <div className="p-3.5 rounded-xl bg-linear-to-r from-blue-500/10 via-indigo-500/10 to-teal-500/10 border border-blue-300 dark:border-blue-700 space-y-2.5">
                  <div className="flex items-center justify-between flex-wrap gap-2">
                    <div className="flex items-center gap-1.5">
                      <span className="text-sm">✨</span>
                      <span className="text-xs font-bold text-blue-950 dark:text-blue-200">
                        Hasil Rekomendasi Diagnosis AI Co-Pilot
                      </span>
                      {isGeneratingDiagnosis && (
                        <span className="inline-flex items-center gap-1 text-[10px] text-blue-600 dark:text-blue-400 font-semibold animate-pulse">
                          <span className="w-2.5 h-2.5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></span>
                          Menganalisis EMR SIMRS...
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      {aiGeneratedDiagnoses.length > 0 && (
                        <>
                          <button
                            type="button"
                            onClick={() => handleSelectAllAIDiag(true)}
                            className="text-[10px] text-blue-700 dark:text-blue-300 hover:underline font-semibold cursor-pointer"
                          >
                            Pilih Semua
                          </button>
                          <span className="text-slate-300 dark:text-slate-600">|</span>
                          <button
                            type="button"
                            onClick={() => handleSelectAllAIDiag(false)}
                            className="text-[10px] text-slate-500 dark:text-slate-400 hover:underline font-medium cursor-pointer"
                          >
                            Batal Pilih
                          </button>
                        </>
                      )}
                      <button
                        type="button"
                        onClick={() => setShowAiDiagPanel(false)}
                        className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-xs px-1 font-bold cursor-pointer"
                      >
                        ✕
                      </button>
                    </div>
                  </div>

                  {aiGenError && (
                    <div className="p-3 rounded-lg bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 text-[11px] text-red-700 dark:text-red-300 flex items-center justify-between flex-wrap gap-2">
                      <span>⚠️ {aiGenError}</span>
                      <button
                        type="button"
                        onClick={handleGenerateAIDiagnosis}
                        disabled={isGeneratingDiagnosis}
                        className="px-2.5 py-1 rounded-lg bg-red-600 hover:bg-red-500 disabled:opacity-50 text-white font-bold text-[10px] flex items-center gap-1 transition-all shadow-xs cursor-pointer active:scale-95"
                      >
                        <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                        <span>Coba Lagi (Retry)</span>
                      </button>
                    </div>
                  )}


                  {aiGeneratedDiagnoses.length > 0 && (
                    <div className="space-y-2">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-h-56 overflow-y-auto pr-1">
                        {aiGeneratedDiagnoses.map((item) => (
                          <div
                            key={item.id}
                            onClick={() => handleToggleSelectAIDiag(item.id)}
                            className={`p-2.5 rounded-lg border text-left cursor-pointer transition-all ${
                              item.selected
                                ? 'bg-white dark:bg-slate-900 border-blue-500 ring-2 ring-blue-500/20 shadow-xs'
                                : 'bg-white/60 dark:bg-slate-900/60 border-slate-200 dark:border-slate-800 hover:border-blue-300 opacity-80'
                            }`}
                          >
                            <div className="flex items-start justify-between gap-2">
                              <div className="flex items-start gap-2">
                                <input
                                  type="checkbox"
                                  checked={item.selected}
                                  onChange={() => handleToggleSelectAIDiag(item.id)}
                                  onClick={(e) => e.stopPropagation()}
                                  className="mt-0.5 rounded text-blue-600 focus:ring-blue-500 cursor-pointer"
                                />
                                <div>
                                  <div className="flex items-center gap-1.5 flex-wrap">
                                    <span
                                      className={`text-[9px] font-bold px-1.5 py-0.2 rounded ${
                                        item.type === 'primary'
                                          ? 'bg-blue-600 text-white'
                                          : 'bg-amber-600 text-white'
                                      }`}
                                    >
                                      {item.type === 'primary' ? 'Primer (Kerja)' : 'Banding'}
                                    </span>
                                    <span className="font-mono text-[10px] font-bold text-slate-700 dark:text-slate-300 bg-slate-100 dark:bg-slate-800 px-1 rounded">
                                      {item.icd10}
                                    </span>
                                    {item.confidence && (
                                      <span className="text-[9px] font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 px-1 rounded">
                                        {item.confidence}
                                      </span>
                                    )}
                                  </div>
                                  <div className="text-[11px] font-bold text-slate-900 dark:text-slate-100 mt-1">
                                    {item.diagnosis}
                                  </div>
                                  {item.justification && (
                                    <div className="text-[10px] text-slate-500 dark:text-slate-400 line-clamp-2 mt-0.5">
                                      {item.justification}
                                    </div>
                                  )}
                                </div>
                              </div>
                              <button
                                type="button"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleInsertSingleAIDiag(item);
                                }}
                                title="Langsung sisipkan item ini ke assessment"
                                className="px-2 py-0.5 rounded bg-blue-100 hover:bg-blue-200 dark:bg-blue-950 dark:hover:bg-blue-900 text-blue-700 dark:text-blue-300 text-[10px] font-bold shrink-0 cursor-pointer"
                              >
                                + Sisipkan
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>

                      <div className="flex items-center justify-between pt-1 border-t border-blue-200 dark:border-blue-800/60">
                        <span className="text-[10px] text-slate-600 dark:text-slate-400">
                          {aiGeneratedDiagnoses.filter((d) => d.selected).length} dari {aiGeneratedDiagnoses.length} diagnosis dipilih
                        </span>
                        <button
                          type="button"
                          onClick={handleInsertSelectedAIDiagnoses}
                          disabled={aiGeneratedDiagnoses.filter((d) => d.selected).length === 0}
                          className="px-3 py-1 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-[11px] font-bold flex items-center gap-1.5 transition-all shadow-xs cursor-pointer active:scale-95"
                        >
                          <span>📥</span>
                          <span>Sisipkan ({aiGeneratedDiagnoses.filter((d) => d.selected).length}) Diagnosis Terpilih ke Editor</span>
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}


              {/* Quick AI & SIMRS Diagnosis Chips */}
              {(diagnosisCategories.primaryItems.length > 0 || diagnosisCategories.diffItems.length > 0) && (
                <div className="p-2.5 rounded-xl bg-white dark:bg-slate-900 border border-blue-200 dark:border-slate-700 space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold text-blue-900 dark:text-blue-300 flex items-center gap-1">
                      <span>🎯</span>
                      <span>Rekomendasi Diagnosis AI / SIMRS (Klik untuk langsung menyisipkan):</span>
                    </span>
                    <button
                      type="button"
                      onClick={() => setShowDiagnosisModal(true)}
                      className="text-[10px] text-blue-600 dark:text-blue-400 font-bold hover:underline cursor-pointer"
                    >
                      Cari Kode Lainnya 🔍
                    </button>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {diagnosisCategories.primaryItems.map((item, idx) => {
                      const itemText = `- Diagnosis Primer (Kerja): ${item.diagnosis} (ICD-10: ${item.icd10})${item.justification ? ` — Justifikasi: ${item.justification}` : ''}`;
                      const isAdded = assessment.includes(item.diagnosis) || (item.icd10 !== 'Unspecified' && assessment.includes(item.icd10));
                      return (
                        <button
                          key={`prim-${idx}`}
                          type="button"
                          onClick={() => {
                            if (!isAdded) {
                              setAssessment((prev) => {
                                const trimmed = prev.trim();
                                if (!trimmed) return itemText;
                                return `${trimmed}\n${itemText}`;
                              });
                            }
                          }}
                          className={`px-2 py-1 rounded-lg text-[10px] font-medium border flex items-center gap-1.5 transition-all cursor-pointer ${isAdded
                            ? 'bg-blue-100 dark:bg-blue-950/60 border-blue-300 dark:border-blue-700 text-blue-800 dark:text-blue-300'
                            : 'bg-blue-50/70 dark:bg-slate-800 border-blue-200 dark:border-slate-700 text-blue-950 dark:text-blue-200 hover:bg-blue-100 hover:border-blue-400'
                            }`}
                        >
                          <span className="font-bold text-[9px] px-1 py-0.5 rounded bg-blue-600 text-white shrink-0">Primer</span>
                          <span className="font-bold font-mono">{item.icd10}</span>
                          <span className="truncate max-w-[200px]">{item.diagnosis}</span>
                          <span className="text-[11px] font-bold shrink-0">{isAdded ? '✓' : '+'}</span>
                        </button>
                      );
                    })}
                    {diagnosisCategories.diffItems.map((item, idx) => {
                      const itemText = `- Diagnosis Banding: ${item.diagnosis} (ICD-10: ${item.icd10})${item.clues ? ` — Petunjuk: ${item.clues}` : ''}`;
                      const isAdded = assessment.includes(item.diagnosis) || (item.icd10 !== 'Unspecified' && assessment.includes(item.icd10));
                      return (
                        <button
                          key={`diff-${idx}`}
                          type="button"
                          onClick={() => {
                            if (!isAdded) {
                              setAssessment((prev) => {
                                const trimmed = prev.trim();
                                if (!trimmed) return itemText;
                                return `${trimmed}\n${itemText}`;
                              });
                            }
                          }}
                          className={`px-2 py-1 rounded-lg text-[10px] font-medium border flex items-center gap-1.5 transition-all cursor-pointer ${isAdded
                            ? 'bg-amber-100 dark:bg-amber-950/60 border-amber-300 dark:border-amber-700 text-amber-800 dark:text-amber-300'
                            : 'bg-amber-50/70 dark:bg-slate-800 border-amber-200 dark:border-slate-700 text-amber-950 dark:text-amber-200 hover:bg-amber-100 hover:border-amber-400'
                            }`}
                        >
                          <span className="font-bold text-[9px] px-1 py-0.5 rounded bg-amber-600 text-white shrink-0">Banding</span>
                          <span className="font-bold font-mono">{item.icd10}</span>
                          <span className="truncate max-w-[200px]">{item.diagnosis}</span>
                          <span className="text-[11px] font-bold shrink-0">{isAdded ? '✓' : '+'}</span>
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}

              <textarea
                value={assessment}
                onChange={(e) => setAssessment(e.target.value)}
                rows={4}
                className="w-full rounded-xl border border-blue-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-3.5 py-2.5 text-xs leading-relaxed text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500/50 font-mono"
                placeholder="Tuliskan diagnosis kerja dan diagnosis banding lengkap dengan kodefikasi ICD-10..."
              />
            </div>
          )}

          {/* P - Plan */}
          {(activeTab === 'all' || activeTab === 'P') && (
            <div className="rounded-2xl border border-indigo-200 dark:border-slate-700 bg-indigo-50/40 dark:bg-slate-850/60 p-4 transition-colors space-y-3">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <label className="text-xs font-bold text-indigo-900 dark:text-indigo-300 flex items-center gap-2">
                  <span className="w-5 h-5 rounded-md bg-indigo-600 text-white flex items-center justify-center text-[10px] font-black">P</span>
                  <span>Plan (Terapi Farmakologi, Rencana Monitoring & Edukasi Pasien)</span>
                </label>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => setShowPlanPicker(!showPlanPicker)}
                    className="px-2.5 py-1 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-[11px] font-bold flex items-center gap-1.5 transition-all shadow-xs"
                  >
                    <span>{showPlanPicker ? '✕' : '➕'}</span>
                    <span>{showPlanPicker ? 'Tutup Panel Plan' : 'Tambah Rekomendasi Plan AI'}</span>
                  </button>
                </div>
              </div>

              {/* Interactive Plan & AI Therapy Quick-Insert Picker */}
              {showPlanPicker && (
                <div className="p-3.5 rounded-2xl border border-indigo-200/90 dark:border-slate-700 bg-white/95 dark:bg-slate-900/95 space-y-3 shadow-xs animate-in fade-in-50 duration-150">
                  <div className="flex items-center justify-between flex-wrap gap-2">
                    <span className="text-[11px] font-bold text-indigo-950 dark:text-indigo-200 flex items-center gap-1.5">
                      <span>💡</span>
                      <span>Katalog Rekomendasi Terapi Obat, Workup, & Plan AI:</span>
                    </span>
                    <span className="text-[10px] text-indigo-600 dark:text-slate-400">
                      Klik badge untuk menyisipkan ke Plan
                    </span>
                  </div>

                  {/* Filter Category Pills */}
                  <div className="flex flex-wrap gap-1.5 border-b border-indigo-100 dark:border-slate-800 pb-2">
                    <button
                      type="button"
                      onClick={() => setSelectedPlanCategory('all')}
                      className={`px-2 py-0.5 rounded-lg text-[10px] font-bold transition-all ${selectedPlanCategory === 'all'
                        ? 'bg-indigo-600 text-white shadow-2xs'
                        : 'bg-indigo-50 dark:bg-slate-800 text-indigo-900 dark:text-indigo-300 hover:bg-indigo-100'
                        }`}
                    >
                      Semua Kategori
                    </button>
                    {planCategories.map((c) => (
                      <button
                        key={c.category}
                        type="button"
                        onClick={() => setSelectedPlanCategory(c.category)}
                        className={`px-2 py-0.5 rounded-lg text-[10px] font-bold transition-all flex items-center gap-1 ${selectedPlanCategory === c.category
                          ? 'bg-indigo-600 text-white shadow-2xs'
                          : c.category.includes('Pasien Ini')
                            ? 'bg-amber-100 dark:bg-amber-950 text-amber-900 dark:text-amber-200 border border-amber-300 dark:border-amber-700'
                            : 'bg-indigo-50 dark:bg-slate-800 text-indigo-900 dark:text-indigo-300 hover:bg-indigo-100'
                          }`}
                      >
                        <span>{c.icon}</span>
                        <span>{c.category}</span>
                      </button>
                    ))}
                  </div>

                  {/* Plan Items Grid */}
                  <div className="space-y-2.5 max-h-56 overflow-y-auto pr-1">
                    {planCategories
                      .filter((c) => selectedPlanCategory === 'all' || selectedPlanCategory === c.category)
                      .map((cat) => (
                        <div key={cat.category} className="space-y-1">
                          <div className="text-[10px] font-bold text-indigo-800 dark:text-indigo-300 uppercase tracking-wider flex items-center gap-1">
                            <span>{cat.icon}</span>
                            <span>{cat.category}</span>
                          </div>
                          <div className="flex flex-wrap gap-1.5">
                            {cat.items.map((item, idx) => {
                              const isAlreadyIncluded = plan.includes(item.text.trim());
                              return (
                                <button
                                  key={idx}
                                  type="button"
                                  onClick={() => appendPlanItem(item.text)}
                                  className={`px-2.5 py-1 rounded-xl text-[11px] font-medium border text-left flex items-center gap-1.5 transition-all ${isAlreadyIncluded
                                    ? 'bg-emerald-50 dark:bg-emerald-950/40 border-emerald-300 dark:border-emerald-700 text-emerald-800 dark:text-emerald-300 font-semibold'
                                    : cat.category.includes('Pasien Ini')
                                      ? 'bg-amber-50/80 dark:bg-amber-950/40 hover:bg-amber-100 dark:hover:bg-amber-900 border-amber-300 dark:border-amber-700 text-amber-950 dark:text-amber-200 hover:scale-[1.01]'
                                      : 'bg-indigo-50/70 dark:bg-slate-800/80 hover:bg-indigo-100 dark:hover:bg-slate-700 border-indigo-200 dark:border-slate-700 text-indigo-950 dark:text-slate-200 hover:scale-[1.01]'
                                    }`}
                                >
                                  <span>{isAlreadyIncluded ? '✓' : '+'}</span>
                                  <span>{item.label}</span>
                                </button>
                              );
                            })}
                          </div>
                        </div>
                      ))}
                  </div>

                  {/* Custom Plan Adder */}
                  <div className="pt-2 border-t border-indigo-100 dark:border-slate-800 flex items-center gap-2 flex-wrap">
                    <span className="text-[10px] font-bold text-indigo-800 dark:text-indigo-400 shrink-0">
                      Plan Kustom:
                    </span>
                    <input
                      type="text"
                      value={customPlanLabel}
                      onChange={(e) => setCustomPlanLabel(e.target.value)}
                      placeholder="Kategori / Judul (cth: Profil Besi / EGD Ulang)"
                      className="px-2.5 py-1 text-xs rounded-lg border border-indigo-200 dark:border-slate-700 bg-indigo-50/40 dark:bg-slate-800 text-slate-900 dark:text-slate-100 flex-1 min-w-[140px] focus:outline-none focus:border-indigo-500"
                    />
                    <input
                      type="text"
                      value={customPlanValue}
                      onChange={(e) => setCustomPlanValue(e.target.value)}
                      placeholder="Instruksi Rencana / Terapi (cth: LFT & Elektrolit 3 hari lagi)"
                      className="px-2.5 py-1 text-xs rounded-lg border border-indigo-200 dark:border-slate-700 bg-indigo-50/40 dark:bg-slate-800 text-slate-900 dark:text-slate-100 flex-1 min-w-[160px] focus:outline-none focus:border-indigo-500"
                    />
                    <button
                      type="button"
                      onClick={handleAddCustomPlan}
                      disabled={!customPlanLabel.trim() && !customPlanValue.trim()}
                      className="px-3 py-1 rounded-lg bg-indigo-700 hover:bg-indigo-600 disabled:opacity-40 text-white text-xs font-bold transition-all shadow-2xs shrink-0"
                    >
                      + Sisipkan
                    </button>
                  </div>
                </div>
              )}

              <textarea
                value={plan}
                onChange={(e) => setPlan(e.target.value)}
                rows={4}
                className="w-full rounded-xl border border-indigo-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-3.5 py-2.5 text-xs leading-relaxed text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
                placeholder="Tuliskan instruksi obat, dosis, rencana pemeriksaan penunjang, dan instruksi kontrol..."
              />
            </div>
          )}

          {/* I - Instruksi PPA / Dokter */}
          {(activeTab === 'all' || activeTab === 'I') && (
            <div className="rounded-2xl border border-purple-200 dark:border-slate-700 bg-purple-50/40 dark:bg-slate-850/60 p-4 transition-colors space-y-3">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <label className="text-xs font-bold text-purple-900 dark:text-purple-300 flex items-center gap-2">
                  <span className="w-5 h-5 rounded-md bg-purple-600 text-white flex items-center justify-center text-[10px] font-black">I</span>
                  <span>Instruksi (Instruksi Tenaga Kesehatan / PPA & Edukasi Pasien)</span>
                </label>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => setShowInstructionPicker(!showInstructionPicker)}
                    className="px-2.5 py-1 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-[11px] font-bold flex items-center gap-1.5 transition-all shadow-xs"
                  >
                    <span>{showInstructionPicker ? '✕' : '➕'}</span>
                    <span>{showInstructionPicker ? 'Tutup Panel Instruksi' : 'Tambah Instruksi Klinis'}</span>
                  </button>
                </div>
              </div>

              {/* Interactive Instruction Data Inserter Panel */}
              {showInstructionPicker && (
                <div className="p-3.5 rounded-2xl bg-white dark:bg-slate-900 border border-purple-300 dark:border-slate-700 shadow-sm space-y-3 animate-in fade-in zoom-in-95 duration-150">
                  <div className="flex items-center justify-between border-b border-purple-100 dark:border-slate-800 pb-2">
                    <span className="text-xs font-bold text-purple-950 dark:text-purple-300 flex items-center gap-1.5">
                      <span>📝</span>
                      <span>Katalog Instruksi Dokter & PPA (Klik untuk Menyisipkan ke Instruksi)</span>
                    </span>
                    <div className="flex items-center gap-1 overflow-x-auto max-w-[65%] py-0.5">
                      <button
                        type="button"
                        onClick={() => setSelectedInstCategory('all')}
                        className={`px-2 py-0.5 rounded-lg text-[10px] font-bold transition-all shrink-0 ${selectedInstCategory === 'all'
                          ? 'bg-purple-600 text-white shadow-2xs'
                          : 'bg-purple-50 dark:bg-slate-800 text-purple-800 dark:text-slate-300 hover:bg-purple-100 dark:hover:bg-slate-700'
                          }`}
                      >
                        Semua
                      </button>
                      {INSTRUCTION_CATEGORIES.map((cat) => (
                        <button
                          key={cat.category}
                          type="button"
                          onClick={() => setSelectedInstCategory(cat.category)}
                          className={`px-2 py-0.5 rounded-lg text-[10px] font-bold transition-all shrink-0 ${selectedInstCategory === cat.category
                            ? 'bg-purple-600 text-white shadow-2xs'
                            : 'bg-purple-50 dark:bg-slate-800 text-purple-800 dark:text-slate-300 hover:bg-purple-100 dark:hover:bg-slate-700'
                            }`}
                        >
                          <span>{cat.icon}</span>
                          <span>{cat.category.split(' ')[1] || cat.category}</span>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Preset Items Grid */}
                  <div className="space-y-2.5 max-h-52 overflow-y-auto pr-1">
                    {INSTRUCTION_CATEGORIES.filter(c => selectedInstCategory === 'all' || c.category === selectedInstCategory).map((cat) => (
                      <div key={cat.category} className="space-y-1.5">
                        <div className="text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider flex items-center gap-1">
                          <span>{cat.icon}</span>
                          <span>{cat.category}</span>
                        </div>
                        <div className="flex flex-wrap gap-1.5">
                          {cat.items.map((item, idx) => {
                            const isAlreadyIncluded = instructions.includes(item.text.replace(/^- /, ''));
                            return (
                              <button
                                key={idx}
                                type="button"
                                onClick={() => appendInstruction(item.text)}
                                className={`px-2.5 py-1 rounded-xl text-[11px] font-medium border text-left flex items-center gap-1.5 transition-all ${isAlreadyIncluded
                                  ? 'bg-purple-100 dark:bg-purple-950/60 border-purple-400 dark:border-purple-700 text-purple-900 dark:text-purple-200 font-semibold'
                                  : 'bg-purple-50/70 dark:bg-slate-800/80 hover:bg-purple-100 dark:hover:bg-slate-700 border-purple-200 dark:border-slate-700 text-purple-950 dark:text-slate-200 hover:scale-[1.01]'
                                  }`}
                              >
                                <span>{isAlreadyIncluded ? '✓' : '+'}</span>
                                <span>{item.label}</span>
                              </button>
                            );
                          })}
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Custom Instruction Input */}
                  <div className="pt-2 border-t border-purple-100 dark:border-slate-800 flex items-center gap-2 flex-wrap">
                    <span className="text-[10px] font-bold text-purple-800 dark:text-purple-400 shrink-0">
                      Instruksi Kustom:
                    </span>
                    <input
                      type="text"
                      value={customInstText}
                      onChange={(e) => setCustomInstText(e.target.value)}
                      placeholder="Masukkan instruksi khusus perawat/pasien..."
                      className="px-2.5 py-1 text-xs rounded-lg border border-purple-200 dark:border-slate-700 bg-purple-50/40 dark:bg-slate-800 text-slate-900 dark:text-slate-100 flex-1 min-w-[200px] focus:outline-none focus:border-purple-500"
                    />
                    <button
                      type="button"
                      onClick={handleAddCustomInstruction}
                      disabled={!customInstText.trim()}
                      className="px-3 py-1 rounded-lg bg-purple-700 hover:bg-purple-600 disabled:opacity-40 text-white text-xs font-bold transition-all shadow-2xs shrink-0"
                    >
                      + Sisipkan
                    </button>
                  </div>
                </div>
              )}

              <textarea
                value={instructions}
                onChange={(e) => setInstructions(e.target.value)}
                rows={3}
                className="w-full rounded-xl border border-purple-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-3.5 py-2.5 text-xs leading-relaxed text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-purple-500/50"
                placeholder="Masukkan instruksi medis: pemantauan TTV berkala, diet nutrisi khusus, jadwal kontrol ulang, edukasi tanda bahaya (red flags)..."
              />
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="px-6 py-4 border-t border-emerald-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-850 flex items-center justify-between flex-wrap gap-3">
          <div className="text-[11px] text-slate-500 dark:text-slate-400 flex items-center gap-1.5">
            <span>🔒</span>
            <span>Data yang dikonfirmasi akan dicatat dalam Audit Trail SIMRS dengan tanda tangan digital DPJP.</span>
          </div>

          <div className="flex items-center gap-2.5">
            <button
              type="button"
              disabled={isSubmitting}
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
            >
              Batal
            </button>
            <button
              type="button"
              disabled={isSubmitting || !subjective.trim() || !assessment.trim()}
              onClick={handleConfirm}
              className="px-5 py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-xs font-bold shadow-md shadow-emerald-600/20 disabled:opacity-50 flex items-center gap-2 transition-all"
            >
              {isSubmitting ? (
                <>
                  <span className="animate-spin text-sm">⏳</span>
                  <span>Mentransmisikan ke SIMRS...</span>
                </>
              ) : (
                <>
                  <span>✅</span>
                  <span>Konfirmasi & Kirim ke SIMRS (MCP)</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* ========================================================================= */}
        {/* MODAL PENCARIAN & KODEFIKASI DIAGNOSIS (ICD-10) */}
        {/* ========================================================================= */}
        {showDiagnosisModal && (
          <div className="fixed inset-0 z-60 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-xs animate-in fade-in duration-150">
            <div className="bg-white dark:bg-slate-900 border border-blue-500/30 rounded-3xl shadow-2xl w-full max-w-2xl max-h-[88vh] flex flex-col overflow-hidden animate-in zoom-in-95 duration-150">

              {/* Header */}
              <div className="px-5 py-3.5 border-b border-blue-100 dark:border-slate-800 bg-gradient-to-r from-blue-50 via-indigo-50 to-blue-50 dark:from-slate-900 dark:via-slate-850 dark:to-slate-900 flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-xl bg-blue-600 text-white flex items-center justify-center text-sm font-bold shadow-md shadow-blue-600/20">
                    🎯
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                      Pencarian & Kodefikasi Diagnosis (ICD-10)
                    </h4>
                    <p className="text-[10px] text-blue-600 dark:text-blue-400">
                      Pilih dan labeli diagnosis sebagai Primer atau Banding untuk dimasukkan ke Assessment
                    </p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => setShowDiagnosisModal(false)}
                  className="w-8 h-8 rounded-full flex items-center justify-center text-slate-400 hover:text-slate-700 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors text-sm font-bold cursor-pointer"
                >
                  ✕
                </button>
              </div>

              {/* Search & Category Filter */}
              <div className="p-4 border-b border-slate-100 dark:border-slate-800 space-y-2.5 bg-slate-50/50 dark:bg-slate-850/50">
                <div className="relative">
                  <span className="absolute left-3 top-2.5 text-xs text-slate-400">🔍</span>
                  <input
                    type="text"
                    value={diagSearchQuery}
                    onChange={(e) => setDiagSearchQuery(e.target.value)}
                    placeholder="Cari kode ICD-10 (mis: K29.1, E11, I10) atau nama diagnosis..."
                    className="w-full pl-8 pr-8 py-2 rounded-xl border border-blue-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-xs text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500/50 font-medium"
                    autoFocus
                  />
                  {diagSearchQuery && (
                    <button
                      type="button"
                      onClick={() => setDiagSearchQuery('')}
                      className="absolute right-2.5 top-2 text-xs text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 cursor-pointer"
                    >
                      ✕
                    </button>
                  )}
                </div>

                {/* Category Pills */}
                <div className="flex items-center gap-1 overflow-x-auto pb-1 max-w-full">
                  {DIAG_CATEGORIES.map((cat) => (
                    <button
                      key={cat}
                      type="button"
                      onClick={() => setDiagCategoryFilter(cat)}
                      className={`px-2.5 py-1 rounded-lg text-[10px] font-bold shrink-0 transition-all cursor-pointer ${diagCategoryFilter === cat
                        ? 'bg-blue-600 text-white shadow-2xs'
                        : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-700'
                        }`}
                    >
                      {cat}
                    </button>
                  ))}
                </div>
              </div>

              {/* Modal Body / Results List */}
              <div className="p-4 overflow-y-auto space-y-3 flex-1 max-h-[36vh]">
                {/* AI / Patient Recommended Section */}
                {(diagnosisCategories.primaryItems.length > 0 || diagnosisCategories.diffItems.length > 0) && !diagSearchQuery && diagCategoryFilter === 'Semua' && (
                  <div className="p-3 rounded-2xl bg-blue-50/70 dark:bg-slate-800/80 border border-blue-200 dark:border-slate-700 space-y-2">
                    <div className="text-[10px] font-bold text-blue-900 dark:text-blue-300 flex items-center gap-1 uppercase tracking-wider">
                      <span>🌟</span>
                      <span>Rekomendasi Diagnosis Sesi Ini (AI & RME Pasien):</span>
                    </div>
                    <div className="space-y-1.5">
                      {diagnosisCategories.primaryItems.map((item, idx) => (
                        <div
                          key={`rec-p-${idx}`}
                          onClick={() => handleSelectIcd10Item({ code: item.icd10, name: item.diagnosis, indonesian: item.diagnosis }, 'primary', item.justification)}
                          className={`p-2 rounded-xl border flex items-center justify-between gap-2 cursor-pointer transition-all ${selectedDiagCode === item.icd10 && diagType === 'primary'
                            ? 'bg-blue-600 text-white border-blue-600 shadow-xs'
                            : 'bg-white dark:bg-slate-900 border-blue-200 dark:border-slate-700 hover:border-blue-400 text-slate-800 dark:text-slate-200'
                            }`}
                        >
                          <div className="flex items-center gap-2 min-w-0">
                            <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-blue-100 dark:bg-blue-950 text-blue-800 dark:text-blue-300 border border-blue-300 dark:border-blue-700 shrink-0">
                              Primer
                            </span>
                            <span className="font-mono font-bold text-xs shrink-0">{item.icd10}</span>
                            <span className="text-xs font-semibold truncate">{item.diagnosis}</span>
                          </div>
                          <span className="text-[10px] font-bold shrink-0 opacity-80">Pilih 👉</span>
                        </div>
                      ))}
                      {diagnosisCategories.diffItems.map((item, idx) => (
                        <div
                          key={`rec-d-${idx}`}
                          onClick={() => handleSelectIcd10Item({ code: item.icd10, name: item.diagnosis, indonesian: item.diagnosis }, 'differential', item.clues)}
                          className={`p-2 rounded-xl border flex items-center justify-between gap-2 cursor-pointer transition-all ${selectedDiagCode === item.icd10 && diagType === 'differential'
                            ? 'bg-amber-600 text-white border-amber-600 shadow-xs'
                            : 'bg-white dark:bg-slate-900 border-amber-200 dark:border-slate-700 hover:border-amber-400 text-slate-800 dark:text-slate-200'
                            }`}
                        >
                          <div className="flex items-center gap-2 min-w-0">
                            <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300 border border-amber-300 dark:border-amber-700 shrink-0">
                              Banding
                            </span>
                            <span className="font-mono font-bold text-xs shrink-0">{item.icd10}</span>
                            <span className="text-xs font-semibold truncate">{item.diagnosis}</span>
                          </div>
                          <span className="text-[10px] font-bold shrink-0 opacity-80">Pilih 👉</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* ICD-10 Database Results */}
                <div className="space-y-1.5">
                  <div className="text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider flex items-center justify-between px-1">
                    <span>Katalog Kode ICD-10 ({filteredIcd10List.length} Ditemukan):</span>
                    <span>Klik untuk memilih</span>
                  </div>

                  {filteredIcd10List.length === 0 ? (
                    <div className="text-center py-6 text-xs text-slate-400">
                      Tidak ada diagnosis yang sesuai dengan kata kunci &quot;{diagSearchQuery}&quot;. Anda dapat mengetik manual di formulir bawah.
                    </div>
                  ) : (
                    filteredIcd10List.map((item) => {
                      const isSelected = selectedDiagCode === item.code;
                      return (
                        <div
                          key={item.code}
                          onClick={() => handleSelectIcd10Item(item, diagType)}
                          className={`p-2.5 rounded-xl border flex items-center justify-between gap-3 cursor-pointer transition-all ${isSelected
                            ? 'bg-blue-50 dark:bg-blue-950/50 border-blue-500 dark:border-blue-400 shadow-2xs'
                            : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 hover:border-blue-300 dark:hover:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-850'
                            }`}
                        >
                          <div className="min-w-0 flex-1">
                            <div className="flex items-center gap-2 mb-0.5">
                              <span className="px-1.5 py-0.5 rounded font-mono font-bold text-[11px] bg-blue-100 dark:bg-blue-950 text-blue-900 dark:text-blue-300 border border-blue-200 dark:border-blue-800 shrink-0">
                                {item.code}
                              </span>
                              <span className="text-[9px] font-semibold px-1.5 py-0.2 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700 shrink-0">
                                {item.category}
                              </span>
                              <span className="text-xs font-bold text-slate-900 dark:text-white truncate">
                                {item.indonesian}
                              </span>
                            </div>
                            <p className="text-[10px] text-slate-500 dark:text-slate-400 truncate italic">
                              {item.name}
                            </p>
                          </div>

                          <div className="flex items-center gap-1 shrink-0">
                            <button
                              type="button"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleSelectIcd10Item(item, 'primary');
                              }}
                              className={`px-2 py-1 rounded-lg text-[10px] font-bold border transition-all cursor-pointer ${isSelected && diagType === 'primary'
                                ? 'bg-blue-600 text-white border-blue-600'
                                : 'bg-blue-50 text-blue-800 dark:bg-slate-800 dark:text-blue-300 border-blue-200 dark:border-slate-700 hover:bg-blue-100'
                                }`}
                            >
                              + Primer
                            </button>
                            <button
                              type="button"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleSelectIcd10Item(item, 'differential');
                              }}
                              className={`px-2 py-1 rounded-lg text-[10px] font-bold border transition-all cursor-pointer ${isSelected && diagType === 'differential'
                                ? 'bg-amber-600 text-white border-amber-600'
                                : 'bg-amber-50 text-amber-800 dark:bg-slate-800 dark:text-amber-300 border-amber-200 dark:border-slate-700 hover:bg-amber-100'
                                }`}
                            >
                              + Banding
                            </button>
                          </div>
                        </div>
                      );
                    })
                  )}
                </div>
              </div>

              {/* Selected Diagnosis Configuration & Customization Panel */}
              <div className="p-4 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-850 space-y-3">
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <span className="text-xs font-bold text-slate-900 dark:text-white flex items-center gap-1.5">
                    <span>⚙️</span>
                    <span>Pengaturan Diagnosis yang Akan Disisipkan:</span>
                  </span>

                  {/* Kategori Label Toggle: Primer vs Banding */}
                  <div className="flex items-center p-0.5 rounded-xl bg-slate-200 dark:bg-slate-800 border border-slate-300 dark:border-slate-700">
                    <button
                      type="button"
                      onClick={() => setDiagType('primary')}
                      className={`px-3 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer ${diagType === 'primary'
                        ? 'bg-blue-600 text-white shadow-xs'
                        : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                        }`}
                    >
                      🎯 Diagnosis Primer
                    </button>
                    <button
                      type="button"
                      onClick={() => setDiagType('differential')}
                      className={`px-3 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer ${diagType === 'differential'
                        ? 'bg-amber-600 text-white shadow-xs'
                        : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                        }`}
                    >
                      ⚖️ Diagnosis Banding
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                  <div className="sm:col-span-2">
                    <label className="text-[10px] font-bold text-slate-500 dark:text-slate-400 block mb-1">
                      Nama Diagnosis:
                    </label>
                    <input
                      type="text"
                      value={selectedDiagName}
                      onChange={(e) => setSelectedDiagName(e.target.value)}
                      placeholder="Nama diagnosis (misal: Gastritis Kronis Erosif)"
                      className="w-full px-3 py-1.5 text-xs rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500/50 font-medium"
                    />
                  </div>
                  <div>
                    <label className="text-[10px] font-bold text-slate-500 dark:text-slate-400 block mb-1">
                      Kode ICD-10:
                    </label>
                    <input
                      type="text"
                      value={selectedDiagCode}
                      onChange={(e) => setSelectedDiagCode(e.target.value)}
                      placeholder="Kode (misal: K29.1)"
                      className="w-full px-3 py-1.5 text-xs rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500/50 font-mono font-bold"
                    />
                  </div>
                </div>

                <div>
                  <label className="text-[10px] font-bold text-slate-500 dark:text-slate-400 block mb-1">
                    {diagType === 'primary' ? 'Justifikasi Klinis (Opsional):' : 'Petunjuk Klinis / Indikator Pembanding (Opsional):'}
                  </label>
                  <input
                    type="text"
                    value={diagJustification}
                    onChange={(e) => setDiagJustification(e.target.value)}
                    placeholder={
                      diagType === 'primary'
                        ? 'Contoh: Nyeri epigastrium > 2 minggu, riwayat konsumsi NSAID rutin'
                        : 'Contoh: Keluhan heartburn dan regurgitasi asam, perlu evaluasi respons PPI'
                    }
                    className="w-full px-3 py-1.5 text-xs rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                  />
                </div>

                <div className="flex items-center justify-end gap-2 pt-1">
                  <button
                    type="button"
                    onClick={() => setShowDiagnosisModal(false)}
                    className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors cursor-pointer"
                  >
                    Batal
                  </button>
                  <button
                    type="button"
                    disabled={!selectedDiagName.trim() && !selectedDiagCode.trim()}
                    onClick={handleAppendDiagnosis}
                    className="px-5 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-40 text-white text-xs font-bold transition-all shadow-md shadow-blue-600/20 flex items-center gap-1.5 cursor-pointer"
                  >
                    <span>➕</span>
                    <span>Sisipkan ke Assessment</span>
                  </button>
                </div>
              </div>

            </div>
          </div>
        )}

      </div>
    </div>
  );
}
