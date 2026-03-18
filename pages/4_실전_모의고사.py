import streamlit as st
import pandas as pd
import sys
import os
import random

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import db_manager

st.set_page_config(page_title="실전 모의고사", page_icon="🏆", layout="wide")

st.title("🏆 실전 모의고사")
st.markdown("실제 시험과 유사하게 과목별로 20문제씩 랜덤하게 추출하여 모의고사를 실시합니다. 제한 시간은 없지만 실전처럼 집중해서 풀어보세요!")

def generate_mock_exam():
    conn = db_manager.get_connection()
    
    # 1. 모든 과목 가져오기
    subjects_df = pd.read_sql_query("SELECT id, subject_name FROM subjects GROUP BY subject_name", conn)
    
    mock_questions = []
    
    # 2. 각 과목별로 랜덤하게 문제 추출 (실제로는 과목당 20문제, 여기서는 샘플 데이터 고려하여 최대치 추출)
    for _, row in subjects_df.iterrows():
        subject_name = row['subject_name']
        
        # 해당 과목의 모든 문제 가져오기 (ORDER BY RANDOM() 사용 시 SQLite에서 지원하지만, Pandas로 처리)
        query = f"SELECT q.*, s.subject_name FROM questions q JOIN subjects s ON q.subject_id = s.id WHERE s.subject_name = '{subject_name}'"
        q_df = pd.read_sql_query(query, conn)
        
        if not q_df.empty:
            # 샘플 데이터량이 적을 수 있으므로 존재하는 문제 전부 또는 최대 20문제 샘플링
            sample_size = min(20, len(q_df))
            sampled_df = q_df.sample(n=sample_size).reset_index(drop=True)
            mock_questions.append(sampled_df)
            
    conn.close()
    
    if mock_questions:
        return pd.concat(mock_questions, ignore_index=True)
    return pd.DataFrame()

# --- 메인 로직 ---
if st.button("새로운 실전 모의고사 시작하기", type="primary") or 'mock_exam_df' not in st.session_state:
    with st.spinner("모의고사를 생성하는 중입니다..."):
        st.session_state.mock_exam_df = generate_mock_exam()
        st.session_state.mock_submitted = False

if not st.session_state.mock_exam_df.empty:
    df = st.session_state.mock_exam_df
    st.info(f"총 {len(df)}문제가 출제되었습니다. 제출 후 자동 채점됩니다.")
    
    with st.form(key="mock_exam_form"):
        # 과목별로 분리해서 보여주기
        current_subject = ""
        questions_per_subject = {}
        
        for idx, row in df.iterrows():
            if current_subject != row['subject_name']:
                current_subject = row['subject_name']
                st.markdown(f"### 📌 과목 : {current_subject}")
                
            q_id = row['id']
            st.markdown(f"**{idx + 1}. {row['question_text']}**")
            
            options = {1: row['option_1'], 2: row['option_2'], 3: row['option_3'], 4: row['option_4']}
            user_choice = st.radio(
                f"보기",
                options=list(options.keys()),
                format_func=lambda x: f"{x}. {options[x]}",
                index=None,
                key=f"mock_q_{q_id}",
                label_visibility="collapsed"
            )
            
            # 채점 결과 및 해설을 문제 바로 아래에 표시
            if st.session_state.get('mock_submitted', False):
                correct_ans = row['correct_answer']
                user_ans = st.session_state.get(f"mock_q_{q_id}")
                
                if user_ans == correct_ans:
                    st.success(f"**정답입니다!**")
                else:
                    st.error(f"**틀렸습니다.** (선택: {user_ans if user_ans else '미선택'}, 정답: {correct_ans})")
                    with st.expander("📖 해설 보기", expanded=True):
                        st.markdown(f"{row['explanation']}")
                        
            st.markdown("---")
            
        submit_mock = st.form_submit_button("최종 답안 제출 및 채점하기", use_container_width=True)

    if submit_mock:
        st.session_state.mock_submitted = True
        st.rerun()
        
    if st.session_state.get('mock_submitted', False):
        st.header("📈 최종 모의고사 결과 분석")
        
        total_questions = len(df)
        total_correct = 0
        subject_scores = {} # 과목별 점수 저장
        
        # 과목 목록 초기화
        for subject in df['subject_name'].unique():
            subject_scores[subject] = {'total': 0, 'correct': 0}
            
        for idx, row in df.iterrows():
            q_id = row['id']
            subj = row['subject_name']
            
            subject_scores[subj]['total'] += 1
            
            user_ans = st.session_state.get(f"mock_q_{q_id}")
            if user_ans == row['correct_answer']:
                total_correct += 1
                subject_scores[subj]['correct'] += 1
                
        # 총점 계산 (100점 만점 기준)
        final_score = (total_correct / total_questions) * 100
        
        # 합격 여부 판단 (평균 60점 이상, 과락 40점 미만 없음)
        is_passed = True
        fail_reasons = []
        
        if final_score < 60:
            is_passed = False
            fail_reasons.append("평균 점수 60점 미만")
            
        col1, col2 = st.columns(2)
        with col1:
            st.metric("총점", f"{final_score:.1f} 점")
        
        # 과목별 상세 점수 및 과락 체크
        st.subheader("과목별 상세 점수")
        for subj, counts in subject_scores.items():
            subj_score = (counts['correct'] / counts['total']) * 100
            if subj_score < 40:
                is_passed = False
                fail_reasons.append(f"{subj} 과목 과락 (40점 미만)")
                st.error(f"{subj}: {counts['correct']}/{counts['total']} ({subj_score:.1f}점) - **과락 주의!**")
            else:
                st.success(f"{subj}: {counts['correct']}/{counts['total']} ({subj_score:.1f}점)")
                
        # 최종 합격 판별
        with col2:
            if is_passed:
                st.success("🎉 **최종 판정: 합격입니다!**")
                st.balloons()
            else:
                st.error("🚨 **최종 판정: 불합격입니다.**")
                st.write("**불합격 사유:**", ", ".join(fail_reasons))
                
        # --- DB에 시험 결과 저장 로직 추가 ---
        if not st.session_state.get('mock_saved', False):
            # 오답 내역 요약 생성
            wrong_details = [
                {"q_id": int(row['id']), "subject": row['subject_name'], "user_ans": st.session_state.get(f"mock_q_{row['id']}"), "correct_ans": int(row['correct_answer'])}
                for _, row in df.iterrows() if st.session_state.get(f"mock_q_{row['id']}") != row['correct_answer']
            ]
            
            # DB 저장 함수 호출
            db_manager.save_exam_result(
                test_type='모의고사',
                total_score=int(final_score),
                is_passed=is_passed,
                details={'fail_reasons': fail_reasons, 'wrong_problems': wrong_details},
                subject_scores=subject_scores
            )
            st.session_state.mock_saved = True # 중복 저장 방지
            st.info("💾 채점 결과가 대시보드에 자동 저장되었습니다!")
            
        # 오답 노트 제공

else:
    st.warning("데이터베이스에 문제 데이터가 충분하지 않습니다.")
