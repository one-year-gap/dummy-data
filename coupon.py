import csv
import random
import os
from datetime import datetime, timedelta, date

# --- 설정 및 상수 ---
# 생성할 더미 데이터의 회원 수 기준 (현재는 1000명 폴더만 타겟팅하도록 배열에 1000만 남겨둠)
SIZES = [1000] 
# 파일들이 저장되어 있는 최상위 폴더명
OUTPUT_DIR = "dummy_data"

def generate_random_date(start_date, end_date):
    """
    주어진 시작일(start_date)과 종료일(end_date) 사이의 임의의(랜덤) 날짜/시간을 반환하는 함수
    """
    # 만약 시작일이 종료일보다 미래이거나 같다면, 랜덤 계산을 하지 않고 시작일을 그대로 반환 (에러 방지)
    if start_date >= end_date:
        return start_date
        
    # 종료일에서 시작일을 빼서 두 날짜 사이의 시간 차이(timedelta 객체)를 구함
    time_between_dates = end_date - start_date
    
    # 시간 차이를 '초(seconds)' 단위의 정수로 변환
    seconds_between_dates = int(time_between_dates.total_seconds())
    
    # 0초부터 두 날짜 사이의 총 초(seconds) 사이에서 랜덤한 초를 하나 뽑음
    random_number_of_seconds = random.randrange(seconds_between_dates)
    
    # 시작일에 뽑힌 랜덤한 초를 더해서 최종적인 랜덤 날짜/시간을 만들어 반환
    return start_date + timedelta(seconds=random_number_of_seconds)

def run_coupon_generation(target_users):
    """
    주어진 회원 수(target_users)에 맞춰 회원 데이터를 읽어오고, 쿠폰 데이터를 생성하여 CSV로 저장하는 메인 함수
    """
    # dummy_data 폴더 하위에 있는 size_1000 폴더의 경로를 생성 (운영체제에 맞게 / 또는 \ 조합)
    dir_path = os.path.join(OUTPUT_DIR, f"size_{target_users}")
    
    # 읽어들일 원본 파일 경로 (dummy_data/size_1000/member.csv)
    member_file = os.path.join(dir_path, 'member.csv')
    # 새로 생성해서 저장할 쿠폰 파일 경로 (dummy_data/size_1000/member_coupon.csv)
    output_file = os.path.join(dir_path, 'member_coupon.csv')
    
    # 만약 member.csv 파일이 해당 경로에 존재하지 않는다면 에러 메시지를 띄우고 함수 종료
    if not os.path.exists(member_file):
        print(f"⚠️ {member_file} 파일이 없습니다. 경로를 확인해주세요.")
        return

    print(f"[{target_users}명 기준] 쿠폰 데이터 생성 시작...")

    # 오늘 날짜 (연, 월, 일만 포함) - 생일 계산 등에 사용
    today = date.today()
    # 현재 날짜와 시간 (연, 월, 일, 시, 분, 초 포함) - 쿠폰 만료 및 사용 처리 등에 사용
    now_dt = datetime.now()

    # 원본 파일(member.csv)은 읽기 모드('r')로 열고, 새 파일(member_coupon.csv)은 쓰기 모드('w')로 염
    # (with 문을 사용하면 블록이 끝날 때 파일이 자동으로 안전하게 닫힘)
    with open(member_file, 'r', encoding='utf-8') as f_in, \
         open(output_file, 'w', newline='', encoding='utf-8') as f_out:
        
        # CSV 읽기 객체 생성
        reader = csv.reader(f_in)
        # CSV 쓰기 객체 생성
        writer = csv.writer(f_out)
        
        # 원본 CSV의 첫 번째 줄(헤더)을 읽어서 가져옴 (이후 반복문은 두 번째 줄인 실제 데이터부터 시작됨)
        header = next(reader)
        
        # 헤더 리스트에서 각 컬럼명이 몇 번째 인덱스에 있는지 위치를 찾아서 저장
        role_idx = header.index('role')
        status_idx = header.index('status')
        birth_date_idx = header.index('birth_date')
        join_date_idx = header.index('join_date')
        
        # 새로 만들 쿠폰 CSV의 첫 번째 줄(헤더)을 작성. (DB에서 자동 증가할 member_coupon_id는 제외)
        writer.writerow(['member_id', 'coupon_id', 'is_used', 'used_at', 'issued_at', 'expired_at', 'created_at', 'updated_at'])
        
        # 데이터의 두 번째 줄부터 끝까지 한 줄씩 읽으면서 반복 (row_num은 1부터 시작하게 설정하여 member_id로 사용)
        for row_num, row in enumerate(reader, start=1):
            
            # 현재 줄 번호를 회원의 고유 ID로 사용
            member_id = row_num
            # 원본 데이터에서 회원의 역할(CUSTOMER/COUNSELOR)을 추출
            role = row[role_idx]
            # 원본 데이터에서 회원의 상태(ACTIVE/BANNED/DELETED/PROCESSING 등)를 추출
            status = row[status_idx]
            
            # 회원이 아니거나(상담사 등), 가입 처리 중인 회원이라면 쿠폰을 주지 않고 다음 줄(continue)로 건너뜀
            if role != 'CUSTOMER' or status not in ['ACTIVE', 'BANNED', 'DELETED']:
                continue
                
            # 문자열 형태의 생년월일과 가입일을 원본 데이터에서 추출
            birth_date_str = row[birth_date_idx]
            join_date_str = row[join_date_idx]
            
            # 'YYYY-MM-DD' 형태의 문자열을 파이썬의 날짜(date) 객체로 변환하여 계산 가능하게 만듦
            birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
            join_date = datetime.strptime(join_date_str, '%Y-%m-%d').date()
            
            # 이 회원이 발급받을 쿠폰들을 임시로 저장할 빈 리스트 생성
            coupons_to_issue = []

            # ----------------------------------------------------
            # 1. 웰컴 쿠폰 (쿠폰 ID: 3) 로직
            # ----------------------------------------------------
            # 발급일: 가입일(join_date)의 오전 10시로 고정
            issued_at_welcome = datetime.combine(join_date, datetime.min.time()) + timedelta(hours=10)
            # 만료일: 발급일로부터 정확히 30일 뒤
            expired_at_welcome = issued_at_welcome + timedelta(days=30)
            
            # (쿠폰ID, 발급일, 만료일) 형태의 튜플로 묶어서 발급 리스트에 추가
            coupons_to_issue.append((3, issued_at_welcome, expired_at_welcome))

            # ----------------------------------------------------
            # 2. 생일 쿠폰 (쿠폰 ID: 2) 로직
            # ----------------------------------------------------
            # 올해의 생일 날짜를 계산 (연도는 올해, 월/일은 회원의 생일)
            try:
                this_year_bday = date(today.year, birth_date.month, birth_date.day)
            except ValueError:
                # 만약 회원이 2월 29일생(윤달)인데 올해가 윤년이 아니라면 에러가 나므로, 3월 1일로 보정 처리
                this_year_bday = date(today.year, 3, 1)

            # '올해 생일'이 '오늘'보다 미래라면(즉, 올해 생일이 아직 안 지났다면)
            if this_year_bday > today:
                try:
                    # 가장 최근에 지난 생일은 '작년 생일'이 됨
                    target_bday = date(today.year - 1, birth_date.month, birth_date.day)
                except ValueError:
                    target_bday = date(today.year - 1, 3, 1) # 윤달 예외 처리
            else:
                # 올해 생일이 이미 지났다면, 가장 최근 생일은 '올해 생일'임
                target_bday = this_year_bday

            # 가입일이 '가장 최근에 지난 생일'보다 같거나 과거여야 함
            # (즉, 가입한 이후에 생일을 한 번이라도 맞이했어야 생일 쿠폰을 발급함)
            if join_date <= target_bday:
                # 발급일: 생일 당일의 오전 9시로 고정
                issued_at_bday = datetime.combine(target_bday, datetime.min.time()) + timedelta(hours=9)
                # 만료일: 발급일로부터 정확히 30일 뒤
                expired_at_bday = issued_at_bday + timedelta(days=30)
                
                # 조건이 맞았으므로 생일 쿠폰을 발급 리스트에 추가
                coupons_to_issue.append((2, issued_at_bday, expired_at_bday))

            # ----------------------------------------------------
            # 발급된 쿠폰 목록을 하나씩 돌면서 CSV 파일에 쓰는 로직 (사용 여부 랜덤)
            # ----------------------------------------------------
            for coupon_id, issued_at, expired_at in coupons_to_issue:
                # 0.0과 1.0 사이의 랜덤 실수를 뽑아서 0.60보다 작으면 사용(True), 아니면 미사용(False). 즉, 60% 확률
                is_used = random.random() < 0.60
                
                # 사용 일시를 담을 변수 (미사용이면 빈칸 유지)
                used_at_str = ''
                
                # 방어 로직: 혹시라도 발급일이 현재 시간보다 미래라면 논리적 오류이므로 무조건 미사용 처리
                if issued_at > now_dt:
                    is_used = False

                # 만약 쿠폰을 사용했다고 랜덤 결정이 났다면
                if is_used:
                    # 쿠폰은 만료일과 현재 시간 중 '더 빠른 날짜'까지만 사용할 수 있음 (미래 시점 사용 방지)
                    max_use_date = min(now_dt, expired_at)
                    
                    # 만약 발급일이 사용 기한보다 과거라면 (정상적인 상황)
                    if issued_at < max_use_date:
                        # 발급일과 기한 사이의 랜덤한 날짜/시간을 생성하여 사용 일시로 지정
                        used_at_dt = generate_random_date(issued_at, max_use_date)
                        # datetime 객체를 DB에 들어갈 문자열 형태(YYYY-MM-DD HH:MM:SS)로 변환
                        used_at_str = used_at_dt.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        # 기한 초과 등으로 사용할 수 있는 시간적 여유가 없다면 사용 실패(미사용) 처리
                        is_used = False

                # 발급일과 만료일 객체를 문자열로 변환
                issued_str = issued_at.strftime('%Y-%m-%d %H:%M:%S')
                expired_str = expired_at.strftime('%Y-%m-%d %H:%M:%S')
                
                # 데이터가 DB에 처음 생성된 날짜(created_at)는 쿠폰 발급일과 동일하게 맞춤
                created_str = issued_str
                # 데이터가 마지막으로 수정된 날짜(updated_at)는, 사용했다면 사용일시, 미사용이라면 발급일시로 설정
                updated_str = used_at_str if is_used else issued_str
                
                # 최종 계산된 값들을 순서에 맞게 리스트로 묶어서 CSV 파일의 한 줄로 기록
                writer.writerow([
                    member_id, coupon_id, is_used, used_at_str, 
                    issued_str, expired_str, created_str, updated_str
                ])

    print(f"[{target_users}명 기준] 쿠폰 데이터 생성 완료!\n")

# 이 스크립트를 터미널에서 직접 실행했을 때만 동작하게 하는 파이썬 관례
if __name__ == "__main__":
    # SIZES 리스트에 정의된 숫자들(현재는 1000)을 하나씩 꺼내서 쿠폰 생성 함수를 호출
    for size in SIZES:
        run_coupon_generation(size)