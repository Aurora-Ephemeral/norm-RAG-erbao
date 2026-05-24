import System from './system';
import Chat from './chat';
import knowLedgeBase from './knowledge'

export default {
    ...System,
    ...Chat,
    ...knowLedgeBase
}