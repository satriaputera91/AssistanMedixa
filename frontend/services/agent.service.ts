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

export interface AgentChatResponse {
  session_id: string;
  user_query: string;
  patient_id?: string | null;
  steps_executed: AgentStep[];
  final_synthesis: string;
  workflow_type?: 'text' | 'audio';
  audio_transcript?: string | null;
  soa_note?: SOANote | null;
  structured_output?: Record<string, any> | null;
  output_validation?: Record<string, any> | null;
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
  messages: { role: string; content: string; timestamp: string; metadata?: Record<string, any> | null }[];
}

export class AgentService {
  public static async executeChat(request: AgentChatRequest): Promise<AgentChatResponse> {
    return ApiClient.post<AgentChatResponse>('/agent/chat', request);
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

