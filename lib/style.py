import streamlit as st


def render_footer() -> None:
    st.divider()
    st.caption("웨더트립은 정보 제공 목적의 서비스이며, 예약·결제 기능은 제공하지 않습니다.")


def patch_multiselect_select_all_label(new_label: str) -> None:
    """multiselect 드롭다운의 'Select all' 항목 텍스트를 교체한다.

    Streamlit은 이 문구를 바꿀 수 있는 공식 파라미터를 제공하지 않아,
    렌더링된 옵션 텍스트를 감시해 치환하는 최소한의 스크립트로 처리한다.
    Streamlit 프론트엔드가 문구를 바꾸면 이 패치도 함께 갱신해야 한다."""
    st.html(
        f"""
        <script>
        (function() {{
            if (window.__wtSelectAllPatched) {{ return; }}
            window.__wtSelectAllPatched = true;
            const relabel = () => {{
                document.querySelectorAll('[role="option"]').forEach((el) => {{
                    if (el.textContent.trim() === "Select all") {{
                        el.textContent = {new_label!r};
                    }}
                }});
            }};
            relabel();
            new MutationObserver(relabel).observe(document.body, {{ childList: true, subtree: true }});
        }})();
        </script>
        """,
        unsafe_allow_javascript=True,
    )
