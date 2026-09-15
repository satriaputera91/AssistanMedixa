'use client';

import { useState, useEffect } from 'react';
import { 
  type MCPTool, 
  type CreateCustomMCPToolInput, 
  type UpdateMCPToolInput 
} from '@/services/admin.service';

interface MCPToolModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmitCreate: (input: CreateCustomMCPToolInput) => Promise<any>;
  onSubmitUpdate: (toolName: string, input: UpdateMCPToolInput) => Promise<any>;
  toolToEdit?: MCPTool | null;
  submitting: boolean;
}

export default function MCPToolModal({
  isOpen,
  onClose,
  onSubmitCreate,
  onSubmitUpdate,
  toolToEdit,
  submitting,
}: MCPToolModalProps) {
  const [name, setName] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('patient_data');
  const [isEnabled, setIsEnabled] = useState(true);
  const [customEndpoint, setCustomEndpoint] = useState('');
  const [inputSchemaJson, setInputSchemaJson] = useState('{\n  "type": "object",\n  "properties": {\n    "mrn": { "type": "string", "description": "Nomor Rekam Medis" }\n  },\n  "required": ["mrn"]\n}');
  const [mockResponseJson, setMockResponseJson] = useState('{\n  "status": "success",\n  "message": "Data berhasil dimuat."\n}');
  const [errorMsg, setErrorMsg] = useState('');

  const isEdit = !!toolToEdit;

  useEffect(() => {
    if (toolToEdit) {
      setName(toolToEdit.name || '');
      setDisplayName(toolToEdit.display_name || '');
      setDescription(toolToEdit.description || '');
      setCategory(toolToEdit.category || 'custom');
      setIsEnabled(toolToEdit.is_enabled ?? true);
      setCustomEndpoint(toolToEdit.custom_endpoint || '');
      setInputSchemaJson(JSON.stringify(toolToEdit.input_schema || {}, null, 2));
      setMockResponseJson(JSON.stringify(toolToEdit.mock_response || {}, null, 2));
    } else {
      setName('');
      setDisplayName('');
      setDescription('');
      setCategory('patient_data');
      setIsEnabled(true);
      setCustomEndpoint('');
      setInputSchemaJson('{\n  "type": "object",\n  "properties": {\n    "mrn": { "type": "string", "description": "Nomor Rekam Medis" }\n  },\n  "required": ["mrn"]\n}');
      setMockResponseJson('{\n  "status": "success",\n  "message": "Data berhasil dimuat."\n}');
    }
    setErrorMsg('');
  }, [toolToEdit, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');

    let parsedSchema = {};
    try {
      if (inputSchemaJson.trim()) {
        parsedSchema = JSON.parse(inputSchemaJson);
      }
    } catch (err: any) {
      setErrorMsg('Format JSON pada Input Schema tidak valid: ' + err.message);
      return;
    }

    let parsedMock = undefined;
    try {
      if (mockResponseJson.trim()) {
        parsedMock = JSON.parse(mockResponseJson);
      }
    } catch (err: any) {
      setErrorMsg('Format JSON pada Mock Response tidak valid: ' + err.message);
      return;
    }

    if (isEdit) {
      try {
        await onSubmitUpdate(toolToEdit.name, {
          display_name: displayName,
          description: description,
          category: category,
          is_enabled: isEnabled,
          input_schema: parsedSchema,
          custom_endpoint: customEndpoint.trim() || undefined,
          mock_response: parsedMock,
        });
        onClose();
      } catch (err: any) {
        setErrorMsg(err.message || 'Gagal memperbarui Tool MCP.');
      }
    } else {
      if (!name.trim()) {
        setErrorMsg('Identifier nama tool tidak boleh kosong.');
        return;
      }
      try {
        await onSubmitCreate({
          name: name.trim(),
          display_name: displayName || name.trim(),
          description: description || `Custom MCP Tool: ${name.trim()}`,
          category: category,
          is_enabled: isEnabled,
          input_schema: parsedSchema,
          custom_endpoint: customEndpoint.trim() || undefined,
          mock_response: parsedMock,
        });
        onClose();
      } catch (err: any) {
        setErrorMsg(err.message || 'Gagal mendaftarkan Tool MCP kustom.');
      }
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-fadeIn">
      <div className="bg-white dark:bg-slate-900 border border-emerald-200 dark:border-slate-800 rounded-2xl w-full max-w-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="px-6 py-4 border-b border-emerald-100 dark:border-slate-800 flex items-center justify-between bg-emerald-50/50 dark:bg-slate-800/50">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🔌</span>
            <div>
              <h3 className="font-bold text-emerald-950 dark:text-white text-base">
                {isEdit ? 'Ubah Konfigurasi Tool MCP' : 'Daftarkan Tool MCP Kustom Baru'}
              </h3>
              <p className="text-xs text-emerald-700 dark:text-slate-400">
                {isEdit 
                  ? `Mengedit definisi parameter untuk ${toolToEdit?.name}` 
                  : 'Tambahkan integrasi tool baru untuk agen klinis / SIMRS'}
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-lg text-emerald-600 dark:text-slate-400 hover:bg-emerald-100 dark:hover:bg-slate-800 transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 overflow-y-auto space-y-4 flex-1 text-xs">
          {errorMsg && (
            <div className="p-3 bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800/60 rounded-xl text-rose-700 dark:text-rose-300 font-medium">
              ⚠️ {errorMsg}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Tool Name Identifier */}
            <div>
              <label className="block font-semibold text-emerald-900 dark:text-slate-200 mb-1">
                Identifier Nama Tool <span className="text-rose-500">*</span>
              </label>
              <input
                type="text"
                disabled={isEdit}
                placeholder="contoh: hospital.check_stock"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className={`w-full px-3 py-2 border rounded-xl bg-white dark:bg-slate-800 text-emerald-950 dark:text-slate-100 font-mono text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none transition-colors ${
                  isEdit ? 'opacity-60 cursor-not-allowed border-slate-300 dark:border-slate-700' : 'border-emerald-200 dark:border-slate-700'
                }`}
              />
              <p className="text-[10px] text-emerald-600 dark:text-slate-400 mt-0.5">
                Format standar JSON-RPC MCP namespace (e.g. simrs.action / hospital.query)
              </p>
            </div>

            {/* Display Name */}
            <div>
              <label className="block font-semibold text-emerald-900 dark:text-slate-200 mb-1">
                Nama Tampilan (Display Title) <span className="text-rose-500">*</span>
              </label>
              <input
                type="text"
                placeholder="contoh: Cek Ketersediaan Stok Farmasi"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                className="w-full px-3 py-2 border border-emerald-200 dark:border-slate-700 rounded-xl bg-white dark:bg-slate-800 text-emerald-950 dark:text-slate-100 focus:ring-2 focus:ring-emerald-500 focus:outline-none transition-colors"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Category */}
            <div>
              <label className="block font-semibold text-emerald-900 dark:text-slate-200 mb-1">
                Kategori Tool
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-3 py-2 border border-emerald-200 dark:border-slate-700 rounded-xl bg-white dark:bg-slate-800 text-emerald-950 dark:text-slate-100 focus:ring-2 focus:ring-emerald-500 focus:outline-none transition-colors"
              >
                <option value="patient_data">Data Pasien & Demografi</option>
                <option value="medical_history">Riwayat Medis & Rawat</option>
                <option value="anamnesis">Anamnesis & Keluhan</option>
                <option value="laboratory">Laboratorium & Diagnostik</option>
                <option value="pharmacy">Farmasi & Stok Obat</option>
                <option value="radiology">Radiologi & PACS</option>
                <option value="transaction">Transaksi & Commit CPPT</option>
                <option value="custom">Kustom / Eksternal Lainnya</option>
              </select>
            </div>

            {/* Status Active */}
            <div>
              <label className="block font-semibold text-emerald-900 dark:text-slate-200 mb-1">
                Status Operasional
              </label>
              <div className="flex items-center gap-3 pt-2">
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={isEnabled}
                    onChange={(e) => setIsEnabled(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-slate-300 peer-focus:outline-none rounded-full peer dark:bg-slate-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-600"></div>
                </label>
                <span className="text-xs font-semibold text-emerald-900 dark:text-slate-200">
                  {isEnabled ? '🟢 Aktif (Siap Dieksekusi)' : '🔴 Nonaktif (Disembunyikan)'}
                </span>
              </div>
            </div>
          </div>

          {/* Description */}
          <div>
            <label className="block font-semibold text-emerald-900 dark:text-slate-200 mb-1">
              Deskripsi Fungsi Tool (LLM Guidance Prompt) <span className="text-rose-500">*</span>
            </label>
            <textarea
              rows={2}
              placeholder="Jelaskan kegunaan tool ini agar LLM / Medical Agent mengetahui kapan harus memanggilnya..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3 py-2 border border-emerald-200 dark:border-slate-700 rounded-xl bg-white dark:bg-slate-800 text-emerald-950 dark:text-slate-100 focus:ring-2 focus:ring-emerald-500 focus:outline-none transition-colors"
            />
          </div>

          {/* Custom Endpoint URL (optional) */}
          <div>
            <label className="block font-semibold text-emerald-900 dark:text-slate-200 mb-1">
              Custom HTTP Endpoint Bridge (Opsional)
            </label>
            <input
              type="text"
              placeholder="https://simrs.hospital.id/api/v1/external-tool-bridge"
              value={customEndpoint}
              onChange={(e) => setCustomEndpoint(e.target.value)}
              className="w-full px-3 py-2 border border-emerald-200 dark:border-slate-700 rounded-xl bg-white dark:bg-slate-800 text-emerald-950 dark:text-slate-100 font-mono text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none transition-colors"
            />
            <p className="text-[10px] text-emerald-600 dark:text-slate-400 mt-0.5">
              Kosongkan untuk menggunakan mock internal engine atau MCP server bawaan.
            </p>
          </div>

          {/* Input Schema JSON */}
          <div>
            <label className="block font-semibold text-emerald-900 dark:text-slate-200 mb-1">
              Input Schema JSON (Standard JSON Schema)
            </label>
            <textarea
              rows={4}
              value={inputSchemaJson}
              onChange={(e) => setInputSchemaJson(e.target.value)}
              className="w-full px-3 py-2 border border-emerald-200 dark:border-slate-700 rounded-xl bg-slate-50 dark:bg-slate-950 font-mono text-[11px] text-emerald-950 dark:text-slate-100 focus:ring-2 focus:ring-emerald-500 focus:outline-none transition-colors"
            />
          </div>

          {/* Mock Response JSON */}
          {!toolToEdit?.is_builtin && (
            <div>
              <label className="block font-semibold text-emerald-900 dark:text-slate-200 mb-1">
                Mock Response Output JSON (Untuk Mode Simulasi/Sandbox)
              </label>
              <textarea
                rows={3}
                value={mockResponseJson}
                onChange={(e) => setMockResponseJson(e.target.value)}
                className="w-full px-3 py-2 border border-emerald-200 dark:border-slate-700 rounded-xl bg-slate-50 dark:bg-slate-950 font-mono text-[11px] text-emerald-950 dark:text-slate-100 focus:ring-2 focus:ring-emerald-500 focus:outline-none transition-colors"
              />
            </div>
          )}

          {/* Footer Actions */}
          <div className="pt-4 border-t border-emerald-100 dark:border-slate-800 flex items-center justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-emerald-200 dark:border-slate-700 text-emerald-800 dark:text-slate-300 hover:bg-emerald-50 dark:hover:bg-slate-800 rounded-xl font-semibold transition-colors"
            >
              Batal
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-semibold shadow-sm transition-all active:scale-[0.98] disabled:opacity-50 flex items-center gap-1.5"
            >
              {submitting ? 'Menyimpan…' : isEdit ? '💾 Simpan Perubahan' : '➕ Daftarkan Tool'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
