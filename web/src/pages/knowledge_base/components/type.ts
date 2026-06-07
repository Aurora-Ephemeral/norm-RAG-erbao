import type { KnowledgeBase } from "../type"
import type { UploadFile } from 'tdesign-react'

export interface KBListItemProps {
    kb: KnowledgeBase,
    active: boolean,
    onSelect: (kb: KnowledgeBase) => void
    onEdit: (kb: KnowledgeBase) => void
    onDelete: (kb: KnowledgeBase) => void
}

export interface DocumentPanelProps {
    kb: KnowledgeBase
    onRefresh: () => void
}

export interface DocumentFilter {
  knowledge_base_id: number
  doc_title?: string
  part_type?: string
  standard_no?: string
}

export interface UploadModalProps {
    visible: boolean
    kbId: number
    onConfirm: () => void
    onCancel: () => void
}

export interface UploadFormValues {
  file: UploadFile[]
  fileName: string
  partType: string
  standardNo: string
}