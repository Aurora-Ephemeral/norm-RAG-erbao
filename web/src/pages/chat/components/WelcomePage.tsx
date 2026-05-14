import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { ChatSender } from '@tdesign-react/chat'

const SPEED = 60
const MODE_VALUES = ['simple', 'complex'] as const
type Mode = typeof MODE_VALUES[number]

interface Props {
    onSend: (text: string) => void
    onStop: () => void
    loading: boolean
}

const WelcomePage: React.FC<Props> = ({ onSend, loading, onStop }) => {
    const { t } = useTranslation()
    const line1Full = t('chat.welcome.line1')
    const line2Full = t('chat.welcome.line2')

    const [line1, setLine1] = useState('')
    const [line2, setLine2] = useState('')
    const [inputValue, setInputValue] = useState('')
    const [mode, setMode] = useState<Mode>('simple')

    const handleStop = () => {
        onStop()
        setInputValue('')
    }

    useEffect(() => {
        let i = 0
        const t1 = setInterval(() => {
            setLine1(line1Full.slice(0, ++i))
            if (i >= line1Full.length) {
                clearInterval(t1)
                let j = 0
                const t2 = setInterval(() => {
                    setLine2(line2Full.slice(0, ++j))
                    if (j >= line2Full.length) clearInterval(t2)
                }, SPEED)
            }
        }, SPEED)
        return () => clearInterval(t1)
    }, [line1Full, line2Full])

    return (
        <div className="flex flex-1 flex-col items-center justify-center gap-6">

            {/* 欢迎文字 */}
            <div className="text-center">
                <h2 className="text-[22px] font-semibold text-[var(--color-text-primary)] mb-2">
                    {line1}
                    {line1.length < line1Full.length && <span className="animate-pulse">|</span>}
                </h2>
                <p className="text-sm text-[var(--color-text-secondary)] min-h-[1.25rem]">
                    {line2}
                    {line1.length >= line1Full.length && line2.length < line2Full.length && (
                        <span className="animate-pulse">|</span>
                    )}
                </p>
            </div>

            {/* 模式选择器 */}
            <div className="w-full max-w-[680px] flex flex-col gap-3">
                <div className="flex flex-col gap-2">
                    <div className="flex justify-center items-center gap-2">
                        {MODE_VALUES.map(value => (
                            <button
                                key={value}
                                onClick={() => setMode(value)}
                                className={[
                                    'px-4 py-1.5 rounded-full text-sm font-medium transition-all duration-200 border',
                                    mode === value
                                        ? 'bg-[var(--color-text-primary)] text-white border-[var(--color-text-primary)]'
                                        : 'bg-transparent text-[var(--color-text-secondary)] border-[var(--color-border)] hover:border-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]',
                                ].join(' ')}
                            >
                                {t(`chat.welcome.modes.${value}.label`)}
                            </button>
                        ))}
                    </div>
                    <p className="text-xs text-[var(--color-text-muted)] px-1 text-center">
                        {t(`chat.welcome.modes.${mode}.desc`)}
                    </p>
                </div>

                {/* 输入框 */}
                <ChatSender
                    value={inputValue}
                    placeholder={t('chat.input.placeholder')}
                    loading={loading}
                    autosize={{ minRows: 2 }}
                    onChange={(e) => setInputValue(e.detail)}
                    onSend={() => onSend(inputValue)}
                    onStop={() => handleStop()}
                />
            </div>
        </div>
    )
}

export default WelcomePage
