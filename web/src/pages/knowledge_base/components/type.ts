import type { KnowledgeBase } from "../type"

export interface KBListItemProps {
    kb: KnowledgeBase,
    active: boolean,
    onSelect: (kb: KnowledgeBase) => void
    onEdit: (kb: KnowledgeBase) => void
    onDelete: (kb: KnowledgeBase) => void
}