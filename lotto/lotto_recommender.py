import csv
import random
from collections import Counter

DATA_FILE = 'lotto_winners.csv'
LOTTO_NUMBERS = list(range(1, 46))

# 데이터 불러오기
def load_lotto_data(filename):
    lotto_numbers = []
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
        # 상위 20개 중 3개, 하위 20개 중 1~2개, 나머지 중간 번호
        n_top = 3
        n_bottom = random.choice([1, 2])
        n_mid = 6 - n_top - n_bottom
        nums = random.sample(top20, n_top) + random.sample(bottom20, n_bottom) + random.sample(mid_nums, n_mid)
        nums.sort()
        # 필터1: 홀짝 3:3 또는 4:2
        n_odd = sum(1 for n in nums if n % 2 == 1)
        n_even = 6 - n_odd
        if not (n_odd in [2, 3, 4]):
            continue
        # 필터2: 연속번호 2개 이하
        if count_consecutive(nums) > 2:
            continue
        # 필터3: 구간 3개 이상
        sections = set(get_section(n) for n in nums)
        if len(sections) < 3:
            continue
        # 필터4: 합계 100~200
        if not (100 <= sum(nums) <= 200):
            continue
        # 중복 조합 방지
        if nums in recommendations:
            continue
        recommendations.append(nums)
    return recommendations

# 통계 분석 결과 출력
def print_statistics(freq_counter):
    print('\n--- 번호별 출현 빈도 상위 10개 ---')
    for num, cnt in freq_counter.most_common(10):
        print(f'{num}번: {cnt}회')
    print('\n--- 번호별 출현 빈도 하위 10개 ---')
    for num, cnt in freq_counter.most_common()[-10:]:
        print(f'{num}번: {cnt}회')
    print('\n--- 전체 번호별 출현 빈도 ---')
    for num in LOTTO_NUMBERS:
        print(f'{num:2d}번: {freq_counter.get(num,0)}회', end='  ')
        if num % 10 == 0:
            print()

# 추천 근거 설명
def print_analysis(freq_counter, recommendations):
    print('\n--- 추천 분석 및 통계적 근거 ---')
    print('이 추천은 역대 1등 번호의 출현 빈도와 실제 당첨 패턴(상위/하위/중위 번호 혼합, 홀짝, 구간, 연속번호, 합계 등)을 반영해 생성되었습니다.')
    print('각 조합은 다음 조건을 모두 만족합니다:')
    print('- 상위 20개 번호 중 3개, 하위 20개 중 1~2개, 나머지는 중간 번호')
    print('- 홀짝 3:3 또는 4:2, 연속번호 2개 이하, 구간 3개 이상, 합계 100~200')
    print('추천 조합에 포함된 번호의 출현 빈도는 다음과 같습니다:')
    for i, rec in enumerate(recommendations, 1):
        freqs = [freq_counter.get(num, 0) for num in rec]
        print(f'{i}번 추천: {rec} -> 출현 빈도: {freqs}, 합계: {sum(rec)}, 홀:{sum(1 for n in rec if n%2==1)}, 짝:{sum(1 for n in rec if n%2==0)}, 구간:{sorted(set(get_section(n) for n in rec))}, 연속:{count_consecutive(rec)}')

if __name__ == '__main__':
    lotto_numbers = load_lotto_data(DATA_FILE)
    freq_counter = get_number_frequency(lotto_numbers)
    recommendations = recommend_smart_numbers(freq_counter, n_recommend=5)

    print('--- 로또 번호 추천 (복합 통계 필터 기반) ---')
    for i, rec in enumerate(recommendations, 1):
        print(f'{i}번 추천: {rec}')

    print_statistics(freq_counter)
    print_analysis(freq_counter, recommendations) 