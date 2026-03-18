import streamlit as st
import pandas as pd
import sys
import os

# 상대 경로로 db_manager 임포트
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import db_manager

st.set_page_config(page_title="단계별 학습", page_icon="📖", layout="wide")

st.title("📖 단계별 학습 (이론 요약)")
st.markdown("산업안전기사 과목별 핵심 이론을 학습할 수 있습니다.")

def load_subjects():
    conn = db_manager.get_connection()
    df = pd.read_sql_query("SELECT id, subject_name, chapter_name, description FROM subjects ORDER BY id", conn)
    conn.close()
    return df

try:
    subjects_df = load_subjects()
    
    if not subjects_df.empty:
        # 과목 선택
        subject_list = subjects_df['subject_name'].unique().tolist()
        selected_subject = st.selectbox("과목을 선택하세요", subject_list)
        
        # 선택한 과목의 단원 목록 필터링
        filtered_df = subjects_df[subjects_df['subject_name'] == selected_subject]
        
        if not filtered_df.empty:
            # 단원 탭 생성
            chapters = filtered_df['chapter_name'].tolist()
            tabs = st.tabs(chapters)
            
            for i, tab in enumerate(tabs):
                with tab:
                    chapter_row = filtered_df.iloc[i]
                    st.subheader(chapter_row['chapter_name'])
                    
                    # 🎧 듣기 버튼 추가 (JS Web Speech API 활용)
                    if st.button(f"🎧 '{chapter_row['chapter_name']}' 핵심 이론 듣기", key=f"listen_btn_{chapter_row['id']}", use_container_width=True):
                        import json
                        import streamlit.components.v1 as components
                        
                        safe_desc = json.dumps(chapter_row['description'], ensure_ascii=False)
                        js_code = f"""
                        <script>
                            window.speechSynthesis.cancel();
                            const text = {safe_desc};
                            const u = new SpeechSynthesisUtterance(text);
                            u.lang = 'ko-KR';
                            u.rate = 1.0;
                            window.speechSynthesis.speak(u);
                        </script>
                        """
                        components.html(js_code, height=0, width=0)
                        st.toast("🔊 이론 낭독을 시작합니다.")
                    
                    # 카드 UI 형태로 설명 표시 (HTML 부분과 마크다운 부분을 분리하여 렌더링 오류 방지)
                    st.markdown('<div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-top: 10px; font-size: 16px;">', unsafe_allow_html=True)
                    st.markdown(chapter_row['description'])
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.info("💡 팁: 실제 데이터가 추가되면 여기에 더 자세한 핵심 요약, 공식, 암기 팁 등이 들어갈 수 있습니다.")
                    
                    # 기출문제 풀러가기 버튼 (페이지 이동 로직)
                    if st.button(f"'{chapter_row['chapter_name']}' 기출문제 풀러가기", key=f"btn_{chapter_row['id']}"):
                        # 사이드바 선택값을 미리 세션에 설정하여 2_단원별_기출문제에서 바로 해당 단원이 나오게 함
                        st.session_state['pre_selected_subject'] = selected_subject
                        st.session_state['pre_selected_chapter'] = chapter_row['id']
                        st.switch_page("pages/2_단원별_기출문제.py")
    else:
        st.warning("등록된 학습 자료(단원 정보)가 없습니다. 관리자에게 문의하세요.")
        
except Exception as e:
    st.error(f"데이터베이스 오류가 발생했습니다: {e}")
