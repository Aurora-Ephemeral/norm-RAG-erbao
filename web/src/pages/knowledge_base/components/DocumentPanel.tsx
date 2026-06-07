
import type { DocumentPanelProps, DocumentFilter } from './type'
import { useEffect, useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { deleteDocument, listDocsByPage } from '@/api/document'
import { DeleteIcon, EditIcon, RefreshIcon, SearchIcon, UploadIcon } from 'tdesign-icons-react'
import {
  Button,
  Input,
  NotificationPlugin,
  Pagination,
  Popconfirm,
  Table,
  Tag,
} from 'tdesign-react'
import type { PrimaryTableCol } from 'tdesign-react'
import type { DocStatusEnum, Document, KnowledgeBase } from '../type'
import UploadModal from './UploadModal'

const PAGE_SIZE = 10

const STATUS_TAG: Record<
  DocStatusEnum,
  { theme: 'success' | 'primary' | 'danger' | 'default'; label: string }
> = {
  ACTIVE:     { theme: 'success', label: '已就绪' },
  PROCESSING: { theme: 'primary', label: '处理中' },
  FAILED:     { theme: 'danger',  label: '处理失败' },
  DELETED:    { theme: 'default', label: '已删除' },
}

const DocumentPanel: React.FC<DocumentPanelProps> = ({kb, onRefresh}) => {

    const { t } = useTranslation()
    const [docs, setDocs] = useState([])
    const [total, setTotal] = useState(0)
    const [currPage, setCurrPage] = useState(1)
    const [filter, setFilter] = useState<DocumentFilter>({knowledge_base_id: kb.id})
    const [docTitle, setDocTitle] = useState('')
    const [partType, setPartType] = useState('')
    const [standardNo, setStandardNo] = useState('')
    const [loading, setLoading] = useState(false)
    const [showUploadModal, setShowUploadModal] = useState(false)


    const fetchDocs = async (current:number, filter: DocumentFilter) => {
        try {
            setLoading(true)
            const res = await listDocsByPage(current, PAGE_SIZE, filter)
            if (res.code === 200) {
                setDocs(res.data || [])
                setTotal(res.total ?? 0)
            }
        } catch (error) {
            NotificationPlugin.error({
                title: t('common.error'),
                content: t('knowledge.error.fetchDocList')
            })
            console.error(error)
        } finally {
            setLoading(false)
        }
    }

    const hanldePageChange = (current: number) => {
        setCurrPage(current)
        fetchDocs(current, filter)
    }

    const handleOpenUploadModal = () => {
        setShowUploadModal(true)
    }

    const handleCloseUploadModal = () => {
        setShowUploadModal(false)
    }

    const handleSearch = () => {
        
    }

    const handleReset = () => {
        
    }

    const handleRefresh = () => {
        fetchDocs(currPage, filter)
    }

    const handleDeleteDoc = async (doc: Document) => {
        
    }
    // fetch document list 
    useEffect(() => {
        setFilter({knowledge_base_id: kb.id, doc_title: '', part_type: '', standard_no: ''})
        fetchDocs(1, filter)
    }, [kb.id])

    const columns: PrimaryTableCol<Document>[] = [
        {
            colKey: 'doc_title',
            title: t('knowledge.document.columns.name'),
            ellipsis: true,
            cell: ({ row }) => <span title={row.doc_title}>{row.doc_title || '-'}</span>,
        },
        {
            colKey: 'doc_status',
            title: t('knowledge.document.columns.status'),
            width: 100,
            cell: ({ row }) => {
            const cfg = STATUS_TAG[row.doc_status] ?? { theme: 'default' as const, label: row.doc_status }
            return (
                <Tag theme={cfg.theme} variant="light">
                {t(`knowledge.document.status.${row.doc_status}`) || cfg.label}
                </Tag>
            )
            },
        },
        {
            colKey: 'part_type',
            title: t('knowledge.document.columns.partType'),
            width: 120,
            cell: ({ row }) => <span>{row.part_type || '-'}</span>,
        },
        {
            colKey: 'standard_no',
            title: t('knowledge.document.columns.standardNo'),
            width: 150,
            cell: ({ row }) => <span>{row.standard_no || '-'}</span>,
        },
        {
            colKey: 'chunk_count',
            title: t('knowledge.document.columns.chunks'),
            width: 90,
            align: 'right',
        },
        {
            colKey: 'token_count',
            title: t('knowledge.document.columns.tokens'),
            width: 90,
            align: 'right',
        },
        {
            colKey: 'created_time',
            title: t('knowledge.document.columns.createdTime'),
            width: 180,
            cell: ({ row }) =>
            new Date(row.created_time).toLocaleString('zh-CN', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
            }),
        },
        {
            colKey: 'actions',
            title: t('knowledge.document.columns.actions'),
            width: 72,
            align: 'center',
            cell: ({ row }) => (
            // Popconfirm for inline, non-modal confirmation on row-level delete
            <Popconfirm
                content={t('knowledge.dialog.deleteDoc.content')}
                confirmBtn={{ content: t('knowledge.dialog.deleteDoc.confirm'), theme: 'danger' }}
                cancelBtn={t('knowledge.dialog.deleteDoc.cancel')}
                onConfirm={() => handleDeleteDoc(row)}
            >
                <Button
                    variant="text"
                    shape="square"
                    size="small"
                    theme="danger"
                    icon={<DeleteIcon />}
                />
            </Popconfirm>
            ),
        },
    ]
    return (
        <div className="p-6">
            <div className='flex items-end justify-between mb-6'>
                <div>
                    <div className="text-[20px] font-semibold mb-1">{kb.kb_name}</div>
                    {kb.description && (
                        <div className="text-[14px] text-[var(--color-text-muted)]">{kb.description}</div>
                    )}
                </div>
                <div className="flex items-center gap-2">
                    <Button
                        variant="outline"
                        icon={<EditIcon />}
                    >
                        {t('knowledge.kb.edit')}
                    </Button>
                    <Button
                        theme="primary"
                        icon={<UploadIcon />}
                        onClick={handleOpenUploadModal}
                    >
                        {t('knowledge.document.upload')}
                    </Button>
                </div>
            </div>
            <div className='flex flex-wrap items-center gap-2 mb-4'>
                     <Input
                        placeholder={t('knowledge.document.filter.namePlaceholder')}
                        value={docTitle}
                        style={{ width: 200 }}
                        prefixIcon={<SearchIcon />}
                        onChange={(val) => setDocTitle(val as string)}
                        onEnter={handleSearch}
                    />
                    <Input
                        placeholder={t('knowledge.document.filter.partTypePlaceholder')}
                        value={partType}
                        style={{ width: 150 }}
                        prefixIcon={<SearchIcon />}
                        onChange={(val) => setPartType(val as string)}
                        onEnter={handleSearch}
                    />
                    <Input
                        placeholder={t('knowledge.document.filter.standardNoPlaceholder')}
                        value={standardNo}
                        style={{ width: 150 }}
                        prefixIcon={<SearchIcon />}
                        onChange={(val) => setStandardNo(val as string)}
                        onEnter={handleSearch}
                    />
                    <Button onClick={handleSearch}>{t('knowledge.document.filter.search')}</Button>
                    <Button variant="outline" onClick={handleReset}>
                        {t('knowledge.document.filter.reset')}
                    </Button>
                    {/* Silent refresh button — also useful when PROCESSING docs need manual check */}
                    <Button
                        variant="text"
                        shape="square"
                        icon={<RefreshIcon />}
                        title={t('knowledge.document.refresh')}
                        onClick={handleRefresh}
                    />
            </div>
            <Table
                data={docs}
                loading={loading}
                rowKey='id'
                columns={columns}
                empty={
                    <span className="text-[var(--color-text-muted)] text-[13px]">
                        {t('knowledge.document.empty')}
                    </span>
                }
                pagination={{
                    total,
                    defaultPageSize: PAGE_SIZE,
                    current: currPage,
                    pageSizeOptions: [],
                    onCurrentChange: hanldePageChange
                }}
            >

            </Table>
            <UploadModal 
                visible={showUploadModal}
                kbId={kb.id}
                onCancel={handleCloseUploadModal}
                onConfirm={handleRefresh}
            />
        </div>
    )
}

export default DocumentPanel