from langchain.prompts import FewShotChatMessagePromptTemplate, ChatPromptTemplate

from app.data import FEW_SHOT_EXAMPLES

_SYSTEM_INSTRUCTION = """\
你是一名专业的汽车零部件质保标准分析助手。
你的用户是一线质保检验人员，需要准确的 DIN / VW / TL 标准信息来指导日常工作。

知识覆盖四大零件类别：板材、螺栓、表面防护、涂装。

下方提供的标准文档分为两部分：
- [主要来源]：与用户问题直接相关的标准内容
- [引用参考]：主要来源中引用的其他标准的补充内容

规则：
1.【依据标准】回答必须基于下方提供的标准文档内容；末尾标注来源（标准号 + 页码）
2.【精确数值】厚度/时间/温度/浓度等参数给精确值，关键数值 **加粗**
3.【拒答边界】文档中无相关内容时，明确说明"所提供的标准文档中未涉及"，不编造
4.【引用整合】如果 [引用参考] 中有与问题相关的补充信息（如被引用标准的具体测试方法、判定标准），应整合到回答中，并注明"根据其引用的 XXX 标准"
5.【实操导向】回答应包含设备要求、测试条件、判定标准等可直接用于检验的信息
"""

def build_few_shot_prompt_template() -> ChatPromptTemplate:
    # 1. format few shot template
    example_prompt = ChatPromptTemplate.from_messages([
        ("human", "合同内容：\n{context}\n\n问题：{question}"),
        ("ai", "{answer}")
    ])
    few_shot_block = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=FEW_SHOT_EXAMPLES
    )

    # 2. build complete prompt
    return ChatPromptTemplate.from_messages([
        ("system", _SYSTEM_INSTRUCTION),
        few_shot_block,
        ("human", "合同内容：\n{context}\n\n问题：{question}")
    ])
