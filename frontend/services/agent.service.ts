import { ApiClient } from './api.client';

export interface AgentChatRequest {
  user_query: string;
  patient_id?: string | null;
  session_id?: string | null;
}

export interface AgentStep {
  step_name: string;
  description: string;
  status: string;
  result: any;
}

export interface TempSOAPContent {
  subjective: string;
  objective: string;
  assessment: string;
  plan?: string;
  instructions?: string;
}

export interface TempSOAPRecord {
  temp_id: string;
  session_id: string;
  patient_id?: string | null;
  patient_name?: string | null;
  mrn?: string | null;
  nik?: string | null;
  user_id: string;
  doctor_name: string;
  audio_filename: string;
  audio_url: string;
  audio_path?: string | null;
  audio_size_bytes: number;
  audio_transcript: string;
  soap_content: TempSOAPContent;
  raw_markdown: string;
  structured_output?: Record<string, any> | null;
  status: 'draft' | 'pending_review' | 'ready_for_simrs' | 'synced_to_simrs';
  simrs_sync_status: 'pending' | 'synced' | 'failed';
  simrs_log_id?: string | null;
  simrs_response?: Record<string, any> | null;
  created_at: string;
  updated_at: string;
  synced_at?: string | null;
}

export interface TempSOAPCommitResponse {
  status: string;
  message: string;
  temp_soap: TempSOAPRecord;
  simrs_response?: Record<string, any> | null;
}

export interface AgentChatResponse {
  session_id: string;
  user_query: string;
  patient_id?: string | null;
  steps_executed: AgentStep[];
  final_synthesis: string;
  workflow_type?: 'text' | 'audio';
  audio_transcript?: string | null;
  soa_note?: SOANote | null;
  temp_soap?: TempSOAPRecord | null;
  structured_output?: Record<string, any> | null;
  output_validation?: Record<string, any> | null;
  hitl_required?: boolean;
  hitl_data?: {
    required: boolean;
    type: string;
    title: string;
    options: Array<{
      key: string;
      label: string;
      icon: string;
      description: string;
      action_type: 'record_audio' | 'upload_file' | 'manual_modal';
    }>;
    missing_subjective?: boolean;
    missing_objective?: boolean;
    patient_id?: string | null;
  } | null;
}


export interface SOAContent {
  subjective: string;
  objective: string;
  assessment: string;
  plan?: string;
}

export interface SOAChange {
  field: string;
  previous: string;
  proposed: string;
}

export interface SOANote {
  note_id: string;
  session_id: string;
  content: SOAContent;
  status: string;
  pending_content?: SOAContent | null;
  changes: SOAChange[];
  updated_at: string;
}

export interface SOAReviewResponse {
  note: SOANote;
  message: string;
}

export interface PatientRecord {
  patient_id: string;
  room_id?: string;
  room_name?: string;
  nik?: string;
  ihs_number?: string;
  name: string;
  age: number;
  gender: string;
  vitals: Record<string, string>;
  diagnoses: string[];
  allergies: string[];
  current_medications: { name: string; dosage: string }[];
  recent_labs: Record<string, string>;
}

export interface ChatSession {
  session_id: string;
  user_id: string;
  title: string;
  created_at: string;
  patient_id?: string;
  temp_soap_id?: string | null;
  temp_soap?: TempSOAPRecord | null;
  messages: { role: string; content: string; timestamp: string; metadata?: Record<string, any> | null }[];
}

export interface WorkflowStatusEvent {
  status: 'running' | 'node_completed' | 'error';
  node_name?: string;
  label?: string;
  icon?: string;
  phase?: string;
  session_id?: string;
  patient_id?: string | null;
  summary?: string;
  step?: any;
  total_steps?: number;
  timestamp: string;
}

export class AgentService {
  public static async executeChat(request: AgentChatRequest): Promise<AgentChatResponse> {
    return ApiClient.post<AgentChatResponse>('/agent/chat', request);
  }

  public static async executeChatStream(
    request: AgentChatRequest,
    onWorkflowStatus?: (event: WorkflowStatusEvent) => void,
  ): Promise<AgentChatResponse> {
    const token = ApiClient.getToken();
    const response = await fetch('/api/v1/agent/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const errorText = await response.text();
      let errorDetail = 'Gagal melakukan stream konsultasi AI';
      try {
        const parsed = JSON.parse(errorText);
        errorDetail = parsed.detail || parsed.message || errorDetail;
      } catch {}
      throw new Error(errorDetail);
    }

    if (!response.body) {
      throw new Error('Response stream tidak tersedia.');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';
    let finalResponse: AgentChatResponse | null = null;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const blocks = buffer.split('\n\n');
      buffer = blocks.pop() || '';

      for (const block of blocks) {
        if (!block.trim()) continue;

        let eventType = 'message';
        let dataStr = '';

        for (const line of block.split('\n')) {
          if (line.startsWith('event:')) {
            eventType = line.replace('event:', '').trim();
          } else if (line.startsWith('data:')) {
            dataStr += line.replace('data:', '').trim();
          }
        }

        if (!dataStr) continue;

        try {
          const parsed = JSON.parse(dataStr);
          if (eventType === 'workflow_status') {
            if (onWorkflowStatus) {
              onWorkflowStatus(parsed as WorkflowStatusEvent);
            }
          } else if (eventType === 'complete') {
            finalResponse = parsed as AgentChatResponse;
          } else if (eventType === 'error') {
            throw new Error(parsed.error || 'Terjadi kesalahan pada alur proses AI');
          }
        } catch (e: any) {
          if (eventType === 'error' || (e.message && e.message.includes('kesalahan'))) {
            throw e;
          }
          console.error('Failed to parse SSE chunk:', e, dataStr);
        }
      }
    }

    if (!finalResponse) {
      throw new Error('Stream selesai tanpa menerima respon final dari agen.');
    }

    return finalResponse;
  }

  public static async executeAudioChat(
    audio: File,
    patientId?: string | null,
    sessionId?: string | null,
  ): Promise<AgentChatResponse> {
    const formData = new FormData();
    formData.append('audio', audio);
    if (patientId) formData.append('patient_id', patientId);
    if (sessionId) formData.append('session_id', sessionId);

    return ApiClient.post<AgentChatResponse>('/agent/chat/audio', formData, true);
  }

  public static async reviewSOA(noteId: string, content: SOAContent): Promise<SOAReviewResponse> {
    return ApiClient.put<SOAReviewResponse>('/agent/soa/review', { note_id: noteId, ...content });
  }

  public static async confirmSOA(noteId: string, accept: boolean): Promise<SOAReviewResponse> {
    return ApiClient.put<SOAReviewResponse>('/agent/soa/confirmation', { note_id: noteId, accept });
  }

  public static async getPatients(roomId?: string): Promise<PatientRecord[]> {
    const url = roomId ? `/agent/patients?room_id=${encodeURIComponent(roomId)}` : '/agent/patients';
    return ApiClient.get<PatientRecord[]>(url);
  }

  public static async lookupPatient(query: string): Promise<PatientRecord> {
    return ApiClient.get<PatientRecord>(`/agent/patients/lookup?query=${encodeURIComponent(query)}`);
  }

  public static async getSessions(): Promise<ChatSession[]> {
    return ApiClient.get<ChatSession[]>('/chat/sessions');
  }

  public static async getSession(sessionId: string): Promise<ChatSession> {
    return ApiClient.get<ChatSession>(`/chat/sessions/${sessionId}`);
  }

  public static async renameSession(sessionId: string, title: string): Promise<ChatSession> {
    return ApiClient.put<ChatSession>(`/chat/sessions/${sessionId}`, { title });
  }

  public static async deleteSession(sessionId: string): Promise<{ status: string; session_id: string }> {
    return ApiClient.delete<{ status: string; session_id: string }>(`/chat/sessions/${sessionId}`);
  }

  public static async getClinicRooms(): Promise<ClinicRoom[]> {
    return ApiClient.get<ClinicRoom[]>('/agent/clinic-rooms');
  }

  public static async getSelectedRoom(): Promise<{ selected_room: ClinicRoom | null }> {
    return ApiClient.get<{ selected_room: ClinicRoom | null }>('/agent/clinic-rooms/selected');
  }

  public static async selectClinicRoom(roomId: string): Promise<{ status: string; selected_room: ClinicRoom }> {
    return ApiClient.post<{ status: string; selected_room: ClinicRoom }>('/agent/clinic-rooms/select', { room_id: roomId });
  }

  // ── Temporary SOAP Pre-SIMRS Methods ──────────────────────────────

  public static async createManualTempSOAP(payload: {
    session_id: string;
    patient_id?: string | null;
    soap_content: TempSOAPContent;
    raw_markdown?: string;
    structured_output?: Record<string, any>;
  }): Promise<TempSOAPRecord> {
    return ApiClient.post<TempSOAPRecord>('/agent/soap-temp', payload);
  }

  public static async getTempSOAPList(patientId?: string, status?: string): Promise<TempSOAPRecord[]> {
    const params = new URLSearchParams();
    if (patientId) params.append('patient_id', patientId);
    if (status) params.append('status', status);
    const query = params.toString() ? `?${params.toString()}` : '';
    return ApiClient.get<TempSOAPRecord[]>(`/agent/soap-temp${query}`);
  }

  public static async getTempSOAP(tempId: string): Promise<TempSOAPRecord> {
    return ApiClient.get<TempSOAPRecord>(`/agent/soap-temp/${tempId}`);
  }

  public static async getTempSOAPBySession(sessionId: string): Promise<TempSOAPRecord | null> {
    return ApiClient.get<TempSOAPRecord | null>(`/agent/soap-temp/session/${sessionId}`);
  }

  public static async updateTempSOAP(
    tempId: string,
    data: { soap_content?: TempSOAPContent; raw_markdown?: string; status?: string }
  ): Promise<TempSOAPRecord> {
    return ApiClient.put<TempSOAPRecord>(`/agent/soap-temp/${tempId}`, data);
  }

  public static async deleteTempSOAP(tempId: string): Promise<{ status: string; temp_id: string }> {
    return ApiClient.delete<{ status: string; temp_id: string }>(`/agent/soap-temp/${tempId}`);
  }

  public static async commitTempSOAPToSIMRS(tempId: string): Promise<TempSOAPCommitResponse> {
    return ApiClient.post<TempSOAPCommitResponse>(`/agent/soap-temp/${tempId}/commit-simrs`, {});
  }

  public static getAudioStreamUrl(tempIdOrAudioUrl: string): string {
    if (tempIdOrAudioUrl.startsWith('http') || tempIdOrAudioUrl.startsWith('/api')) {
      return tempIdOrAudioUrl;
    }
    return `/api/v1/agent/soap-temp/${tempIdOrAudioUrl}/audio`;
  }
}

export interface ClinicRoom {
  room_id: string;
  room_name: string;
  room_code: string;
  floor: string;
  building: string;
  specialty: string;
  status: string;
}

