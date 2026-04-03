import { Provider } from "react-redux"
import { RouterProvider } from "react-router-dom"
import { store } from '@/store'
import { router } from '@/router'

const App: React.FC = () => {
    return (
        <Provider store={store}>
            <RouterProvider router={router} />
        </Provider>
    )
}

export default App;