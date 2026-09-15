'use client';

interface HITLOptionsCardProps {
  onStartRecord: () => void;
  onUploadFile: () => void;
  onOpenManualModal: () => void;
}

export default function HITLOptionsCard({
  onStartRecord,
  onUploadFile,
  onOpenManualModal,
}: HITLOptionsCardProps) {
  return (
    <div className="mt-3 p-4 rounded-2xl bg-gradient-to-br from-amber-500/10 via-emerald-500/5 to-teal-500/10 dark:from-amber-950/30 dark:via-emerald-950/20 dark:to-teal-950/30 border-2 border-amber-400/80 dark:border-amber-600/70 shadow-md space-y-3 animate-in fade-in slide-in-from-bottom-2 duration-200">
      {/* Header Banner */}
      <div className="flex items-center justify-between gap-2 flex-wrap">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-amber-500 animate-ping" />
          <span className="text-xs font-bold text-amber-950 dark:text-amber-200 uppercase tracking-wider">
            Verifikasi Data Klinis
          </span>
        </div>

        <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300 border border-amber-300 dark:border-amber-800">
          Data S/O Diperlukan
        </span>
      </div>

      <p className="text-xs font-semibold text-emerald-950 dark:text-slate-200">
        Mohon maaf hasil anamnesis atau pemeriksaan belum disampaikan, Silahkan isi terlebih dahulu?
      </p>

      {/* 3 Interactive Option Buttons */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 pt-1">
        {/* Option 1: Rekaman Suara */}
        <button
          type="button"
          onClick={onStartRecord}
          className="p-3 rounded-xl bg-white dark:bg-slate-900 hover:bg-emerald-50 dark:hover:bg-slate-800 border border-emerald-300 dark:border-slate-700 shadow-2xs hover:shadow-sm transition-all text-left flex flex-col justify-between group active:scale-[0.98]"
        >
          <div className="flex items-center gap-2 mb-1.5">
            <span className="text-lg group-hover:scale-110 transition-transform">🎙️</span>
            <span className="text-xs font-bold text-emerald-950 dark:text-white group-hover:text-emerald-600">
              Rekam Langsung
            </span>
          </div>
          <p className="text-[10px] text-emerald-700 dark:text-slate-400 leading-tight">
            Rekam audio konsultasi dokter-pasien via Generative AI STT &amp; auto SOAP.
          </p>
        </button>

        {/* Option 2: Upload File */}
        <button
          type="button"
          onClick={onUploadFile}
          className="p-3 rounded-xl bg-white dark:bg-slate-900 hover:bg-cyan-50 dark:hover:bg-slate-800 border border-cyan-300 dark:border-slate-700 shadow-2xs hover:shadow-sm transition-all text-left flex flex-col justify-between group active:scale-[0.98]"
        >
          <div className="flex items-center gap-2 mb-1.5">
            <span className="text-lg group-hover:scale-110 transition-transform">📄</span>
            <span className="text-xs font-bold text-cyan-950 dark:text-white group-hover:text-cyan-600">
              Upload Berkas
            </span>
          </div>
          <p className="text-[10px] text-cyan-800 dark:text-slate-400 leading-tight">
            Unggah rekaman audio, berkas lab, atau dokumen rekam medis.
          </p>
        </button>

        {/* Option 3: Input Manual */}
        <button
          type="button"
          onClick={onOpenManualModal}
          className="p-3 rounded-xl bg-gradient-to-br from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white shadow-sm hover:shadow-md transition-all text-left flex flex-col justify-between group active:scale-[0.98]"
        >
          <div className="flex items-center gap-2 mb-1.5">
            <span className="text-lg group-hover:scale-110 transition-transform">✍️</span>
            <span className="text-xs font-bold text-white">
              Input Manual (S &amp; O)
            </span>
          </div>
          <p className="text-[10px] text-emerald-100 leading-tight">
            Form 2 langkah (Subjektif &amp; Objektif) simpan ke SOAP Temporary DB.
          </p>
        </button>
      </div>
    </div>
  );
}
