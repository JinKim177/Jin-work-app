---
name: mascot
description: Generate 2 AI images from a short text description using OpenAI's image API (gpt-image-1) and save them as PNG files in images/ with an English filename. Use when the user wants an AI-generated image, illustration, or mascot created and saved to the project.
---

# mascot

짧은 설명을 받아 OpenAI 이미지 생성 API로 이미지 2장을 만들어 `images/` 폴더에 저장하는 스킬.

## 무엇을

`practice/feature3_generate_image.py`의 `generate_image(prompt)`를 호출해서, 설명 텍스트로 이미지 2장을 만들고 저장한다. (근태 앱과 무관한 실험 스크립트라 `practice/`로 옮겨져 있다.)

## 입력

- 이미지 설명 텍스트 (예: "내 서비스 마스코트 - 물방울 모양 귀여운 캐릭터")
- `practice/.env`의 `OPENAI_API_KEY`

## 순서

1. PowerShell로 (프로젝트 루트에서) `python practice/feature3_generate_image.py "설명 텍스트"`를 실행한다.
2. 내부적으로 OpenAI 이미지 생성 API(`gpt-image-1`)를 호출해 이미지 2장을 만든다.
3. 설명을 GPT(`gpt-4o-mini`)로 짧은 영어 슬러그로 바꾼다 (파일명용, 실패 시 영문/숫자만 남기는 방식으로 대체).
4. `practice/images/` 폴더(없으면 자동 생성)에 `슬러그-날짜-번호.png` 형식으로 두 장을 저장한다.

## 출력

- `practice/images/`에 저장된 이미지 파일 경로 2개

## 주의

- API 키가 없으면 호출 전에 에러 메시지로 안내하고 멈춘다 (비용 발생 없음).
- 실행마다 이미지 생성 + 슬러그 변환용 텍스트 호출까지 비용이 발생한다.
