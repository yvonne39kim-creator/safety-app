import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import db_manager

st.set_page_config(page_title="종합 기출문제", page_icon="🏫", layout="wide")

st.title("🏫 종합 기출문제")
st.markdown("원하는 연도, 회차 또는 여러 과목을 선택하여 종합적으로 기출문제를 풀어봅니다.")

# --- 데이터 로드 ---
@st.cache_data
def load_filter_data():
    conn = db_manager.get_connection()
    subjects_df = pd.read_sql_query("SELECT id, subject_name FROM subjects GROUP BY subject_name", conn)
    years_df = pd.read_sql_query("SELECT DISTINCT exam_year FROM questions ORDER BY exam_year DESC", conn)
    rounds_df = pd.read_sql_query("SELECT DISTINCT exam_round FROM questions ORDER BY exam_round", conn)
    conn.close()
    return subjects_df, years_df['exam_year'].tolist(), rounds_df['exam_round'].tolist()

def load_comprehensive_questions(selected_subjects, year, round_num):
    conn = db_manager.get_connection()
    
    # 동적 쿼리 생성
    query = "SELECT q.*, s.subject_name FROM questions q JOIN subjects s ON q.subject_id = s.id WHERE 1=1"
    params = []
    
    if selected_subjects:
        placeholders = ', '.join(['?'] * len(selected_subjects))
        query += f" AND s.subject_name IN ({placeholders})"
        params.extend(selected_subjects)
        
    if year != "전체":
        query += " AND q.exam_year = ?"
        params.append(year)
        
    if round_num != "전체":
        query += " AND q.exam_round = ?"
        params.append(round_num)
        
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

# --- 메인 로직 ---
try:
    subjects_df, available_years, available_rounds = load_filter_data()
    
    with st.sidebar.expander("📝 출제 필터 설정", expanded=True):
        selected_subjects = st.multiselect("과목 선택 (비워두면 전체 과목)", subjects_df['subject_name'].tolist())
        selected_year = st.selectbox("출제 연도", ["전체"] + available_years)
        selected_round = st.selectbox("회차", ["전체"] + available_rounds)
        
        load_btn = st.button("문제 불러오기")

    # 세션 스테이트 관리
    if load_btn:
        st.session_state.comp_questions = load_comprehensive_questions(selected_subjects, selected_year, selected_round)
        st.session_state.comp_submitted = False
        st.session_state.comp_answers = {}
        
    # 문제가 로드된 경우 렌더링
    if 'comp_questions' in st.session_state and not st.session_state.comp_questions.empty:
        q_df = st.session_state.comp_questions
        st.info(f"총 {len(q_df)}문제가 로드되었습니다.")
        
        with st.form(key="comp_exam_form"):
            for idx, row in q_df.iterrows():
                q_id = row['id']
                st.markdown(f"**문제 {idx + 1}. [{row['subject_name']}]** (출제년도: {row['exam_year']}-{row['exam_round']}회)")
                st.write(row['question_text'])
                
                options = {1: row['option_1'], 2: row['option_2'], 3: row['option_3'], 4: row['option_4']}
                
                # 라디오 버튼 그룹
                user_choice = st.radio(
                    f"보기 (문제 {idx + 1})",
                    options=list(options.keys()),
                    format_func=lambda x: f"{x}. {options[x]}",
                    index=None,
                    key=f"cq_{q_id}",
                    label_visibility="collapsed"
                )
                
                # 채점 결과 및 해설을 문제 바로 아래에 표시
                if st.session_state.get('comp_submitted', False):
                    correct_ans = row['correct_answer']
                    user_ans = st.session_state.get(f"cq_{q_id}")
                    
                    if user_ans == correct_ans:
                        st.success(f"**정답입니다!**")
                    else:
                        st.error(f"**틀렸습니다.** (선택: {user_ans if user_ans else '미선택'}, 정답: {correct_ans})")
                        with st.expander("📖 해설 보기", expanded=True):
                            st.markdown(f"{row['explanation']}")
                            
                st.markdown("---")
            
            submit_comp = st.form_submit_button("채점 및 결과보기")
            
        if submit_comp:
            st.session_state.comp_submitted = True
            st.rerun()
            
        # 전체 결과 요약만 하단에 표시
        if st.session_state.get('comp_submitted', False):
            st.header("💯 최종 채점 결과")
            
            correct_count = 0
            for idx, row in q_df.iterrows():
                q_id = row['id']
                if st.session_state.get(f"cq_{q_id}") == row['correct_answer']:
                    correct_count += 1
            
            score_percent = (correct_count / len(q_df)) * 100
            st.metric(label="최종 점수", value=f"{correct_count} / {len(q_df)} ( {score_percent:.1f}점 )")
            
            if score_percent >= 60:
                st.balloons()
                st.success("🎉 합격권입니다! 훌륭합니다.")
            else:
                st.warning("💪 아쉽습니다. 오답을 다시 한번 확인해 보세요.")
                
            if st.button("돌아가기 (새로운 조건으로 풀기)"):
                st.session_state.comp_submitted = False
                st.session_state.comp_questions = pd.DataFrame() # 초기화
                st.rerun()

    elif 'comp_questions' in st.session_state and st.session_state.comp_questions.empty:
        st.warning("선택한 조건에 맞는 기출문제가 없습니다.")
    else:
        st.info("👈 왼쪽 사이드바에서 문제 조건을 선택하고 '문제 불러오기'를 클릭하세요.")

except Exception as e:
    st.error(f"오류가 발생했습니다: {e}")
