---
name: todos-brief
description: Same as the todos skill, but adds a one-line headline summarizing total to-do count and memo count above the list. Use when the user wants the to-do list together with a quick top-line count summary.
---

# todos-brief

`todos` 스킬 결과 위에, 전체 할 일 건수와 메모 건수를 담은 한 줄 요약을 덧붙이는 스킬.

## 무엇을

`practice/feature7_todos_with_headline.py`의 `generate_todos_with_headline()`을 호출해서, `practice/organized/todo/` 메모의 할 일 목록 위에 한 줄 요약을 붙인다. (근태 앱과 무관한 실험 스크립트라 `practice/`로 옮겨져 있다.)

## 입력

- `practice/organized/todo/` 폴더 안의 `.md` 파일들

## 순서

1. PowerShell로 (프로젝트 루트에서) `python practice/feature7_todos_with_headline.py`를 실행한다.
2. `practice/organized/todo/` 폴더의 메모들을 읽는다.
3. 전체 할 일 항목 수와 메모 건수를 세어 `[한 줄 요약] 오늘 할 일 총 N건 (메모 M건)` 형식의 한 줄을 만든다.
4. 그 아래에 `todos` 스킬과 동일한 "오늘 할 일" 목록을 이어 붙인다.

## 출력

- 한 줄 요약 + "오늘 할 일" 목록 텍스트
