'use client';
import { useState, useCallback } from 'react';
import {
  AgentService,
  type AgentChatResponse,
  type PatientRecord,
  type ChatSession,
  type SOAContent,
  type TempSOAPRecord,
  type TempSOAPContent,
} from '@/services/agent.service';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  metadata?: Record<string, any> | null;
}

function formatErrorMessage(e: any, defaultMsg = 'Permintaan gagal'): string {
  if (e?.status >= 500 || e?.message?.includes('500') || e?.message?.includes('Internal Server Error')) {
    return '⚠️ Terjadi kendala teknis pada server (Error 500). Silakan coba beberapa saat lagi.';
  }
  if (
    e?.message &&
    (e.message.includes('ECONNRESET') ||
      e.message.includes('socket hang up') ||
      e.message.includes('Failed to fetch') ||
      e.message.includes('Tidak dapat terhubung'))
  ) {
    return '⚠️ Koneksi ke server terputus. Silakan periksa koneksi Anda dan coba beberapa saat lagi.';
  }
  return `⚠️ ${e?.message || defaultMsg}`;
}

export function useAgentChat() {
  const [patients, setPatients] = useState<PatientRecord[]>([]);
  const [selectedPatient, setSelectedPatient] = useState('');
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [executing, setExecuting] = useState(false);
  const [steps, setSteps] = useState<any[]>([]);
  const [activeTempSOAP, setActiveTempSOAP] = useState<TempSOAPRecord | null>(null);
  const [activeNode, setActiveNode] = useState<string | null>(null);
  const [completedNodes, setCompletedNodes] = useState<string[]>([]);
  const [latestSummary, setLatestSummary] = useState<string>('');

  const loadPatients = useCallback(async (roomId?: string) => {
    try {
      const data = await AgentService.getPatients(roomId);
      setPatients(data);
    } catch (e) {
      console.error('Failed to load patients:', e);
    }
  }, []);

  const loadSessions = useCallback(async () => {
    try {
      const data = await AgentService.getSessions();
      setSessions(data);
    } catch (e) {
      console.error('Failed to load sessions:', e);
    }
  }, []);

  const loadSessionMessages = useCallback(async (sessionId: string) => {
    setActiveSessionId(sessionId);
    try {
      const data = await AgentService.getSession(sessionId);
      setMessages(
        (data.messages || []).map((m: any) => ({
          role: m.role,
          content: m.content,
          timestamp: m.timestamp,
          metadata: m.metadata,
        }))
      );
      if (data.patient_id) setSelectedPatient(data.patient_id);
      if (data.temp_soap) {
        setActiveTempSOAP(data.temp_soap);
      } else if (data.temp_soap_id) {
        try {
          const soapData = await AgentService.getTempSOAP(data.temp_soap_id);
          setActiveTempSOAP(soapData);
        } catch {
          setActiveTempSOAP(null);
        }
      } else {
        setActiveTempSOAP(null);
      }
    } catch (e) {
      console.error('Failed to load session:', e);
    }
  }, []);

  const sendMessage = useCallback(async (query: string) => {
    if (!query.trim() || executing) return;

    const userMsg: ChatMessage = {
      role: 'user',
      content: query,
      timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMsg]);
    setExecuting(true);
    setSteps([]);
    setActiveNode('planner');
    setCompletedNodes([]);
    setLatestSummary('Memulai alur penalaran klinis terintegrasi...');

    try {
      const data = await AgentService.executeChatStream(
        {
          user_query: query,
          patient_id: selectedPatient || null,
          session_id: activeSessionId || null,
        },
        (statusEv) => {
          if (statusEv.node_name) {
            setActiveNode(statusEv.node_name);
            setCompletedNodes(prev => (prev.includes(statusEv.node_name!) ? prev : [...prev, statusEv.node_name!]));
          }
          if (statusEv.summary) {
            setLatestSummary(statusEv.summary);
          }
          if (statusEv.step) {
            setSteps(prev => {
              const alreadyHas = prev.some(s => s.step_name === statusEv.step.step_name);
              return alreadyHas ? prev : [...prev, statusEv.step];
            });
          }
        }
      );

      const aiMsg: ChatMessage = {
        role: 'assistant',
        content:
          data.final_synthesis?.trim() ||
          'Mohon maaf Dokter, informasi klinis tersebut belum tersedia di basis pengetahuan saya saat ini.',
        timestamp: new Date().toISOString(),
        metadata: {
          ...(data.soa_note ? { type: 'soa_note', note: data.soa_note } : {}),
          ...(data.temp_soap ? { type: 'temp_soap', temp_soap: data.temp_soap } : {}),
          hitl_required: data.hitl_required,
          hitl_data: data.hitl_data,
          steps: data.steps_executed || [],
        },
      };
      setMessages(prev => [...prev, aiMsg]);
      setSteps(data.steps_executed || []);
      if (data.session_id) setActiveSessionId(data.session_id);

      // Refresh sessions list after successful chat
      await loadSessions();
    } catch (e: any) {
      const is500OrServerErr = e?.status >= 500 || e?.message?.includes('500') || e?.message?.includes('Internal Server Error') || e?.status === 500;
      const errMsg: ChatMessage = {
        role: 'assistant',
        content: formatErrorMessage(e, 'Proses agen gagal'),
        timestamp: new Date().toISOString(),
        metadata: {
          is_error: true,
          error_code: is500OrServerErr ? 500 : (e?.status || 500),
          retry_query: query,
        },
      };
      setMessages(prev => [...prev, errMsg]);
    } finally {
      setExecuting(false);
      setTimeout(() => {
        setActiveNode(null);
      }, 3000);
    }

  }, [executing, selectedPatient, activeSessionId, loadSessions]);

  const replaceSOANote = useCallback((note: any) => {
    setMessages(prev => prev.map(message => (
      message.metadata?.type === 'soa_note' && message.metadata?.note?.note_id === note.note_id
        ? { ...message, metadata: { ...message.metadata, note } }
        : message
    )));
  }, []);

  const reviewSOA = useCallback(async (noteId: string, content: SOAContent) => {
    if (executing) return;
    setExecuting(true);
    try {
      const data = await AgentService.reviewSOA(noteId, content);
      replaceSOANote(data.note);
      setMessages(prev => [...prev, {
        role: 'assistant', content: data.message, timestamp: new Date().toISOString(),
        metadata: { type: 'soa_confirmation', note_id: noteId },
      }]);
      await loadSessions();
    } catch (e: any) {
      setMessages(prev => [...prev, { role: 'assistant', content: formatErrorMessage(e, 'Peninjauan resume gagal'), timestamp: new Date().toISOString() }]);
    } finally {
      setExecuting(false);
    }
  }, [executing, loadSessions, replaceSOANote]);

  const confirmSOA = useCallback(async (noteId: string, accept: boolean) => {
    if (executing) return;
    setExecuting(true);
    try {
      const data = await AgentService.confirmSOA(noteId, accept);
      replaceSOANote(data.note);
      setMessages(prev => [...prev, {
        role: 'assistant', content: data.message, timestamp: new Date().toISOString(),
        metadata: { type: 'soa_confirmation_result', note_id: noteId },
      }]);
      await loadSessions();
    } catch (e: any) {
      setMessages(prev => [...prev, { role: 'assistant', content: formatErrorMessage(e, 'Konfirmasi resume gagal'), timestamp: new Date().toISOString() }]);
    } finally {
      setExecuting(false);
    }
  }, [executing, loadSessions, replaceSOANote]);

  const sendAudio = useCallback(async (audio: File) => {
    if (executing) return;

    const userMsg: ChatMessage = {
      role: 'user',
      content: `[Rekaman Audio] ${audio.name}`,
      timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMsg]);
    setExecuting(true);
    setSteps([]);

    try {
      const data = await AgentService.executeAudioChat(
        audio,
        selectedPatient || null,
        activeSessionId || null,
      );
      if (data.temp_soap) {
        setActiveTempSOAP(data.temp_soap);
      }
      setMessages(prev => [...prev, {
        role: 'assistant',
        content:
          data.final_synthesis?.trim() ||
          'Mohon maaf Dokter, resume audio klinis belum dapat diproses.',
        timestamp: new Date().toISOString(),
        metadata: {
          ...(data.temp_soap ? { type: 'temp_soap', temp_soap: data.temp_soap } : {}),
          ...(data.soa_note ? { type: 'soa_note', note: data.soa_note } : {}),
          steps: data.steps_executed || [],
        },
      }]);
      setSteps(data.steps_executed || []);
      if (data.session_id) setActiveSessionId(data.session_id);
      await loadSessions();
    } catch (e: any) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: formatErrorMessage(e, 'Pemrosesan audio gagal'),
        timestamp: new Date().toISOString(),
        metadata: {
          is_error: true,
          error_code: e?.status || 500,
          retry_audio_file: audio,
        },
      }]);
    } finally {
      setExecuting(false);
    }

  }, [executing, selectedPatient, activeSessionId, loadSessions]);

  const commitTempSOAP = useCallback(async (tempId: string) => {
    if (executing) return;
    setExecuting(true);
    try {
      const res = await AgentService.commitTempSOAPToSIMRS(tempId);
      setActiveTempSOAP(res.temp_soap);
      // Update metadata in messages
      setMessages(prev => prev.map(m => {
        if (m.metadata?.temp_soap?.temp_id === tempId) {
          return {
            ...m,
            metadata: {
              ...m.metadata,
              temp_soap: res.temp_soap,
            },
          };
        }
        return m;
      }));
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `✅ **Catatan CPPT S-O-A-P berhasil dikirim dan disinkronisasikan ke SIMRS!**\n\n- No. Rekam Medis: \`${res.temp_soap.mrn || 'N/A'}\`\n- Diagnosa: ${res.temp_soap.soap_content?.assessment || '-'}\n- Log SIMRS: \`${res.simrs_response?.log_id || 'OK'}\``,
        timestamp: new Date().toISOString(),
        metadata: {
          type: 'simrs_sync_result',
          temp_id: tempId,
          simrs_response: res.simrs_response,
        },
      }]);
      await loadSessions();
      return res;
    } catch (e: any) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: formatErrorMessage(e, 'Gagal mengirim CPPT ke SIMRS'),
        timestamp: new Date().toISOString(),
      }]);
      throw e;
    } finally {
      setExecuting(false);
    }
  }, [executing, loadSessions]);

  const updateTempSOAP = useCallback(async (tempId: string, content: TempSOAPContent) => {
    try {
      const updated = await AgentService.updateTempSOAP(tempId, { soap_content: content });
      setActiveTempSOAP(updated);
      setMessages(prev => prev.map(m => {
        if (m.metadata?.temp_soap?.temp_id === tempId) {
          return {
            ...m,
            metadata: {
              ...m.metadata,
              temp_soap: updated,
            },
          };
        }
        return m;
      }));
      return updated;
    } catch (e) {
      console.error('Failed to update temp soap:', e);
      throw e;
    }
  }, []);

  const startNewSession = useCallback(() => {
    setActiveSessionId('');
    setMessages([]);
    setSteps([]);
    setActiveTempSOAP(null);
  }, []);

  const renameSession = useCallback(async (sessionId: string, newTitle: string) => {
    if (!newTitle.trim()) return;
    try {
      await AgentService.renameSession(sessionId, newTitle.trim());
      setSessions(prev => prev.map(s => s.session_id === sessionId ? { ...s, title: newTitle.trim() } : s));
    } catch (e: any) {
      console.error('Failed to rename session:', e);
      throw e;
    }
  }, []);

  const deleteSession = useCallback(async (sessionId: string) => {
    try {
      await AgentService.deleteSession(sessionId);
      setSessions(prev => prev.filter(s => s.session_id !== sessionId));
      if (activeSessionId === sessionId) {
        startNewSession();
      }
    } catch (e: any) {
      console.error('Failed to delete session:', e);
      throw e;
    }
  }, [activeSessionId, startNewSession]);

  return {
    patients,
    selectedPatient,
    setSelectedPatient,
    sessions,
    activeSessionId,
    messages,
    executing,
    steps,
    activeNode,
    completedNodes,
    latestSummary,
    activeTempSOAP,
    loadPatients,
    loadSessions,
    loadSessionMessages,
    startNewSession,
    renameSession,
    deleteSession,
    sendMessage,
    sendAudio,
    reviewSOA,
    confirmSOA,
    commitTempSOAP,
    updateTempSOAP,
  };
}
