import streamlit as st
import pandas as pd
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import db_manager

st.set_page_config(page_title="단원별 기출문제", page_icon="📝", layout="wide")

st.title("📝 단원별 기출문제")
st.markdown("툭정 단원의 기출문제를 풀어보고, **틀렸을 경우에만** 아래에 해설을 확인할 수 있습니다.")

# --- 데이터 로드 함수 ---
@st.cache_data
def load_subjects():
    conn = db_manager.get_connection()
    df = pd.read_sql_query("SELECT id, subject_name, chapter_name FROM subjects ORDER BY id", conn)
    conn.close()
    return df

def load_questions(subject_id):
    conn = db_manager.get_connection()
    df = pd.read_sql_query(f"SELECT * FROM questions WHERE subject_id = {subject_id}", conn)
    conn.close()
    return df

# --- 메인 로직 ---
try:
    subjects_df = load_subjects()
    
    if not subjects_df.empty:
        # 사이드바에서 과목/단원 선택
        st.sidebar.header("학습 범위 선택")
        
        subject_list = subjects_df['subject_name'].unique().tolist()
        
        # 세션 스테이트에 저장된 사전 선택값(1_단계별_학습에서 넘어온 값) 확인
        default_subject_idx = 0
        if 'pre_selected_subject' in st.session_state and st.session_state['pre_selected_subject'] in subject_list:
            default_subject_idx = subject_list.index(st.session_state['pre_selected_subject'])
            
        selected_subject = st.sidebar.selectbox("과목", subject_list, index=default_subject_idx)
        
        filtered_chapters = subjects_df[subjects_df['subject_name'] == selected_subject]
        chapter_ids = filtered_chapters['id'].tolist()
        chapter_options = dict(zip(filtered_chapters['id'], filtered_chapters['chapter_name']))
        
        default_chapter_idx = 0
        if 'pre_selected_chapter' in st.session_state and st.session_state['pre_selected_chapter'] in chapter_ids:
             if selected_subject == st.session_state.get('pre_selected_subject'):
                 default_chapter_idx = chapter_ids.index(st.session_state['pre_selected_chapter'])
        
        selected_subject_id = st.sidebar.selectbox(
            "단원", 
            options=chapter_ids, 
            index=default_chapter_idx,
            format_func=lambda x: chapter_options[x]
        )
        
        # 적용 후 초기화
        if 'pre_selected_subject' in st.session_state:
            del st.session_state['pre_selected_subject']
        if 'pre_selected_chapter' in st.session_state:
            del st.session_state['pre_selected_chapter']
        
        questions_df = load_questions(selected_subject_id)
        st.subheader(f"{selected_subject} - {chapter_options[selected_subject_id]}")
        
        if not questions_df.empty:
            # --- 세션 상태 통합 초기화 ---
            if 'answers' not in st.session_state: st.session_state.answers = {}
            if 'submitted' not in st.session_state: st.session_state.submitted = False
            if 'listen_mode' not in st.session_state: st.session_state.listen_mode = False
            if 'listen_idx' not in st.session_state: st.session_state.listen_idx = 0
            if 'listen_phase' not in st.session_state: st.session_state.listen_phase = "question"
            
            if 'current_chapter' not in st.session_state or st.session_state.current_chapter != selected_subject_id:
                st.session_state.answers = {}
                st.session_state.submitted = False
                st.session_state.listen_mode = False
                st.session_state.listen_idx = 0
                st.session_state.listen_phase = "question"
                st.session_state.current_chapter = selected_subject_id
            
            st.markdown("---")
            
            # 음성 강제 정지 트리거
            if st.session_state.get('stop_audio_trigger', False):
                import streamlit.components.v1 as components
                components.html("<script>window.speechSynthesis.cancel();</script>", height=0, width=0)
                st.session_state.stop_audio_trigger = False
                
            listen_toggle = st.toggle("🎧 **음성 지원 듣기 모드** (1문제씩 10초 간격 자동 진행)", value=st.session_state.listen_mode)
            
            if listen_toggle != st.session_state.listen_mode:
                st.session_state.listen_mode = listen_toggle
                st.session_state.listen_idx = 0
                st.session_state.listen_phase = "question"
                if not listen_toggle:
                    st.session_state.stop_audio_trigger = True
                st.rerun()

            if st.session_state.listen_mode:
                # ==========================================
                # [듣기 모드] 플래시카드 & TTS UI
                # ==========================================
                total_q = len(questions_df)
                if st.session_state.listen_idx >= total_q:
                    st.success("단원의 모든 문제를 전부 들었습니다! 수고하셨습니다. 🎉")
                    if st.button("처음부터 다시 듣기", type="primary"):
                        st.session_state.listen_idx = 0
                        st.session_state.listen_phase = "question"
                        st.rerun()
                else:
                    import streamlit.components.v1 as components
                    import re

                    def clean_for_speech(text):
                        if not isinstance(text, str): return ""
                        return re.sub(r'[*_#~\[\]\(\)\<\>\:\;\{\}\|\+\=\-]', ' ', text)
                    
                    row = questions_df.iloc[st.session_state.listen_idx]
                    q_num = st.session_state.listen_idx + 1
                    
                    st.progress(q_num / total_q, text=f"진행 상황: {q_num} / {total_q} 문제")
                    st.markdown(f"### 문제 {q_num}.")
                    st.markdown(f"**{row['question_text']}**")
                    st.markdown(f"1. {row['option_1']}  \n2. {row['option_2']}  \n3. {row['option_3']}  \n4. {row['option_4']}")
                    
                    if st.session_state.listen_phase == "question":
                        st.warning("⏱️ **음성 재생 중입니다... (10초 대기 후 자동으로 정답이 공개됩니다)**")
                        
                        safe_q = json.dumps(clean_for_speech(row['question_text']), ensure_ascii=False)
                        safe_o1 = json.dumps(clean_for_speech(row['option_1']), ensure_ascii=False)
                        safe_o2 = json.dumps(clean_for_speech(row['option_2']), ensure_ascii=False)
                        safe_o3 = json.dumps(clean_for_speech(row['option_3']), ensure_ascii=False)
                        safe_o4 = json.dumps(clean_for_speech(row['option_4']), ensure_ascii=False)
                        
                        js_code = f"""
                        <script>
                            window.speechSynthesis.cancel();
                            const text = {safe_q} + ". 1번, " + {safe_o1} + ". 2번, " + {safe_o2} + ". 3번, " + {safe_o3} + ". 4번, " + {safe_o4} + ". 정답을 생각해 보세요. 10초 뒤 정답을 공개합니다.";
                            const u = new SpeechSynthesisUtterance(text);
                            u.lang = 'ko-KR';
                            u.rate = 1.0;
                            u.onend = function() {{
                                setTimeout(() => {{
                                    const buttons = window.parent.document.querySelectorAll('button');
                                    const btn = Array.from(buttons).find(b => b.innerText.includes('정답 자동확인'));
                                    if(btn) btn.click();
                                }}, 10000); // 10초 대기 !!
                            }};
                            window.speechSynthesis.speak(u);
                        </script>
                        """
                        components.html(js_code, height=0, width=0)
                        
                        # 두 개의 버튼을 가로로 정렬
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("⏹️ 재생 정지 및 닫기", key="btn_stop_q", use_container_width=True):
                                st.session_state.listen_mode = False
                                st.session_state.stop_audio_trigger = True
                                st.rerun()
                        with col2:
                            if st.button("정답 바로 확인하기 ⏭️ (정답 자동확인)", key="btn_show_ans", type="primary", use_container_width=True):
                                st.session_state.listen_phase = "answer"
                                st.rerun()
                            
                    elif st.session_state.listen_phase == "answer":
                        st.success(f"✅ **정답: {row['correct_answer']}번**")
                        st.info(f"**해설:**\n\n{row['explanation']}")
                        
                        safe_ans = json.dumps(clean_for_speech(str(row['correct_answer'])), ensure_ascii=False)
                        safe_exp = json.dumps(clean_for_speech(row['explanation']), ensure_ascii=False)
                        
                        js_code2 = f"""
                        <script>
                            window.speechSynthesis.cancel();
                            const text = "정답은 " + {safe_ans} + "번 입니다. 해설. " + {safe_exp} + ". 잠시 후 다음 문제로 넘어갑니다.";
                            const u = new SpeechSynthesisUtterance(text);
                            u.lang = 'ko-KR';
                            u.rate = 1.0;
                            u.onend = function() {{
                                setTimeout(() => {{
                                    const buttons = window.parent.document.querySelectorAll('button');
                                    const btn = Array.from(buttons).find(b => b.innerText.includes('다음 문제 자동넘김'));
                                    if(btn) btn.click();
                                }}, 3000); // 해설은 3초만 대기!!
                            }};
                            window.speechSynthesis.speak(u);
                        </script>
                        """
                        components.html(js_code2, height=0, width=0)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("⏹️ 재생 정지 및 닫기", key="btn_stop_a", use_container_width=True):
                                st.session_state.listen_mode = False
                                st.session_state.stop_audio_trigger = True
                                st.rerun()
                        with col2:
                            if st.button("다음 문제로 ⏭️ (다음 문제 자동넘김)", key="btn_next_q", type="primary", use_container_width=True):
                                st.session_state.listen_idx += 1
                                st.session_state.listen_phase = "question"
                                st.rerun()
            else:
                # ==========================================
                # [일반 풀이 모드] 스크롤 리스트 폼
                # ==========================================
                with st.form(key="chapter_questions_form"):
                    for idx, row in questions_df.iterrows():
                        q_id = row['id']
                        
                        st.markdown("---")
                        st.markdown(f"**문제 {idx + 1}.** (출제년도: {row['exam_year']})")
                        st.markdown(f"**{row['question_text']}**")
                        
                        options = {
                            1: row['option_1'],
                            2: row['option_2'],
                            3: row['option_3'],
                            4: row['option_4']
                        }
                        
                        user_choice = st.radio(
                            "보기",
                            options=list(options.keys()),
                            format_func=lambda x: f"{x}. {options[x]}",
                            index=None,
                            key=f"q_{q_id}"
                        )
                        
                        if st.session_state.submitted:
                            correct_ans = row['correct_answer']
                            user_ans = st.session_state.get(f"q_{q_id}")
                            
                            if user_ans == correct_ans:
                                st.success(f"**정답입니다!**")
                            else:
                                st.error(f"**틀렸습니다.** (선택: {user_ans if user_ans else '미선택'}, 정답: {correct_ans})")
                                with st.expander(f"📖 문제 {idx + 1} 해설 보기", expanded=True):
                                    st.markdown(f"**왜 틀렸을까요?**\n\n{row['explanation']}")
                    
                    submit_button = st.form_submit_button(label="채점하기")

                if submit_button:
                    st.session_state.submitted = True
                    st.rerun()
                    
                if st.session_state.submitted:
                    st.markdown("---")
                    st.header("📊 최종 채점 결과")
                    correct_count = 0
                    total_q = len(questions_df)
                    for idx, row in questions_df.iterrows():
                        if st.session_state.get(f"q_{row['id']}") == row['correct_answer']:
                            correct_count += 1
                            
                    st.metric(label="총 점수", value=f"{correct_count} / {total_q} 정답")
                    if st.button("다시 풀기"):
                        st.session_state.submitted = False
                        for key in list(st.session_state.keys()):
                            if key.startswith("q_"):
                                del st.session_state[key]
                        st.rerun()

        else:
            st.info("현재 선택한 단원에 등록된 문제가 없습니다.")
            
    else:
        st.warning("데이터베이스에 과목 정보가 없습니다.")
        
except Exception as e:
    st.error(f"오류가 발생했습니다: {e}")
