import { Layout, Tooltip, Button } from "tdesign-react"
import { useTranslation } from "react-i18next"
import { ChatIcon, FolderOpenIcon } from 'tdesign-icons-react';
import { useNavigate, useLocation } from "react-router-dom"
import styles from './style.module.scss'

const Header: React.FC = () => {

    const { Header } = Layout
    const { t, i18n } = useTranslation()
    const currLang: string = i18n.language
    const navigate = useNavigate()
    const location = useLocation()

    const isChat = location.pathname.startsWith('/chat') || location.pathname === '/'

    const changeLanguage = () => {
        i18n.changeLanguage(currLang === 'zh' ? 'en' : 'zh')
    }

    const changePage = () => {
        navigate(isChat ? '/knowledgeBase' : '/chat')
    }

    return (
        <Header className={styles["app-header"]}>
            <div className={styles["app-header__logo"]}>
                {t("system.name")}
            </div>
            <div style={{ flex: 1 }}></div>
            <Tooltip content={t("system.language")} placement="bottom">
                <Button
                    variant="text"
                    shape="square"
                    onClick={changeLanguage}
                >
                    {currLang === 'zh' ? 'EN' : '中'}
                </Button>
            </Tooltip>
            <Tooltip content={isChat ? t("system.knowledge") : t("system.chat")} placement="bottom">
                <Button
                    variant="text"
                    shape="square"
                    icon={isChat ? <FolderOpenIcon size="20px" /> : <ChatIcon size="20px" />}
                    onClick={changePage}
                />
            </Tooltip>
        </Header>
    )
}

export default Header
