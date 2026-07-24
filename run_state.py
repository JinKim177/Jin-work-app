"""
실행 상태 기록 (Feature 5에서 사용)

last_run.txt에 마지막으로 실행 완료된 날짜(YYYY-MM-DD) 하나만 기록한다.
그 외의 저장/로그는 남기지 않는다.
"""

import os

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "last_run.txt")


def has_run_today(today_str: str, state_path: str = STATE_FILE) -> bool:
    """상태 파일에 기록된 날짜가 오늘과 같으면 True."""
    if not os.path.exists(state_path):
        return False
    with open(state_path, "r", encoding="utf-8") as f:
        recorded = f.read().strip()
    return recorded == today_str


def mark_run_today(today_str: str, state_path: str = STATE_FILE) -> None:
    """상태 파일에 오늘 날짜를 기록한다."""
    with open(state_path, "w", encoding="utf-8") as f:
        f.write(today_str)
