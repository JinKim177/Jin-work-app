"""
Feature 4: 사람 확인(승인) 절차
명세: specs/feature-4-spec.md

근태 요약 텍스트를 보여주고, 터미널에서 y/n으로 승인을 받는다.
승인하면 텍스트를 다시 보여주고, 거부하면 안내 문구만 출력하고 끝낸다.
"""


def confirm_summary(summary_text: str) -> bool:
    """summary_text를 보여주고 y/n 승인을 받는다. 승인 여부(True/False)를 돌려준다."""
    print(summary_text)
    print()

    while True:
        answer = input("이 내용을 카톡에 붙여넣어도 될까요? (y/n): ").strip().lower()
        if answer in ("y", "n"):
            break
        print("y 또는 n으로만 답해주세요.")

    print()
    if answer == "y":
        print("승인되었습니다. 아래 내용을 그대로 복사해서 카톡에 붙여넣으세요.")
        print()
        print(summary_text)
        return True

    print("승인되지 않았습니다. 원본 근태 데이터를 확인한 뒤 다시 실행해주세요.")
    return False
