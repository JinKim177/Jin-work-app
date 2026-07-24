"""
Feature 6: 요약 결과에서 '오늘 할 일'만 따로 뽑아 보여주기

organized/todo/ 폴더(이미 '할 일'로 분류된 메모)를 읽어, 각 메모의 할 일 항목만
따로 뽑아 "오늘 할 일" 목록으로 보여준다. (연습용 샘플: organized/todo/*.md)
"""

import glob
import os

TODO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "organized", "todo")


def load_todo_memos(folder_path: str = TODO_DIR) -> list[tuple[str, str]]:
    """폴더 안의 .md 메모들을 (파일명, 내용) 목록으로 읽어온다."""
    paths = sorted(glob.glob(os.path.join(folder_path, "*.md")))
    memos = []
    for path in paths:
        with open(path, "r", encoding="utf-8") as f:
            memos.append((os.path.basename(path), f.read()))
    return memos


def parse_todo_item(content: str) -> tuple[str, list[str]]:
    """메모 내용에서 제목(# 할 일 - ...)과 할 일 항목(- ...)만 뽑아낸다."""
    title = ""
    items = []
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("# "):
            title = line[2:].split("-", 1)[-1].strip()
        elif line.startswith("- "):
            items.append(line[2:].strip())
    return title, items


def build_today_todo_summary(memos: list[tuple[str, str]]) -> str:
    """모든 할 일 메모를 하나의 '오늘 할 일' 목록 텍스트로 합친다."""
    lines = ["[오늘 할 일]"]
    for _, content in memos:
        title, items = parse_todo_item(content)
        if not items:
            continue
        lines.append("")
        lines.append(f"▶ {title}" if title else "▶ (제목 없음)")
        for item in items:
            lines.append(f"- {item}")
    return "\n".join(lines)


def extract_todays_todos(folder_path: str = TODO_DIR) -> str:
    memos = load_todo_memos(folder_path)
    return build_today_todo_summary(memos)


if __name__ == "__main__":
    memos = load_todo_memos()
    if not memos:
        print(f"{TODO_DIR} 폴더에 할 일 메모가 없습니다.")
    else:
        print(extract_todays_todos())
