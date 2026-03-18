import streamlit as st
import pandas as pd
import sys
import os
import plotly.express as px
import plotly.graph_objects as go

# 상위 경로를 시스템 패스에 추가하여 db_manager 임포트
sys.path.append(os.path.dirname(__file__))
import db_manager

st.set_page_config(
    page_title="산업안전기사 취득 도우미",
    page_icon="👷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for vibrant, mobile-friendly design across the app
st.markdown("""
<style>
    /* 화려한 애니메이션 그라데이션 배경 */
    .stApp {
        background: linear-gradient(-45deg, #ff9a9e, #fecfef, #a1c4fd, #c2e9fb);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        font-family: 'Pretendard', 'Noto Sans KR', sans-serif;
    }
    
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* 사이드바 최상단 기존 'app' 메뉴 숨기기 */
    div[data-testid="stSidebarNav"] li:first-child {
        display: none !important;
    }
    
    /* 헤더 및 텍스트 스타일링 */
    h1, h2, h3 {
        color: #1e272e;
        font-weight: 800;
        text-shadow: 2px 2px 4px rgba(255, 255, 255, 0.8);
    }
    
    /* 대시보드 및 일반 메트릭 박스 스타일 (고급 Glassmorphism 효과) */
    [data-testid="stMetricValue"] {
        font-size: 3rem;
        background: -webkit-linear-gradient(45deg, #ff6b6b, #c0392b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        text-shadow: 2px 2px 10px rgba(255, 107, 107, 0.3);
    }
    [data-testid="stMetricLabel"] {
        font-size: 1.2rem;
        color: #2c3e50;
        font-weight: 700;
    }
    
    /* 투명하고 입체적인 카드 UI */
    .css-1wivap2, .css-1r6slb0, .css-1n76uvr, .st-emotion-cache-1wivap2, [data-testid="stVerticalBlock"] > div > div { 
        background: rgba(255, 255, 255, 0.65) !important;
        backdrop-filter: blur(15px) !important;
        -webkit-backdrop-filter: blur(15px) !important;
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.8) !important;
        box-shadow: 0 10px 30px 0 rgba(31, 38, 135, 0.15) !important;
        padding: 25px !important;
        margin-bottom: 20px !important;
        transition: all 0.4s ease;
    }
    .css-1wivap2:hover, [data-testid="stVerticalBlock"] > div > div:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 15px 40px 0 rgba(31, 38, 135, 0.25) !important;
        background: rgba(255, 255, 255, 0.8) !important;
    }

    /* 버튼 스타일링 (네온 글로우 효과 적용) */
    .stButton>button {
        background: linear-gradient(90deg, #ff0844 0%, #ffb199 100%);
        color: white;
        border: none;
        border-radius: 50px;
        padding: 0.7rem 2rem;
        font-size: 1.2rem;
        font-weight: 900;
        box-shadow: 0 4px 15px rgba(255, 8, 68, 0.4);
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #ffb199 0%, #ff0844 100%);
        box-shadow: 0 8px 25px rgba(255, 8, 68, 0.6);
        transform: translateY(-3px) scale(1.05);
        color: #ffffff;
    }

    /* 모바일 환경 대응 */
    @media (max-width: 768px) {
        .stApp {
            padding: 5px;
        }
        h1 { font-size: 2rem !important; }
        h2 { font-size: 1.6rem !important; }
        h3 { font-size: 1.3rem !important; }
        [data-testid="stMetricValue"] { font-size: 2.2rem; }
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("👷‍♂️ 나의 학습 대시보드 (산업안전기사)")
    st.markdown("""
    환영합니다! 이 메인 화면은 **사용자님의 학습 성과를 한눈에 보여주는 대시보드**입니다.  
    👈 왼쪽 메뉴를 통해 새로운 기출문제나 이론을 학습해 보세요!
    """)    
    
    st.markdown("---")
    
    # 대시보드 렌더링 시작
    try:
        history_df, subject_df = db_manager.get_exam_history_stats()
        
        if history_df.empty:
            st.info("💡 아직 학습 기록이 없습니다. 왼쪽 메뉴에서 '실전 모의고사'나 '기출문제'를 풀면 이곳에 멋진 통계 그래프가 나타납니다!")
            
            # 앱 주요 가이드 안내문 (기록이 없을 때만 표시)
            st.markdown("""
            ### 📚 앱 활용 가이드
            *   **단계별 학습 (이론):** 과목별 핵심 이론 요약 및 설명
            *   **단원별 기출문제:** 단원별 문제 풀이 및 오답 시 상세 해설 제공
            *   **종합 기출문제:** 전체 범위에서 다양한 문제를 선택하여 풀이
            *   **실전 모의고사:** 실제 시험과 동일한 환경으로 모의고사 응시 및 자동 채점
            """)
        else:
            # --- 1. 핵심 지표 (Metrics) ---
            st.subheader("💡 핵심 학습 지표")
            col1, col2, col3 = st.columns(3)
            
            total_exams = len(history_df)
            passed_exams = history_df['is_passed'].sum()
            pass_rate = (passed_exams / total_exams * 100) if total_exams > 0 else 0
            
            avg_score = history_df['total_score'].mean()
            
            with col1:
                st.metric("총 응시 횟수", f"{total_exams} 회")
            with col2:
                st.metric("평균 점수", f"{avg_score:.1f} 점")
            with col3:
                st.metric("모의고사 합격률", f"{pass_rate:.1f} %")
                
            st.markdown("---")
            
            # --- 2. 성적 추이 그래프 (Line Chart) ---
            st.subheader("📈 성적 추이 (최근 응시 기록 기준)")
            
            history_df['date_str'] = pd.to_datetime(history_df['test_date']).dt.strftime('%m-%d %H:%M')
            
            fig_line = px.line(
                history_df, 
                x='date_str', 
                y='total_score', 
                markers=True,
                title="나의 점수 변화 곡선",
                labels={'total_score': '총점 (100점 만점)', 'date_str': '응시 일시'},
                color_discrete_sequence=['#ff7675'] # 화사한 코랄색
            )
            fig_line.add_hline(y=60, line_dash="dash", line_color="green", annotation_text="합격선 (60점)")
            fig_line.update_layout(yaxis_range=[0, 105], plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_line, use_container_width=True)
            
            # --- 3. 취약 과목 분석 (Radar Chart) ---
            if not subject_df.empty:
                st.markdown("---")
                st.subheader("🎯 취약 과목 분석 (누적 정답률)")
                
                subject_df['accuracy'] = (subject_df['correct_q'] / subject_df['total_q'] * 100).fillna(0)
                
                fig_radar = go.Figure()
                fig_radar.add_trace(go.Scatterpolar(
                    r=subject_df['accuracy'].tolist(),
                    theta=subject_df['subject_name'].tolist(),
                    fill='toself',
                    name='과목별 정답률',
                    fillcolor='rgba(116, 185, 255, 0.5)', # 파스텔 블루 반투명
                    line=dict(color='#0984e3', width=2)
                ))
                
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100]
                        )
                    ),
                    showlegend=False,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                
                col_chart, col_text = st.columns([6, 4])
                with col_chart:
                    st.plotly_chart(fig_radar, use_container_width=True)
                
                with col_text:
                    st.markdown("#### 과목별 상세 데이터")
                    styled_df = subject_df[['subject_name', 'accuracy']].copy()
                    styled_df['accuracy'] = styled_df['accuracy'].apply(lambda x: f"{x:.1f}%")
                    styled_df.columns = ['과목명', '정답률']
                    st.dataframe(styled_df, hide_index=True, use_container_width=True)
                    
                    weakest_subject = subject_df.loc[subject_df['accuracy'].idxmin()]
                    st.warning(f"🚨 **집중 학습 필요:** '{weakest_subject['subject_name']}' 과목의 정답률이 {weakest_subject['accuracy']:.1f}%로 가장 낮습니다. 먼저 복습해 보세요!")
    
    except Exception as e:
        st.error(f"대시보드 데이터를 불러오는 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main()
