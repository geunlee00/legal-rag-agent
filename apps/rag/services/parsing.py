"""법령 본문(JSON)을 조(條) 단위 청크로 변환하는 핵심 로직.

★ 이 파일의 parse_articles()는 당신이 직접 구현합니다. (1-b의 핵심)

입력  : law_api.get_law_body(mst) 결과 dict
        - body["조문"]["조문단위"] 에 조(條) 목록이 들어있음
        - 각 조: {"조문번호", "조문제목", "조문내용", "조문여부", "항": {...}}
        - "항" 아래에 "호"[], "목"[] 이 중첩될 수 있음

출력  : 조 하나당 딕셔너리 하나의 리스트
        [{"article_no": "제2조", "article_title": "정의", "content": "..."}, ...]
"""

import re

def _as_text(value):
    """문자열이면 그대로, 리스트면 줄바꿈으로 합쳐 문자열로 정규화."""
    if isinstance(value, list):
        return "\n".join(_as_text(v) for v in value)
    return value or ""

def _collect_texts(node):
    """항/호/목처럼 중첩된 구조에서 텍스트만 순서대로 뽑아 리스트로 반환."""
    texts = []
    if isinstance(node, dict):
        # 이 노드가 직접 가진 내용
        for key in ("항내용", "호내용", "목내용"):
            if node.get(key):
                texts.append(_as_text(node[key]))
        # 하위로 재귀
        for key in ("항", "호", "목"):
            if key in node:
                texts.extend(_collect_texts(node[key]))
    elif isinstance(node, list):
        for item in node:
            texts.extend(_collect_texts(item))
    return texts


def parse_articles(body):
    units = body.get("조문", {}).get("조문단위", [])
    if isinstance(units, dict):        # 조가 1개면 dict로 옴 → 리스트로
        units = [units]

    articles = []
    for u in units:
        if u.get("조문여부") != "조문":   # 장/절 제목 등은 제외
            continue

        head = _as_text(u.get("조문내용")).strip()
        # "제2조(정의) ..." 앞부분에서 '제N조' 또는 '제N조의M' 추출
        m = re.match(r"(제\d+조(?:의\d+)?)", head)
        article_no = m.group(1) if m else ""
        title = _as_text(u.get("조문제목")).strip()

        texts = [head] + _collect_texts(u.get("항", {}))
        content = "\n".join(t.strip() for t in texts if t and t.strip())

        articles.append({
            "article_no": article_no,
            "article_title": title,
            "content": content,
        })
    return articles