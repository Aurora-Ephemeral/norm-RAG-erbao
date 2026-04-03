import { Layout, Tooltip, Button } from "tdesign-react"
import { useTranslation } from "react-i18next"
import { ChatIcon, FolderOpenIcon } from 'tdesign-icons-react';
import styles from './style.module.scss'
import { useState } from "react";

const Header: React.FC = () => {

    const { Header } = Layout
    const { t, i18n } = useTranslation()
    const currLang:String = i18n.language

    const [ currPage, setCurrPage ] = useState('chat')

    const changeLanguage = () => {
        if(currLang === 'zh') {
            i18n.changeLanguage('en')
        } else {
            i18n.changeLanguage('zh')
        }
    }

    const changePage = () => {
        //TODO: add navigation logic 
        if(currPage === 'chat') {
            setCurrPage('knowledge')
        } else {
            setCurrPage('chat')
        }
    }
    return (
        <Header className={styles["app-header"]}>
            <div className={styles["app-header__logo"]}>
                { t("system.name")}
            </div>
            <div style={{flex: 1}}></div>
            <Tooltip content={t("system.language")} placement="bottom">
                <Button 
                    variant="text"
                    shape="square"
                    onClick={changeLanguage}
                >
                    {currLang == 'zh' ? 'EN' : '中'}
                </Button>
            </Tooltip>
            <Tooltip content={currPage == 'chat' ? t("system.chat") : t("system.knowledge")} placement="bottom">
                <Button 
                    variant="text"
                    shape="square"
                    icon={currPage == 'chat' ?  <FolderOpenIcon size="20px"/> : <ChatIcon size="20px"/>}
                    onClick={changePage}
                >
                </Button>
            </Tooltip>
        </Header>
        
    )
}

export default Header