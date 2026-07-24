---
name: attendance-auto
description: Check whether today's automatic attendance report conditions are met (weekday, past 08:00, not already run today) and if so, auto-generate the attendance summary and save it to outputs/ without human confirmation. Use for the scheduled/unattended daily run check (feature5), not for a normal manual report request.
---

# attendance-auto

평일 08:00 자동 실행 조건을 판단해서, 조건을 만족하면 근태 요약을 사람 확인 없이 자동으로 만들어 파일로 저장하는 스킬.

## 무엇을

`auto_run_check.py`를 실행해서, "오늘 이미 실행됐는지 / 평일인지 / 08:00이 지났는지"를 확인하고, 모두 만족하면 근태 요약을 자동 생성해 파일로 저장한다.

## 입력

- 근태 엑셀 파일들이 있는 폴더 경로 (기본값: `inputs/`)
- 실행 상태 파일: `last_run.txt` (마지막 실행 날짜만 기록)

## 순서

1. PowerShell로 `python auto_run_check.py [폴더 경로]`를 실행한다.
2. 스크립트 내부에서 순서대로 확인한다: 주말이면 종료 → 오늘 이미 실행 기록 있으면 종료 → 08:00 이전이면 종료 → 오늘 파일 없으면 안내만 하고 종료.
3. 모든 조건을 만족하면 근태 요약 텍스트를 만들어 `outputs/today-summary-YYYYMMDD.txt`로 저장하고, `last_run.txt`에 오늘 날짜를 기록한다.

## 출력

- 조건 미충족: 상태 안내 메시지만 출력 (파일 생성 없음)
- 조건 충족: `outputs/today-summary-YYYYMMDD.txt`에 저장된 근태 요약 텍스트 (사람 확인 절차는 생략됨 — 나중에 사람이 파일을 열어 직접 확인해야 함)
