import { useTranslation } from 'react-i18next'
import { Button, DialogPlugin, NotificationPlugin, Loading, Empty } from 'tdesign-react'
import { AddIcon } from 'tdesign-icons-react'
import { useEffect, useState } from 'react'
import type { KnowledgeBase } from './type'
import { deleteKB, listAllKB } from '@/api/knowledgebase'
import KBListItem from './components/KBListItem'
const KnowledgeBasePage: React.FC = () => {
    
    const { t } = useTranslation()
    const [ showKBModal, setShowKBModal ] = useState(false)
    const [ kbList, setKbList ] = useState<KnowledgeBase[]>([])
    const [kbLoading, setKbLoading] = useState(false)
    const [selectedKbId, setSelectedKbId] = useState<number | null>(null)

    const handleSelectKB = (kb: KnowledgeBase) => {
        setSelectedKbId(kb.id)
    }

    const handleDeleteKB = async (kb: KnowledgeBase) => {
        
    }

    const handleEditKB = async (kb: KnowledgeBase) => {
        
    }

    const fetchKBList = async () => {
        setKbLoading(true)
        try {
            const res = await listAllKB()
            if (res.code === 200) {
                setKbList(res.data || [])
            }
        } catch (error) {
            NotificationPlugin.error({
                title: t('common.error'),
                content: t('knowledge.error.fetchList'),
            })
        } finally {
            setKbLoading(false)
        }
    }

    useEffect(() => {
        fetchKBList()
    }, [])
    return (
        <div>
            {/* sidebar */}
            <aside className="w-[280px] shrink-0 border-r border-[var(--color-border)] flex flex-col">
                <div className="flex items-center justify-between p-4 text-[13px] font-medium text-[var(--color-text-secondary)] uppercase tracking-[1px]">
                    <span>{t('knowledge.sidebar.title')}</span>
                    <Button 
                        variant="text"
                        shape="square"
                        size="small"
                        icon={<AddIcon />}
                        title={t('knowledge.sidebar.add')}
                        onClick={() => setShowKBModal(true)}
                    />
                </div>
                <div className="flex-1 overflow-y-auto px-2 pb-2 flex flex-col gap-2">
                    {
                        kbLoading ? <Loading size="small"/> : (
                            kbList.length == 0 ? (
                                <div className="p-6 text-center text-[var(--color-text-muted)] text-[13px]">
                                    {t('knowledge.sidebar.empty')}
                                </div>
                            ) : (
                                kbList.map((kb) => (
                                    <KBListItem 
                                        key={kb.id} 
                                        kb={kb}
                                        active={kb.id == selectedKbId} 
                                        onSelect={handleSelectKB}
                                        onEdit={handleEditKB}
                                        onDelete={handleDeleteKB}
                                    />
                                ))
                            )
                        )
                    }
                </div>
            </aside>
            <main className='flex-1 overflow-y-auto'>
                {
                    selectedKbId ? (
                        <div>

                        </div>
                    ):(
                        <Empty title={t('knowledge.sidebar.placeholder')}/>
                    )
                }
            </main>

        </div>
    );
}

export default KnowledgeBasePage;