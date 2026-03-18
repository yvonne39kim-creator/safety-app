import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import db_manager

st.set_page_config(page_title="단원별 기출문제", page_icon="📝", layout="wide")

st.title("📝 단원별 기출문제")
st.markdown("특정 단원의 기출문제를 풀어보고, **틀렸을 경우에만** 아래에 해설을 확인할 수 있습니다.")

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
             # 선택한 과목과 넘어온 단원의 과목이 일치할 때만 단원 기본값 적용
             if selected_subject == st.session_state.get('pre_selected_subject'):
                 default_chapter_idx = chapter_ids.index(st.session_state['pre_selected_chapter'])
        
        selected_subject_id = st.sidebar.selectbox(
            "단원", 
            options=chapter_ids, 
            index=default_chapter_idx,
            format_func=lambda x: chapter_options[x]
        )
        
        # 적용 후 세션의 사전 선택값 초기화 (사용자가 이후 자유롭게 변경할 수 있도록)
        if 'pre_selected_subject' in st.session_state:
            del st.session_state['pre_selected_subject']
        if 'pre_selected_chapter' in st.session_state:
            del st.session_state['pre_selected_chapter']
        
        # 선택된 단원의 문제 불러오기
        questions_df = load_questions(selected_subject_id)
        
        st.subheader(f"{selected_subject} - {chapter_options[selected_subject_id]}")
        
        if not questions_df.empty:
            # 세션 스테이트 초기화 (사용자 답안 저장용)
            if 'answers' not in st.session_state:
                st.session_state.answers = {}
            if 'submitted' not in st.session_state:
                st.session_state.submitted = False
                
            # 단원이 바뀌면 세션 스테이트 초기화
            if 'current_chapter' not in st.session_state or st.session_state.current_chapter != selected_subject_id:
                st.session_state.answers = {}
                st.session_state.submitted = False
                st.session_state.current_chapter = selected_subject_id
            
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
                    
                    # 라디오 버튼으로 보기 제공 (초기 선택 없음)
                    user_choice = st.radio(
                        "보기",
                        options=list(options.keys()),
                        format_func=lambda x: f"{x}. {options[x]}",
                        index=None,
                        key=f"q_{q_id}"
                    )
                    
                    # 채점 결과 및 해설을 문제 바로 아래에 표시
                    if st.session_state.submitted:
                        correct_ans = row['correct_answer']
                        user_ans = st.session_state.get(f"q_{q_id}")
                        
                        if user_ans == correct_ans:
                            st.success(f"**정답입니다!**")
                        else:
                            st.error(f"**틀렸습니다.** (선택: {user_ans if user_ans else '미선택'}, 정답: {correct_ans})")
                            with st.expander(f"📖 문제 {idx + 1} 해설 보기", expanded=True):
                                st.markdown(f"**왜 틀렸을까요?**\n\n{row['explanation']}")
                
                # 제출 버튼
                submit_button = st.form_submit_button(label="채점하기")

            # 제출 버튼이 눌렸을 때 결과 처리
            if submit_button:
                st.session_state.submitted = True
                st.rerun() # UI 업데이트를 위해 리런
                
            if st.session_state.submitted:
                st.markdown("---")
                st.header("📊 최종 채점 결과")
                
                correct_count = 0
                total_questions = len(questions_df)
                
                for idx, row in questions_df.iterrows():
                    q_id = row['id']
                    if st.session_state.get(f"q_{q_id}") == row['correct_answer']:
                        correct_count += 1
                        
                st.metric(label="총 점수", value=f"{correct_count} / {total_questions} 정답")
                
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
