"""
Feature 5: 평일 08:00 자동 실행 판단
명세: specs/feature-5-spec.md

이 스크립트가 호출된 시점에 "지금이 자동 실행 조건을 만족하는지"를 판단해서,
조건을 만족하면 Feature 3 파이프라인(파일 찾기 + 요약 생성)을 실행하고
결과를 outputs/ 폴더에 파일로 저장한다 (사람 확인 절차는 생략).

이 스크립트 자체를 몇 분 간격으로 언제 호출할지(Windows 작업 스케줄러 등록 등)는
이 기능의 범위 밖이다 — 사람이 OS 스케줄러에 직접 등록한다.

사용법:
    python auto_run_check.py [폴더 경로]
"""

import os
import sys
from datetime import datetime

from feature1_attendance_summary import generate_attendance_summary
from feature2_find_todays_file import find_todays_attendance_file
from run_state import has_run_today, mark_run_today

OUTPUTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
AUTO_RUN_HOUR = 8


def check_and_run(folder_path: str = "inputs") -> None:
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")

    if now.weekday() >= 5:  # 0=월 ... 5=토, 6=일
        print("주말이라 자동 실행 대상이 아닙니다.")
        return

    if has_run_today(today_str):
        print(f"오늘({today_str})은 이미 실행 기록이 있어 자동 실행하지 않습니다.")
        return

    if now.hour < AUTO_RUN_HOUR:
        print(f"아직 자동 실행 시각(오전 {AUTO_RUN_HOUR}시) 이전입니다.")
        return

    file_path = find_todays_attendance_file(folder_path)
    if file_path is None:
        today_md = now.strftime("%m.%d")
        print(f"오늘({today_md}) 근태 파일을 아직 찾지 못해 자동 실행을 하지 않았습니다.")
        return

    summary = generate_attendance_summary(file_path)

    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUTS_DIR, f"today-summary-{now.strftime('%Y%m%d')}.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(summary)

    mark_run_today(today_str)
    print(f"자동 실행 완료. 결과를 저장했습니다: {out_path}")
    print("사람 확인(y/n) 절차는 생략되었습니다 — 이 파일을 열어 직접 확인 후 사용하세요.")


if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else "inputs"
    check_and_run(folder)
