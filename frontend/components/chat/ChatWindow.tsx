'use client';
import { useRef, useEffect, useState, type ChangeEvent } from 'react';
import type { ChatMessage } from '@/hooks/useAgentChat';
import type { SOAContent, PatientRecord } from '@/services/agent.service';
import SOAEditor from './SOAEditor';
import MarkdownContent from './MarkdownContent';
import AudioRecorderModal from './AudioRecorderModal';
import AgentStatusIndicator from './AgentStatusIndicator';
import BotAvatar from '@/components/common/BotAvatar';
import WorkflowExpandable from './WorkflowExpandable';
import NewConsultationSelection from './NewConsultationSelection';
import DiagnosisEditor from './DiagnosisEditor';
import MedicationEditorModal from './MedicationEditorModal';
import AnamnesisEditorModal from './AnamnesisEditorModal';
import CPPTEditorModal, { type CPPTContent, parseSOAPFromAIText } from './CPPTEditorModal';

interface ChatWindowProps {
  messages: ChatMessage[];
  executing: boolean;
  onSend: (query: string) => void;
  onSendAudio: (audio: File) => void;
  onReviewSOA: (noteId: string, content: SOAContent) => void;
  onConfirmSOA: (noteId: string, accept: boolean) => void;
  onCommitTempSOAP?: (tempId: string) => Promise<any>;
  onUpdateTempSOAP?: (tempId: string, content: any) => Promise<any>;
  patients?: PatientRecord[];
  selectedPatient?: string;
  onSelectPatient?: (patientId: string) => void;
}

// FAQ for Active Patient Consultation (SIMRS MCP & EHR Data)
const PATIENT_FAQS = [
  { icon: '📋', label: '1. Ambil Informasi Demografi Pasien', text: 'Ambil data profil demografi pasien dari modul RME SIMRS.' },
  { icon: '📝', label: '2. Ambil Anamnesis Sebelumnya', text: 'Tarik data anamnesis dari modul RME SIMRS.' },
  { icon: '🧪', label: '3. Evaluasi Hasil Lab & Pemeriksaan SIMRS', text: 'Evaluasi hasil laboratorium serial, nilai eGFR, rasio uACR, elektrolit, dan tanda vital dari pasien ini.' },
  { icon: '🎯', label: '4. Rekomendasi Diagnosis & ICD-10 Pasien', text: 'Berikan rekomendasi diagnosis kerja (primer) dan diagnosis banding lengkap beserta kodefikasi ICD-10 dan tingkat keyakinan.' },
  { icon: '💊', label: '5. Rekomendasi Terapi Obat Pasien Ini', text: 'Berikan rekomendasi rejimen obat lini pertama dan panduan penyesuaian dosis ginjal (Renal Dosing) pada pasien ini.' },
  { icon: '💉', label: '6. Rekomendasi Tindakan & Prosedur Medis', text: 'Berikan rekomendasi tindakan medis, prosedur diagnostik/intervensi klinis, monitoring khusus, dan tata laksana non-farmakologi untuk pasien ini.' },
  { icon: '📖', label: '7. Penjelasan Patofisiologi Penyakit Pasien', text: 'Tampilkan penjelasan patofisiologi penyakit, kriteria diagnostik baku, dan tahapan klinis (staging) pada pasien ini.' },
  { icon: '🚨', label: '8. Deteksi Tanda Bahaya & Red Flags Pasien', text: 'Lakukan deteksi tanda bahaya klinis (clinical red flags), ambang kedaruratan, dan risiko komplikasi pada pasien ini.' },
  { icon: '🛡️', label: '9. Skrining Interaksi & Keamanan Obat Pasien', text: 'Lakukan skrining interaksi obat-ke-obat (DDI), kontraindikasi riwayat alergi silang, dan keamanan farmakologi pasien ini.' },
  { icon: '📤', label: '10. Buat Draft CPPT S/O/A/P', text: 'Buat resume catatan perkembangan pasien terintegrasi (CPPT / S-O-A-P) dari data SOAP temp / konsultasi klinis dan kirim/sinkronisasikan ke modul RME SIMRS.' },
];

// FAQ for General Medical Consultation (Knowledge Management, Guidelines, Drug Dosing, Literature)
const GENERAL_FAQS = [
  { icon: '📖', label: '1. Pedoman Klinis & Kriteria Diagnosis', text: 'Jelaskan pedoman diagnosis baku, staging klinis, dan kriteria diagnostik penyakit menurut konsensus medis dan literatur terkini.' },
  { icon: '💊', label: '2. Panduan Terapi & Rejimen Lini Pertama', text: 'Bagaimana panduan pemilihan terapi obat lini pertama, lini kedua, dan kombinasi berdasarkan pedoman klinis berbasis bukti (Evidence-Based Medicine)?' },
  { icon: '💉', label: '3. Panduan Tindakan & Prosedur Medis', text: 'Jelaskan indikasi baku, protokol persiapan, kontraindikasi, dan langkah prosedur tindakan klinis/intervensi medis.' },
  { icon: '⚖️', label: '4. Penyesuaian Dosis Ginjal & Hepar', text: 'Bagaimana panduan penyesuaian dosis obat (Renal Dosing & Hepatic Adjustment) pada pasien dengan penurunan eGFR atau gangguan fungsi hati?' },
  { icon: '🛡️', label: '5. Skrining Interaksi Obat & Kontraindikasi', text: 'Jelaskan mekanisme interaksi obat-ke-obat (DDI) mayor yang sering terjadi, kombinasi berisiko tinggi, dan kontraindikasi absolut farmakologi.' },
  { icon: '🚨', label: '6. Deteksi Tanda Bahaya & Kedaruratan', text: 'Apa saja tanda bahaya (clinical red flags), ambang kritis tanda vital, dan kriteria rujukan darurat pada kondisi medis akut?' },
  { icon: '🧪', label: '7. Interpretasi Biomarker & Hasil Lab', text: 'Bagaimana interpretasi klinis profil biomarker laboratorium, batas normal/kritis, dan algoritma diagnostik berbasis bukti?' },
  { icon: '📚', label: '8. Ringkasan Studi Klinis & Meta-Analisis', text: 'Sajikan ringkasan meta-analisis dan uji klinis acak (RCT) terbaru mengenai efektivitas dan keamanan intervensi medis.' },
  { icon: '👥', label: '9. Pertimbangan Populasi Khusus', text: 'Bagaimana panduan klinis dan pertimbangan dosis obat pada populasi khusus seperti geriatri, pediatri, dan wanita hamil/menyusui?' },
  { icon: '💬', label: '10. Edukasi & Konseling Pasien', text: 'Sajikan rekomendasi edukasi gaya hidup, kepatuhan terapi obat, tanda bahaya pemantauan mandiri, dan jadwal kontrol rutin bagi pasien.' },
];

export default function ChatWindow({
  messages,
  executing,
  onSend,
  onSendAudio,
  onReviewSOA,
  onConfirmSOA,
  onCommitTempSOAP,
  onUpdateTempSOAP,
  patients = [],
  selectedPatient = '',
  onSelectPatient,
}: ChatWindowProps) {
  const threadRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const audioInputRef = useRef<HTMLInputElement>(null);
  const [recorderOpen, setRecorderOpen] = useState(false);
  const [sessionStarted, setSessionStarted] = useState(false);
  const [editedMessages, setEditedMessages] = useState<Record<number, string>>({});
  const [activeDiagnosisEditIdx, setActiveDiagnosisEditIdx] = useState<number | null>(null);
  const [activeMedicationEditIdx, setActiveMedicationEditIdx] = useState<number | null>(null);
  const [activeAnamnesisEditIdx, setActiveAnamnesisEditIdx] = useState<number | null>(null);
  const [activeCPPTEditIdx, setActiveCPPTEditIdx] = useState<number | null>(null);
  const [cpptModalOpen, setCpptModalOpen] = useState(false);
  const [cpptInitialContent, setCpptInitialContent] = useState<Partial<CPPTContent> | undefined>(undefined);
  const [committingTempId, setCommittingTempId] = useState<string | null>(null);

  useEffect(() => {
    if (messages.length > 0) {
      setSessionStarted(true);
    } else {
      setSessionStarted(false);
    }
  }, [messages.length]);

  useEffect(() => {
    if (threadRef.current) {
      threadRef.current.scrollTop = threadRef.current.scrollHeight;
    }
  }, [messages, executing]);

  const isChatActive = messages.length > 0 || sessionStarted;

  const handleSend = (e?: React.SyntheticEvent) => {
    if (e) e.preventDefault();
    if (!inputRef.current) return;
    const val = inputRef.current.value.trim();
    if (!val || executing) return;

    onSend(val);
    inputRef.current.value = '';
  };

  const handleAudioSelected = (e: ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      onSendAudio(files[0]);
      e.target.value = '';
    }
  };

  /** Open CPPT modal, optionally pre-filling from SOA note content */
  const openCpptModal = (initial?: Partial<CPPTContent>, editIdx: number | null = null) => {
    setCpptInitialContent(initial);
    setActiveCPPTEditIdx(editIdx);
    setCpptModalOpen(true);
  };

  const currentPatient = patients.find(p => p.patient_id === selectedPatient);

  return (
    <div className="flex-1 flex flex-col h-full bg-emerald-50/50 dark:bg-slate-950 overflow-hidden relative transition-colors">
      {/* Audio Recorder Modal */}
      <AudioRecorderModal
        isOpen={recorderOpen}
        onClose={() => setRecorderOpen(false)}
        onSendAudio={onSendAudio}
        disabled={executing}
      />

      {/* Diagnosis & ICD-10 Interactive Editor Modal */}
      {activeDiagnosisEditIdx !== null && (
        <DiagnosisEditor
          initialContent={editedMessages[activeDiagnosisEditIdx] || messages[activeDiagnosisEditIdx]?.content || ''}
          onSave={(updatedMarkdown) => {
            setEditedMessages(prev => ({ ...prev, [activeDiagnosisEditIdx]: updatedMarkdown }));
            setActiveDiagnosisEditIdx(null);
          }}
          onClose={() => setActiveDiagnosisEditIdx(null)}
        />
      )}

      {/* Medication & Therapy Interactive Editor Modal */}
      {activeMedicationEditIdx !== null && (
        <MedicationEditorModal
          initialContent={editedMessages[activeMedicationEditIdx] || messages[activeMedicationEditIdx]?.content || ''}
          onSave={(updatedMarkdown) => {
            setEditedMessages(prev => ({ ...prev, [activeMedicationEditIdx]: updatedMarkdown }));
            setActiveMedicationEditIdx(null);
          }}
          onClose={() => setActiveMedicationEditIdx(null)}
        />
      )}

      {/* Anamnesis Interactive Editor Modal */}
      {activeAnamnesisEditIdx !== null && (
        <AnamnesisEditorModal
          initialContent={editedMessages[activeAnamnesisEditIdx] || messages[activeAnamnesisEditIdx]?.content || ''}
          onSave={(updatedMarkdown) => {
            setEditedMessages(prev => ({ ...prev, [activeAnamnesisEditIdx]: updatedMarkdown }));
            setActiveAnamnesisEditIdx(null);
          }}
          onClose={() => setActiveAnamnesisEditIdx(null)}
        />
      )}

      {/* CPPT & S/O/A/P Interactive Review & Confirmation Modal */}
      {cpptModalOpen && (
        <CPPTEditorModal
          isOpen={cpptModalOpen}
          onClose={() => {
            setCpptModalOpen(false);
            setCpptInitialContent(undefined);
            setActiveCPPTEditIdx(null);
          }}
          patient={currentPatient}
          messages={messages}
          initialContent={cpptInitialContent}
          isSubmitting={executing}
          onConfirmSend={(content) => {
            if (activeCPPTEditIdx !== null) {
              const updatedMd = `## 📋 Resume Klinis Terpadu & CPPT (S-O-A-P + Instruksi)\n\n### 👤 S — Subjective\n${content.subjective}\n\n### 🔬 O — Objective\n${content.objective}\n\n### 🎯 A — Assessment\n${content.assessment}\n\n### 💊 P — Plan (Rencana Terapi)\n${content.plan}\n\n### 📝 I — Instruksi Klinis (PPA)\n${content.instructions || 'Sesuai edukasi dan tata laksana klinis.'}\n\n---\n*(✅ Telah divalidasi dan dikonfirmasi oleh Dokter Penanggung Jawab)*`;
              setEditedMessages(prev => ({ ...prev, [activeCPPTEditIdx]: updatedMd }));
            }
            setCpptModalOpen(false);
            setCpptInitialContent(undefined);
            setActiveCPPTEditIdx(null);

            const formattedPrompt = `Kirim dan sinkronisasikan CPPT S/O/A/P terkonfirmasi DPJP ke SIMRS:
- Subjective (S): ${content.subjective}
- Objective (O): ${content.objective}
- Assessment (A): ${content.assessment}
- Plan (P): ${content.plan}
- Instruksi (I): ${content.instructions || '-'}`;
            onSend(formattedPrompt);
          }}
        />
      )}

      {/* Message Thread */}
      <div ref={threadRef} className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-5">
        {!isChatActive && !executing ? (
          <NewConsultationSelection
            patients={patients}
            onSelectGeneral={() => {
              if (onSelectPatient) onSelectPatient('');
              setSessionStarted(true);
              setTimeout(() => inputRef.current?.focus(), 100);
            }}
            onSelectPatient={(patientId) => {
              if (onSelectPatient) onSelectPatient(patientId);
              setSessionStarted(true);
              setTimeout(() => inputRef.current?.focus(), 100);
            }}
          />
        ) : (
          <>
            {isChatActive && messages.length === 0 && !executing && (
              <div className="text-center py-10 text-emerald-700 dark:text-emerald-400 space-y-3 animate-in fade-in duration-200">
                <div className="flex justify-center">
                  <BotAvatar size="lg" />
                </div>
                <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-100 dark:bg-slate-800 text-xs font-bold text-emerald-900 dark:text-emerald-300 border border-emerald-300 dark:border-slate-700 shadow-2xs">
                  <span>
                    {currentPatient
                      ? `🏥 Pasien Terhubung: ${currentPatient.name} (${currentPatient.patient_id})`
                      : '🌐 Mode Konsultasi Medis Umum'}
                  </span>
                  <button
                    type="button"
                    onClick={() => {
                      setSessionStarted(false);
                      if (onSelectPatient) onSelectPatient('');
                    }}
                    className="ml-2 text-[10px] text-emerald-700 dark:text-emerald-400 underline hover:text-emerald-950 dark:hover:text-white font-semibold"
                  >
                    Ganti Mode
                  </button>
                </div>
                <h3 className="text-base sm:text-lg font-bold text-emerald-950 dark:text-white">
                  Siap Membantu Evaluasi Klinis Anda
                </h3>
                <p className="text-xs max-w-md mx-auto text-emerald-600 dark:text-slate-400">
                  {currentPatient
                    ? `Data rekam medis SIMRS pasien ${currentPatient.name} telah siap. Silakan tanyakan evaluasi klinis, kontraindikasi obat, atau perbaruan resume SOAP.`
                    : 'Silakan tanyakan panduan klinis, literatur farmasi, atau protokol medis di bawah.'}
                </p>
              </div>
            )}

            {messages.map((m, i) => {
              const displayContent = editedMessages[i] || m.content;
              const isNoPatientWarning =
                displayContent.includes('Data Rekam Medis Pasien Belum Dipilih') ||
                displayContent.includes('Data Rekam Medis Belum Dipilih') ||
                displayContent.includes('belum ada data pasien aktif yang dipilih') ||
                displayContent.includes('Pasien Belum Dipilih') ||
                displayContent.includes('Data Pasien Belum Dipilih');

              const isAnamnesisMessage =
                m.role === 'assistant' &&
                !isNoPatientWarning &&
                Boolean(selectedPatient) &&
                (displayContent.includes('Hasil Anamnesis') ||
                  displayContent.includes('Data Anamnesis') ||
                  displayContent.includes('Tabel Komponen Anamnesis') ||
                  (displayContent.includes('Keluhan Utama') &&
                    displayContent.includes('Riwayat Penyakit Sekarang') &&
                    (displayContent.includes('RPD') || displayContent.includes('Riwayat Alergi'))));

              const isDiagnosisMessage =
                m.role === 'assistant' &&
                !isNoPatientWarning &&
                Boolean(selectedPatient) &&
                (displayContent.includes('🎯 Rekomendasi Diagnosis') ||
                  (displayContent.includes('Diagnosis') &&
                    displayContent.includes('ICD-10') &&
                    (displayContent.includes('Diagnosis Kerja') ||
                      displayContent.includes('Diagnosis Banding') ||
                      displayContent.includes('Primer'))));

              const isMedicationMessage =
                m.role === 'assistant' &&
                !isNoPatientWarning &&
                Boolean(selectedPatient) &&
                (displayContent.includes('Rekomendasi Terapi Obat') ||
                  displayContent.includes('Rekomendasi Obat') ||
                  displayContent.includes('Terapi Farmakologi') ||
                  displayContent.includes('Rejimen Farmakoterapi') ||
                  (displayContent.includes('Nama Obat') &&
                    displayContent.includes('Dosis') &&
                    (displayContent.includes('Rejimen') || displayContent.includes('Regimen') || displayContent.includes('Indikasi'))));

              const isCPPTMessage =
                m.role === 'assistant' &&
                !isNoPatientWarning &&
                (displayContent.includes('Resume CPPT') ||
                  displayContent.includes('Resume Klinis (S-O-A-P)') ||
                  displayContent.includes('Resume Klinis') ||
                  displayContent.includes('Transkrip Percakapan Medis') ||
                  displayContent.includes('S — Subjective') ||
                  displayContent.includes('S - Subjective') ||
                  (displayContent.includes('Subjective') &&
                    displayContent.includes('Assessment') &&
                    (displayContent.includes('Objective') || displayContent.includes('Plan'))) ||
                  (displayContent.includes('CPPT') &&
                    displayContent.includes('S/O/A/P')) ||
                  Boolean(m.metadata?.type === 'soa_note' && m.metadata?.note));

              const hasSOANote =
                m.role === 'assistant' &&
                !isNoPatientWarning &&
                m.metadata?.type === 'soa_note' &&
                Boolean(m.metadata.note);

              const isErrorMessage =
                m.role === 'assistant' &&
                (Boolean(m.metadata?.is_error) ||
                  displayContent.includes('Error 500') ||
                  displayContent.includes('kendala teknis') ||
                  displayContent.startsWith('⚠️ Terjadi kendala') ||
                  displayContent.startsWith('⚠️ Koneksi ke server'));


              return (
                <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div
                    className={`max-w-3xl rounded-2xl p-5 ${m.role === 'user'
                      ? 'bg-emerald-600 text-white rounded-br-none shadow-md'
                      : isErrorMessage
                        ? 'bg-red-50/90 dark:bg-red-950/40 border border-red-300 dark:border-red-800 text-red-950 dark:text-red-200 rounded-bl-none shadow-sm'
                        : 'bg-white dark:bg-slate-900 border border-emerald-200 dark:border-slate-800 text-emerald-900 dark:text-slate-100 rounded-bl-none shadow-sm'
                      }`}
                  >
                    <div className="text-[10px] opacity-80 mb-2 font-semibold uppercase tracking-wider flex items-center gap-1.5">
                      {m.role === 'user' ? (
                        <span>👤 Anda (Dokter)</span>
                      ) : (
                        <span className={`flex items-center gap-1.5 font-bold ${isErrorMessage ? 'text-red-700 dark:text-red-400' : 'text-emerald-700 dark:text-emerald-400'}`}>
                          <BotAvatar size="sm" />
                          <span>{isErrorMessage ? 'Sistem AI Medis (Error)' : 'Asisten AI Medis'}</span>
                        </span>
                      )}
                      <span className="opacity-50">• {new Date(m.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                      {editedMessages[i] && (
                        <span className="ml-auto px-2 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300 text-[9px] font-bold border border-emerald-300 dark:border-emerald-700">
                          ✏️ Telah Divalidasi Dokter
                        </span>
                      )}
                    </div>

                    {m.role === 'user' ? (
                      <div className="whitespace-pre-wrap text-sm leading-relaxed font-medium">
                        {displayContent}
                      </div>
                    ) : (
                      <>
                        <MarkdownContent content={displayContent} />

                        {/* Retry Button for Error 500 / Server Errors */}
                        {isErrorMessage && (
                          <div className="mt-3 pt-2.5 border-t border-red-200 dark:border-red-800/60 flex items-center justify-between flex-wrap gap-2">
                            <button
                              type="button"
                              onClick={() => {
                                if (m.metadata?.retry_audio_file) {
                                  onSendAudio(m.metadata.retry_audio_file);
                                } else {
                                  let retryQuery = m.metadata?.retry_query;
                                  if (!retryQuery) {
                                    for (let k = i - 1; k >= 0; k--) {
                                      if (messages[k]?.role === 'user' && !messages[k]?.content.startsWith('[Rekaman Audio]')) {
                                        retryQuery = messages[k].content;
                                        break;
                                      }
                                    }
                                  }
                                  if (retryQuery) {
                                    onSend(retryQuery);
                                  }
                                }
                              }}
                              disabled={executing}
                              className="px-3.5 py-1.5 rounded-xl bg-red-600 hover:bg-red-500 disabled:opacity-50 text-white font-bold text-xs flex items-center gap-1.5 transition-all shadow-xs active:scale-95 cursor-pointer"
                            >
                              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                              </svg>
                              <span>Coba Lagi (Retry)</span>
                            </button>
                          </div>
                        )}

                        {/* Interactive Edit Button for Anamnesis Messages */}
                        {/* {isAnamnesisMessage && (
                          <div className="mt-3 pt-3 border-t border-emerald-100 dark:border-slate-800 flex items-center justify-between flex-wrap gap-2">

                            <span className="text-[11px] text-emerald-700 dark:text-slate-400 flex items-center gap-1 font-semibold">
                              <span>📝</span>
                              <span>Data Anamnesis Klinis Pasien (RME SIMRS)</span>
                            </span>
                            <button
                              type="button"
                              onClick={() => setActiveAnamnesisEditIdx(i)}
                              className="px-3.5 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs flex items-center gap-1.5 transition-all shadow-xs"
                            >
                              <span>✏️</span>
                              <span>Edit & Sesuaikan Tabel Anamnesis</span>
                            </button>
                          </div>
                        )} */}

                        {/* Interactive Edit & Search ICD-10 Button for Diagnosis Messages */}
                        {/*isDiagnosisMessage && (
                          <div className="mt-3 pt-3 border-t border-emerald-100 dark:border-slate-800 flex items-center justify-between flex-wrap gap-2">
                            <span className="text-[11px] text-emerald-700 dark:text-slate-400 flex items-center gap-1 font-semibold">
                              <span>🎯</span>
                              <span>Dukungan Keputusan Klinis Diagnosis & ICD-10</span>
                            </span>
                            <button
                              type="button"
                              onClick={() => setActiveDiagnosisEditIdx(i)}
                              className="px-3.5 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs flex items-center gap-1.5 transition-all shadow-xs"
                            >
                              <span>✏️</span>
                              <span>Edit & Cari Kode ICD-10</span>
                            </button>
                          </div>
                        )*/}

                        {/* Interactive Edit & Search Medication Button for Therapy Messages */}
                        {/* {isMedicationMessage && (
                          <div className="mt-3 pt-3 border-t border-emerald-100 dark:border-slate-800 flex items-center justify-between flex-wrap gap-2">
                            <span className="text-[11px] text-teal-700 dark:text-teal-400 flex items-center gap-1 font-semibold">
                              <span>💊</span>
                              <span>Dukungan Keputusan Terapi Obat & Dosis Klinis</span>
                            </span>
                            <button
                              type="button"
                              onClick={() => setActiveMedicationEditIdx(i)}
                              className="px-3.5 py-1.5 rounded-xl bg-teal-600 hover:bg-teal-500 text-white font-bold text-xs flex items-center gap-1.5 transition-all shadow-xs"
                            >
                              <span>✏️</span>
                              <span>Edit & Cari Rekomendasi Obat</span>
                            </button>
                          </div>
                        )} */}

                        {/* Temporary SOAP & Audio Recording Card */}
                        {m.metadata?.temp_soap && (
                          <div className="mt-4 rounded-xl border border-emerald-300/90 dark:border-emerald-700/70 bg-gradient-to-br from-emerald-50/90 via-teal-50/40 to-white dark:from-slate-900 dark:via-slate-850 dark:to-slate-900 p-4 shadow-sm space-y-3.5 animate-in fade-in duration-200">
                            {/* Header & Status */}
                            <div className="flex items-center justify-between flex-wrap gap-2 pb-2.5 border-b border-emerald-200/70 dark:border-slate-800">
                              <div className="flex items-center gap-2">
                                <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-600 text-white text-sm shadow-2xs">
                                  💾
                                </span>
                                <div>
                                  <h4 className="text-xs font-bold text-emerald-950 dark:text-emerald-200 flex items-center gap-1.5">
                                    <span>Data SOAP Temp (Tersimpan di DB Aplikasi)</span>
                                    <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-mono">
                                      ({m.metadata.temp_soap.temp_id})
                                    </span>
                                  </h4>
                                  <p className="text-[10px] text-emerald-700 dark:text-slate-400">
                                    Sesi: {m.metadata.temp_soap.session_id} • DPJP: {m.metadata.temp_soap.doctor_name || 'Dokter'}
                                  </p>
                                </div>
                              </div>
                              <div>
                                {m.metadata.temp_soap.status === 'synced_to_simrs' || m.metadata.temp_soap.simrs_sync_status === 'synced' ? (
                                  <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-100 dark:bg-emerald-950/80 text-emerald-800 dark:text-emerald-300 text-[10px] font-bold border border-emerald-300 dark:border-emerald-700 shadow-2xs">
                                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                                    <span>✅ Tersinkronisasi ke SIMRS</span>
                                    {m.metadata.temp_soap.simrs_log_id && (
                                      <span className="opacity-70 font-mono">({m.metadata.temp_soap.simrs_log_id})</span>
                                    )}
                                  </span>
                                ) : (
                                  <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-amber-100 dark:bg-amber-950/80 text-amber-800 dark:text-amber-300 text-[10px] font-bold border border-amber-300 dark:border-amber-700 shadow-2xs">
                                    <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-ping"></span>
                                    <span>🟡 Draft Temp (Belum ke SIMRS)</span>
                                  </span>
                                )}
                              </div>
                            </div>

                            {/* Audio Consultation Player */}
                            {m.metadata.temp_soap.audio_url && (
                              <div className="rounded-lg bg-white dark:bg-slate-800/90 border border-emerald-200 dark:border-slate-700 p-3 flex flex-col gap-2 shadow-2xs">
                                <div className="flex items-center justify-between text-xs">
                                  <span className="font-semibold text-emerald-900 dark:text-slate-200 flex items-center gap-1.5">
                                    <span>🎙️ Rekaman Suara Konsultasi:</span>
                                    <span className="font-medium text-emerald-750 dark:text-emerald-300 truncate max-w-xs">{m.metadata.temp_soap.audio_filename}</span>
                                  </span>
                                  <span className="text-[10px] text-emerald-600 dark:text-slate-400 font-mono">
                                    {m.metadata.temp_soap.audio_size_bytes ? `${Math.round(m.metadata.temp_soap.audio_size_bytes / 1024)} KB` : 'Audio WAV'}
                                  </span>
                                </div>
                                <audio
                                  controls
                                  className="w-full h-8 accent-emerald-600 rounded"
                                  src={m.metadata.temp_soap.audio_url.startsWith('http') || m.metadata.temp_soap.audio_url.startsWith('/api')
                                    ? m.metadata.temp_soap.audio_url
                                    : `/api/v1/agent/soap-temp/${m.metadata.temp_soap.temp_id}/audio`}
                                  preload="metadata"
                                >
                                  Browser Anda tidak mendukung elemen pemutar audio.
                                </audio>
                              </div>
                            )}

                            {/* Action Buttons: Review & Send to SIMRS */}
                            <div className="flex items-center justify-between flex-wrap gap-2 pt-1">
                              <button
                                type="button"
                                onClick={() => {
                                  const sContent = m.metadata?.temp_soap?.soap_content;
                                  const parsed = sContent ? {
                                    subjective: sContent.subjective || '',
                                    objective: sContent.objective || '',
                                    assessment: sContent.assessment || '',
                                    plan: sContent.plan || '',
                                    instructions: sContent.instructions || '',
                                  } : parseSOAPFromAIText(displayContent, messages, currentPatient);
                                  openCpptModal(parsed, i);
                                }}
                                className="px-3.5 py-1.5 rounded-xl bg-white dark:bg-slate-800 hover:bg-emerald-50 dark:hover:bg-slate-750 text-emerald-800 dark:text-emerald-300 font-bold text-xs border border-emerald-300 dark:border-slate-700 flex items-center gap-1.5 transition-all shadow-2xs cursor-pointer"
                              >
                                <span>✏️</span>
                                <span>Tinjau & Edit SOAP Temp</span>
                              </button>

                              {m.metadata.temp_soap.status !== 'synced_to_simrs' && m.metadata.temp_soap.simrs_sync_status !== 'synced' && (
                                <button
                                  type="button"
                                  onClick={async () => {
                                    if (onCommitTempSOAP && m.metadata?.temp_soap?.temp_id) {
                                      setCommittingTempId(m.metadata.temp_soap.temp_id);
                                      try {
                                        await onCommitTempSOAP(m.metadata.temp_soap.temp_id);
                                      } finally {
                                        setCommittingTempId(null);
                                      }
                                    }
                                  }}
                                  disabled={executing || committingTempId === m.metadata.temp_soap.temp_id}
                                  className="px-4 py-1.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 disabled:opacity-50 text-white font-bold text-xs flex items-center gap-1.5 transition-all shadow-xs active:scale-95 cursor-pointer"
                                >
                                  {committingTempId === m.metadata.temp_soap.temp_id ? (
                                    <>
                                      <svg className="w-3.5 h-3.5 animate-spin" viewBox="0 0 24 24" fill="none">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                      </svg>
                                      <span>Mengirim ke SIMRS...</span>
                                    </>
                                  ) : (
                                    <>
                                      <span>🚀</span>
                                      <span>Kirim & Sinkronkan ke SIMRS</span>
                                    </>
                                  )}
                                </button>
                              )}
                            </div>
                          </div>
                        )}

                        <WorkflowExpandable steps={m.metadata?.steps} />
                      </>
                    )}
                  </div>
                </div>
              );
            })}

            {executing && (
              <div className="flex justify-start">
                <AgentStatusIndicator executing={executing} />
              </div>
            )}
          </>
        )}
      </div>

      {/* Input Bar (Only displayed when consultation mode is selected/active) */}
      {isChatActive && (
        <div className="p-4 border-t border-emerald-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 backdrop-blur shrink-0 transition-colors animate-in slide-in-from-bottom-2 duration-150">
          {/* Quick FAQ Prompts (2 Rows: 5 cards on top, 4 cards on bottom) */}
          {(() => {
            const activeFaqs = selectedPatient ? PATIENT_FAQS : GENERAL_FAQS;
            const isGeneralMode = !selectedPatient;

            return (
              <div className="mb-3 max-w-5xl mx-auto space-y-1.5">
                <div className="flex items-center justify-between mb-1 px-0.5 flex-wrap gap-1">
                  <span className="text-[10px] font-bold text-emerald-800 dark:text-emerald-400 uppercase tracking-wider flex items-center gap-1">
                    <span>{isGeneralMode ? '📚' : '💡'}</span>
                    <span>
                      {isGeneralMode
                        ? 'FAQ Konsultasi Medis Umum & Knowledge Management (Literatur, Dosis, Pedoman):'
                        : 'FAQ & Kueri Cepat Rekam Medis Pasien (SIMRS):'}
                    </span>
                  </span>
                  <span className="text-[9px] font-bold px-2 py-0.5 rounded-full bg-emerald-100/90 dark:bg-slate-800 text-emerald-900 dark:text-emerald-300 border border-emerald-200 dark:border-slate-700">
                    {isGeneralMode ? '🌐 Mode Literatur Medis / RAG' : '🏥 Mode Pasien Terhubung SIMRS'}
                  </span>
                </div>

                {/* Row 1: 5 cards */}
                <div className="grid grid-cols-2 sm:grid-cols-5 gap-1.5">
                  {activeFaqs.slice(0, 5).map((p, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => {
                        const isCpptFaq = /CPPT|SOAP|Draft|Draft CPPT/i.test(p.label);
                        if (isCpptFaq && selectedPatient) {
                          let targetIdx: number | null = null;
                          let foundTempSoapContent: any = null;

                          // 1. Check messages for active temp_soap
                          for (let i = messages.length - 1; i >= 0; i--) {
                            if (messages[i].metadata?.temp_soap?.soap_content) {
                              targetIdx = i;
                              foundTempSoapContent = messages[i].metadata?.temp_soap?.soap_content;
                              break;
                            }
                          }

                          if (foundTempSoapContent) {
                            const parsed = {
                              subjective: foundTempSoapContent.subjective || '',
                              objective: foundTempSoapContent.objective || '',
                              assessment: foundTempSoapContent.assessment || '',
                              plan: foundTempSoapContent.plan || '',
                              instructions: foundTempSoapContent.instructions || '',
                            };
                            openCpptModal(parsed, targetIdx);
                            return;
                          }

                          // 2. Fallback search
                          for (let i = messages.length - 1; i >= 0; i--) {
                            const c = messages[i].content;
                            if (c.includes('Resume Klinis (S-O-A-P)') || c.includes('Transkrip Percakapan Medis') || c.includes('Resume CPPT') || c.includes('Catatan Perkembangan Pasien Terintegrasi') || (c.includes('Subjective') && c.includes('Objective'))) {
                              targetIdx = i;
                              break;
                            }
                          }
                          const initialText = targetIdx !== null ? (editedMessages[targetIdx] || messages[targetIdx].content) : '';
                          const parsed = parseSOAPFromAIText(initialText, messages, currentPatient);
                          openCpptModal(parsed, targetIdx);
                          return;
                        }
                        if (inputRef.current) {
                          inputRef.current.value = p.text;
                          inputRef.current.focus();
                        }
                      }}
                      className="px-2.5 py-1.5 bg-emerald-50/90 dark:bg-slate-800/90 hover:bg-emerald-100 dark:hover:bg-slate-700 text-emerald-950 dark:text-emerald-200 rounded-xl border border-emerald-200/90 dark:border-slate-700 text-xs font-medium transition-all shadow-2xs hover:shadow-xs active:scale-[0.98] flex items-start gap-1.5 text-left group min-h-[44px]"
                    >
                      <span className="shrink-0 text-sm mt-0.5">{p.icon}</span>
                      <span className="text-[11px] leading-tight font-medium whitespace-normal break-words group-hover:text-emerald-950 dark:group-hover:text-white">
                        {p.label}
                      </span>
                    </button>
                  ))}
                </div>

                {/* Row 2: 5 cards */}
                <div className="grid grid-cols-2 sm:grid-cols-5 gap-1.5">
                  {activeFaqs.slice(5, 10).map((p, idx) => (
                    <button
                      key={idx + 5}
                      type="button"
                      onClick={() => {
                        const isCpptFaq = /CPPT|SOAP|Draft|Draft CPPT/i.test(p.label);
                        if (isCpptFaq && selectedPatient) {
                          let targetIdx: number | null = null;
                          let foundTempSoapContent: any = null;

                          // 1. Check messages for active temp_soap
                          for (let i = messages.length - 1; i >= 0; i--) {
                            if (messages[i].metadata?.temp_soap?.soap_content) {
                              targetIdx = i;
                              foundTempSoapContent = messages[i].metadata?.temp_soap?.soap_content;
                              break;
                            }
                          }

                          if (foundTempSoapContent) {
                            const parsed = {
                              subjective: foundTempSoapContent.subjective || '',
                              objective: foundTempSoapContent.objective || '',
                              assessment: foundTempSoapContent.assessment || '',
                              plan: foundTempSoapContent.plan || '',
                              instructions: foundTempSoapContent.instructions || '',
                            };
                            openCpptModal(parsed, targetIdx);
                            return;
                          }

                          // 2. Fallback search
                          for (let i = messages.length - 1; i >= 0; i--) {
                            const c = messages[i].content;
                            if (c.includes('Resume Klinis (S-O-A-P)') || c.includes('Transkrip Percakapan Medis') || c.includes('Resume CPPT') || c.includes('Catatan Perkembangan Pasien Terintegrasi') || (c.includes('Subjective') && c.includes('Objective'))) {
                              targetIdx = i;
                              break;
                            }
                          }
                          const initialText = targetIdx !== null ? (editedMessages[targetIdx] || messages[targetIdx].content) : '';
                          const parsed = parseSOAPFromAIText(initialText, messages, currentPatient);
                          openCpptModal(parsed, targetIdx);
                          return;
                        }
                        if (inputRef.current) {
                          inputRef.current.value = p.text;
                          inputRef.current.focus();
                        }
                      }}
                      className="px-2.5 py-1.5 bg-emerald-50/90 dark:bg-slate-800/90 hover:bg-emerald-100 dark:hover:bg-slate-700 text-emerald-950 dark:text-emerald-200 rounded-xl border border-emerald-200/90 dark:border-slate-700 text-xs font-medium transition-all shadow-2xs hover:shadow-xs active:scale-[0.98] flex items-start gap-1.5 text-left group min-h-[44px]"
                    >
                      <span className="shrink-0 text-sm mt-0.5">{p.icon}</span>
                      <span className="text-[11px] leading-tight font-medium whitespace-normal break-words group-hover:text-emerald-950 dark:group-hover:text-white">
                        {p.label}
                      </span>
                    </button>
                  ))}
                </div>
              </div>
            );
          })()}

          <div className="max-w-5xl mx-auto flex gap-2 sm:gap-3 items-center">
            <input
              ref={audioInputRef}
              type="file"
              accept="audio/wav,audio/mp3,audio/mpeg,audio/m4a,.wav,.mp3,.m4a"
              className="hidden"
              onChange={handleAudioSelected}
            />
            <button
              type="button"
              onClick={() => setRecorderOpen(true)}
              disabled={executing}
              title="Rekam audio mikrofon langsung untuk transkripsi dan resume SOAP"
              className="px-3 py-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-semibold transition-all shadow-sm flex items-center gap-1.5 shrink-0"
            >
              <span>🎙️</span>
              <span className="hidden sm:inline">Rekam</span>
            </button>
            <button
              type="button"
              onClick={() => audioInputRef.current?.click()}
              disabled={executing}
              title="Unggah file rekaman audio klinis (MP3 / WAV) untuk transkripsi & diarisasi"
              className="px-3 py-3 bg-emerald-100 dark:bg-slate-800 hover:bg-emerald-200 dark:hover:bg-slate-700 disabled:opacity-50 text-emerald-900 dark:text-slate-200 border border-emerald-300 dark:border-slate-700 rounded-xl text-xs font-semibold transition-colors shrink-0 flex items-center gap-1"
            >
              <span>📁</span>
              <span>Upload Audio</span>
            </button>
            <input
              ref={inputRef}
              type="text"
              placeholder="Tanyakan evaluasi klinis, data SIMRS, atau pembaruan rekam medis..."
              onKeyDown={(e) => e.key === 'Enter' && handleSend(e)}
              className="flex-1 px-4 py-3 bg-emerald-50 dark:bg-slate-800/80 border border-emerald-200 dark:border-slate-700 rounded-xl text-emerald-950 dark:text-slate-100 placeholder-emerald-400 dark:placeholder-slate-500 text-sm focus:outline-none focus:border-emerald-500 transition-colors"
            />
            <button
              type="button"
              onClick={handleSend}
              disabled={executing}
              className="px-6 py-3 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-semibold rounded-xl text-sm transition-all shadow-md shrink-0"
            >
              {executing ? 'Memproses…' : 'Kirim'}
            </button>
          </div>

          {/* Persistent Medical Disclaimer Box */}
          <div className="mt-2.5 text-center">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg border border-amber-300/80 dark:border-amber-600/40 bg-amber-50/80 dark:bg-amber-950/40 text-[10px] text-amber-800 dark:text-amber-300 font-medium shadow-2xs">
              <span>⚠️</span>
              <span>
                <strong>Disclaimer Medis:</strong> AI Decision Support Tool ini bukan pengganti keputusan klinis dokter. Setiap rekomendasi obat dan tindakan medis wajib divalidasi oleh dokter penanggung jawab pelayanan (DPJP).
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
