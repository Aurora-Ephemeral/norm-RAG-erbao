import System from './system';
import Common from './common';
import Chat from './chat';
import knowLedgeBase from './knowledge'

export default {
    ...Common,
    ...System,
    ...Chat,
    ...knowLedgeBase
}