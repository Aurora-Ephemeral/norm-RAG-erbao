import type { KBListItemProps } from './type'
import { useTranslation } from 'react-i18next'
import { Button } from 'tdesign-react'
import { DeleteIcon, EditIcon, FolderOpenIcon } from 'tdesign-icons-react'
const KBListItem: React.FC<KBListItemProps> = ({
    kb,
    active,
    onSelect,
    onEdit,
    onDelete
}) => {
    const { t } = useTranslation()
    return (
    <div className={[
        'group flex items-start justify-between p-3 cursor-pointer transition-colors duration-150',
        active ? 'bg-[var(--color-bg-active)]' : 'hover:bg-[var(--color-bg-hover)]'
        ].join(' ')}>
        <div className="flex-1 min-w-0" onClick={() => onSelect(kb)}>
            <div className="text-[14px] font-medium truncate">{kb.kb_name}</div>
            <div className="text-[12px] text-[var(--color-text-muted)] mt-0.5">
                {t('knowledge.kb.documents', { count: kb.document_count })}
            </div>
        </div>
        <div className="flex items-center opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
            <Button
                variant="text"
                shape="square"
                size="small"
                icon={<EditIcon size="14px" />}
                title={t('knowledge.kb.edit')}
                onClick={() => onEdit(kb)}
            />
            <Button
                variant="text"
                shape="square"
                size="small"
                theme="danger"
                icon={<DeleteIcon size="14px" />}
                title={t('knowledge.kb.delete')}
                onClick={() => onDelete(kb)}
            />
        </div>
    </div>
    )
}

export default KBListItem