"""BM25 키워드 검색 (하이브리드 검색의 sparse 파트).

- kiwipiepy 형태소 분석으로 한국어를 토큰화 (조사·어미 제거, 명사 중심)
- rank_bm25로 BM25 점수 계산
- 코퍼스(589조문)가 작아 인메모리 인덱스를 지연 생성해 캐싱한다.
  (데이터가 바뀌면 프로세스 재시작 또는 rebuild() 호출)
"""

from kiwipiepy import Kiwi
from rank_bm25 import BM25Okapi

from apps.rag.models import LawChunk

_kiwi = Kiwi()
# 키워드로 의미 있는 품사만: 일반명사·고유명사·외래어(CCTV 등)·숫자·한자
_KEEP_TAGS = ("NNG", "NNP", "SL", "SN", "SH")


def tokenize(text):
    return [t.form for t in _kiwi.tokenize(text) if t.tag in _KEEP_TAGS]


class _BM25Index:
    def __init__(self):
        self.ids = []
        self.bm25 = None

    def build(self):
        rows = list(LawChunk.objects.values_list("id", "content"))
        self.ids = [r[0] for r in rows]
        corpus = [tokenize(r[1]) for r in rows]
        self.bm25 = BM25Okapi(corpus)

    def search(self, query, k):
        if self.bm25 is None:
            self.build()
        scores = self.bm25.get_scores(tokenize(query))
        ranked = sorted(zip(self.ids, scores), key=lambda x: x[1], reverse=True)
        return ranked[:k]


_index = _BM25Index()


def rebuild():
    """데이터 변경 후 인덱스를 다시 만든다."""
    _index.build()


def search_keyword_ids(query, k=20):
    """BM25 상위 k개 chunk id를 점수 내림차순으로 반환 (점수>0만)."""
    return [cid for cid, score in _index.search(query, k) if score > 0]
