"""편람 PDF에서 페이지별 텍스트를 뽑고 노이즈를 정리한다.

편람 PDF의 특성(정리 대상):
- 페이지 상단에 장 제목이 머리말로 반복  (예: "제2장. 공문서 관리 등 행정업무의 처리")
- 세로 사이드바 탭이 한 글자씩 끼어듦     (예: "공" "문" "서")
- 하단에 페이지 번호
- (cid:NNNN) 같은 폰트 깨짐 아티팩트

반환: [{"page": 인쇄페이지, "chapter": 현재 장, "text": 정리된 본문}, ...]
      (본문이 비어있는 페이지는 제외)
"""

import re

import pdfplumber

_CID = re.compile(r"\(cid:\d+\)")
_CHAPTER = re.compile(r"^제\s*\d+\s*장[.\s]")   # 머리말의 장 제목
_SECTION_ONLY = re.compile(r"^제\s*\d+\s*절$")  # 사이드바에 홀로 뜨는 절 표시
_PAGENO_ONLY = re.compile(r"^\d{1,4}$")


def _clean_page(raw):
    """페이지 텍스트에서 (장 제목, 인쇄페이지, 본문)을 분리·정리."""
    raw = _CID.sub("", raw or "")
    lines = [ln.rstrip() for ln in raw.splitlines()]

    chapter = None
    page_no = None
    body = []
    for ln in lines:
        s = ln.strip()
        if not s:
            continue
        if _CHAPTER.match(s):          # 머리말(장 제목) → 메타로만
            chapter = s
            continue
        if _SECTION_ONLY.match(s):     # 사이드바 절 표시 제거
            continue
        if len(s) == 1:                # 세로 사이드바 한 글자 제거
            continue
        if _PAGENO_ONLY.match(s):      # 페이지 번호 → 메타로만
            page_no = int(s)
            continue
        body.append(s)

    return chapter, page_no, "\n".join(body)


def load_pages(path):
    """PDF를 페이지별로 정리해 리스트로 반환. 장 제목은 이후 페이지로 이어짐."""
    pages = []
    current_chapter = ""
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages):
            chapter, page_no, body = _clean_page(page.extract_text() or "")
            if chapter:
                current_chapter = chapter
            body = body.strip()
            if not body:
                continue
            pages.append({
                "page": page_no or (i + 1),   # 인쇄 페이지 없으면 PDF 순번
                "chapter": current_chapter,
                "text": body,
            })
    return pages
