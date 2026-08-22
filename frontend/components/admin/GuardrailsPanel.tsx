'use client';

import { useState, useEffect } from 'react';
import {
  GuardrailsService,
  type GuardrailConfig,
  type TestGuardrailResponse,
  type GuardrailViolation,
} from '@/services/guardrails.service';

export default function GuardrailsPanel() {
  const [config, setConfig] = useState<GuardrailConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // New Keyword input
  const [newKeyword, setNewKeyword] = useState('');

  // Simulator state
  const [testText, setTestText] = useState('Pasien NIK 3201012345670001 meminta resep palsu antibiotik untuk keperluan izin.');
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<TestGuardrailResponse | null>(null);

  // Violations list
  const [violations, setViolations] = useState<GuardrailViolation[]>([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [cfg, viols] = await Promise.all([
        GuardrailsService.getConfig(),
        GuardrailsService.getViolations(),
      ]);
      setConfig(cfg);
      setViolations(viols);
    } catch (e: any) {
      setError(e.message || 'Gagal memuat konfigurasi Guardrails.');
    } finally {
      setLoading(false);
    }
  };

  const handleToggle = (key: keyof GuardrailConfig) => {
    if (!config) return;
    setConfig({ ...config, [key]: !config[key] });
  };

  const handleAddKeyword = (e: React.FormEvent) => {
    e.preventDefault();
    if (!config || !newKeyword.trim()) return;
    const kw = newKeyword.trim().toLowerCase();
    if (!config.banned_keywords.includes(kw)) {
      setConfig({
        ...config,
        banned_keywords: [...config.banned_keywords, kw],
      });
    }
    setNewKeyword('');
  };

  const handleRemoveKeyword = (kwToRemove: string) => {
    if (!config) return;
    setConfig({
      ...config,
      banned_keywords: config.banned_keywords.filter((k) => k !== kwToRemove),
    });
  };

  const handleSaveConfig = async () => {
    if (!config) return;
    setSaving(true);
    setFeedback(null);
    setError(null);
    try {
      const updated = await GuardrailsService.updateConfig(config);
      setConfig(updated);
      setFeedback('✅ Konfigurasi Guardrails AI berhasil diperbarui!');
      setTimeout(() => setFeedback(null), 4000);
    } catch (e: any) {
      setError(e.message || 'Gagal menyimpan konfigurasi.');
    } finally {
      setSaving(false);
    }
  };

  const handleRunSimulator = async () => {
    if (!testText.trim()) return;
    setTesting(true);
    try {
      const res = await GuardrailsService.testGuardrail({ text: testText, target_type: 'input' });
      setTestResult(res);
      // Reload violations if any violation was recorded
      if (!res.passed) {
        const viols = await GuardrailsService.getViolations();
        setViolations(viols);
      }
    } catch (e: any) {
      window.alert(e.message || 'Pengujian simulator gagal.');
    } finally {
      setTesting(false);
    }
  };

  const handleClearViolation = async (id: string) => {
    try {
      await GuardrailsService.clearViolation(id);
      setViolations((prev) => prev.filter((v) => v.id !== id));
    } catch (e: any) {
      window.alert(e.message || 'Gagal menghapus log insiden.');
    }
  };

  if (loading) {
    return (
      <div className="p-8 text-center text-emerald-700 dark:text-emerald-400">
        <div className="text-3xl animate-spin mb-2">🛡️</div>
        <p className="text-xs font-semibold">Memuat Modul AI Safety & Guardrails...</p>
      </div>
    );
  }

  if (!config) return null;

  return (
    <div className="space-y-8">
      {/* Header Banner */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-emerald-900 via-teal-900 to-slate-900 text-white shadow-lg border border-emerald-700/40 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5 mb-1">
            <span className="p-2 rounded-xl bg-emerald-500/20 text-xl border border-emerald-400/30">
              🛡️
            </span>
            <h2 className="text-lg font-bold">Modul AI Safety & Clinical Guardrails</h2>
          </div>
          <p className="text-xs text-emerald-200/80 max-w-2xl leading-relaxed">
            Perlindungan berlapis untuk mendeteksi PII, memfilter kata terlarang, mencegah manipulasi prompt, dan memastikan kepatuhan standar keamanan medis klinis.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 cursor-pointer bg-white/10 px-3 py-2 rounded-xl border border-white/20 hover:bg-white/15 transition-colors">
            <input
              type="checkbox"
              checked={config.enabled}
              onChange={() => handleToggle('enabled')}
              className="w-4 h-4 text-emerald-500 rounded focus:ring-emerald-400 accent-emerald-500"
            />
            <span className="text-xs font-semibold">
              {config.enabled ? '🟢 Guardrails Aktif' : '🔴 Nonaktif'}
            </span>
          </label>

          <button
            type="button"
            onClick={handleSaveConfig}
            disabled={saving}
            className="px-4 py-2 bg-emerald-500 hover:bg-emerald-400 disabled:opacity-50 text-slate-950 font-bold rounded-xl text-xs transition-all shadow-md active:scale-95"
          >
            {saving ? 'Menyimpan…' : 'Simpan Pengaturan'}
          </button>
        </div>
      </div>

      {feedback && (
        <div className="p-3 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-300 dark:border-emerald-700 text-xs text-emerald-900 dark:text-emerald-300 font-medium">
          {feedback}
        </div>
      )}

      {error && (
        <div className="p-3 rounded-xl bg-red-50 dark:bg-red-950/60 border border-red-300 dark:border-red-700 text-xs text-red-900 dark:text-red-300 font-medium">
          {error}
        </div>
      )}

      {/* Main Settings Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Policy Toggles */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-emerald-200 dark:border-slate-800 shadow-sm space-y-4">
            <h3 className="text-sm font-bold text-emerald-950 dark:text-white uppercase tracking-wider flex items-center gap-2">
              <span>⚙️</span> Kebijakan & Filter Keamanan
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
              {/* PII Redaction */}
              <div
                onClick={() => handleToggle('pii_redaction_enabled')}
                className="p-3.5 rounded-xl border border-emerald-200 dark:border-slate-800 bg-emerald-50/40 dark:bg-slate-800/40 hover:bg-emerald-50 dark:hover:bg-slate-800 cursor-pointer transition-colors flex items-start gap-3"
              >
                <input
                  type="checkbox"
                  checked={config.pii_redaction_enabled}
                  onChange={() => {}}
                  className="mt-0.5 w-4 h-4 text-emerald-600 rounded accent-emerald-500"
                />
                <div>
                  <div className="text-xs font-bold text-emerald-950 dark:text-white">Redaksi Data PII</div>
                  <div className="text-[11px] text-emerald-700 dark:text-slate-400">
                    Sensor otomatis NIK 16 digit, nomor telepon, kartu kredit, dan email.
                  </div>
                </div>
              </div>

              {/* Strictly Medical */}
              <div
                onClick={() => handleToggle('strictly_medical_scope')}
                className="p-3.5 rounded-xl border border-emerald-200 dark:border-slate-800 bg-emerald-50/40 dark:bg-slate-800/40 hover:bg-emerald-50 dark:hover:bg-slate-800 cursor-pointer transition-colors flex items-start gap-3"
              >
                <input
                  type="checkbox"
                  checked={config.strictly_medical_scope}
                  onChange={() => {}}
                  className="mt-0.5 w-4 h-4 text-emerald-600 rounded accent-emerald-500"
                />
                <div>
                  <div className="text-xs font-bold text-emerald-950 dark:text-white">Batasan Ruang Lingkup Medis</div>
                  <div className="text-[11px] text-emerald-700 dark:text-slate-400">
                    Tolak pertanyaan di luar konsultasi medis atau rekam medis SIMRS.
                  </div>
                </div>
              </div>

              {/* Hallucination Shield */}
              <div
                onClick={() => handleToggle('hallucination_prevention')}
                className="p-3.5 rounded-xl border border-emerald-200 dark:border-slate-800 bg-emerald-50/40 dark:bg-slate-800/40 hover:bg-emerald-50 dark:hover:bg-slate-800 cursor-pointer transition-colors flex items-start gap-3"
              >
                <input
                  type="checkbox"
                  checked={config.hallucination_prevention}
                  onChange={() => {}}
                  className="mt-0.5 w-4 h-4 text-emerald-600 rounded accent-emerald-500"
                />
                <div>
                  <div className="text-xs font-bold text-emerald-950 dark:text-white">Pencegah Halusinasi Klinis</div>
                  <div className="text-[11px] text-emerald-700 dark:text-slate-400">
                    Wajibkan rujukan data berbasis RAG vektor & pedoman klinis terverifikasi.
                  </div>
                </div>
              </div>

              {/* Toxic Filter */}
              <div
                onClick={() => handleToggle('toxic_content_filter')}
                className="p-3.5 rounded-xl border border-emerald-200 dark:border-slate-800 bg-emerald-50/40 dark:bg-slate-800/40 hover:bg-emerald-50 dark:hover:bg-slate-800 cursor-pointer transition-colors flex items-start gap-3"
              >
                <input
                  type="checkbox"
                  checked={config.toxic_content_filter}
                  onChange={() => {}}
                  className="mt-0.5 w-4 h-4 text-emerald-600 rounded accent-emerald-500"
                />
                <div>
                  <div className="text-xs font-bold text-emerald-950 dark:text-white">Prompt Injection Shield</div>
                  <div className="text-[11px] text-emerald-700 dark:text-slate-400">
                    Tangkal upaya jailbreak, manipulasi prompt sistem, atau instruksi ilegal.
                  </div>
                </div>
              </div>

              {/* Auto Disclaimer */}
              <div
                onClick={() => handleToggle('auto_disclaimer_enforced')}
                className="p-3.5 rounded-xl border border-emerald-200 dark:border-slate-800 bg-emerald-50/40 dark:bg-slate-800/40 hover:bg-emerald-50 dark:hover:bg-slate-800 cursor-pointer transition-colors flex items-start gap-3 sm:col-span-2"
              >
                <input
                  type="checkbox"
                  checked={config.auto_disclaimer_enforced}
                  onChange={() => {}}
                  className="mt-0.5 w-4 h-4 text-emerald-600 rounded accent-emerald-500"
                />
                <div>
                  <div className="text-xs font-bold text-emerald-950 dark:text-white">Penegakan Disclaimer Medis Otomatis</div>
                  <div className="text-[11px] text-emerald-700 dark:text-slate-400">
                    Menyisipkan disclaimer standar pada setiap respons evaluasi klinis yang dihasilkan AI.
                  </div>
                </div>
              </div>
            </div>

            {/* Threshold Controls */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-3 border-t border-emerald-100 dark:border-slate-800">
              <div>
                <label className="block text-xs font-semibold text-emerald-900 dark:text-slate-200 mb-1">
                  Tingkat Ketat Kebijakan (*Policy Level*)
                </label>
                <select
                  value={config.safety_level}
                  onChange={(e) => setConfig({ ...config, safety_level: e.target.value })}
                  className="w-full p-2.5 rounded-xl bg-emerald-50 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 text-xs text-emerald-950 dark:text-white focus:outline-none focus:border-emerald-500"
                >
                  <option value="Strict">Strict (Tolak Risiko Sedang & Tinggi)</option>
                  <option value="Moderate">Moderate (Beri Peringatan pada Risiko Sedang)</option>
                  <option value="Permissive">Permissive (Hanya Tolak Pelanggaran Kritis)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-emerald-900 dark:text-slate-200 mb-1">
                  Batas Maksimal Karakter Query: <span className="text-emerald-600 font-mono">{config.max_query_length}</span>
                </label>
                <input
                  type="range"
                  min="300"
                  max="5000"
                  step="100"
                  value={config.max_query_length}
                  onChange={(e) => setConfig({ ...config, max_query_length: parseInt(e.target.value, 10) })}
                  className="w-full accent-emerald-600 mt-2"
                />
              </div>
            </div>
          </div>

          {/* Banned Keywords Manager */}
          <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-emerald-200 dark:border-slate-800 shadow-sm space-y-4">
            <h3 className="text-sm font-bold text-emerald-950 dark:text-white uppercase tracking-wider flex items-center gap-2">
              <span>🚫</span> Daftar Kata Kunci Terlarang (*Banned Keywords*)
            </h3>

            <form onSubmit={handleAddKeyword} className="flex gap-2">
              <input
                type="text"
                value={newKeyword}
                onChange={(e) => setNewKeyword(e.target.value)}
                placeholder="Tambahkan kata kunci terlarang (misal: 'surat sakit palsu')..."
                className="flex-1 px-3.5 py-2 text-xs bg-emerald-50 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 rounded-xl text-emerald-950 dark:text-white focus:outline-none focus:border-emerald-500"
              />
              <button
                type="submit"
                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-semibold transition-colors"
              >
                + Tambah
              </button>
            </form>

            <div className="flex flex-wrap gap-2 pt-1">
              {config.banned_keywords.map((kw, i) => (
                <span
                  key={i}
                  className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-red-50 dark:bg-red-950/60 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300"
                >
                  <span>{kw}</span>
                  <button
                    type="button"
                    onClick={() => handleRemoveKeyword(kw)}
                    title="Hapus kata kunci"
                    className="text-red-500 hover:text-red-700 dark:hover:text-red-200 font-bold ml-1"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Live Simulator Tester */}
        <div className="space-y-6">
          <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-emerald-200 dark:border-slate-800 shadow-sm space-y-4">
            <h3 className="text-sm font-bold text-emerald-950 dark:text-white uppercase tracking-wider flex items-center gap-2">
              <span>🧪</span> Simulator Evaluasi Guardrail
            </h3>
            <p className="text-[11px] text-emerald-700 dark:text-slate-400">
              Uji coba kalimat pertanyaan atau transkrip terhadap aturan guardrails aktif secara langsung.
            </p>

            <textarea
              rows={4}
              value={testText}
              onChange={(e) => setTestText(e.target.value)}
              placeholder="Masukkan teks pengujian..."
              className="w-full p-3 text-xs bg-emerald-50 dark:bg-slate-800 border border-emerald-200 dark:border-slate-700 rounded-xl text-emerald-950 dark:text-white focus:outline-none focus:border-emerald-500 leading-relaxed font-mono"
            />

            <button
              type="button"
              onClick={handleRunSimulator}
              disabled={testing}
              className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-bold rounded-xl text-xs transition-colors shadow-sm"
            >
              {testing ? 'Mengevaluasi…' : 'Jalankan Uji Guardrail'}
            </button>

            {/* Test Result Card */}
            {testResult && (
              <div
                className={`p-4 rounded-xl border space-y-2.5 text-xs animate-in fade-in duration-200 ${
                  testResult.passed
                    ? 'bg-emerald-50/80 dark:bg-emerald-950/40 border-emerald-300 dark:border-emerald-700'
                    : 'bg-red-50/80 dark:bg-red-950/40 border-red-300 dark:border-red-700'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-emerald-950 dark:text-white">Hasil Evaluasi:</span>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase ${
                      testResult.passed
                        ? 'bg-emerald-200 text-emerald-900 dark:bg-emerald-900 dark:text-emerald-200'
                        : 'bg-red-200 text-red-900 dark:bg-red-900 dark:text-red-200'
                    }`}
                  >
                    {testResult.verdict}
                  </span>
                </div>

                <div className="flex items-center justify-between text-[11px]">
                  <span>Tingkat Risiko: <strong>{testResult.risk_level}</strong></span>
                  <span>Skor Risiko: <strong className="font-mono">{testResult.risk_score}</strong> / 1.0</span>
                </div>

                {testResult.violations.length > 0 && (
                  <div className="space-y-1">
                    <span className="font-semibold text-red-800 dark:text-red-300">Pelanggaran Terdeteksi:</span>
                    <ul className="list-disc pl-4 text-[11px] text-red-700 dark:text-red-400 space-y-0.5">
                      {testResult.violations.map((v, idx) => (
                        <li key={idx}>{v}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {testResult.redacted_text && testResult.redacted_text !== testText && (
                  <div className="space-y-1 pt-1 border-t border-emerald-200 dark:border-slate-800">
                    <span className="font-semibold text-emerald-900 dark:text-slate-200">Hasil Teks Disensor:</span>
                    <p className="p-2 rounded bg-white dark:bg-slate-900 font-mono text-[10px] text-slate-800 dark:text-slate-200">
                      {testResult.redacted_text}
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Incident & Violation Logs */}
      <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-emerald-200 dark:border-slate-800 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-emerald-950 dark:text-white uppercase tracking-wider flex items-center gap-2">
            <span>📋</span> Log Insiden & Pelanggaran Guardrails ({violations.length})
          </h3>
          <button
            type="button"
            onClick={loadData}
            className="text-xs font-semibold text-emerald-700 dark:text-emerald-400 hover:underline"
          >
            🔄 Segarkan Log
          </button>
        </div>

        {violations.length === 0 ? (
          <div className="p-8 text-center text-xs text-emerald-600 dark:text-slate-400 bg-emerald-50/30 dark:bg-slate-800/30 rounded-xl">
            Tidak ada insiden pelanggaran guardrail yang tercatat. Sistem aman.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-emerald-200 dark:border-slate-800 text-[11px] font-bold text-emerald-800 dark:text-slate-400 uppercase tracking-wider">
                  <th className="pb-3 pr-4">Waktu</th>
                  <th className="pb-3 pr-4">Pengguna</th>
                  <th className="pb-3 pr-4">Kutipan Query</th>
                  <th className="pb-3 pr-4">Aturan Dilanggar</th>
                  <th className="pb-3 pr-4">Tindakan</th>
                  <th className="pb-3 pr-4">Risiko</th>
                  <th className="pb-3 text-right">Aksi</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-emerald-100 dark:divide-slate-800/60">
                {violations.map((viol) => (
                  <tr key={viol.id} className="hover:bg-emerald-50/40 dark:hover:bg-slate-800/40 transition-colors">
                    <td className="py-3 pr-4 font-mono text-[10px] text-emerald-700 dark:text-slate-400 whitespace-nowrap">
                      {new Date(viol.timestamp).toLocaleString('id-ID', {
                        day: 'numeric',
                        month: 'short',
                        hour: '2-digit',
                        minute: '2-digit',
                        second: '2-digit',
                      })}
                    </td>
                    <td className="py-3 pr-4 font-semibold text-emerald-950 dark:text-white whitespace-nowrap">
                      {viol.doctor_name}
                    </td>
                    <td className="py-3 pr-4 text-emerald-800 dark:text-slate-300 max-w-xs truncate" title={viol.query}>
                      "{viol.query}"
                    </td>
                    <td className="py-3 pr-4 text-red-700 dark:text-red-400 font-medium">
                      {viol.violated_rule}
                    </td>
                    <td className="py-3 pr-4 font-mono text-[10px] text-emerald-800 dark:text-slate-300">
                      {viol.action_taken}
                    </td>
                    <td className="py-3 pr-4">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                          viol.risk_level === 'High' || viol.risk_level === 'Critical'
                            ? 'bg-red-100 dark:bg-red-950 text-red-800 dark:text-red-300 border border-red-200 dark:border-red-800'
                            : 'bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300 border border-amber-200 dark:border-amber-800'
                        }`}
                      >
                        {viol.risk_level}
                      </span>
                    </td>
                    <td className="py-3 text-right">
                      <button
                        type="button"
                        onClick={() => handleClearViolation(viol.id)}
                        className="text-[11px] text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-200 font-semibold underline"
                      >
                        Hapus
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
