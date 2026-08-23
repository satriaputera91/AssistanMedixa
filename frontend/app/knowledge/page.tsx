'use client';
import { useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useKnowledge } from '@/hooks/useKnowledge';
import Navbar from '@/components/common/Navbar';
import MetricCard from '@/components/common/MetricCard';
import FileUploader from '@/components/knowledge/FileUploader';
import KnowledgeForm from '@/components/knowledge/KnowledgeForm';
import KnowledgeTable from '@/components/knowledge/KnowledgeTable';
import RAGSearchExplorer from '@/components/knowledge/RAGSearchExplorer';

export default function KnowledgePage() {
  const { userName, userRole, loading, logout } = useAuth('admin');
  const {
    items,
    totalItems,
    totalVectors,
    submitting,
    uploading,
    error,
    loadKnowledge,
    submitForm,
    uploadFile,
    deleteItem,
  } = useKnowledge();

  useEffect(() => {
    if (!loading) loadKnowledge();
  }, [loading, loadKnowledge]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-emerald-50 text-emerald-700">
        <div className="text-center">
          <div className="text-3xl mb-3 animate-pulse">📚</div>
          <p className="text-sm">Memuat basis pengetahuan…</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-emerald-50 dark:bg-slate-950 text-emerald-950 dark:text-slate-100 overflow-hidden transition-colors">
      <Navbar userName={userName} userRole={userRole} onLogout={logout} activePage="knowledge" />

      <main className="flex-1 overflow-y-auto p-6 md:p-8 space-y-8">
        {error && (
          <div className="flex items-center justify-between gap-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            <span>{error}</span>
            <button onClick={loadKnowledge} className="shrink-0 font-semibold underline">Coba lagi</button>
          </div>
        )}
        {/* Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <MetricCard label="Dokumen Terindeks" value={totalItems} color="emerald" icon="📄" />
          <MetricCard label="Total Vektor Qdrant" value={totalVectors} color="emerald" icon="🔗" />
        </div>

        {/* Semantic Search Explorer */}
        <RAGSearchExplorer />

        {/* Upload & Form */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <FileUploader onUpload={uploadFile} uploading={uploading} />
          <KnowledgeForm onSubmit={submitForm} submitting={submitting} />
        </div>

        {/* Knowledge Table */}
        <KnowledgeTable items={items} onDelete={deleteItem} />
      </main>
    </div>
  );
}
