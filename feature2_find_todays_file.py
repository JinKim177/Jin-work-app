"""
Feature 2: 근태 엑셀 파일 자동 인식
명세: specs/feature-2-spec.md (specs/feature-3-spec.md에서 확정된 규칙 반영)

- 최신 파일 판단: 파일명 속 날짜(MM.DD) 기준
- 오늘 날짜와 일치하는 파일만 인정 (재처리 방지)
- 같은 날짜 파일이 여러 개면 수정 시각이 가장 최근인 것을 고름
- 찾는 파일이 없으면 예외를 던지지 않고 None을 돌려줌
"""

import glob
import os
import re
import sys
from datetime import datetime

FILENAME_PATTERN = re.compile(r"^ERP-일일근태현황\((\d{2})\.(\d{2})\)\.xlsx$")


def find_attendance_file_by_date(folder_path: str, target_date) -> str | None:
    """지정 폴더에서 target_date(date/datetime, MM.DD 기준)와 일치하는 근태 엑셀 파일 경로를 찾는다. 없으면 None."""
    target = target_date.strftime("%m.%d")

    candidates = []
    for path in glob.glob(os.path.join(folder_path, "*.xlsx")):
        filename = os.path.basename(path)
        match = FILENAME_PATTERN.match(filename)
        if not match:
            continue
        file_date = f"{match.group(1)}.{match.group(2)}"
        if file_date == target:
            candidates.append(path)

    if not candidates:
        return None

    candidates.sort(key=os.path.getmtime, reverse=True)
    return candidates[0]


def find_todays_attendance_file(folder_path: str) -> str | None:
    """지정 폴더에서 오늘 날짜와 일치하는 근태 엑셀 파일 경로를 찾는다. 없으면 None."""
    return find_attendance_file_by_date(folder_path, datetime.now())


if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else "inputs"
    result = find_todays_attendance_file(folder)
    today = datetime.now().strftime("%m.%d")
    if result:
        print(f"오늘({today}) 근태 파일을 찾았습니다: {result}")
    else:
        print(f"오늘({today}) 근태 파일을 아직 찾지 못했습니다.")
