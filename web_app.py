"""
근태 요약 웹 화면 (Streamlit, 승인 절차 없는 조회 전용 버전)

날짜를 고르면 그 날짜의 근태 엑셀 파일을 inputs/ 폴더에서 찾아
근태 요약 텍스트를 화면에 보여준다. 사람 확인(y/n) 절차는 이 화면엔 없음 —
조회/확인 용도로만 쓰고, 실제 카톡 발송 전 최종 승인은 기존 터미널 흐름
(run_today_attendance_summary.py)을 그대로 이용한다.

화면 구성 자체(입력 -> 버튼 -> 결과)와 기능은 그대로이며,
색·글꼴·여백·배치(CSS)만 다듬은 버전이다.

실행:
    streamlit run web_app.py
"""

import glob
import html
import os
import re
from datetime import date

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from feature1_attendance_summary import (
    WEEKDAY_KO,
    generate_attendance_summary,
    load_rows,
    remove_blank_rows,
    remove_duplicate_rows,
    resolve_report_date,
    select_columns,
)
from feature2_find_todays_file import FILENAME_PATTERN, find_attendance_file_by_date

INPUTS_DIR = "inputs"

# 근태코드(정체성 구분용) 배지 색 순서 — 고정 순서로만 배정하고 순환하지 않는다.
# 8종을 넘는 근태코드는 회색(CODE_COLOR_FALLBACK)으로 폴백한다.
CODE_COLORS = [
    "#2a78d6",  # blue
    "#eb6834",  # orange
    "#1baf7a",  # aqua
    "#eda100",  # yellow
    "#e87ba4",  # magenta
    "#008300",  # green
    "#4a3aa7",  # violet
    "#e34948",  # red
]
CODE_COLOR_FALLBACK = "#9a988f"


def _parse_summary(summary_text):
    """카톡 포맷 요약 텍스트를 화면 렌더링용 구조로 분해한다."""
    blocks = summary_text.split("\n\n")
    title = blocks[0]

    total_lines = blocks[1].split("\n")
    total_match = re.search(r"총\s*(\d+)명", total_lines[0])
    total_count = total_match.group(1) if total_match else "?"

    # 근태요약 블록은 4개씩 줄바꿈되어 있고 줄 경계엔 쉼표가 없으므로,
    # 각 줄의 괄호를 벗겨낸 뒤 쉼표로 다시 이어붙여야 항목이 안 뭉친다.
    fragments = [line.strip().lstrip("(").rstrip(")") for line in total_lines[1:]]
    joined_rest = ", ".join(fragments)
    total_items = []
    for part in joined_rest.split(","):
        part = part.strip()
        if not part:
            continue
        m = re.match(r"^(.*?)(\d+)$", part)
        if m:
            total_items.append((m.group(1), m.group(2)))

    def parse_person_block(block):
        lines = block.split("\n")
        header = lines[0]
        rows = []
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            if line == "해당 없음":
                rows.append(None)
                continue
            m = re.match(r"^(\S+)\s+(\d+)명\((.*)\)$", line)
            rows.append(m.groups() if m else (line, "", ""))
        return header, rows

    leader_header, leader_rows = parse_person_block(blocks[2])
    member_header, member_rows = parse_person_block(blocks[3])

    return {
        "title": title,
        "total_count": total_count,
        "total_items": total_items,
        "leader_header": leader_header,
        "leader_rows": leader_rows,
        "member_header": member_header,
        "member_rows": member_rows,
    }


def _assign_code_colors(codes):
    mapping = {}
    for code in codes:
        if code not in mapping:
            idx = len(mapping)
            mapping[code] = CODE_COLORS[idx] if idx < len(CODE_COLORS) else CODE_COLOR_FALLBACK
    return mapping


def _list_attendance_files_by_date(folder_path):
    """근태 엑셀 파일을 MM.DD 날짜 키로 묶는다. 같은 날짜 파일이 여러 개면 최신 수정본만 남긴다."""
    by_date = {}
    for path in glob.glob(os.path.join(folder_path, "*.xlsx")):
        m = FILENAME_PATTERN.match(os.path.basename(path))
        if not m:
            continue
        date_key = f"{m.group(1)}.{m.group(2)}"
        if date_key not in by_date or os.path.getmtime(path) > os.path.getmtime(by_date[date_key]):
            by_date[date_key] = path
    return dict(sorted(by_date.items()))


def _code_counts_by_date(folder_path):
    """날짜별 근태코드 인원수를 집계한다: {report_date(datetime): {근태코드: 인원수}}."""
    result = {}
    for path in _list_attendance_files_by_date(folder_path).values():
        rows, col_index = load_rows(path)
        records = select_columns(rows, col_index)
        records = remove_blank_rows(records)
        records = remove_duplicate_rows(records)

        counts = {}
        for r in records:
            code = r["근태코드"]
            counts[code] = counts.get(code, 0) + 1

        result[resolve_report_date(records)] = counts
    return dict(sorted(result.items()))


def _ordered_codes(counts_by_date):
    """날짜 순서대로 훑으며 처음 등장하는 순서로 근태코드 목록을 만든다."""
    order = []
    for counts in counts_by_date.values():
        for code in counts:
            if code not in order:
                order.append(code)
    return order


def _matrix_title(counts_by_date):
    """표에 표시된 날짜들 중 가장 최근 달을 기준으로 '7월 근태 현황' 같은 제목을 만든다."""
    last_date = list(counts_by_date.keys())[-1]
    return f"{last_date.month}월 근태 현황"


def _render_date_matrix_html(counts_by_date):
    codes = _ordered_codes(counts_by_date)
    colors = _assign_code_colors(codes)
    esc = html.escape

    header_cells = "".join(
        "<th>"
        f'<span class="matrix-date-main">{esc(f"{d.month}월{d.day}일")}</span>'
        f'<span class="matrix-date-dow">{esc(WEEKDAY_KO[d.weekday()])}요일</span>'
        "</th>"
        for d in counts_by_date
    )

    body_rows = []
    for code in codes:
        color = colors.get(code, CODE_COLOR_FALLBACK)
        cells = "".join(
            f'<td class="matrix-count">{counts.get(code, 0) or "–"}</td>'
            for counts in counts_by_date.values()
        )
        body_rows.append(
            "<tr>"
            f'<th class="matrix-row-label">'
            f'<span class="att-dot" style="background:{color}"></span>{esc(code)}'
            "</th>"
            f"{cells}"
            "</tr>"
        )

    return f"""
    <div class="matrix-wrap">
    <table class="matrix-table">
        <thead><tr><th class="matrix-corner">근태구분</th>{header_cells}</tr></thead>
        <tbody>{''.join(body_rows)}</tbody>
    </table>
    </div>
    """


def _render_summary_html(parsed):
    colors = _assign_code_colors(code for code, _ in parsed["total_items"])
    esc = html.escape

    def dot(code):
        return f'<span class="att-dot" style="background:{colors.get(code, CODE_COLOR_FALLBACK)}"></span>'

    def chip(code, count):
        return (
            f'<span class="att-chip">{dot(code)}'
            f'<span class="att-chip-code">{esc(code)}</span>'
            f'<span class="att-chip-count">{esc(count)}명</span></span>'
        )

    def row(code, count, detail):
        return (
            '<div class="att-row">'
            f'{dot(code)}'
            f'<span class="att-code">{esc(code)}</span>'
            f'<span class="att-count">{esc(count)}명</span>'
            f'<span class="att-detail">({esc(detail)})</span>'
            "</div>"
        )

    def rows_html(rows):
        if not rows:
            return '<div class="att-empty">해당 없음</div>'
        parts = []
        for r in rows:
            parts.append('<div class="att-empty">해당 없음</div>' if r is None else row(*r))
        return "".join(parts)

    chips_html = "".join(chip(code, count) for code, count in parsed["total_items"])

    return f"""
    <div class="result-card">
        <div class="result-title">{esc(parsed['title'])}</div>
        <div class="result-total">
            <div class="result-total-label">근태요약</div>
            <div class="result-total-count">총 <span>{esc(parsed['total_count'])}</span>명</div>
            <div class="att-chip-row">{chips_html}</div>
        </div>
        <div class="result-section">
            <div class="result-section-header">
                <span class="section-badge leader">팀장</span>{esc(parsed['leader_header'])}
            </div>
            {rows_html(parsed['leader_rows'])}
        </div>
        <div class="result-section">
            <div class="result-section-header">
                <span class="section-badge member">팀원</span>{esc(parsed['member_header'])}
            </div>
            {rows_html(parsed['member_rows'])}
        </div>
    </div>
    """


# ── 안내 챗봇 (우측 하단 플로팅) ───────────────────────────────────────
# 이 서비스가 뭘 하는지는 기획서·CLAUDE.md를 그대로 읽어 GPT에게 근거로 넘긴다.
CHATBOT_MODEL = "gpt-4o-mini"
_APP_DIR = os.path.dirname(os.path.abspath(__file__))
_CHATBOT_CONTEXT_FILES = [
    os.path.join(_APP_DIR, "CLAUDE.md"),
    os.path.join(_APP_DIR, "specs", "App_기획서.md"),
    os.path.join(_APP_DIR, "specs", "App_자동화_흐름도.md"),
]


def _load_chatbot_context():
    parts = []
    for path in _CHATBOT_CONTEXT_FILES:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                parts.append(f"### {os.path.basename(path)}\n\n{f.read()}")
    return "\n\n---\n\n".join(parts)


def _chatbot_system_prompt():
    return (
        "너는 '대양그룹-대영포장 발안'의 일일근태 자동화 서비스 화면에 붙어 있는 안내 챗봇이다.\n"
        "아래 참고 문서(이 서비스의 기획서와 프로젝트 안내)를 근거로, 방문자가 이 서비스에 대해 묻는 "
        "질문에 한국어로 친절하고 간결하게 답한다.\n"
        "문서에 없는 내용은 추측해서 답하지 말고, 모른다고 답한다.\n\n"
        "--- 참고 문서 ---\n\n" + _load_chatbot_context()
    )


def _ask_chatbot(history):
    """history: [{"role": "user"/"assistant", "content": str}, ...]. 마지막 사용자 질문에 대한 답을 돌려준다."""
    load_dotenv(os.path.join(_APP_DIR, "practice", ".env"))
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return "OPENAI_API_KEY가 설정되어 있지 않아 답변할 수 없습니다. practice/.env를 확인해주세요."

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=CHATBOT_MODEL,
            messages=[{"role": "system", "content": _chatbot_system_prompt()}] + history,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"답변 생성 중 문제가 발생했습니다: {e}"


st.set_page_config(page_title="발안공장 일일근태보고", page_icon="📋", layout="centered")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    .stApp {
        background: #F4F6FA;
    }

    .block-container {
        max-width: 760px;
        padding-top: 1.4rem;
        padding-bottom: 1.5rem;
    }

    /* 상단 히어로 배너 */
    .hero {
        background: linear-gradient(135deg, #12213F 0%, #1C2E52 55%, #26406E 100%);
        border-radius: 20px;
        padding: 20px 26px;
        margin-bottom: 14px;
        box-shadow: 0 12px 32px rgba(18, 33, 63, 0.25);
    }
    .hero-eyebrow {
        color: rgba(255,255,255,0.6);
        font-size: 13px;
        font-weight: 600;
        letter-spacing: .04em;
        text-transform: uppercase;
        margin: 0 0 8px 0;
    }
    .hero-title {
        color: #FFFFFF;
        font-size: 21px;
        font-weight: 800;
        margin: 0;
        line-height: 1.3;
    }

    /* 기능 탭 */
    div[data-testid="stTabs"] div[role="tablist"] {
        gap: 4px;
        border-bottom: 1px solid #E7EAF3;
    }
    div[data-testid="stTabs"] button[role="tab"] {
        height: auto;
        padding: 8px 18px;
        font-weight: 600;
        font-size: 14px;
        color: #6B7280;
    }
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        color: #12213F;
    }
    div[data-testid="stTabs"] div[data-baseweb="tab-highlight"] {
        background-color: #12213F;
        height: 3px;
    }
    div[data-testid="stTabs"] div[data-baseweb="tab-border"] {
        display: none;
    }
    div[data-testid="stTabs"] > div:first-child {
        margin-bottom: 18px;
    }

    /* 카드형 컨테이너 */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #FFFFFF;
        border-radius: 20px;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
        padding: 6px 4px;
    }

    .card-label {
        font-size: 13px;
        font-weight: 700;
        color: #12213F;
        letter-spacing: .03em;
        text-transform: uppercase;
        margin-bottom: 4px;
    }

    /* 버튼: 알약형 네이비 */
    .stButton > button {
        background-color: #12213F;
        color: #FFFFFF;
        border: none;
        border-radius: 999px;
        padding: 10px 30px;
        font-weight: 600;
        font-size: 14.5px;
        box-shadow: 0 6px 16px rgba(18, 33, 63, 0.25);
    }
    .stButton > button:hover {
        background-color: #1C2E52;
        color: #FFFFFF;
    }

    /* 날짜 입력창 라운딩 */
    div[data-baseweb="input"] {
        border-radius: 14px !important;
    }

    /* 알림 박스 라운딩 */
    div[data-testid="stAlert"] {
        border-radius: 14px;
    }

    /* 결과 카드 */
    .result-card {
        padding: 4px 2px;
    }
    .result-title {
        font-size: 16px;
        font-weight: 800;
        color: #12213F;
        padding-bottom: 8px;
        margin-bottom: 10px;
        border-bottom: 1px solid #E7EAF3;
    }

    .result-total {
        background: #F8FAFC;
        border: 1px solid #E7EAF3;
        border-radius: 14px;
        padding: 12px 16px;
        margin-bottom: 14px;
    }
    .result-total-label {
        font-size: 11px;
        font-weight: 700;
        color: #898781;
        letter-spacing: .04em;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .result-total-count {
        font-size: 18px;
        font-weight: 800;
        color: #12213F;
    }
    .result-total-count span {
        font-size: 23px;
        color: #2A78D6;
    }
    .att-chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-top: 10px;
    }
    .att-chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #FFFFFF;
        border: 1px solid #E7EAF3;
        border-radius: 999px;
        padding: 5px 12px;
        font-size: 13px;
    }
    .att-chip-code {
        font-weight: 600;
        color: #12213F;
    }
    .att-chip-count {
        font-weight: 700;
        color: #52514E;
        font-size: 12px;
    }

    .result-section {
        margin-bottom: 10px;
    }
    .result-section-header {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 13px;
        font-weight: 700;
        color: #12213F;
        margin-bottom: 6px;
    }
    .section-badge {
        font-size: 11px;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 999px;
        color: #FFFFFF;
    }
    .section-badge.leader {
        background: #4A3AA7;
    }
    .section-badge.member {
        background: #1BAF7A;
    }

    .att-dot {
        width: 8px;
        height: 8px;
        min-width: 8px;
        border-radius: 50%;
        display: inline-block;
    }
    .att-row {
        display: flex;
        align-items: center;
        gap: 10px;
        background: #FFFFFF;
        border: 1px solid #F0F1F5;
        border-radius: 10px;
        padding: 7px 12px;
        margin-bottom: 4px;
    }
    .att-code {
        font-weight: 700;
        color: #12213F;
        min-width: 60px;
    }
    .att-count {
        font-weight: 800;
        color: #2A78D6;
        min-width: 44px;
    }
    .att-detail {
        color: #6B7280;
        font-size: 13px;
    }
    .att-empty {
        color: #9CA3AF;
        font-style: italic;
        font-size: 13px;
        padding: 10px 14px;
    }

    /* 날짜별 근태 현황 표 */
    .matrix-wrap {
        overflow-x: auto;
        border: 1px solid #E7EAF3;
        border-radius: 14px;
    }
    .matrix-table {
        border-collapse: separate;
        border-spacing: 0;
        width: 100%;
        font-size: 13.5px;
    }
    .matrix-table th,
    .matrix-table td {
        padding: 12px 20px;
        border-bottom: 1px solid #EEF0F5;
        white-space: nowrap;
    }
    .matrix-table thead th {
        background: #F8FAFC;
        color: #12213F;
        text-align: center;
        border-bottom: 1px solid #E7EAF3;
        vertical-align: middle;
    }
    .matrix-corner {
        text-align: left !important;
        font-size: 12.5px;
        font-weight: 700;
        letter-spacing: .02em;
    }
    .matrix-date-main {
        display: block;
        font-size: 13.5px;
        font-weight: 800;
        color: #12213F;
    }
    .matrix-date-dow {
        display: block;
        font-size: 11px;
        font-weight: 600;
        color: #9CA3AF;
        margin-top: 2px;
    }
    .matrix-row-label {
        display: flex;
        align-items: center;
        gap: 9px;
        font-weight: 700;
        font-size: 13.5px;
        color: #12213F;
        text-align: left;
        background: #F8FAFC;
        border-right: 1px solid #E7EAF3;
    }
    .matrix-table tbody tr:last-child th,
    .matrix-table tbody tr:last-child td {
        border-bottom: none;
    }
    .matrix-table tbody tr:nth-child(even) td {
        background: #FBFCFE;
    }
    .matrix-table tbody tr:hover td {
        background: #EEF3FC;
    }
    .matrix-table tbody tr:hover th {
        background: #EEF3FC;
    }
    .matrix-count {
        text-align: center;
        font-size: 14.5px;
        font-weight: 800;
        color: #2A78D6;
        font-variant-numeric: tabular-nums;
    }

    /* 파일 찾음 안내 - 눈에 덜 띄어도 되는 보조 정보라 최소 크기로 축소 */
    .file-found-note {
        font-size: 10px;
        color: #9CA3AF;
        margin: 0 0 10px 0;
        line-height: 1.4;
    }

    /* 카톡 붙여넣기용 원문 텍스트 블록 - 복사 아이콘이 뜨는 st.code 위 라벨 */
    .copy-label {
        margin-top: 8px;
    }
    .stCodeBlock, pre {
        border-radius: 14px !important;
        background: #F8FAFC !important;
        border: 1px solid #E7EAF3 !important;
    }
    .stCodeBlock code,
    .stCodeBlock pre,
    .stCodeBlock span,
    .stCodeBlock * {
        color: #12213F !important;
    }

    /* 우측 하단 플로팅 챗봇 */
    .st-key-chat_toggle_wrap {
        position: fixed;
        bottom: 24px;
        right: 24px;
        z-index: 999;
        width: auto;
    }
    .st-key-chat_toggle_wrap .stButton > button {
        width: 56px !important;
        height: 56px !important;
        padding: 0 !important;
        border-radius: 50% !important;
        font-size: 24px !important;
        line-height: 1 !important;
        box-shadow: 0 8px 20px rgba(18, 33, 63, 0.35) !important;
    }

    .st-key-chat_panel_wrap {
        position: fixed;
        bottom: 92px;
        right: 24px;
        width: 340px;
        max-width: calc(100vw - 32px);
        z-index: 998;
        box-shadow: 0 16px 40px rgba(15, 23, 42, 0.18) !important;
    }
    .chat-panel-title {
        font-size: 14px;
        font-weight: 800;
        color: #12213F;
        padding: 2px 4px 10px 4px;
        margin-bottom: 8px;
        border-bottom: 1px solid #E7EAF3;
    }
    .chat-empty-hint {
        font-size: 12.5px;
        color: #9CA3AF;
        padding: 4px;
        margin: 0 0 8px 0;
    }
    .st-key-chat_panel_messages {
        max-height: 300px;
        overflow-y: auto;
        margin-bottom: 8px;
        padding-right: 2px;
    }
    .st-key-chat_form div[data-testid="stForm"] {
        border: none;
        padding: 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <p class="hero-eyebrow">대양그룹-대영포장 발안 · Daily Attendance</p>
        <p class="hero-title">오늘의 근태 보고서를 조회하세요</p>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_attendance, tab_by_date = st.tabs(["일일근태보고서", "월별근태현황"])

with tab_attendance:
    with st.container(border=True):
        st.markdown('<div class="card-label">조회할 날짜</div>', unsafe_allow_html=True)
        selected_date = st.date_input(" ", value=date.today(), label_visibility="collapsed")
        st.write("")
        clicked = st.button("보고서 조회")

    if clicked:
        file_path = find_attendance_file_by_date(INPUTS_DIR, selected_date)

        with st.container(border=True):
            if file_path is None:
                st.warning(f"{selected_date.strftime('%m.%d')} 날짜의 근태 파일을 찾지 못했습니다.")
            else:
                summary = generate_attendance_summary(file_path)
                st.markdown('<div class="card-label">결과</div>', unsafe_allow_html=True)
                st.markdown(
                    f'<p class="file-found-note">파일을 찾았습니다: {html.escape(file_path)}</p>',
                    unsafe_allow_html=True,
                )
                parsed = _parse_summary(summary)
                st.markdown(_render_summary_html(parsed), unsafe_allow_html=True)

                st.markdown('<div class="card-label copy-label">복사용 텍스트 (카톡 붙여넣기)</div>', unsafe_allow_html=True)
                st.code(summary, language=None)

with tab_by_date:
    all_counts_by_date = _code_counts_by_date(INPUTS_DIR)
    available_months = sorted({d.month for d in all_counts_by_date})

    with st.container(border=True):
        st.markdown('<div class="card-label">조회할 월</div>', unsafe_allow_html=True)
        if available_months:
            selected_month = st.selectbox(
                " ",
                options=available_months,
                format_func=lambda m: f"{m}월",
                index=len(available_months) - 1,
                label_visibility="collapsed",
                key="matrix_month_select",
            )
        else:
            st.markdown(
                '<p class="file-found-note">inputs 폴더에서 인식할 수 있는 근태 파일이 없습니다.</p>',
                unsafe_allow_html=True,
            )
            selected_month = None
        st.write("")
        matrix_clicked = st.button("조회", key="matrix_query_button")

    if matrix_clicked:
        with st.container(border=True):
            month_counts = (
                {d: c for d, c in all_counts_by_date.items() if d.month == selected_month}
                if selected_month is not None
                else {}
            )
            if not month_counts:
                st.warning(
                    f"{selected_month}월 근태 파일을 찾지 못했습니다."
                    if selected_month is not None
                    else "표시할 근태 파일이 없습니다."
                )
            else:
                st.markdown(
                    f'<div class="card-label">{html.escape(_matrix_title(month_counts))}</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(_render_date_matrix_html(month_counts), unsafe_allow_html=True)


# ── 우측 하단 플로팅 챗봇 위젯 ────────────────────────────────────────
if "chat_open" not in st.session_state:
    st.session_state.chat_open = False
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

with st.container(key="chat_toggle_wrap"):
    if st.button("✕" if st.session_state.chat_open else "💬", key="chat_toggle_btn"):
        st.session_state.chat_open = not st.session_state.chat_open
        st.rerun()

if st.session_state.chat_open:
    with st.container(key="chat_panel_wrap", border=True):
        st.markdown('<div class="chat-panel-title">무엇이든 물어보세요</div>', unsafe_allow_html=True)

        with st.container(key="chat_panel_messages"):
            if not st.session_state.chat_messages:
                st.markdown(
                    '<p class="chat-empty-hint">이 서비스에 대해 궁금한 점을 물어보세요.</p>',
                    unsafe_allow_html=True,
                )
            for msg in st.session_state.chat_messages:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])

        with st.container(key="chat_form"):
            with st.form("chat_form_inner", clear_on_submit=True, border=False):
                form_cols = st.columns([5, 1])
                with form_cols[0]:
                    chat_input_text = st.text_input(
                        "질문",
                        label_visibility="collapsed",
                        placeholder="질문을 입력하세요",
                    )
                with form_cols[1]:
                    chat_submitted = st.form_submit_button("전송")

        if chat_submitted and chat_input_text.strip():
            st.session_state.chat_messages.append({"role": "user", "content": chat_input_text.strip()})
            with st.spinner("답변 작성 중..."):
                reply = _ask_chatbot(st.session_state.chat_messages)
            st.session_state.chat_messages.append({"role": "assistant", "content": reply})
            st.rerun()
