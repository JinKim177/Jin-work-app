"""
Feature 7: 결과를 한 줄 요약과 함께 보여주기

feature6이 뽑은 '오늘 할 일' 목록 위에, 전체 건수를 정리한 한 줄 요약을 덧붙여 보여준다.
(feature1의 근태 요약은 이미 자체적으로 '1. 근태요약 : 총 N명' 줄이 있어 대상에서 제외했다.)
"""

from feature6_extract_todos import TODO_DIR, build_today_todo_summary, load_todo_memos, parse_todo_item


def build_headline(memos: list[tuple[str, str]]) -> str:
    """메모 건수와 전체 할 일 항목 수를 담은 한 줄 요약을 만든다."""
    total_items = sum(len(parse_todo_item(content)[1]) for _, content in memos)
    return f"[한 줄 요약] 오늘 할 일 총 {total_items}건 (메모 {len(memos)}건)"


def generate_todos_with_headline(folder_path: str = TODO_DIR) -> str:
    memos = load_todo_memos(folder_path)
    headline = build_headline(memos)
    body = build_today_todo_summary(memos)
    return f"{headline}\n\n{body}"


if __name__ == "__main__":
    print(generate_todos_with_headline())
