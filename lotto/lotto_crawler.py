import requests
from bs4 import BeautifulSoup
import csv
import time
import re
import os

# 최신 회차 번호 자동 조회 함수
def get_latest_round():
    url = 'https://dhlottery.co.kr/gameResult.do?method=byWin'
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    strong_tag = soup.select_one('div.win_result h4 strong')
    if strong_tag is None:
        raise Exception('최신 회차 정보를 찾을 수 없습니다.')
    round_text = strong_tag.text
    round_num = int(re.sub(r'[^0-9]', '', round_text))
    return round_num

# 저장 파일명
OUTPUT_FILE = 'lotto_winners.csv'

# 기존 파일에서 최신 회차(첫 줄의 회차) 읽기
def get_saved_latest_round(filename):
    if not os.path.exists(filename):
        return 0
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        try:
            first_row = next(reader)
            # 최신 회차는 첫 줄의 1번째 값(회차)로 추정
            # 실제로는 번호만 저장되어 있으므로, 최신 회차를 알 수 없음
            # 대신, 저장된 줄 수로 회차 추정 (최신순 저장이므로)
            f.seek(0)
            row_count = sum(1 for _ in reader)
            return row_count
        except StopIteration:
            return 0

# 회차별 1등 번호 크롤링 함수
def get_lotto_numbers(round_num):
    url = f'https://dhlottery.co.kr/gameResult.do?method=byWin&drwNo={round_num}'
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code != 200:
            return None
        soup = BeautifulSoup(resp.text, 'html.parser')
        win_numbers = []
        number_tags = soup.select('div.win_result span.ball_645')
        if len(number_tags) < 7:
            return None
        for tag in number_tags:
            win_numbers.append(int(tag.text.strip()))
        return win_numbers
    except Exception as e:
        print(f'{round_num}회차: 오류 발생 - {e}')
        return None

if __name__ == '__main__':
    LAST_ROUND = get_latest_round()
    print(f'최신 회차: {LAST_ROUND}회차까지 크롤링합니다.')
    # 기존 파일에서 저장된 최신 회차 확인
    saved_latest = get_saved_latest_round(OUTPUT_FILE)
    print(f'이미 저장된 회차 수: {saved_latest}')
    new_data = []
    # 최신 회차부터 저장된 회차 다음까지 크롤링
    for rnd in range(LAST_ROUND, saved_latest, -1):
        nums = get_lotto_numbers(rnd)
        if nums:
            new_data.append(nums)
            print(f'{rnd}회차: {nums}')
        else:
            print(f'{rnd}회차: 데이터 없음')
        time.sleep(1.0)  # 서버 부하 방지 및 차단 방지
    # 기존 데이터 읽기
    old_data = []
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            old_data = list(reader)
    # 새 데이터 + 기존 데이터 합치기 (최신순)
    all_data = new_data + old_data
    # 파일로 저장
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(all_data)
    print(f'총 {len(all_data)}개 회차 저장 완료!') 