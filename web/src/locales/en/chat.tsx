export default {
    chat: {
        sidebar: {
            title: 'History',
            newChat: 'New Chat',
            empty: 'No conversations yet',
        },
        input: {
            placeholder: 'Type a message...',
        },
        error: {
            fetchList: 'Failed to load conversations',
            fetchDetail: 'Failed to load conversation',
            create: 'Failed to create conversation',
            send: 'Failed to send message',
        },
        welcome: {
            line1: 'Hello, I am your intelligent Q&A assistant',
            line2: 'I can help you query industrial standards, technical specs and product parameters',
            modes: {
                simple: {
                    label: 'Simple Q&A',
                    desc: 'Directly matches document content, suitable for precise queries and parameter lookups',
                },
                complex: {
                    label: 'Complex Answer',
                    desc: 'Launches Agent for cross-document analysis, suitable for comparative research and multi-step reasoning',
                },
            },
        },
    },
}
