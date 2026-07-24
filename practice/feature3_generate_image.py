"""
Feature 3: AI 이미지 생성 (OpenAI 이미지 생성 API)

짧은 설명(prompt)을 받아 이미지를 한 번에 2장 생성하고 images/ 폴더에 png로 저장한다.
파일명은 "영어 설명-날짜-번호.png" 형식이다 (예: cute-mascot-cat-20260723-1.png).

사용법:
    python feature3_generate_image.py "내 서비스 마스코트 - 물방울 모양 귀여운 캐릭터"

준비:
    1) pip install openai python-dotenv  (이미 설치됨)
    2) 이 파일과 같은 practice/ 폴더에 .env 파일을 만들고 아래처럼 키를 넣는다.
         OPENAI_API_KEY=sk-...
       (.env가 없으면 시스템 환경변수 OPENAI_API_KEY를 대신 사용한다)

주의:
    실제 실행 시 OpenAI 이미지 생성 API가 호출되며, 호출마다 비용이 발생한다.
"""

import base64
import os
import re
import sys
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI

IMAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
MODEL = "gpt-image-1"
SIZE = "1024x1024"
NUM_IMAGES = 2
SLUG_MODEL = "gpt-4o-mini"


def slugify_english(text: str) -> str:
    """영어 텍스트를 파일명에 쓸 수 있게 소문자-하이픈 형태로 다듬는다."""
    text = re.sub(r"[^0-9A-Za-z\s-]", "", text)
    text = re.sub(r"\s+", "-", text.strip()).strip("-")
    return text.lower()


def to_english_slug(client: OpenAI, description: str) -> str:
    """설명(어떤 언어든)을 파일명에 쓸 짧은 영어 슬러그로 바꾼다. 실패하면 대체값을 쓴다."""
    try:
        response = client.chat.completions.create(
            model=SLUG_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Translate the user's image description into a short English "
                        "filename slug: 2-5 lowercase words separated by hyphens, "
                        "letters and numbers only, no punctuation. Reply with only the slug."
                    ),
                },
                {"role": "user", "content": description},
            ],
            max_tokens=20,
        )
        slug = slugify_english(response.choices[0].message.content or "")
    except Exception:
        slug = slugify_english(description)

    return (slug or "image")[:40]


def make_filename(slug: str, index: int) -> str:
    """영어 슬러그 + 날짜 + 번호로 파일명을 만든다."""
    date_str = datetime.now().strftime("%Y%m%d")
    return f"{slug}-{date_str}-{index}.png"


def generate_image(prompt: str) -> list[str]:
    """prompt로 이미지를 NUM_IMAGES장 생성해 images/ 폴더에 저장하고, 저장된 파일 경로 목록을 돌려준다."""
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY가 설정되어 있지 않습니다. "
            "프로젝트 루트에 .env 파일을 만들고 OPENAI_API_KEY=sk-... 를 넣거나 "
            "환경변수로 설정한 뒤 다시 실행하세요."
        )

    client = OpenAI(api_key=api_key)

    response = client.images.generate(
        model=MODEL,
        prompt=prompt,
        size=SIZE,
        n=NUM_IMAGES,
    )

    slug = to_english_slug(client, prompt)

    os.makedirs(IMAGES_DIR, exist_ok=True)
    saved_paths = []
    for index, item in enumerate(response.data, start=1):
        image_bytes = base64.b64decode(item.b64_json)
        filename = make_filename(slug, index)
        out_path = os.path.join(IMAGES_DIR, filename)
        with open(out_path, "wb") as f:
            f.write(image_bytes)
        saved_paths.append(out_path)

    return saved_paths


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('사용법: python feature3_generate_image.py "이미지 설명"')
        sys.exit(1)

    description = sys.argv[1]
    saved_paths = generate_image(description)
    for path in saved_paths:
        print(f"이미지 저장 완료: {path}")
