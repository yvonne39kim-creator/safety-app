import requests
from bs4 import BeautifulSoup
import sqlite3
import os
import re

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "safety_engineer.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def scrape_exam_data(year, round_num, target_url):
    """
    지정된 URL에서 기출문제를 크롤링하여 DB에 저장합니다.
    (주의: 실제 서비스되는 웹사이트의 HTML 구조에 맞춰 파서를 수정해야 합니다.)
    이 코드는 예시 구조(가상의 HTML 구조)를 바탕으로 작성되었습니다.
    """
    print(f"[{year}년 {round_num}회] 기출문제 크롤링 시작: {target_url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(target_url, headers=headers)
        response.raise_for_status()
        
        # 인코딩 처리 (한글 깨짐 방지)
        response.encoding = response.apparent_encoding 
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # -------------------------------------------------------------
        # [파싱 로직 작성 부분]
        # 실제 사이트(comcbt, 문제풀이닷컴 등)의 DOM 구조 분석 후 아래 코드를 수정해야 합니다.
        # 예시 구조:
        # <div class="question-item">
        #   <div class="subject">안전관리론</div>
        #   <div class="q-text">1. 다음 중 ...</div>
        #   <ul class="options">
        #     <li>1. 보기1</li><li>2. 보기2</li>...
        #   </ul>
        #   <div class="answer">정답: 3</div>
        #   <div class="explanation">해설: ....</div>
        # </div>
        # -------------------------------------------------------------
        
        # 가상의 파싱 예제
        questions_parsed = []
        question_blocks = soup.find_all('div', class_='question-item') # 실제 클래스명으로 변경 필요
        
        if not question_blocks:
            print("문제 블록을 찾을 수 없습니다. HTML 구조를 확인하거나 셀레니움이 필요한지 검토하세요.")
            # 크롤링된 HTML의 일부를 출력하여 구조 확인 (디버깅 용도)
            # print(soup.prettify()[:1000])
            return
            
        for block in question_blocks:
            try:
                subject = block.find('div', class_='subject').text.strip()
                q_text = block.find('div', class_='q-text').text.strip()
                
                ops = block.find('ul', class_='options').find_all('li')
                opt1 = ops[0].text.strip() if len(ops) > 0 else ""
                opt2 = ops[1].text.strip() if len(ops) > 1 else ""
                opt3 = ops[2].text.strip() if len(ops) > 2 else ""
                opt4 = ops[3].text.strip() if len(ops) > 3 else ""
                
                ans_text = block.find('div', class_='answer').text.strip()
                # "정답: 3" 에서 숫자만 추출
                correct_ans = int(re.search(r'\d+', ans_text).group()) if re.search(r'\d+', ans_text) else 1
                
                exp_block = block.find('div', class_='explanation')
                explanation = exp_block.text.strip() if exp_block else "해설이 없습니다."
                
                questions_parsed.append({
                    'subject': subject,
                    'q_text': q_text,
                    'opt1': opt1, 'opt2': opt2, 'opt3': opt3, 'opt4': opt4,
                    'correct_ans': correct_ans,
                    'explanation': explanation
                })
            except Exception as e:
                print(f"개별 문제 파싱 중 에러 발생: {e}")
                continue
                
        # 파싱된 데이터를 DB에 저장
        save_to_db(year, round_num, questions_parsed)
        
    except requests.exceptions.RequestException as e:
        print(f"네트워크 요청 오류: {e}")

def save_to_db(year, round_num, questions_parsed):
    conn = get_connection()
    cursor = conn.cursor()
    
    count = 0
    for q in questions_parsed:
        # 1. 과목 ID 가져오기 (없으면 새로 생성 고민.. 여기서는 기존 subject 매핑 필요)
        # 임시로 가장 첫 번째 과목 단원에 넣거나, 과목 맵핑 테이블을 정교하게 짜야 함.
        cursor.execute("SELECT id FROM subjects WHERE subject_name = ? LIMIT 1", (q['subject'],))
        subject_row = cursor.fetchone()
        
        if subject_row:
            subject_id = subject_row[0]
        else:
            # 매칭되는 과목이 없으면 새로 추가
            cursor.execute("INSERT INTO subjects (subject_name, chapter_name, description) VALUES (?, ?, ?)", 
                           (q['subject'], f"{q['subject']} 모의고사단원", "크롤링 자동생성 단원"))
            subject_id = cursor.lastrowid
            
        # 2. 문제 삽입
        cursor.execute('''
            INSERT INTO questions 
            (subject_id, exam_year, exam_round, question_text, option_1, option_2, option_3, option_4, correct_answer, explanation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (subject_id, year, round_num, q['q_text'], q['opt1'], q['opt2'], q['opt3'], q['opt4'], q['correct_ans'], q['explanation']))
        count += 1
        
    conn.commit()
    conn.close()
    print(f"총 {count}개의 문제가 DB에 저장되었습니다.")

if __name__ == "__main__":
    print("크롤러 스크립트입니다. 타겟 사이트의 DOM 구조를 확인한 후 파서를 완성해야 합니다.")
    print("예시 동작을 위해 kinz.kr 또는 comcbt.com의 특정 문제 URL을 입력하여 테스트하세요.")
    
    # [테스트 실행 예제]
    # scrape_exam_data(2023, 1, "https://www.comcbt.com/xe/...")
