import streamlit as st
import streamlit.components.v1 as components

st.title("TTS Test")

if 'q_idx' not in st.session_state:
    st.session_state.q_idx = 1

st.write(f"현재 문제: {st.session_state.q_idx}번")

if st.button("다음 문제 넘어가기 (수동)"):
    st.session_state.q_idx += 1
    st.rerun()

if st.button("듣기 모드 시작"):
    st.session_state.listening = True
    st.rerun()

if st.session_state.get('listening'):
    st.write(f"🔊 {st.session_state.q_idx}번 문제를 읽는 중입니다...")
    
    # 1초 후 읽기 끝났다고 가정, 3초 지연 후 다음 문제 버튼 클릭 테스트
    js = f"""
    <script>
        const u = new SpeechSynthesisUtterance("{st.session_state.q_idx}번 문제입니다. 안녕하세요.");
        u.lang = 'ko-KR';
        u.onend = function() {{
            console.log("Speech ended. Waiting 3s...");
            setTimeout(() => {{
                // Find parent button
                const buttons = window.parent.document.querySelectorAll('button');
                const nextBtn = Array.from(buttons).find(b => b.innerText.includes('다음 문제 넘어가기'));
                if (nextBtn) {{
                    console.log("Clicking next!");
                    nextBtn.click();
                }}
            }}, 3000);
        }};
        window.speechSynthesis.speak(u);
    </script>
    """
    components.html(js, height=0, width=0)
