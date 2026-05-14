import { createSlice, type PayloadAction } from '@reduxjs/toolkit'

interface ChatState {
    activeConvId: string
}

const initialState: ChatState = {
    activeConvId: '',
}

export const chatSlice = createSlice({
    name: 'chat',
    initialState,
    reducers: {
        setActiveConvId: (state, action: PayloadAction<string>) => {
            state.activeConvId = action.payload
        },
    },
})


export const { setActiveConvId } = chatSlice.actions
export default chatSlice.reducer