import { configureStore } from '@reduxjs/toolkit'
import counterReducer from './counterSlice'
import chatReducer from './chatSlice'

export const store = configureStore({
  reducer: {
    counter: counterReducer,
    chat: chatReducer,
  },
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
