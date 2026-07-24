---
name: categorize
description: Read all memos in memos/ and use GPT to assign a category label to each one, showing "filename -> category" results. Use when the user wants memos automatically classified or tagged by topic.
---

# categorize

`memos/` 폴더의 메모(.md)들을 읽어, GPT로 각 메모에 어울리는 카테고리를 붙여 보여주는 스킬.

## 무엇을

`practice/feature4_categorize_memos.py`의 `categorize_memos()`를 호출해서, `practice/memos/` 안의 모든 메모에 카테고리를 붙인다. 메모 파일 자체는 수정하지 않는다. (근태 앱과 무관한 실험 스크립트라 `practice/`로 옮겨져 있다.)

## 입력

- `practice/memos/` 폴더 안의 `.md` 파일들
- `practice/.env`의 `OPENAI_API_KEY`

## 순서

1. PowerShell로 (프로젝트 루트에서) `python practice/feature4_categorize_memos.py`를 실행한다.
2. `practice/memos/` 폴더의 `.md` 파일을 모두 읽는다.
3. 각 메모 내용을 GPT(`gpt-4o-mini`)에 보내 어울리는 카테고리 하나(짧은 단어~구)를 받는다.
4. "파일명 -> 카테고리" 형태로 결과를 정리해서 보여준다.

## 출력

- 메모별 "파일명 -> 카테고리" 목록

## 주의

- 메모 개수만큼 GPT 호출이 발생해 비용이 든다.
