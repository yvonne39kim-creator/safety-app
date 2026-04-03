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

# Custom CSS for Premium Minimalist Design (Card Gorilla Style)
st.markdown("""
<style>
    /* 세련된 폰트 및 배경 */
    .stApp {
        background-color: #F8F9FA !important;
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
    }
    
    /* 사이드바 보정 */
    div[data-testid="stSidebarNav"] li:first-child { display: none !important; }
    
    /* 화면 타이틀 숨기거나 스타일링 (Streamlit 기본 렌더링 요소 제어) */
    h1 { color: #111; font-weight: 800; letter-spacing: -1px; margin-bottom: 2rem; }
    
    /* 카드고릴라 섹션 타이틀 */
    .section-title {
        font-size: 1.6rem;
        font-weight: 800;
        color: #111;
        margin-bottom: 16px;
        letter-spacing: -0.5px;
    }

    .gorilla-container {
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
        margin-bottom: 40px;
    }

    /* 공통 카드 스타일 */
    .gorilla-card {
        flex: 1;
        min-width: 240px;
        border-radius: 20px;
        padding: 32px 24px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 250px;
    }
    .gorilla-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.08);
    }

    /* 카드 솔리드 컬러 (카드고릴라 레퍼런스 톤) */
    .card-orange { background: #FFC07F; color: #111; }
    .card-mint   { background: #A3D1C6; color: #111; }
    .card-green  { background: #CDE2C8; color: #111; }
    .card-yellow { background: #FDE68A; color: #111; }

    /* 카드 내부 글씨체 */
    .g-badge {
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 8px;
        color: rgba(0,0,0,0.5);
        display: flex;
        align-items: center;
        gap: 4px;
    }
    .g-title {
        font-size: 1.1rem;
        font-weight: 500;
        margin-bottom: 4px;
        line-height: 1.2;
        color: #333;
    }
    .g-subtitle {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -1.5px;
        margin-bottom: 30px;
        line-height: 1.1;
        color: #111;
    }
    
    /* 하단 버튼 스타일 */
    .g-btn {
        display: inline-block;
        background: rgba(255,255,255,0.4);
        color: #111;
        padding: 8px 20px;
        border-radius: 24px;
        font-size: 0.95rem;
        font-weight: 700;
        width: fit-content;
        transition: background 0.2s;
        border: none;
        cursor: pointer;
    }
    .g-btn:hover { background: rgba(255,255,255,0.7); }

    /* 카드 우측 하단 큰 아이콘 */
    .g-bg-icon {
        position: absolute;
        right: -10px;
        bottom: -15px;
        font-size: 7rem;
        opacity: 0.2;
        pointer-events: none;
    }
    
    /* 대안적인 메트릭 박스 커스터마이징 */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        letter-spacing: -1px;
    }
    div[data-testid="metric-container"] {
        background: #fff;
        padding: 24px 30px;
        border-radius: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
        border: 1px solid #f1f3f5;
    }
</style>
""", unsafe_allow_html=True)

def main():
    try:
        history_df, subject_df = db_manager.get_exam_history_stats()
        
        if history_df.empty:
            st.markdown("""
            <div class="section-title">학습 가이드차트</div>
            <div class="gorilla-container">
                <div class="gorilla-card card-orange">
                    <div>
                        <div class="g-badge">🕒 Level 1</div>
                        <div class="g-title">기초를 탄탄하게</div>
                        <div class="g-subtitle">단계별 학습</div>
                        <div class="g-btn">보러가기</div>
                    </div>
                    <div class="g-bg-icon">📚</div>
                </div>
                <div class="gorilla-card card-mint">
                    <div>
                        <div class="g-badge">🕒 Level 2</div>
                        <div class="g-title">개념 완벽 흡수</div>
                        <div class="g-subtitle">단원별 문제</div>
                        <div class="g-btn">보러가기</div>
                    </div>
                    <div class="g-bg-icon">🎯</div>
                </div>
                <div class="gorilla-card card-green">
                    <div>
                        <div class="g-badge">🕒 Level 3</div>
                        <div class="g-title">실시간 기출풀이</div>
                        <div class="g-subtitle">종합 100제</div>
                        <div class="g-btn">보러가기</div>
                    </div>
                    <div class="g-bg-icon">📑</div>
                </div>
                <div class="gorilla-card card-yellow">
                    <div>
                        <div class="g-badge">🕒 Level 4</div>
                        <div class="g-title">합격 당락 결정</div>
                        <div class="g-subtitle">실전 모의고사</div>
                        <div class="g-btn">보러가기</div>
                    </div>
                    <div class="g-bg-icon">⏳</div>
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
