---
name: weekly-summary
description: Read weekly data files (current period and previous period) and produce a summary draft with a 3-line summary, what changed vs. the previous period, and a list of issues to watch. Use when the user asks for a weekly summary/recap from provided data files.
---

# Weekly Summary

주간 데이터를 읽어 정리 초안을 만드는 스킬.

## 입력

그때그때 사용자가 주는 주간 데이터 파일들 (이번 회차 파일, 지난 회차 파일). 파일 형식은 다양할 수 있음(텍스트, 표, 문서 등).

## 순서

1. 사용자가 준 데이터 파일들을 읽는다.
2. 핵심 내용을 세 줄로 요약하고, 지난 회차 대비 달라진 점을 한 줄 덧붙인다.
3. 챙겨야 할 이슈를 목록으로 정리한다.
4. 결과를 파일 하나로 저장한다.

## 출력

다음 세 부분을 포함한 정리 파일 하나:
- 핵심 요약 (3줄)
- 지난 회차 대비 달라진 점 (1줄)
- 챙길 이슈 목록

## 조건

- 준 자료에 없는 내용은 지어내지 않는다. 데이터에서 근거를 찾을 수 없으면 추측하지 말고 생략하거나 "자료에서 확인 안 됨"으로 표시한다.
- 이번 회차 데이터만 있고 지난 회차 데이터가 없으면, "달라진 점"은 비교 불가로 명시한다.
