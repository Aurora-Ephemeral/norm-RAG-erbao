import { Outlet } from "react-router-dom"
import Header from "./Header"

import styles from './style.module.scss'

const Layout: React.FC = () => {

    return (
        <div className={styles['app-layout']}>
            <Header />
            <div className={styles['app-layout__body']}>
                <main className={styles['app-layout__content']}>
                    <Outlet />
                </main>
            </div>
        </div>
    )
}

export default Layout