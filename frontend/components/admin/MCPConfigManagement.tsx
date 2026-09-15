'use client';

import { useState } from 'react';
import {
  type MCPConfig,
  type MCPTool,
  type UpdateMCPConfigInput,
  type CreateCustomMCPToolInput,
  type UpdateMCPToolInput,
  type MCPTestConnectionResponse,
  type MCPTestRunToolResponse
} from '@/services/admin.service';
import MCPToolModal from './MCPToolModal';

interface MCPConfigManagementProps {
  config: MCPConfig | null;
  tools: MCPTool[];
  onUpdateConfig: (input: UpdateMCPConfigInput) => Promise<any>;
  onTestConnection: () => Promise<MCPTestConnectionResponse>;
  onCreateTool: (input: CreateCustomMCPToolInput) => Promise<any>;
  onUpdateTool: (toolName: string, input: UpdateMCPToolInput) => Promise<any>;
  onToggleToolStatus: (toolName: string) => Promise<any>;
  onDeleteTool: (toolName: string) => Promise<any>;
  onTestRunTool: (input: { tool_name: string; arguments?: Record<string, any> }) => Promise<MCPTestRunToolResponse>;
  savingConfig: boolean;
  savingTool: boolean;
  testingConnection: boolean;
  testingTool: boolean;
}

type TabType = 'server' | 'tools' | 'playground';

export default function MCPConfigManagement({
  config,
  tools,
  onUpdateConfig,
  onTestConnection,
  onCreateTool,
  onUpdateTool,
  onToggleToolStatus,
  onDeleteTool,
  onTestRunTool,
  savingConfig,
  savingTool,
  testingConnection,
  testingTool,
}: MCPConfigManagementProps) {
  const [activeTab, setActiveTab] = useState<TabType>('tools');
  const [toolModalOpen, setToolModalOpen] = useState(false);
  const [selectedToolToEdit, setSelectedToolToEdit] = useState<MCPTool | null>(null);

  // Server config form state
  const [serverName, setServerName] = useState(config?.server_name || 'simrs-hospital-emr-bridge');
  const [mode, setMode] = useState(config?.mode || 'mock');
  const [endpointUrl, setEndpointUrl] = useState(config?.endpoint_url || 'https://simrs.hospital.id/api/v1/mcp');
  const [authType, setAuthType] = useState(config?.auth_type || 'bearer');
  const [authToken, setAuthToken] = useState(config?.auth_token || '');
  const [timeoutSeconds, setTimeoutSeconds] = useState(config?.timeout_seconds || 10);
  const [retryAttempts, setRetryAttempts] = useState(config?.retry_attempts || 3);
  const [enableAuditLogging, setEnableAuditLogging] = useState(config?.enable_audit_logging ?? true);
  const [autoSyncEnabled, setAutoSyncEnabled] = useState(config?.auto_sync_enabled ?? true);

  // Status & notifications
  const [configSuccessMsg, setConfigSuccessMsg] = useState('');
  const [testConnResult, setTestConnResult] = useState<MCPTestConnectionResponse | null>(null);
  const [errorMsg, setErrorMsg] = useState('');

  // Tools filter state
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  // Playground state
  const [playgroundToolName, setPlaygroundToolName] = useState(tools[0]?.name || 'simrs.get_patient_profile');
  const [playgroundArgs, setPlaygroundArgs] = useState('{\n  "mrn": "P-10492"\n}');
  const [playgroundResult, setPlaygroundResult] = useState<MCPTestRunToolResponse | null>(null);
  const [playgroundError, setPlaygroundError] = useState('');

  const handleSaveConfig = async (e: React.FormEvent) => {
    e.preventDefault();
    setConfigSuccessMsg('');
    setErrorMsg('');
    try {
      await onUpdateConfig({
        server_name: serverName,
        mode: mode,
        endpoint_url: endpointUrl,
        auth_type: authType,
        auth_token: authToken,
        timeout_seconds: Number(timeoutSeconds),
        retry_attempts: Number(retryAttempts),
        enable_audit_logging: enableAuditLogging,
        auto_sync_enabled: autoSyncEnabled,
      });
      setConfigSuccessMsg('✅ Konfigurasi MCP Server berhasil disimpan.');
      setTimeout(() => setConfigSuccessMsg(''), 4000);
    } catch (err: any) {
      setErrorMsg(err.message || 'Gagal menyimpan konfigurasi server.');
    }
  };

  const handleTestConnectionClick = async () => {
    setErrorMsg('');
    try {
      const res = await onTestConnection();
      setTestConnResult(res);
    } catch (err: any) {
      setErrorMsg('Gagal melakukan uji koneksi: ' + err.message);
    }
  };

  const handleOpenCreateModal = () => {
    setSelectedToolToEdit(null);
    setToolModalOpen(true);
  };

  const handleOpenEditModal = (tool: MCPTool) => {
    setSelectedToolToEdit(tool);
    setToolModalOpen(true);
  };

  const handleDeleteToolClick = async (tool: MCPTool) => {
    if (!confirm(`Apakah Anda yakin ingin menghapus tool kustom "${tool.display_name}" (${tool.name})?`)) {
      return;
    }
    try {
      await onDeleteTool(tool.name);
    } catch (err: any) {
      alert(err.message || 'Gagal menghapus tool.');
    }
  };

  const handleRunPlayground = async () => {
    setPlaygroundError('');
    setPlaygroundResult(null);
    let parsedArgs = {};
    try {
      if (playgroundArgs.trim()) {
        parsedArgs = JSON.parse(playgroundArgs);
      }
    } catch (err: any) {
      setPlaygroundError('Format JSON argumen tidak valid: ' + err.message);
      return;
    }

    try {
      const res = await onTestRunTool({
        tool_name: playgroundToolName,
        arguments: parsedArgs,
      });
      setPlaygroundResult(res);
    } catch (err: any) {
      setPlaygroundError(err.message || 'Eksekusi tool gagal.');
    }
  };

  const loadPresetArgument = (toolName: string) => {
    setPlaygroundToolName(toolName);
    if (toolName.includes('patient_profile') || toolName.includes('patient_history') || toolName.includes('patient_anamnesis') || toolName.includes('patient_labs')) {
      setPlaygroundArgs('{\n  "mrn": "P-10492"\n}');
    } else if (toolName.includes('update_patient_record')) {
      setPlaygroundArgs('{\n  "mrn": "P-10492",\n  "doctor_notes": "Pasien stabil, kontrol rutin 3 bulan.",\n  "primary_diagnosis": "Hypertension (ICD-10 I10)",\n  "treatment_plan": "Lisinopril 20mg 1x1, evaluasi fungsi ginjal."\n}');
    } else {
      setPlaygroundArgs('{\n  "query": "Metformin 500mg"\n}');
    }
  };

  const filteredTools = tools.filter((t) => {
    const matchesSearch =
      t.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.display_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || t.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const activeCount = tools.filter((t) => t.is_enabled).length;

  return (
    <div className="space-y-6">
      {/* Modal Add/Edit Tool */}
      <MCPToolModal
        isOpen={toolModalOpen}
        onClose={() => setToolModalOpen(false)}
        onSubmitCreate={onCreateTool}
        onSubmitUpdate={onUpdateTool}
        toolToEdit={selectedToolToEdit}
        submitting={savingTool}
      />

      {/* Top Banner Card: MCP Server Status */}
      <div className="bg-gradient-to-r from-emerald-800 to-teal-900 rounded-2xl p-6 text-white shadow-lg relative overflow-hidden">
        <div className="absolute right-0 top-0 translate-x-4 -translate-y-4 w-48 h-48 bg-emerald-500/10 rounded-full blur-2xl pointer-events-none"></div>
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 relative z-10">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-white/10 backdrop-blur-md flex items-center justify-center text-3xl shadow-inner border border-white/20">
              🔌
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <h2 className="text-xl font-bold tracking-tight">Model Context Protocol (MCP) Hub</h2>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-emerald-400/20 text-emerald-300 border border-emerald-400/30">
                  v{config?.protocol_version || '2024-11-05'}
                </span>
                <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${config?.mode === 'live'
                    ? 'bg-blue-400/20 text-blue-300 border border-blue-400/30'
                    : 'bg-amber-400/20 text-amber-300 border border-amber-400/30'
                  }`}>
                  Mode: {config?.mode?.toUpperCase() || 'MOCK'}
                </span>
              </div>
              <p className="text-xs text-emerald-100/90 leading-relaxed">
                Kelola jembatan protokol JSON-RPC interoperabilitas SIMRS, registrasi tool dinamis, dan parameter schema untuk AI Medical Agent.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleTestConnectionClick}
              disabled={testingConnection}
              className="px-4 py-2 bg-white/10 hover:bg-white/20 active:scale-95 border border-white/20 text-white rounded-xl text-xs font-semibold backdrop-blur-sm transition-all flex items-center gap-2 shadow-sm"
            >
              {testingConnection ? (
                <>
                  <span className="animate-spin text-sm">🔄</span>
                  <span>Menguji Koneksi…</span>
                </>
              ) : (
                <>
                  <span>⚡</span>
                  <span>Uji Koneksi Server</span>
                </>
              )}
            </button>
            <button
              type="button"
              onClick={handleOpenCreateModal}
              className="px-4 py-2 bg-emerald-500 hover:bg-emerald-400 active:scale-95 text-emerald-950 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 shadow-md"
            >
              <span>➕</span>
              <span>Tool Kustom Baru</span>
            </button>
          </div>
        </div>

        {/* Quick Stats Strip */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-6 pt-4 border-t border-white/15 text-xs">
          <div>
            <span className="text-emerald-200/80 text-[11px] block">Status Jaringan</span>
            <span className="font-semibold text-emerald-300 flex items-center gap-1 mt-0.5">
              🟢 Terhubung ({config?.latency_ms || 12} ms)
            </span>
          </div>
          <div>
            <span className="text-emerald-200/80 text-[11px] block">Katalog Tool Aktif</span>
            <span className="font-semibold text-white mt-0.5 block">
              {activeCount} dari {tools.length} Tool Aktif
            </span>
          </div>
          <div>
            <span className="text-emerald-200/80 text-[11px] block">Server Name</span>
            <span className="font-semibold text-white font-mono text-[11px] mt-0.5 truncate block">
              {config?.server_name || 'simrs-hospital-emr-bridge'}
            </span>
          </div>
          <div>
            <span className="text-emerald-200/80 text-[11px] block">Pemeriksaan Terakhir</span>
            <span className="font-semibold text-white mt-0.5 block text-[11px]">
              {config?.last_health_check ? new Date(config.last_health_check).toLocaleTimeString('id-ID') : 'Baru saja'}
            </span>
          </div>
        </div>
      </div>

      {/* Test Connection Alert Banner */}
      {testConnResult && (
        <div className="p-4 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 rounded-2xl flex items-center justify-between gap-3 text-xs animate-fadeIn">
          <div className="flex items-center gap-2">
            <span className="text-xl">✅</span>
            <div>
              <p className="font-bold text-emerald-950 dark:text-emerald-200">{testConnResult.message}</p>
              <p className="text-emerald-700 dark:text-emerald-400 text-[11px]">
                Endpoint: <code className="font-mono">{testConnResult.endpoint_url}</code> | Mode: <strong>{testConnResult.mode}</strong> | Latensi: <strong>{testConnResult.latency_ms} ms</strong> | Tool Tersedia: <strong>{testConnResult.active_tools_count}</strong>
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={() => setTestConnResult(null)}
            className="text-emerald-600 dark:text-emerald-400 hover:text-emerald-800 text-sm font-bold"
          >
            ✕
          </button>
        </div>
      )}

      {errorMsg && (
        <div className="p-4 bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 rounded-2xl flex items-center justify-between gap-3 text-xs animate-fadeIn">
          <div className="flex items-center gap-2 text-rose-800 dark:text-rose-200">
            <span className="text-xl">⚠️</span>
            <p className="font-semibold">{errorMsg}</p>
          </div>
          <button
            type="button"
            onClick={() => setErrorMsg('')}
            className="text-rose-600 dark:text-rose-400 hover:text-rose-800 text-sm font-bold"
          >
            ✕
          </button>
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="flex border-b border-emerald-200 dark:border-slate-800 gap-2">
        <button
          type="button"
          onClick={() => setActiveTab('tools')}
          className={`pb-3 px-4 text-xs font-bold transition-all flex items-center gap-2 border-b-2 ${activeTab === 'tools'
              ? 'border-emerald-600 text-emerald-600 dark:text-emerald-400 dark:border-emerald-400'
              : 'border-transparent text-emerald-800/60 dark:text-slate-400 hover:text-emerald-950 dark:hover:text-slate-200'
            }`}
        >
          <span>🧰</span>
          <span>Katalog Tool MCP & Toggle Dinamis</span>
          <span className="px-2 py-0.5 rounded-full bg-emerald-100 dark:bg-slate-800 text-[10px] text-emerald-800 dark:text-slate-300">
            {tools.length}
          </span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('server')}
          className={`pb-3 px-4 text-xs font-bold transition-all flex items-center gap-2 border-b-2 ${activeTab === 'server'
              ? 'border-emerald-600 text-emerald-600 dark:text-emerald-400 dark:border-emerald-400'
              : 'border-transparent text-emerald-800/60 dark:text-slate-400 hover:text-emerald-950 dark:hover:text-slate-200'
            }`}
        >
          <span>⚙️</span>
          <span>Pengaturan Server & Koneksi</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('playground')}
          className={`pb-3 px-4 text-xs font-bold transition-all flex items-center gap-2 border-b-2 ${activeTab === 'playground'
              ? 'border-emerald-600 text-emerald-600 dark:text-emerald-400 dark:border-emerald-400'
              : 'border-transparent text-emerald-800/60 dark:text-slate-400 hover:text-emerald-950 dark:hover:text-slate-200'
            }`}
        >
          <span>🧪</span>
          <span>MCP Interactive Playground</span>
          <span className="px-2 py-0.5 rounded-full bg-teal-100 dark:bg-teal-950/60 text-[10px] text-teal-800 dark:text-teal-300 border border-teal-300 dark:border-teal-700">
            Uji Coba
          </span>
        </button>
      </div>

      {/* ── TAB 1: TOOLS DIRECTORY ────────────────────────────────────────── */}
      {activeTab === 'tools' && (
        <div className="space-y-4">
          {/* Search & Category Filter Bar */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-white dark:bg-slate-900 p-4 rounded-2xl border border-emerald-200 dark:border-slate-800 shadow-sm">
            <div className="flex items-center gap-2 w-full sm:w-auto flex-1">
              <span className="text-emerald-600 dark:text-slate-400 text-sm">🔍</span>
              <input
                type="text"
                placeholder="Cari tool MCP berdasarkan nama, namespace, atau deskripsi..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-3 py-1.5 text-xs bg-transparent border-0 focus:outline-none text-emerald-950 dark:text-white placeholder:text-slate-400"
              />
            </div>

            <div className="flex items-center gap-2 w-full sm:w-auto">
              <span className="text-xs text-slate-500 shrink-0">Kategori:</span>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="px-3 py-1.5 border border-emerald-200 dark:border-slate-700 rounded-xl bg-white dark:bg-slate-800 text-emerald-950 dark:text-slate-100 text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"
              >
                <option value="all">Semua Kategori</option>
                <option value="patient_data">Data Pasien & Demografi</option>
                <option value="medical_history">Riwayat Medis</option>
                <option value="anamnesis">Anamnesis</option>
                <option value="laboratory">Laboratorium & Diagnostik</option>
                <option value="pharmacy">Farmasi</option>
                <option value="radiology">Radiologi</option>
                <option value="transaction">Transaksi & Commit</option>
                <option value="custom">Kustom</option>
              </select>
            </div>
          </div>

          {/* Tools Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredTools.map((tool) => (
              <div
                key={tool.name}
                className={`bg-white dark:bg-slate-900 border rounded-2xl p-5 shadow-sm transition-all relative overflow-hidden flex flex-col justify-between ${tool.is_enabled
                    ? 'border-emerald-200 dark:border-slate-800 hover:border-emerald-400'
                    : 'border-slate-200 dark:border-slate-800/60 opacity-70 bg-slate-50/50 dark:bg-slate-900/40'
                  }`}
              >
                <div>
                  {/* Top line: Name & Status Switch */}
                  <div className="flex items-start justify-between gap-3 mb-2">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-base">
                          {tool.category === 'patient_data' && '👤'}
                          {tool.category === 'medical_history' && '📜'}
                          {tool.category === 'anamnesis' && '🩺'}
                          {tool.category === 'laboratory' && '🧪'}
                          {tool.category === 'pharmacy' && '💊'}
                          {tool.category === 'radiology' && '🩻'}
                          {tool.category === 'transaction' && '💾'}
                          {tool.category === 'custom' && '🧩'}
                        </span>
                        <h4 className="font-bold text-emerald-950 dark:text-white text-sm truncate">
                          {tool.display_name}
                        </h4>
                        {tool.is_builtin ? (
                          <span className="px-2 py-0.5 rounded-full text-[9px] font-bold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700">
                            Bawaan SIMRS
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 rounded-full text-[9px] font-bold bg-purple-100 dark:bg-purple-950/60 text-purple-700 dark:text-purple-300 border border-purple-300 dark:border-purple-800">
                            Custom Tool
                          </span>
                        )}
                      </div>
                      <p className="font-mono text-[11px] text-emerald-700 dark:text-emerald-400 mt-0.5">
                        {tool.name}
                      </p>
                    </div>

                    {/* Toggle Switch */}
                    <div className="flex items-center gap-2 shrink-0">
                      <label className="relative inline-flex items-center cursor-pointer" title="Aktifkan / Nonaktifkan Tool">
                        <input
                          type="checkbox"
                          checked={tool.is_enabled}
                          onChange={() => onToggleToolStatus(tool.name)}
                          className="sr-only peer"
                        />
                        <div className="w-10 h-5 bg-slate-300 peer-focus:outline-none rounded-full peer dark:bg-slate-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-emerald-600"></div>
                      </label>
                    </div>
                  </div>

                  {/* Description */}
                  <p className="text-xs text-emerald-900/80 dark:text-slate-300 leading-relaxed mb-3">
                    {tool.description}
                  </p>

                  {/* Schema Summary */}
                  <div className="p-2.5 bg-slate-50 dark:bg-slate-950 rounded-xl border border-slate-100 dark:border-slate-800 text-[11px] font-mono text-slate-700 dark:text-slate-300 mb-3">
                    <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">Required Parameters:</span>
                    {tool.input_schema?.required && tool.input_schema.required.length > 0 ? (
                      <div className="flex flex-wrap gap-1">
                        {tool.input_schema.required.map((req: string) => (
                          <span key={req} className="px-1.5 py-0.5 rounded bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300 font-semibold">
                            {req}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <span className="text-slate-400 italic">Tidak ada parameter wajib</span>
                    )}
                  </div>
                </div>

                {/* Footer Strip: Stats & Actions */}
                <div className="pt-3 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between text-[11px]">
                  <span className="text-slate-500 dark:text-slate-400">
                    📊 Dieksekusi: <strong>{tool.execution_count || 0}x</strong>
                  </span>

                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => {
                        loadPresetArgument(tool.name);
                        setActiveTab('playground');
                      }}
                      className="px-2.5 py-1 text-teal-700 dark:text-teal-300 hover:bg-teal-50 dark:hover:bg-teal-950/50 rounded-lg font-semibold transition-colors flex items-center gap-1"
                    >
                      <span>🧪</span>
                      <span>Uji</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => handleOpenEditModal(tool)}
                      className="px-2.5 py-1 text-emerald-700 dark:text-emerald-300 hover:bg-emerald-50 dark:hover:bg-emerald-950/50 rounded-lg font-semibold transition-colors flex items-center gap-1"
                    >
                      <span>✏️</span>
                      <span>Edit</span>
                    </button>
                    {!tool.is_builtin && (
                      <button
                        type="button"
                        onClick={() => handleDeleteToolClick(tool)}
                        className="px-2.5 py-1 text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/50 rounded-lg font-semibold transition-colors flex items-center gap-1"
                      >
                        <span>🗑️</span>
                        <span>Hapus</span>
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {filteredTools.length === 0 && (
            <div className="p-8 text-center bg-white dark:bg-slate-900 border border-emerald-200 dark:border-slate-800 rounded-2xl">
              <p className="text-3xl mb-2">🔍</p>
              <h4 className="font-bold text-emerald-950 dark:text-white text-sm">Tidak Ada Tool MCP Ditemukan</h4>
              <p className="text-xs text-slate-500 mt-1">Coba sesuaikan kata kunci pencarian atau filter kategori.</p>
            </div>
          )}
        </div>
      )}

      {/* ── TAB 2: SERVER SETTINGS ────────────────────────────────────────── */}
      {activeTab === 'server' && (
        <form onSubmit={handleSaveConfig} className="bg-white dark:bg-slate-900 border border-emerald-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-5 text-xs">
          {configSuccessMsg && (
            <div className="p-3.5 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 rounded-xl text-emerald-800 dark:text-emerald-300 font-semibold flex items-center gap-2">
              {configSuccessMsg}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {/* Server Name */}
            <div>
              <label className="block font-semibold text-emerald-900 dark:text-slate-200 mb-1">
                Nama Server MCP Identifier
              </label>
              <input
                type="text"
                value={serverName}
                onChange={(e) => setServerName(e.target.value)}
                className="w-full px-3 py-2 border border-emerald-200 dark:border-slate-700 rounded-xl bg-white dark:bg-slate-800 text-emerald-950 dark:text-slate-100 font-mono text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"
              />
            </div>

            {/* Mode Selector */}
            <div>
              <label className="block font-semibold text-emerald-900 dark:text-slate-200 mb-1">
                Mode Integrasi SIMRS / Satu Sehat
              </label>
              <select
                value={mode}
                onChange={(e) => setMode(e.target.value)}
                className="w-full px-3 py-2 border border-emerald-200 dark:border-slate-700 rounded-xl bg-white dark:bg-slate-800 text-emerald-950 dark:text-slate-100 text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"
              >
                <option value="mock">In-Memory Mock SIMRS Database (Standalone / Pengujian Cepat)</option>
                <option value="live">Live External SIMRS / FHIR Bridge (HTTP REST & JSON-RPC)</option>
                <option value="hybrid">Hybrid Fallback Mode (Prioritaskan Live, Fallback ke Mock)</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {/* Endpoint URL */}
            <div className="md:col-span-2">
              <label className="block font-semibold text-emerald-900 dark:text-slate-200 mb-1">
                Live MCP Bridge Endpoint URL
              </label>
              <input
                type="text"
                placeholder="https://simrs.hospital.id/api/v1/mcp"
                value={endpointUrl}
                onChange={(e) => setEndpointUrl(e.target.value)}
                className="w-full px-3 py-2 border border-emerald-200 dark:border-slate-700 rounded-xl bg-white dark:bg-slate-800 text-emerald-950 dark:text-slate-100 font-mono text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"
              />
            </div>

            {/* Auth Type */}
            <div>
              <label className="block font-semibold text-emerald-900 dark:text-slate-200 mb-1">
                Tipe Otentikasi
              </label>
              <select
                value={authType}
                onChange={(e) => setAuthType(e.target.value)}
                className="w-full px-3 py-2 border border-emerald-200 dark:border-slate-700 rounded-xl bg-white dark:bg-slate-800 text-emerald-950 dark:text-slate-100 text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"
              >
                <option value="bearer">Bearer Token (JWT)</option>
                <option value="api_key">API Key Header (X-API-Key)</option>
                <option value="none">Tanpa Otentikasi (Internal Network)</option>
              </select>
            </div>
          </div>

          {authType !== 'none' && (
            <div>
              <label className="block font-semibold text-emerald-900 dark:text-slate-200 mb-1">
                Token / Secret Key Otentikasi
              </label>
              <input
                type="password"
                placeholder="Masukkan Authorization Token atau API Key..."
                value={authToken}
                onChange={(e) => setAuthToken(e.target.value)}
                className="w-full px-3 py-2 border border-emerald-200 dark:border-slate-700 rounded-xl bg-white dark:bg-slate-800 text-emerald-950 dark:text-slate-100 font-mono text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"
              />
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5 pt-2">
            <div>
              <label className="block font-semibold text-emerald-900 dark:text-slate-200 mb-1">
                Connection Timeout (detik)
              </label>
              <input
                type="number"
                min={1}
                max={60}
                value={timeoutSeconds}
                onChange={(e) => setTimeoutSeconds(Number(e.target.value))}
                className="w-full px-3 py-2 border border-emerald-200 dark:border-slate-700 rounded-xl bg-white dark:bg-slate-800 text-emerald-950 dark:text-slate-100 text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block font-semibold text-emerald-900 dark:text-slate-200 mb-1">
                Maksimal Retry Saat Kegagalan
              </label>
              <input
                type="number"
                min={0}
                max={10}
                value={retryAttempts}
                onChange={(e) => setRetryAttempts(Number(e.target.value))}
                className="w-full px-3 py-2 border border-emerald-200 dark:border-slate-700 rounded-xl bg-white dark:bg-slate-800 text-emerald-950 dark:text-slate-100 text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-3 border-t border-slate-100 dark:border-slate-800">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={enableAuditLogging}
                onChange={(e) => setEnableAuditLogging(e.target.checked)}
                className="rounded text-emerald-600 focus:ring-emerald-500"
              />
              <span className="text-emerald-950 dark:text-slate-200 font-medium">
                Aktifkan Audit Trail Logging untuk setiap pemanggilan Tool MCP
              </span>
            </label>

            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={autoSyncEnabled}
                onChange={(e) => setAutoSyncEnabled(e.target.checked)}
                className="rounded text-emerald-600 focus:ring-emerald-500"
              />
              <span className="text-emerald-950 dark:text-slate-200 font-medium">
                Sinkronisasi otomatis hasil CPPT ke SIMRS saat disetujui dokter
              </span>
            </label>
          </div>

          <div className="pt-4 border-t border-slate-100 dark:border-slate-800 flex justify-end">
            <button
              type="submit"
              disabled={savingConfig}
              className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-bold shadow-md transition-all active:scale-95 disabled:opacity-50 flex items-center gap-2"
            >
              {savingConfig ? 'Menyimpan…' : '💾 Simpan Konfigurasi Server'}
            </button>
          </div>
        </form>
      )}

      {/* ── TAB 3: PLAYGROUND ─────────────────────────────────────────────── */}
      {activeTab === 'playground' && (
        <div className="bg-white dark:bg-slate-900 border border-emerald-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-5 text-xs">
          <div>
            <h3 className="font-bold text-emerald-950 dark:text-white text-sm mb-1">
              🧪 MCP Interactive Tool Playground & Test Runner
            </h3>
            <p className="text-slate-500 dark:text-slate-400">
              Eksekusi dan uji langsung tool MCP dengan argumen kustom untuk melihat payload JSON respons secara real-time.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {/* Tool Selection */}
            <div>
              <label className="block font-semibold text-emerald-900 dark:text-slate-200 mb-1">
                Pilih Tool MCP yang Ingin Diuji
              </label>
              <select
                value={playgroundToolName}
                onChange={(e) => loadPresetArgument(e.target.value)}
                className="w-full px-3 py-2 border border-emerald-200 dark:border-slate-700 rounded-xl bg-white dark:bg-slate-800 text-emerald-950 dark:text-slate-100 font-mono text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"
              >
                {tools.map((t) => (
                  <option key={t.name} value={t.name}>
                    {t.name} ({t.display_name}) {!t.is_enabled ? '[NONAKTIF]' : ''}
                  </option>
                ))}
              </select>
            </div>

            {/* Quick Sample Presets */}
            <div className="flex flex-col justify-end">
              <span className="text-[11px] font-semibold text-slate-500 mb-1">Muat Contoh Argumen Uji:</span>
              <div className="flex gap-2 flex-wrap">
                <button
                  type="button"
                  onClick={() => setPlaygroundArgs('{\n  "mrn": "P-10492"\n}')}
                  className="px-2.5 py-1 bg-slate-100 dark:bg-slate-800 hover:bg-emerald-100 dark:hover:bg-slate-700 rounded-lg text-[11px] font-mono text-slate-700 dark:text-slate-300"
                >
                  MRN: P-10492
                </button>
                <button
                  type="button"
                  onClick={() => setPlaygroundArgs('{\n  "mrn": "P-20811"\n}')}
                  className="px-2.5 py-1 bg-slate-100 dark:bg-slate-800 hover:bg-emerald-100 dark:hover:bg-slate-700 rounded-lg text-[11px] font-mono text-slate-700 dark:text-slate-300"
                >
                  MRN: P-20811 (Jantung)
                </button>
                <button
                  type="button"
                  onClick={() => setPlaygroundArgs('{\n  "mrn": "P-30124"\n}')}
                  className="px-2.5 py-1 bg-slate-100 dark:bg-slate-800 hover:bg-emerald-100 dark:hover:bg-slate-700 rounded-lg text-[11px] font-mono text-slate-700 dark:text-slate-300"
                >
                  MRN: P-30124 (Anemia)
                </button>
              </div>
            </div>
          </div>

          {/* JSON Arguments Input */}
          <div>
            <label className="block font-semibold text-emerald-900 dark:text-slate-200 mb-1">
              Input Argumen JSON-RPC (Arguments Object)
            </label>
            <textarea
              rows={5}
              value={playgroundArgs}
              onChange={(e) => setPlaygroundArgs(e.target.value)}
              className="w-full px-3 py-2 border border-emerald-200 dark:border-slate-700 rounded-xl bg-slate-50 dark:bg-slate-950 font-mono text-xs text-emerald-950 dark:text-slate-100 focus:ring-2 focus:ring-emerald-500 focus:outline-none"
            />
          </div>

          <div className="flex justify-end">
            <button
              type="button"
              onClick={handleRunPlayground}
              disabled={testingTool}
              className="px-5 py-2.5 bg-teal-600 hover:bg-teal-500 text-white rounded-xl font-bold shadow-md transition-all active:scale-95 disabled:opacity-50 flex items-center gap-2"
            >
              {testingTool ? (
                <>
                  <span className="animate-spin">🔄</span>
                  <span>Mengeksekusi Tool…</span>
                </>
              ) : (
                <>
                  <span>⚡</span>
                  <span>Eksekusi Uji Coba (Run Tool)</span>
                </>
              )}
            </button>
          </div>

          {/* Error Message */}
          {playgroundError && (
            <div className="p-4 bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 rounded-xl text-rose-800 dark:text-rose-200 font-semibold">
              ⚠️ {playgroundError}
            </div>
          )}

          {/* Execution Result Viewer */}
          {playgroundResult && (
            <div className="space-y-2 pt-3 border-t border-slate-100 dark:border-slate-800 animate-fadeIn">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-emerald-950 dark:text-white">Hasil Eksekusi:</span>
                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${playgroundResult.status === 'success' ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300' : 'bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300'
                    }`}>
                    {playgroundResult.status}
                  </span>
                  <span className="text-[11px] text-slate-500">
                    ⏱️ Latensi: <strong>{playgroundResult.latency_ms} ms</strong> | Mode: <strong>{playgroundResult.execution_mode}</strong>
                  </span>
                </div>
              </div>

              <div className="p-4 bg-slate-900 text-slate-100 rounded-2xl font-mono text-xs overflow-x-auto max-h-96 shadow-inner border border-slate-800">
                <pre>{JSON.stringify(playgroundResult.result, null, 2)}</pre>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
