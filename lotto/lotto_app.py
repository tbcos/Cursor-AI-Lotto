import streamlit as st
import csv
import random
from collections import Counter
import os
import pandas as pd

DATA_FILE = 'lotto_winners.csv'
LOTTO_NUMBERS = list(range(1, 46))

# 데이터 불러오기
def load_lotto_data(filename):
    lotto_numbers = []
    if not os.path.exists(filename):
        return []
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            numbers = [int(n) for n in row[:6]]
            lotto_numbers.append(numbers)
    return lotto_numbers

# 번호별 출현 빈도 계산
def get_number_frequency(lotto_numbers):
    all_numbers = [num for row in lotto_numbers for num in row]
    counter = Counter(all_numbers)
    return counter

# 구간 판별 함수
def get_section(num):
    if num <= 10:
        return 1
    elif num <= 20:
        return 2
    elif num <= 30:
        return 3
    elif num <= 40:
        return 4
    else:
        return 5

# 연속번호 개수 세기
def count_consecutive(nums):
    nums = sorted(nums)
    cnt = 0
    max_cnt = 0
    for i in range(1, len(nums)):
        if nums[i] == nums[i-1] + 1:
            cnt += 1
            max_cnt = max(max_cnt, cnt)
        else:
            cnt = 0
    return max_cnt + 1 if max_cnt > 0 else 0

# 스마트 추천 함수 (복합 필터 적용)
def recommend_smart_numbers(freq_counter, n_recommend=5):
    top20 = [num for num, _ in freq_counter.most_common(20)]
    bottom20 = [num for num, _ in freq_counter.most_common()[-20:]]
    mid_nums = [num for num in LOTTO_NUMBERS if num not in top20 and num not in bottom20]
    recommendations = []
    tries = 0
    while len(recommendations) < n_recommend and tries < 10000:
        tries += 1
        n_top = 3
        n_bottom = random.choice([1, 2])
        n_mid = 6 - n_top - n_bottom
        nums = random.sample(top20, n_top) + random.sample(bottom20, n_bottom) + random.sample(mid_nums, n_mid)
        nums.sort()
        n_odd = sum(1 for n in nums if n % 2 == 1)
        n_even = 6 - n_odd
        if not (n_odd in [2, 3, 4]):
            continue
        if count_consecutive(nums) > 2:
            continue
        sections = set(get_section(n) for n in nums)
        if len(sections) < 3:
            continue
        if not (100 <= sum(nums) <= 200):
            continue
        if nums in recommendations:
            continue
        recommendations.append(nums)
    return recommendations

# Streamlit 앱 시작
st.title('로또 번호 추천 및 통계 분석')

st.info('역대 1등 번호 통계와 당첨 패턴을 반영한 스마트 추천!')

lotto_numbers = load_lotto_data(DATA_FILE)
if not lotto_numbers:
    st.error('lotto_winners.csv 파일이 없습니다. 크롤러를 먼저 실행해 주세요.')
    st.stop()

freq_counter = get_number_frequency(lotto_numbers)

n_recommend = st.slider('추천 조합 개수', 1, 10, 5)
if st.button('로또 번호 추천 받기'):
    recommendations = recommend_smart_numbers(freq_counter, n_recommend=n_recommend)
    st.subheader('추천 번호')
    # hot/cold 번호 정의
    hot_set = set([num for num, _ in freq_counter.most_common(10)])
    cold_set = set([num for num, _ in freq_counter.most_common()[-10:]])
    for i, rec in enumerate(recommendations, 1):
        n_hot = sum(1 for n in rec if n in hot_set)
        n_cold = sum(1 for n in rec if n in cold_set)
        n_odd = sum(1 for n in rec if n % 2 == 1)
        n_even = 6 - n_odd
        sections = sorted(set(get_section(n) for n in rec))
        section_str = ', '.join(str(s) for s in sections)
        freqs = [freq_counter.get(num, 0) for num in rec]
        st.write(f'{i}번 추천: {rec}')
        st.caption(f'출현 빈도: {freqs}, 합계: {sum(rec)}, hot: {n_hot}개, cold: {n_cold}개, 홀:{n_odd}, 짝:{n_even}, 구간:{section_str}, 연속:{count_consecutive(rec)}')

    st.divider()
    # 카드 스타일 통계 시각화
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div style="background-color:#f8f9fa;padding:18px 12px 12px 12px;border-radius:12px;box-shadow:0 2px 8px #eee;">', unsafe_allow_html=True)
        st.markdown('<h5 style="color:#1a73e8;">번호별 출현 빈도 상위 10개</h5>', unsafe_allow_html=True)
        top10 = freq_counter.most_common(10)
        for num, cnt in top10:
            st.markdown(f'<span style="font-size:1.1em;font-weight:bold;color:#222;">{num}번</span>: <span style="color:#e67e22;font-weight:bold;">{cnt}회</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div style="background-color:#f8f9fa;padding:18px 12px 12px 12px;border-radius:12px;box-shadow:0 2px 8px #eee;">', unsafe_allow_html=True)
        st.markdown('<h5 style="color:#e91e63;">번호별 출현 빈도 하위 10개</h5>', unsafe_allow_html=True)
        bottom10 = freq_counter.most_common()[-10:]
        for num, cnt in bottom10:
            st.markdown(f'<span style="font-size:1.1em;font-weight:bold;color:#222;">{num}번</span>: <span style="color:#16a085;font-weight:bold;">{cnt}회</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div style="background-color:#f8f9fa;padding:18px 12px 12px 12px;border-radius:12px;box-shadow:0 2px 8px #eee;max-height:350px;overflow:auto;">', unsafe_allow_html=True)
        st.markdown('<h5 style="color:#4caf50;">전체 번호별 출현 빈도</h5>', unsafe_allow_html=True)
        freq_table = {num: freq_counter.get(num, 0) for num in LOTTO_NUMBERS}
        df = pd.DataFrame({"번호": list(freq_table.keys()), "출현빈도": list(freq_table.values())})
        st.dataframe(df)
        st.markdown('</div>', unsafe_allow_html=True)
    st.divider()
    st.markdown('''
    **추천 근거**
    - 상위 20개 번호 중 3개, 하위 20개 중 1~2개, 나머지는 중간 번호
    - 홀짝 3:3 또는 4:2, 연속번호 2개 이하, 구간 3개 이상, 합계 100~200
    - 역대 1등 번호의 출현 빈도와 실제 당첨 패턴을 반영
    ''')
else:
    st.info('아래 버튼을 눌러 추천 번호를 받아보세요!') 