# CLAUDE.md

이 파일은 이 저장소에서 작업할 때 Claude Code(claude.ai/code)에게 방향을 알려주는 안내 문서입니다.

## 이 저장소는 무엇인가

매일 반복되는 사무 업무 하나를 자동화하는 작은 파이썬 스크립트 모음입니다: 일일근태현황
엑셀 파일(ERP-일일근태현황)을 읽어, 팀장근태와 팀원근태로 나누고 근태 종류별 인원수(소속팀
포함)를 정리해서 카톡방에 바로 붙여넣을 수 있는 요약 텍스트를 만듭니다. 이건 **범용 애플리케이션이
아니라**, 한 사람의 일일 보고 업무를 위해 만든, 각자 별도의 명세 파일을 가진 좁은 범위의
기능(feature)들의 파이프라인입니다.

모든 것이 한글로 되어 있습니다(명세, 코드 주석, 출력 텍스트, CLI 안내 문구). 새로 코드나
문서를 추가할 때도 이 기조를 유지하세요 — 이 도메인에서 영문 식별자/영문 출력으로 바꾸지
마세요.

패키지 매니페스트(`requirements.txt`/`pyproject.toml`)가 없고, 테스트 스위트도 없으며, 이
디렉터리는 git 저장소가 아닙니다.

## 명세 기반 기능 구조

`feature*.py` 파일은 각각 정확히 하나의 `specs/feature-N-spec.md`를 구현합니다. 명세가
범위(scope)의 기준입니다 — 각 명세에는 "지금은 뺄 것" 항목이 명시되어 있어, 아직 만들면 안
되는 것이 무엇인지 알려줍니다. 기능을 확장할 때는 먼저 해당 명세를 확인하세요. 의도적으로
미룬 범위를 조용히 추가하지 마세요. 명세들이 근거로 삼는 상위 문서:

- [specs/App_기획서.md](specs/App_기획서.md) — 제품 목표, 입력 형식(열 구성, 시트명), 제약 사항
- [specs/App_자동화_흐름도.md](specs/App_자동화_흐름도.md) — 11단계 처리 흐름, 단계별 사람/AI 담당 구분
- [practice/docs/자동화_후보_비교표.md](practice/docs/자동화_후보_비교표.md) — 다른 자동화 후보들과 비교해 왜 이 업무를 선택했는지 (근태 앱과 무관한 나머지 연습 자료와 함께 `practice/`로 옮겨짐)

## 파이프라인 구조

각 기능은 다음 순서로 이어집니다:

```
feature2_find_todays_file.py  → inputs/ 폴더에서 오늘 날짜의 ERP-일일근태현황(MM.DD).xlsx를 찾음
        ↓ (파일 경로)
feature1_attendance_summary.py → xlsx를 읽어 팀장/팀원 분리, 근태 종류별 그룹핑,
        ↓                        카톡 포맷 요약 문자열 생성
confirm_summary.py             → 요약을 출력하고 터미널 y/n 승인을 기다림
        ↓
run_state.py                   → last_run.txt에 오늘 날짜를 기록 (중복 실행 방지용 키)
```

두 개의 진입점이 이 체인을 서로 다르게 조립합니다:

- **`run_today_attendance_summary.py`** — 수동/대화형 경로. 오늘 파일을 찾아 요약을 만들고,
  `confirm_summary.py`를 통해 사람의 y/n 확인을 거쳐야 완료로 취급합니다. 승인(`y`)한 경우에만
  `last_run.txt`에 기록하며, 거부하면 기록을 남기지 않아 그날 다시 시도할 수 있습니다.
- **`auto_run_check.py`** — 무인/스케줄 실행 경로 (Feature 5). 외부 스케줄러(Windows 작업
  스케줄러 — 이 스케줄러 등록 자체는 이 코드의 범위 밖)가 주기적으로 호출한다고 가정합니다.
  호출될 때마다 평일인지, 오늘 이미 실행됐는지(`run_state.has_run_today`), 08:00이 지났는지를
  확인하고, 조건을 모두 만족할 때만 feature1+2 파이프라인을 사람 확인 절차 **없이** 실행해서
  결과를 `outputs/today-summary-YYYYMMDD.txt`에 그대로 저장합니다 (나중에 사람이 확인).

`feature1_attendance_summary.py` 내부는
`load_rows → select_columns → remove_blank_rows → remove_duplicate_rows → split_leader_member →
build_summary_phrase (팀장/팀원 각각 1회씩) → merge_summaries + build_total_summary →
format_for_kakao` 순서로 파이프라인화되어 있습니다. 흐름도의 "한 단계 = 한 가지 일" 원칙에
따라 각 함수가 단일 책임을 갖도록 설계되어 있어 단계별로 독립적으로 테스트하기 쉽습니다 —
아직 테스트 파일은 없지만, 새 로직을 추가할 때도 단계를 합치지 말고 이 "함수 하나 = 단계
하나" 구조를 유지하세요. `format_for_kakao`는 `build_title`이 만드는 날짜 제목과
`build_total_summary`가 만드는 "1. 근태요약 : 총 N명" 한 줄 요약 블록을 결과 맨 위에 자체
포함하므로, 근태 결과에 대해서는 별도의 "한 줄 요약 덧붙이기" 기능이 필요 없습니다.

근태 엑셀 형식은 고정되어 있습니다: 시트명 `HuDut020ControlDB`, 1행은 필드 코드, **2행이 실제
한글 헤더**, 3행부터 데이터. 열 구성은 [specs/App_기획서.md](specs/App_기획서.md)에 정리되어
있습니다. 팀장/팀원 분리 규칙은: H열(부서명) 값이 "팀장"으로 끝나면 팀장, 그 외는 전부
팀원입니다 (정확히 일치가 아니라 접미사(suffix) 검사입니다).

## 근태 파이프라인과 무관한 실험용 스크립트 (practice/로 이동됨)

`feature3_generate_image.py`(OpenAI 이미지 생성 → `images/`), `feature4_categorize_memos.py`
(GPT 기반 `memos/*.md` 카테고리 분류), `feature6_extract_todos.py`, `feature7_todos_with_headline.py`는
근태 파이프라인과 연결되지 않은 독립적인 실험 스크립트입니다 — 번호가 붙어 있지만 feature1~5
명세 체인에 속하지 않습니다. `App_기획서.md` 기준으로 저장소를 정리하면서 이 네 스크립트와
그 스크립트들이 참조하는 폴더(`images/`, `memos/`, `organized/`, `.env`)를 모두
**`practice/`** 아래로 옮겼습니다 — 옮긴 뒤에도 그대로 동작하도록 `.env` 로딩을
스크립트 자기 파일 위치 기준 경로로 고쳤습니다. 실행 예:
`python practice/feature3_generate_image.py "설명"`, `python practice/feature4_categorize_memos.py`.
feature3·4는 OpenAI API를 호출하며(유료), `practice/.env`의 `OPENAI_API_KEY`를
`python-dotenv`로 읽어옵니다.

`practice/inbox/`, `practice/organized/`와 `practice/inputs/` 아래의 `d2_*`, `sales-report.*`
파일들은 `.claude/skills/weekly-summary` 스킬과 수동 메모 정리 연습을 위한 가상의 연습용
데이터(가상 회사 "썸머빌")입니다. `practice/organized/`는 카테고리별 하위 폴더(`meeting/`,
`ideas/`, `todo/`, `research/`, `feedback/`)로 이미 사람이 분류해 둔 결과이며,
`practice/organized/todo/`는 `practice/feature6_extract_todos.py`가 실제로 읽어서
소비합니다 — 나머지 카테고리 폴더와 `inbox/`, `d2_*`는 이 저장소의 다른 어떤 스크립트도
소비하지 않습니다.

`practice/feature6_extract_todos.py`는 `practice/organized/todo/*.md`(이미 '할 일'로 분류된
메모)를 읽어, 각 메모의 제목(`# 할 일 - ...`)과 불릿 항목(`- ...`)만 뽑아 "오늘 할 일" 목록
텍스트로 합쳐 보여준다. GPT 카테고리 분류(`feature4`)와 달리 이미 분류된 폴더를 그대로 읽는
방식이라 OpenAI API 호출이나 비용이 들지 않는다. 이것도 근태 파이프라인과는 무관한 별도
기능이다.

`practice/feature7_todos_with_headline.py`는 `feature6`의 함수들을 그대로 불러와, 전체 할 일
건수를 담은 한 줄 요약(`[한 줄 요약] 오늘 할 일 총 N건 (메모 M건)`)을 목록 위에 덧붙인다.
`feature1`은 이미 자체 한 줄 요약 블록이 있어 대상에서 제외했다(위 참고).

참고로 근태 앱을 소개하는 발표 원고 [docs/1분_발표원고.md](docs/1분_발표원고.md)는 `practice/`로
옮기지 않고 그대로 `docs/`에 남아 있습니다.

## 명령어

의존성 매니페스트가 없으므로 필요할 때마다 직접 설치하세요:
```
pip install openpyxl openai python-dotenv
```

Python 3.10 이상이 필요합니다(`X | None` 유니온 타입 문법 사용). `__pycache__`에 남은 컴파일
결과물을 보면 실제로는 3.14 버전이 쓰이고 있습니다.

개별 기능 직접 실행:
```
python feature1_attendance_summary.py [xlsx경로]              # 기본값: inputs/sample-attendance-fake.xlsx
python feature2_find_todays_file.py [폴더경로]                 # 기본값: inputs
python practice/feature4_categorize_memos.py                  # practice/memos/*.md를 읽음, OPENAI_API_KEY 필요
python practice/feature3_generate_image.py "이미지 설명"        # 호출마다 비용 발생, OPENAI_API_KEY 필요
python practice/feature6_extract_todos.py                      # practice/organized/todo/*.md를 읽음, API 불필요
python practice/feature7_todos_with_headline.py                # feature6 + 한 줄 요약, API 불필요
```

전체 수동 파이프라인 실행 (대화형, y/n 승인 프롬프트 있음):
```
python run_today_attendance_summary.py [폴더경로]      # 기본값: inputs
```

스케줄/무인 실행용 체크 실행 (프롬프트 없음, outputs/에 저장, 언제 호출할지는 외부
스케줄러가 결정):
```
python auto_run_check.py [폴더경로]                    # 기본값: inputs
```

이 저장소에는 설정된 lint나 test 명령어가 없습니다.

## 작업 규칙

**절대 규칙** (예외 없이 항상 지킬 것)
1. 내 역할은 인사 담당이며, 답변은 항상 한국어로 한다.
2. 실명·실제 사내 자료는 절대 넣지 않는다 — 연습·테스트는 항상 가짜 데이터로.
3. 추측하지 말고, 모르면 모른다고 말한다.

**규칙 인덱스** (주제별 상세 규칙은 `rules/` 폴더 참고)
- 말투 규칙 → [rules/tone.md](rules/tone.md)
- 결과 형식 규칙 → [rules/format.md](rules/format.md)
- 하지 말 것 규칙 → [rules/dont.md](rules/dont.md)

**우선순위**: 규칙끼리 부딪치면 절대 규칙 > `rules/dont.md` > `rules/tone.md`·`rules/format.md` 순으로 따른다.
