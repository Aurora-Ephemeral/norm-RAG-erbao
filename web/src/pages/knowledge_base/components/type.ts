import type { KnowledgeBase } from "../type"

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