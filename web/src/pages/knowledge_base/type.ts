// ─── Enums ───────────────────────────────────────────────────────────────────

export type VisibilityEnum = 'PRIVATE' | 'PUBLIC' | 'TEAM'
export type KBStatusEnum = 'ACTIVE' | 'ARCHIVED' | 'DISABLED'
export type RetrievalStrategyEnum = 'VECTOR' | 'HYBRID' | 'KEYWORD'
export type DocStatusEnum = 'ACTIVE' | 'PROCESSING' | 'FAILED' | 'DELETED'

// ─── Knowledge Base ───────────────────────────────────────────────────────────

export interface KnowledgeBase {
  id: number
  kb_name: string
  description?: string
  owner_user_id: number
  visibility: VisibilityEnum
  status: KBStatusEnum
  document_count: number
  chunk_count: number
  embedding_model?: string
  chunk_size?: number
  chunk_overlap?: number
  top_k?: number
  retrieval_strategy: RetrievalStrategyEnum
  metadata_json?: Record<string, unknown>
  created_time: string
  updated_time: string
}

export interface KnowledgeBaseCreate {
  kb_name: string
  description?: string
  owner_user_id: number
  visibility?: VisibilityEnum
  embedding_model?: string
  chunk_size?: number
  chunk_overlap?: number
  top_k?: number
  retrieval_strategy?: RetrievalStrategyEnum
}

export interface KnowledgeBaseUpdate {
  kb_name?: string
  description?: string
  visibility?: VisibilityEnum
  status?: KBStatusEnum
  embedding_model?: string
  chunk_size?: number
  chunk_overlap?: number
  top_k?: number
  retrieval_strategy?: RetrievalStrategyEnum
}

// ─── Document ─────────────────────────────────────────────────────────────────

export interface Document {
  id: number
  document_uuid: string
  file_id: number
  knowledge_base_id: number
  doc_title?: string
  doc_type?: string
  language?: string
  version: number
  is_latest: boolean
  doc_status: DocStatusEnum
  part_type?: string
  standard_no?: string
  chunk_count: number
  token_count: number
  metadata_json?: Record<string, unknown>
  created_time: string
  updated_time: string
}

export interface DocumentFilter {
  knowledge_base_id: number
  doc_title?: string
  part_type?: string
  standard_no?: string
}

// ─── File ─────────────────────────────────────────────────────────────────────

export interface RawFile {
  id: number
  file_uuid: string
  file_md5: string
  file_sha256?: string
  file_name: string
  file_ext?: string
  mime_type?: string
  file_size: number
  storage_type: 'S3' | 'LOCAL'
  storage_path: string
  created_time: string
  updated_time: string
}

export interface FileUploadResult {
  file_exist: boolean
  doc_exist: boolean
  data: RawFile
}

// ─── HTTP ─────────────────────────────────────────────────────────────────────

export type { HTTPResponse, HTTPResponsePage } from '@/api/type'
