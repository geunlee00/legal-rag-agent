"""OpenAI 임베딩 서비스.

- 모델: text-embedding-3-small (1536차원)
- 입력이 모델 최대 토큰(8191)을 넘으면 안전하게 잘라서 요청한다.
- OPENAI_API_KEY는 환경변수(.env)에서 자동으로 읽힌다.
"""

import tiktoken
from openai import OpenAI

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536
MAX_TOKENS = 8000  # 모델 한도(8191)보다 여유 있게

_client = None
_encoder = tiktoken.get_encoding("cl100k_base")


def get_client():
    """OpenAI 클라이언트 싱글턴."""
    global _client
    if _client is None:
        _client = OpenAI()  # OPENAI_API_KEY 자동 사용
    return _client


def _truncate(text):
    """토큰 한도를 넘으면 잘라낸다(드문 초장문 조문 대비)."""
    tokens = _encoder.encode(text)
    if len(tokens) > MAX_TOKENS:
        return _encoder.decode(tokens[:MAX_TOKENS])
    return text


def embed_texts(texts):
    """문자열 리스트 → 임베딩 벡터(list[float]) 리스트. 순서 보존."""
    safe = [_truncate(t) for t in texts]
    resp = get_client().embeddings.create(model=EMBEDDING_MODEL, input=safe)
    return [d.embedding for d in resp.data]
