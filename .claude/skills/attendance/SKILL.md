---
name: attendance
description: Find today's attendance excel file in inputs/, generate a leader/member attendance summary report text (feature1+2), and get human y/n confirmation (feature4) before showing the final KakaoTalk-ready text. Use when the user asks to generate or check today's daily attendance report.
---

# attendance

오늘 날짜의 근태 엑셀 파일을 자동으로 찾아 요약 보고 텍스트를 만들고, 사람의 y/n 확인을 거쳐 최종 텍스트를 보여주는 스킬.

## 무엇을

`run_today_attendance_summary.py`를 실행해서, 오늘 날짜의 근태 엑셀 파일을 찾고 → 팀장근태/팀원근태 요약 텍스트를 만들고 → 사람 확인(y/n)까지 마친 최종 결과를 보여준다.

## 입력

- 근태 엑셀 파일들이 있는 폴더 경로 (기본값: `inputs/`)
- 파일명 패턴: `ERP-일일근태현황(MM.DD).xlsx`

## 순서

1. PowerShell로 `python run_today_attendance_summary.py [폴더 경로]`를 실행한다 (폴더 경로 생략 시 `inputs/`).
2. 오늘 날짜와 일치하는 파일을 찾으면, "1. 근태요약 / 2. 팀장근태 / 3. 팀원근태" 형식의 텍스트가 보이고 y/n 입력을 요구한다.
3. 사용자가 승인(y)하면 최종 텍스트를 그대로 보여주고, `last_run.txt`에 오늘 날짜가 기록된다.
4. 거부(n)하면 "승인되지 않았습니다" 안내만 보여준다.

## 출력

- 오늘 파일을 찾은 경우: 카톡에 그대로 붙여넣을 수 있는 최종 근태 요약 텍스트
- 오늘 파일이 없는 경우: "아직 찾지 못했습니다" 안내 메시지
