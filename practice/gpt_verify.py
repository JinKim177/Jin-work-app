"""
GPT 기반 문서 검증 (cross-review 스킬의 1단계)

주어진 텍스트 파일을 "사실·논리·누락·톤/형식" 4가지 기준으로 GPT가 검토해서
같은 폴더에 "<파일명>-gpt-review.md"로 저장한다. 원문은 수정하지 않는다.

사용법:
    python gpt_verify.py <검증할 파일 경로>

준비:
    이 파일과 같은 practice/ 폴더의 .env에 OPENAI_API_KEY=sk-... 가 설정되어 있어야 한다.
"""

import os
import sys
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI

MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """너는 문서를 검수하는 깐깐한 검토자다.
아래 4가지 기준으로만 문제점을 짚어라. 각 기준은 마크다운 소제목(##)으로 구분한다.

- 사실: 숫자·이름·날짜·인용 중 근거 없이 지어낸 것으로 의심되는 부분
- 논리: 주장과 근거가 맞지 않는 부분
- 누락: 꼭 있어야 하는데 빠진 내용
- 톤·형식: 받는 사람 기준으로 어색하거나 부적절한 부분

규칙:
- 원문을 다시 쓰거나 고쳐 쓰지 않는다. 지적만 한다.
- 각 지적은 "- 문장/부분: ... / 문제: ..." 형식의 불릿으로, 어느 문장(또는 어느 항목)인지와 왜 문제인지를 짧게 적는다.
- 해당 기준에서 지적할 게 없으면 "- 특이사항 없음"이라고만 적는다.
- 확인할 수 없는 것을 사실이라고 지어내지 않는다. 텍스트 자체의 내적 일관성과 문서로서의 완성도만 가지고 판단한다."""


def verify_file(target_path: str) -> str:
    """target_path 파일을 GPT로 검증해서 리뷰 파일을 만들고, 그 경로를 돌려준다."""
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY가 설정되어 있지 않습니다. "
            "practice/.env에 OPENAI_API_KEY=sk-... 를 넣은 뒤 다시 실행하세요."
        )

    with open(target_path, "r", encoding="utf-8") as f:
        content = f.read()

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": content},
        ],
    )
    review_body = response.choices[0].message.content.strip()

    base = os.path.splitext(os.path.basename(target_path))[0]
    out_dir = os.path.dirname(os.path.abspath(target_path))
    out_path = os.path.join(out_dir, f"{base}-gpt-review.md")

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    header = (
        f"# GPT 검증 결과 — {os.path.basename(target_path)}\n\n"
        f"검증일시: {now}\n검증 모델: {MODEL}\n\n---\n\n"
    )
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(header + review_body + "\n")

    return out_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python gpt_verify.py <검증할 파일 경로>")
        sys.exit(1)

    saved_path = verify_file(sys.argv[1])
    print(f"저장 완료: {saved_path}")
