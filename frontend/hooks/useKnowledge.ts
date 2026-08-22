'use client';
import { useState, useCallback } from 'react';
import { RAGService, type KnowledgeItem, type KnowledgeFormInput } from '@/services/rag.service';

export function useKnowledge() {
  const [items, setItems] = useState<KnowledgeItem[]>([]);
  const [totalItems, setTotalItems] = useState(0);
  const [totalVectors, setTotalVectors] = useState(0);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');

  const loadKnowledge = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const data = await RAGService.getKnowledgeList();
      setItems(data.items);
      setTotalItems(data.total_items);
      setTotalVectors(data.total_vectors);
    } catch (e: any) {
      console.error('Failed to load knowledge:', e);
      setError(e.message || 'Basis pengetahuan tidak dapat dimuat.');
    } finally {
      setLoading(false);
    }
  }, []);

  const submitForm = useCallback(async (input: KnowledgeFormInput): Promise<boolean> => {
    setSubmitting(true);
    try {
      await RAGService.submitKnowledgeForm(input);
      await loadKnowledge();
      return true;
    } catch (e: any) {
      console.error('Failed to submit knowledge:', e);
      setError(e.message || 'Pengetahuan tidak dapat disimpan.');
      return false;
    } finally {
      setSubmitting(false);
    }
  }, [loadKnowledge]);

  const uploadFile = useCallback(async (file: File, category: string, specialty: string): Promise<boolean> => {
    setUploading(true);
    try {
      await RAGService.uploadDocumentFile(file, category, specialty);
      await loadKnowledge();
      return true;
    } catch (e: any) {
      console.error('Failed to upload document:', e);
      setError(e.message || 'Dokumen tidak dapat diunggah.');
      return false;
    } finally {
      setUploading(false);
    }
  }, [loadKnowledge]);

  const deleteItem = useCallback(async (itemId: string): Promise<boolean> => {
    try {
      await RAGService.deleteKnowledge(itemId);
      await loadKnowledge();
      return true;
    } catch (e: any) {
      console.error('Failed to delete knowledge:', e);
      setError(e.message || 'Pengetahuan tidak dapat dihapus.');
      return false;
    }
  }, [loadKnowledge]);

  return {
    items,
    totalItems,
    totalVectors,
    loading,
    submitting,
    uploading,
    error,
    loadKnowledge,
    submitForm,
    uploadFile,
    deleteItem,
  };
}
