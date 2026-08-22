import { ApiClient } from './api.client';

export interface GuardrailConfig {
  enabled: boolean;
  pii_redaction_enabled: boolean;
  strictly_medical_scope: boolean;
  hallucination_prevention: boolean;
  toxic_content_filter: boolean;
  auto_disclaimer_enforced: boolean;
  min_confidence_score: number;
  max_query_length: number;
  banned_keywords: string[];
  allowed_domains: string[];
  safety_level: string;
  updated_at?: string;
}

export interface TestGuardrailRequest {
  text: string;
  target_type?: 'input' | 'output';
}

export interface TestGuardrailResponse {
  passed: boolean;
  verdict: string;
  risk_score: number;
  risk_level: 'Low' | 'Medium' | 'High' | 'Critical';
  violations: string[];
  redacted_text?: string;
  applied_rules: string[];
}

export interface GuardrailViolation {
  id: string;
  timestamp: string;
  user_id: string;
  doctor_name: string;
  query: string;
  violated_rule: string;
  action_taken: string;
  risk_level: string;
  verdict: string;
}

export class GuardrailsService {
  public static async getConfig(): Promise<GuardrailConfig> {
    return ApiClient.get<GuardrailConfig>('/guardrails/config');
  }

  public static async updateConfig(config: GuardrailConfig): Promise<GuardrailConfig> {
    return ApiClient.put<GuardrailConfig>('/guardrails/config', config);
  }

  public static async testGuardrail(req: TestGuardrailRequest): Promise<TestGuardrailResponse> {
    return ApiClient.post<TestGuardrailResponse>('/guardrails/test', req);
  }

  public static async getViolations(): Promise<GuardrailViolation[]> {
    return ApiClient.get<GuardrailViolation[]>('/guardrails/violations');
  }

  public static async clearViolation(id: string): Promise<{ status: string }> {
    return ApiClient.delete<{ status: string }>(`/guardrails/violations/${id}`);
  }
}
