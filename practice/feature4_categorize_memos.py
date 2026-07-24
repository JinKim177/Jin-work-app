"""
Feature 4: 메모 자동 카테고리 분류 (GPT API)

memos/ 폴더의 메모(.md)들을 읽어, 각 메모에 어울리는 카테고리를 GPT가 붙여서
"파일명 -> 카테고리" 형태로 보여준다. 메모 파일 자체는 수정하지 않는다.

사용법:
    python feature4_categorize_memos.py

준비:
    feature3_generate_image.py와 동일하게, 같은 practice/ 폴더의 .env에
    OPENAI_API_KEY=sk-... 가 설정되어 있어야 한다.
"""

import glob
import os

from dotenv import load_dotenv
from openai import OpenAI

MEMOS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "memos")
MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = (
    "다음은 회사 업무 메모입니다. 이 메모에 가장 어울리는 카테고리를 "
    "한 단어~짧은 구(2~6자 내외, 예: 회의록, 고객 문의, 지출 내역, 채용, "
    "장애 보고, 마케팅 아이디어)로 답하세요. 카테고리만 답하고 다른 설명은 붙이지 마세요."
)


def load_memos() -> list[tuple[str, str]]:
    """memos/ 폴더의 .md 파일들을 (파일명, 내용) 목록으로 읽어온다."""
    paths = sorted(glob.glob(os.path.join(MEMOS_DIR, "*.md")))
    memos = []
    for path in paths:
        with open(path, "r", encoding="utf-8") as f:
            memos.append((os.path.basename(path), f.read()))
    return memos


def categorize(client: OpenAI, content: str) -> str:
    """메모 내용을 GPT에 보내 어울리는 카테고리 한 개를 받아온다."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": content},
        ],
        max_tokens=20,
    )
    return response.choices[0].message.content.strip()


def categorize_memos() -> list[tuple[str, str]]:
    """모든 메모에 카테고리를 붙여 (파일명, 카테고리) 목록을 돌려준다."""
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY가 설정되어 있지 않습니다. "
            "프로젝트 루트 .env에 OPENAI_API_KEY=sk-... 를 넣은 뒤 다시 실행하세요."
        )

    client = OpenAI(api_key=api_key)

    memos = load_memos()
    if not memos:
        return []

    results = []
    for filename, content in memos:
        category = categorize(client, content)
        results.append((filename, category))
    return results


if __name__ == "__main__":
    results = categorize_memos()
    if not results:
        print(f"memos/ 폴더에 .md 메모가 없습니다. ({MEMOS_DIR})")
    else:
        print("[메모 카테고리 분류 결과]")
        for filename, category in results:
            print(f"- {filename} -> {category}")
