import json
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "safety_engineer.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def get_or_create_subject(cursor, subject_name, chapter_name):
    """과목 및 단원이 없으면 생성하고 ID를 반환합니다."""
    cursor.execute("SELECT id FROM subjects WHERE subject_name = ? AND chapter_name = ?", (subject_name, chapter_name))
    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        cursor.execute("INSERT INTO subjects (subject_name, chapter_name, description) VALUES (?, ?, ?)", 
                       (subject_name, chapter_name, f"{subject_name} - {chapter_name} 내용입니다."))
        return cursor.lastrowid

def import_json_to_db(json_file_path):
    """JSON 파일을 읽어 DB에 삽입합니다."""
    if not os.path.exists(json_file_path):
        print(f"오류: {json_file_path} 파일을 찾을 수 없습니다.")
        return

    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    conn = get_connection()
    cursor = conn.cursor()
    
    count = 0
    for q in data:
        # 과목/단원 매핑
        subject_id = get_or_create_subject(cursor, q['subject'], q['chapter_name'])
        
        # 중복 문제 체크 (문제 텍스트 기준)
        cursor.execute("SELECT id FROM questions WHERE question_text = ? AND exam_year = ?", (q['question_text'], q['exam_year']))
        if cursor.fetchone() is None:
            # 존재하지 않으면 삽입
            cursor.execute('''
                INSERT INTO questions 
                (subject_id, exam_year, exam_round, question_text, option_1, option_2, option_3, option_4, correct_answer, explanation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                subject_id, 
                q['exam_year'], 
                q['exam_round'], 
                q['question_text'], 
                q['opt1'], 
                q['opt2'], 
                q['opt3'], 
                q['opt4'], 
                q['correct_answer'], 
                q['explanation']
            ))
            count += 1
        
    conn.commit()
    conn.close()
    
    print(f"'{json_file_path}' 데이터 가져오기 완료!")
    print(f"새로 추가된 문제: {count}개.")

if __name__ == "__main__":
    current_dir = os.path.dirname(__file__)
    json_path = os.path.join(current_dir, "data", "sample_questions.json")
    print(f"[{json_path}] 에서 데이터를 읽어 DB에 적재합니다...")
    import_json_to_db(json_path)
