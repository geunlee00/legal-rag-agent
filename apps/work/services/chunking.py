"""편람 페이지들을 토큰 크기 기반 + 겹침(overlap)으로 청킹한다.

★ 이 파일의 chunk_pages()는 직접 구현합니다. (핵심)

입력  : load_pages() 결과 [{"page", "chapter", "text"}, ...]
출력  : [{"chapter", "section", "page", "content"}, ...]

아이디어:
    - 페이지 텍스트를 줄(line) 단위로 펼치되 각 줄의 page/chapter를 기억
    - 줄을 max_tokens까지 모아 한 청크로 만들고, 다음 청크는 몇 줄 겹쳐 시작
    - 청크의 page/chapter = 그 청크가 시작된 줄의 값
"""


def chunk_pages(pages, max_tokens=400, overlap_lines=2):
    raise NotImplementedError("chunk_pages를 직접 구현하세요 (아래 안내 참고)")
