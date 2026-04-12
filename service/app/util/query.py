import re
from typing import Dict, List
from langchain_community.embeddings import DashScopeEmbeddings
import numpy as np

CATE_RULES: Dict[str, List[str]] = {
    "板材": [
        "板材", "钢板", "钢带", "冷轧", "热镀锌", "拉伸", "屈服", "抗拉强度",
        "延伸率", "冲压", "深冲", "sheet", "steel", "Blech", "Stahl",
    ],
    "螺栓": [
        "螺栓", "紧固件", "螺钉", "螺母", "扭矩", "预紧力", "强度等级",
        "bolt", "fastener", "screw", "nut", "Schraube", "Drehmoment",
    ],
    "表面防护": [
        "表面防护", "表防", "镀铬", "镀锌", "镀镍", "阳极氧化", "电镀",
        "盐雾", "腐蚀", "防腐", "镀层", "涂层厚度", "膜厚",
        "CASS", "NSS", "铜加速", "中性盐雾",
        "附着力", "网格切割", "划格", "热冲击", "冷凝水",
        "铝合金", "锌合金", "镁合金", "铜合金", "不锈钢",
        "PV1210", "PV1209",
        "Korrosion", "Salzsprüh", "Beschichtung",
    ],
    "涂装": [
        "涂装", "喷涂", "油漆", "涂料", "漆膜", "底漆", "面漆", "清漆",
        "光泽", "色差", "硬度", "铅笔硬度",
        "paint", "coating", "lacquer", "Lack", "Beschichtung",
    ],
}

_STD_RE = re.compile(
    r"(VW\s?\d{4,6}(?:-\d+)?|TL\s?\d{2,4}|PV\s?\d{3,5}"
    r"|DIN\s*EN\s*ISO\s*\d{3,6}(?:-\d+)?|DIN\s*EN\s*\d{3,6})",
    re.IGNORECASE,
)


class IntentRouter:
    def __init__(self, threshold = 0.5):
        self.threshold = threshold
        self.embeddings = DashScopeEmbeddings()
        self.cat_centroids = {}
        self._init_centroids()

    def _init_centroids(self):
        for cat, items in CATE_RULES.items():
            vectors = self.embeddings.embed_documents(items)
            self.cat_centroids[cat] = vectors
    @staticmethod
    def cos_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def predict(self, query: str) -> Dict[str, List[str]]:
        final_cat = []
        final_norms = []
        # rule-based:
        for m in _STD_RE.finditer(query):
            sid = re.sub(r"\s+", "", m.group(0)).upper()
            if sid not in final_norms:
                final_norms.append(sid)

        for cat, kws in CATE_RULES.items():
            if any(k.lower() in query.lower() for k in kws):
                final_cat.append(cat)
        # semantic comparing for category
        if len(final_cat) == 0:
            query_vector = self.embeddings.embed_query(query)
            scores = {
                cat: max([self.cos_similarity(item, query_vector) for item in item_vectors]) for cat, item_vectors in self.cat_centroids.items()
            }
            cat_over_threshold = {k:v for k, v in scores.items() if v > self.threshold}
            if len(cat_over_threshold) > 0:
               final_cat = cat_over_threshold.keys()

        return {"category": final_cat, "norms": final_norms}



