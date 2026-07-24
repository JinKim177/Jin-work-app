---
name: todos
description: Extract to-do items from memos already sorted into organized/todo/ and show them as a single "오늘 할 일" list grouped by memo. Use when the user wants today's to-dos pulled together from already-categorized memo files.
---

# todos

`practice/organized/todo/` 폴더의 할 일 메모들에서 할 일 항목만 뽑아 "오늘 할 일" 목록으로 보여주는 스킬.

## 무엇을

`practice/feature6_extract_todos.py`의 `extract_todays_todos()`를 호출해서, 이미 "todo"로 분류된 메모들에서 할 일 항목만 뽑아 하나의 목록으로 합친다. (근태 앱과 무관한 실험 스크립트라 `practice/`로 옮겨져 있다.)

## 입력

- `practice/organized/todo/` 폴더 안의 `.md` 파일들 (제목은 `# 할 일 - ...`, 항목은 `- ...` 형식)

## 순서

1. PowerShell로 (프로젝트 루트에서) `python practice/feature6_extract_todos.py`를 실행한다.
2. `practice/organized/todo/` 폴더의 `.md` 파일을 모두 읽는다.
3. 각 메모에서 제목과 `- `로 시작하는 할 일 항목만 뽑아낸다.
4. 메모별로 묶어 `[오늘 할 일]` 목록 텍스트를 만든다.

## 출력

- 메모별로 묶인 "오늘 할 일" 목록 텍스트 (할 일이 없는 메모는 건너뜀)
