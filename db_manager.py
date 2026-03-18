import sqlite3
import pandas as pd
import os
import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "safety_engineer.db")

def get_connection():
    """데이터베이스 연결 객체를 반환합니다."""
    # check_same_thread=False는 Streamlit 환경에서 스레드 문제를 방지하기 위해 사용
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    # 결과를 딕셔너리 형태로 반환받기 위해 row_factory 설정
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """데이터베이스 초기화 및 필요한 테이블을 생성합니다."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. 과목 및 단원 정보 (학습용)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_name TEXT NOT NULL,
        chapter_name TEXT NOT NULL,
        description TEXT
    )
    ''')
    
    # 2. 기출문제 테이블
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_id INTEGER,
        exam_year INTEGER,
        exam_round INTEGER,
        question_text TEXT NOT NULL,
        option_1 TEXT NOT NULL,
        option_2 TEXT NOT NULL,
        option_3 TEXT NOT NULL,
        option_4 TEXT NOT NULL,
        correct_answer INTEGER NOT NULL,
        explanation TEXT,
        image_path TEXT, -- 문제에 관련된 이미지 경로 (필요 시)
        FOREIGN KEY (subject_id) REFERENCES subjects (id)
    )
    ''')
    
    # 3. 사용자 학습 기록 (모의고사 등 채점 기록)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS exam_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        test_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        test_type TEXT, -- '단원별', '종합', '모의고사'
        total_score INTEGER,
        is_passed BOOLEAN,
        details TEXT -- JSON 형태로 오답 내역 등 상세 정보 저장
    )
    ''')
    
    # 4. 취약 과목 분석을 위한 저장 테이블 (모의고사 채점 시 과목별 데이터 저장용)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS exam_subject_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        history_id INTEGER,
        subject_name TEXT,
        total_questions INTEGER,
        correct_answers INTEGER,
        FOREIGN KEY (history_id) REFERENCES exam_history (id)
    )
    ''')

    conn.commit()
    conn.close()

def save_exam_result(test_type, total_score, is_passed, details, subject_scores=None):
    """모의고사 및 기출문제 풀이 결과를 DB에 저장합니다."""
    import json
    conn = get_connection()
    cursor = conn.cursor()
    
    details_json = json.dumps(details, ensure_ascii=False) if details else "{}"
    
    cursor.execute('''
        INSERT INTO exam_history (test_type, total_score, is_passed, details)
        VALUES (?, ?, ?, ?)
    ''', (test_type, total_score, is_passed, details_json))
    
    history_id = cursor.lastrowid
    
    # 과목별 상세 성적이 있다면 (모의고사 등)
    if subject_scores:
        for subj, counts in subject_scores.items():
            cursor.execute('''
                INSERT INTO exam_subject_scores (history_id, subject_name, total_questions, correct_answers)
                VALUES (?, ?, ?, ?)
            ''', (history_id, subj, counts['total'], counts['correct']))
            
    conn.commit()
    conn.close()
    return history_id

def get_exam_history_stats():
    """대시보드 통계용 데이터를 로드합니다."""
    conn = get_connection()
    
    # 전체 응시 이력
    history_df = pd.read_sql_query("SELECT * FROM exam_history ORDER BY test_date", conn)
    
    # 과목별 통계 (모의고사 기준 누적 데이터)
    subject_df = pd.read_sql_query('''
        SELECT subject_name, SUM(total_questions) as total_q, SUM(correct_answers) as correct_q 
        FROM exam_subject_scores 
        GROUP BY subject_name
    ''', conn)
    
    conn.close()
    return history_df, subject_df

    conn.commit()
    conn.close()

def load_sample_data():
    """앱 초기 실행 시 테스트를 위한 샘플 데이터를 넣습니다."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 이미 데이터가 있는지 확인
    cursor.execute("SELECT COUNT(*) FROM subjects")
    if cursor.fetchone()[0] == 0:
        # 과목 샘플 데이터
        subjects_data = [
            ('안전관리론', '1. 안전보건관리의 개요', '안전보건관리의 목적과 중요성에 대해 학습합니다.'),
            ('안전관리론', '2. 재해조사 및 분석', '산업재해 발생 시 조사 및 분석 방법에 대해 학습합니다.'),
            ('인간공학 및 시스템안전공학', '1. 인간공학적 설계', '인간의 신체적, 인지적 특성을 고려한 설계 원리입니다.')
        ]
        cursor.executemany("INSERT INTO subjects (subject_name, chapter_name, description) VALUES (?, ?, ?)", subjects_data)
        
        # 문제 샘플 데이터
        questions_data = [
            (1, 2023, 1, '다음 중 하인리히의 재해 발생 5단계 원리에 속하지 않는 것은?', '사회적 환경 및 유전적 요소', '개인적 결함', '불안전한 행동 및 불안전한 상태', '사고 통제', 4, '하인리히의 도미노 이론 5단계: 1.사회적 환경/유전적 요소 -> 2.개인적 결함 -> 3.불안전 행동/상태 -> 4.사고 -> 5.재해. 사고 통제는 속하지 않습니다.'),
            (1, 2023, 1, '버드(Bird)의 신도미노 이론에서 재해 발생의 직접원인은?', '통제의 부족', '기본 원인 (기원)', '징후 (직접 원인)', '접촉 (사고)', 3, '버드의 이론은 1.통제부족(관리) -> 2.기본원인(기원) -> 3.직접원인(징후) -> 4.사고(접촉) -> 5.상해(손해) 순서입니다.'),
            (3, 2023, 2, '시스템 수명주기 단계 중 예비위험분석(PHA)이 가장 적절하게 수행되는 단계는?', '구상 단계', '시스템 정의 단계', '개발 단계', '운영 단계', 1, '예비위험분석(PHA, Preliminary Hazard Analysis)은 시스템 수명주기 중 가장 초기인 구상(개발 초기) 단계에 수행되어 모든 주요 위험 요소를 파악합니다.')
        ]
        cursor.executemany("INSERT INTO questions (subject_id, exam_year, exam_round, question_text, option_1, option_2, option_3, option_4, correct_answer, explanation) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", questions_data)
        
        conn.commit()
    conn.close()

# 스크립트가 직접 실행될 때 초기화 수행
if __name__ == "__main__":
    init_db()
    load_sample_data()
    print("Database initialized and sample data loaded.")
