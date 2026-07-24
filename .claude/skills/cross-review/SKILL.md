---
name: cross-review
description: Cross-verify a given text file against 4 criteria (fact, logic, omission, tone/format) — first via GPT API (saved to a "<filename>-gpt-review.md" file), then independently by Claude without reading the GPT review first — then show a comparison table of common findings, one-sided findings, and conflicting findings with each side's reasoning. Use when the user wants a report or document double-checked by both GPT and Claude independently.
---

# cross-review

주어진 파일을 GPT와 Claude(나) 둘이 각각 독립적으로 검증한 뒤, 결과를 "공통 / 한쪽만 / 엇갈림"으로 비교해서 표로 보여주는 스킬.

## 무엇을

1) GPT API로 파일을 검증해 리뷰 파일로 저장 → 2) Claude가 같은 파일을 같은 기준으로 독립 검증(GPT 결과를 먼저 보지 않음) → 3) 두 결과를 비교한 표를 보여준다.

## 입력

- 검증할 파일 경로 (텍스트 파일, 예: `outputs/today-summary-20260724.txt`)
- `practice/.env`의 `OPENAI_API_KEY`

## 점검 기준 (양쪽 다 동일하게 적용)

- **사실**: 숫자·이름·날짜·인용 중 근거 없이 지어낸 것으로 의심되는 부분
- **논리**: 주장과 근거가 맞지 않는 부분
- **누락**: 꼭 있어야 하는데 빠진 내용
- **톤·형식**: 받는 사람 기준으로 어색하거나 부적절한 부분

## 순서

1. PowerShell로 (프로젝트 루트에서) `python practice/gpt_verify.py <검증할 파일 경로>`를 실행한다. GPT(`gpt-4o-mini`)가 위 4가지 기준으로 파일을 검토해 같은 폴더에 `<파일명>-gpt-review.md`로 저장한다 (원문은 수정하지 않음).
2. **이 시점에는 방금 만들어진 gpt-review 파일을 아직 열어보지 않는다.**
3. Claude가 검증 대상 파일을 같은 4가지 기준으로 독립적으로 검토한다. 가능하면 그 내용의 원본 소스(예: 이 텍스트가 어떤 데이터/파일에서 나왔는지)까지 직접 대조해서 근거를 확인한다. 각 지적은 "어느 문장/부분인지 + 왜 문제인지" 형식으로 짧게 정리한다.
4. 그다음에야 1단계에서 저장된 `<파일명>-gpt-review.md`를 연다.
5. 두 검증 결과를 대조해서 표로 정리한다:
   - **공통으로 지적한 것** → 확실히 고칠 후보
   - **한쪽만 지적한 것** → 확인해볼 것
   - **서로 엇갈리는 것** → 각각의 판단 근거를 함께 적는다 (누가 왜 그렇게 판단했는지)

## 출력

- `<파일명>-gpt-review.md` — GPT 검증 결과 파일 (검증 대상과 같은 폴더에 저장)
- 채팅 응답으로 "공통 / 한쪽만 / 엇갈림" 3단 비교 표

## 주의

- GPT 호출 1회당 비용이 발생한다.
- 3단계(Claude 독립 검증)는 반드시 gpt-review 파일을 열기 전에 먼저 끝내야 한다 — 순서가 바뀌면 Claude의 판단이 GPT 결과에 편향될 수 있다.
