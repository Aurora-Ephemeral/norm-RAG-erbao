export default {
    chat: {
        sidebar: {
            title: '历史会话',
            newChat: '新建对话',
            empty: '暂无历史会话',
        },
        input: {
            placeholder: '请输入消息...',
        },
        error: {
            fetchList: '获取会话列表失败',
            fetchDetail: '获取会话详情失败',
            create: '创建会话失败',
            send: '发送失败',
        },
        welcome: {
            line1: '你好，我是智能标准问答助手',
            line2: '可以帮你查询工业标准、技术规范和产品参数',
            modes: {
                simple: {
                    label: '简单问答',
                    desc: '直接匹配文档内容，适用于精确查询、参数查找等单一问题',
                },
                complex: {
                    label: '复杂回答',
                    desc: '启动 Agent 跨文档分析，适用于对比研究、多步骤推理等复杂任务',
                },
            },
        },
    },
}
