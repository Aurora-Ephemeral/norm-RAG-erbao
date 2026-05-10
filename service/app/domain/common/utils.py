def count_tokens(text: str) -> int:
    chinese = sum(1 for c in text if '一' <= c <= '鿿')
    others = len(text) - chinese
    return int((chinese / 1.5 + others / 3.5) * 1.1)
