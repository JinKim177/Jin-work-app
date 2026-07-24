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

import html
import re
from datetime import date

import streamlit as st

from feature1_attendance_summary import generate_attendance_summary
from feature2_find_todays_file import find_attendance_file_by_date

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


def _assign_code_colors(total_items):
    mapping = {}
    for code, _ in total_items:
        if code not in mapping:
            idx = len(mapping)
            mapping[code] = CODE_COLORS[idx] if idx < len(CODE_COLORS) else CODE_COLOR_FALLBACK
    return mapping


def _render_summary_html(parsed):
    colors = _assign_code_colors(parsed["total_items"])
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
