"""국가법령정보센터(law.go.kr) Open API 클라이언트.

- 목록 API(lawSearch.do): 법령명으로 검색
- 본문 API(lawService.do): 법령일련번호(MST)로 조문 전체 조회
- 인증값 OC는 환경변수(.env)에서 읽는다.
"""

import os
import json
import urllib.request
import urllib.parse

BASE_URL = "http://www.law.go.kr/DRF/"


def _request(endpoint, **params):
    """공통 요청 함수. 항상 JSON 타입으로 호출하고 dict로 파싱해 반환."""
    oc = os.getenv("OC")
    if not oc:
        raise RuntimeError("환경변수 OC가 설정되지 않았습니다. .env를 확인하세요.")

    query = urllib.parse.urlencode({"OC": oc, "type": "JSON", **params})
    url = f"{BASE_URL}{endpoint}?{query}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read()
    # 응답은 UTF-8 JSON
    return json.loads(raw.decode("utf-8"))


def search_laws(query, display=20, page=1):
    """법령명으로 검색 → 법령 목록(dict 리스트) 반환.

    결과가 1건이면 API가 dict 하나로 주므로 리스트로 정규화한다.
    """
    data = _request("lawSearch.do", target="law", query=query, display=display, page=page)
    laws = data.get("LawSearch", {}).get("law", [])
    if isinstance(laws, dict):
        laws = [laws]
    return laws


def get_law_body(mst):
    """법령일련번호(MST)로 본문 전체(dict) 반환.

    반환 dict 안에 '조문' -> '조문단위'(조 목록)와 '기본정보'가 들어있다.
    """
    data = _request("lawService.do", target="law", MST=mst)
    return data.get("법령", data)
