import streamlit as st
import pandas as pd
import sys
import os
import plotly.express as px
import plotly.graph_objects as go

# 상위 경로를 시스템 패스에 추가하여 db_manager 임포트
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
try:
    import db_manager
except ModuleNotFoundError:
    sys.path.append(os.path.dirname(__file__))
    import db_manager

st.set_page_config(
    page_title="산업안전기사 취득 도우미",
    page_icon="👷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Minimalist Design
st.markdown("""
<style>
    /* 세련된 미니멀리즘 배경 */
    .stApp {
        background-color: #F8FAFC !important;
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, 'Helvetica Neue', 'Segoe UI', 'Apple SD Gothic Neo', 'Noto Sans KR', 'Malgun Gothic', sans-serif;
    }
    
    /* 사이드바 최상단 기존 'app' 메뉴 숨기기 */
    div[data-testid="stSidebarNav"] li:first-child {
        display: none !important;
    }
    
    /* 타이틀 및 헤더 */
    h1 {
        color: #0F172A;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-bottom: 0.5rem;
    }
    h2, h3, h4 {
        color: #1E293B;
        font-weight: 700;
        letter-spacing: -0.3px;
    }
    
    /* 대안적인 p 구문 색상 조정 */
    p {
        color: #475569;
        font-size: 1.05rem;
        line-height: 1.6;
    }
    
    /* 대시보드 메트릭 박스 (클린, 애플 스타일 섀도우) */
    [data-testid="stMetricValue"] {
        font-size: 2.4rem;
        color: #0F172A;
        font-weight: 800;
        margin-bottom: -5px;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.95rem;
        color: #64748B;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* 미니멀 카드 UI */
    .css-1wivap2, .css-1r6slb0, .css-1n76uvr, .st-emotion-cache-1wivap2, [data-testid="stVerticalBlock"] > div > div { 
        background: #FFFFFF !important;
        border-radius: 16px !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03) !important;
        padding: 24px !important;
        margin-bottom: 24px !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .css-1wivap2:hover, [data-testid="stVerticalBlock"] > div > div:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.04) !important;
    }

    /* 버튼 스타일 조정 (모던 플랫) */
    .stButton>button {
        background-color: #1E293B;
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-size: 1rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #334155;
        color: #FFFFFF;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    /* 새로 도입할 가이드 카드 레이아웃 */
    .guide-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
        gap: 24px;
        margin-top: 30px;
        margin-bottom: 40px;
    }
    .guide-card {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 30px 24px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        text-align: left;
    }
    .guide-card:hover {
        transform: translateY(-6px);
        border-color: #818CF8;
        box-shadow: 0 20px 25px -5px rgba(99, 102, 241, 0.1), 0 10px 10px -5px rgba(99, 102, 241, 0.04);
    }
    .guide-icon {
        font-size: 2.2rem;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #EEF2FF;
        color: #4F46E5;
        width: 64px;
        height: 64px;
        border-radius: 14px;
    }
    .guide-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 12px;
        letter-spacing: -0.3px;
    }
    .guide-desc {
        font-size: 0.95rem;
        color: #64748B;
        line-height: 1.6;
        margin: 0;
    }

    /* 오류 경고 알림 등 모던하게 */
    .stAlert {
        border-radius: 12px !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("나의 학습 대시보드")
    st.markdown("""
    산업안전기사 자격증 취득을 위한 완벽한 동반자입니다.  
    현재 누적된 **나의 학습 성과**를 한눈에 확인하고, 체계적으로 실력을 향상시키세요.
    """)    
    
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # 대시보드 렌더링 시작
    try:
        history_df, subject_df = db_manager.get_exam_history_stats()
        
        if history_df.empty:
            st.info("👋 환영합니다! 아직 학습 기록이 없습니다. 왼쪽 메뉴를 통해 첫 학습이나 시험을 시작해 보세요.")
            
            # --- 프리미엄 세련된 앱 활용 가이드 UI ---
            st.markdown("""
            <div class="guide-container">
                <div class="guide-card">
                    <div class="guide-icon">📚</div>
                    <div class="guide-title">1. 단계별 학습</div>
                    <p class="guide-desc">과목별 필수 핵심 이론을 읽고 요약하며 기초를 탄탄히 다집니다. 처음 시작하는 분들에게 추천합니다.</p>
                </div>
                <div class="guide-card">
                    <div class="guide-icon">🎯</div>
                    <div class="guide-title">2. 단원별 기출문제</div>
                    <p class="guide-desc">이론을 마친 후 각 세부 단원별로 할당된 문항을 풀이합니다. 오답 해설을 통해 개념을 완벽히 흡수하세요.</p>
                </div>
                <div class="guide-card">
                    <div class="guide-icon">📑</div>
                    <div class="guide-title">3. 종합 기출문제</div>
                    <p class="guide-desc">전체 범위에서 다양한 문제들을 랜덤으로 선택하여 풀이하며 모의고사에 대비한 감각을 익힙니다.</p>
                </div>
                <div class="guide-card">
                    <div class="guide-icon">⏳</div>
                    <div class="guide-title">4. 실전 모의고사</div>
                    <p class="guide-desc">실제 시험장과 동일한 환경으로 100문제를 시간 내에 응시하고, 성적 추이와 취약 과목을 분석받습니다.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            # --- 1. 핵심 지표 (Metrics) ---
            st.sidebar.markdown("---")
            st.sidebar.success("💡 꾸준히 학습 중이시네요! 멋집니다.")
            
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
                
            st.markdown("<br/>", unsafe_allow_html=True)
            
            # --- 2. 성적 추이 그래프 (Line Chart) ---
            st.subheader("📈 성적 추이")
            
            history_df['date_str'] = pd.to_datetime(history_df['test_date']).dt.strftime('%m-%d %H:%M')
            
            # 프리미엄 인디고 색상 매핑
            fig_line = px.line(
                history_df, 
                x='date_str', 
                y='total_score', 
                markers=True,
                labels={'total_score': '총점 (100점 만점)', 'date_str': '응시 일시'}
            )
            fig_line.update_traces(line_color='#4F46E5', line_width=3, marker=dict(size=8, color='#4F46E5'))
            fig_line.add_hline(y=60, line_dash="dash", line_color="#10B981", annotation_text="합격 기준선 (60점)", annotation_font_color="#10B981")
            
            # 깔끔한 레이아웃 적용
            fig_line.update_layout(
                yaxis_range=[0, 105], 
                plot_bgcolor='rgba(0,0,0,0)', 
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=30, b=20),
                xaxis=dict(showgrid=False),
                yaxis=dict(gridcolor='#E2E8F0')
            )
            st.plotly_chart(fig_line, use_container_width=True)
            
            # --- 3. 취약 과목 분석 (Radar Chart) ---
            if not subject_df.empty:
                st.markdown("<br/>", unsafe_allow_html=True)
                st.subheader("🎯 취약 과목 분석")
                
                subject_df['accuracy'] = (subject_df['correct_q'] / subject_df['total_q'] * 100).fillna(0)
                
                fig_radar = go.Figure()
                fig_radar.add_trace(go.Scatterpolar(
                    r=subject_df['accuracy'].tolist(),
                    theta=subject_df['subject_name'].tolist(),
                    fill='toself',
                    name='정답률',
                    fillcolor='rgba(99, 102, 241, 0.2)', # Indigo 반투명
                    line=dict(color='#4F46E5', width=2)
                ))
                
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100],
                            gridcolor='#E2E8F0',
                            linecolor='rgba(0,0,0,0)'
                        ),
                        angularaxis=dict(
                            gridcolor='#E2E8F0',
                            linecolor='rgba(0,0,0,0)'
                        ),
                        bgcolor='rgba(0,0,0,0)'
                    ),
                    showlegend=False,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=40, r=40, t=30, b=30)
                )
                
                col_chart, col_text = st.columns([5, 5])
                with col_chart:
                    st.plotly_chart(fig_radar, use_container_width=True)
                
                with col_text:
                    st.markdown("#### 과목별 누적 정답률")
                    styled_df = subject_df[['subject_name', 'accuracy']].copy()
                    styled_df['accuracy'] = styled_df['accuracy'].apply(lambda x: f"{x:.1f}%")
                    styled_df.columns = ['과목명', '정답률']
                    st.dataframe(styled_df, hide_index=True, use_container_width=True)
                    
                    weakest_subject = subject_df.loc[subject_df['accuracy'].idxmin()]
                    st.error(f"🚨 **집중 분석:** 현재 '{weakest_subject['subject_name']}' 과목의 정답률이 가장 저조({weakest_subject['accuracy']:.1f}%)합니다. 단원별 문제를 통해 반복 학습하는 것을 추천합니다.")
    
    except Exception as e:
        st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main()
