"""
Feature 3 + 4: 파일 자동 인식 + 요약 텍스트 생성 + 사람 확인 연결
명세: specs/feature-3-spec.md, specs/feature-4-spec.md

지정 폴더에서 오늘 날짜의 근태 엑셀 파일을 찾아(Feature 2),
찾은 파일을 근태 요약 텍스트 생성(Feature 1)에 넘겨 카톡용 요약 텍스트를 만들고,
사람의 y/n 확인(Feature 4)을 거친 뒤 최종 텍스트를 보여준다.

사람이 승인(y)하면 실행 상태 파일에 오늘 날짜를 기록한다 (Feature 5 —
같은 날 08:00 자동 실행과 중복되지 않도록 하기 위함). 거부(n)한 경우에는
데이터를 다시 확인해야 하므로 기록하지 않는다.

사용법:
    python run_today_attendance_summary.py [폴더 경로]
    (폴더 경로를 안 주면 기본값 inputs/ 사용)
"""

import sys
from datetime import datetime

from confirm_summary import confirm_summary
from feature1_attendance_summary import generate_attendance_summary
from feature2_find_todays_file import find_todays_attendance_file
from run_state import mark_run_today


def run(folder_path: str = "inputs") -> str | None:
    """오늘 근태 파일을 찾아 요약 텍스트를 만든다. 파일이 없으면 None을 돌려준다."""
    file_path = find_todays_attendance_file(folder_path)
    if file_path is None:
        return None
    return generate_attendance_summary(file_path)


if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else "inputs"
    today = datetime.now().strftime("%m.%d")

    summary = run(folder)
    if summary is None:
        print(f"오늘({today}) 근태 파일을 아직 찾지 못했습니다.")
    else:
        approved = confirm_summary(summary)
        if approved:
            mark_run_today(datetime.now().strftime("%Y-%m-%d"))
