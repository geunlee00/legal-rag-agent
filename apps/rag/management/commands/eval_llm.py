"""리랭커 전/후 검색 품질을 LLM 평가로 비교한다.

사용 예:
    python manage.py eval_llm            # 전체 질문
    python manage.py eval_llm --n 3      # 앞 3개만 (빠른 확인)

측정:
    - context precision: baseline(하이브리드만) vs rerank(리랭커 적용)
    - faithfulness     : rerank 파이프라인 최종 답변 기준
"""

from django.core.management.base import BaseCommand

from apps.rag.eval.questions import EVAL_QUESTIONS
from apps.rag.eval.metrics import context_precision, faithfulness
from apps.rag.services.hybrid import hybrid_search
from apps.rag.services.rerank import rerank
from apps.rag.services.rag import SYSTEM_PROMPT
from apps.rag.services.embedding import get_client


def _to_contexts(docs):
    return [f"{d.law.name} {d.article_no} {d.article_title}\n{d.content}" for d in docs]


def _baseline_contexts(q):
    return _to_contexts(hybrid_search(q, k=5))                      # 리랭커 없이 RRF top-5


def _rerank_contexts(q):
    cands = hybrid_search(q, k=15, candidates=30)
    return _to_contexts(rerank(q, cands, top_k=5))                  # 후보 → 리랭커 top-5


def _generate(q, contexts):
    ctx = "\n\n".join(contexts)
    resp = get_client().chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"참고 조문:\n{ctx}\n\n질문: {q}"},
        ],
        temperature=0,
    )
    return resp.choices[0].message.content


class Command(BaseCommand):
    help = "리랭커 전/후 context precision + faithfulness 비교 (LLM 평가)"

    def add_arguments(self, parser):
        parser.add_argument("--n", type=int, default=len(EVAL_QUESTIONS), help="평가할 질문 수")

    def handle(self, *args, **options):
        questions = EVAL_QUESTIONS[: options["n"]]
        base_cp, rr_cp, faith = [], [], []

        self.stdout.write("질문별 context precision (base → rerank) / faithfulness\n")
        for i, q in enumerate(questions, 1):
            b_ctx = _baseline_contexts(q)
            r_ctx = _rerank_contexts(q)

            cp_b = context_precision(q, b_ctx)
            cp_r = context_precision(q, r_ctx)
            answer = _generate(q, r_ctx)
            f = faithfulness(q, answer, r_ctx)

            base_cp.append(cp_b)
            rr_cp.append(cp_r)
            faith.append(f)
            self.stdout.write(f"[{i:>2}] {cp_b:.2f} → {cp_r:.2f}  | faith {f:.2f} | {q[:28]}")

        def avg(xs):
            return sum(xs) / len(xs) if xs else 0.0

        self.stdout.write("\n===== 평균 =====")
        self.stdout.write(f"context precision (baseline): {avg(base_cp):.3f}")
        self.stdout.write(f"context precision (rerank)  : {avg(rr_cp):.3f}")
        self.stdout.write(f"faithfulness (rerank)       : {avg(faith):.3f}")
