import { ApiClient } from './api.client';

export interface KnowledgeFormInput {
  title: string;
  category: 'disease' | 'medicine' | 'terminology' | string;
  specialty: string;
  icd10_code?: string | null;
  rxnorm_code?: string | null;
  synonyms?: string[];
  keywords?: string[];
  evidence_level?: string;
  content: string;
}

export interface KnowledgeItem {
  id: string;
  title: string;
  category: string;
  specialty: string;
  icd10_code?: string | null;
  rxnorm_code?: string | null;
  loinc_code?: string | null;
  synonyms: string[];
  keywords: string[];
  evidence_level?: string | null;
  chunks_count: number;
  created_at: string;
}

export interface KnowledgeListResponse {
  total_items: number;
  total_vectors: number;
  items: KnowledgeItem[];
}

export interface RAGChunkResult {
  title: string;
  category: string;
  specialty: string;
  icd10_code?: string | null;
  rxnorm_code?: string | null;
  evidence_level?: string | null;
  reranked_score: number;
  boost_applied: number;
  chunk_snippet: string;
}

export interface RAGSearchResponse {
  status: string;
  query: string;
  results_count: number;
  chunks: RAGChunkResult[];
}

export interface RAGSearchRequest {
  query: string;
  top_k?: number;
  category_filter?: string | null;
}

export class RAGService {
  public static async getKnowledgeList(): Promise<KnowledgeListResponse> {
    return ApiClient.get<KnowledgeListResponse>('/rag/knowledge');
  }

  public static async submitKnowledgeForm(input: KnowledgeFormInput): Promise<any> {
    return ApiClient.post('/rag/knowledge', input);
  }

  public static async uploadDocumentFile(file: File, category: string, specialty: string): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', category);
    formData.append('specialty', specialty);

    return ApiClient.post('/rag/upload-doc', formData, true);
  }

  public static async deleteKnowledge(itemId: string): Promise<any> {
    return ApiClient.delete(`/rag/knowledge/${itemId}`);
  }

  public static async search(request: RAGSearchRequest): Promise<RAGSearchResponse> {
    return ApiClient.post<RAGSearchResponse>('/rag/search', request);
  }

  public static async extractKeywords(text: string, title?: string, maxKeywords: number = 10): Promise<string[]> {
    const res = await ApiClient.post<{ status: string; keywords: string[]; count: number }>('/rag/extract-keywords', {
      text,
      title,
      max_keywords: maxKeywords,
    });
    return res.keywords || [];
  }
}


