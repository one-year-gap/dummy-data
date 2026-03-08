import csv
import random
import os
import json
import base64
import bcrypt
from datetime import datetime, timedelta, date
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# --- 암호화 설정 (자바의 AES/ECB/PKCS5Padding 과 동일하게 맞춤) ---
# 32바이트 비밀키 (SECRET_KEY 환경변수 값 적용)
AES_SECRET_KEY = b'Xy9zPvQ3kL5mRnJwT8bH2cD4fG7jA1sE'

def encrypt_aes(raw_text):
    # 자바의 AES/ECB/PKCS5Padding 과 호환되는 암호화 함수
    cipher = AES.new(AES_SECRET_KEY, AES.MODE_ECB)
    
    # 파이썬의 PKCS7 패딩은 자바의 PKCS5 패딩과 완벽하게 호환됨
    encrypted_bytes = cipher.encrypt(pad(raw_text.encode('utf-8'), AES.block_size))
    return base64.b64encode(encrypted_bytes).decode('utf-8')

# 10만번 연산 방지를 위해 '1234'의 BCrypt 해시를 미리 한 번만 생성
# 자바 Spring Security의 BCryptPasswordEncoder와 호환됨
DEFAULT_PASSWORD_HASH = bcrypt.hashpw(b"1234", bcrypt.gensalt()).decode('utf-8')

# --- 설정 및 상수 ---
SIZES = [10, 100, 1000, 10000, 50000, 100000]
OUTPUT_DIR = "dummy_data"

# 이름 생성을 위한 한국인 성/이름 풀
LAST_NAMES = ['김', '이', '박', '최', '정', '강', '조', '윤', '장', '임', '한', '오', '서', '신', '권', '황', '안', '송', '전', '홍']
FIRST_NAMES = ['하영', '민준', '서준', '도윤', '예준', '시우', '하준', '지호', '주원', '지훈', '건우', '서연', '서윤', '지우', '서현', '하은', '하윤', '민서', '지유', '윤서', '지민', '영현', '수아', '은우', '다은']

# 대한민국 17개 시/도 지역 풀
ADDRESS_POOL = {
    '서울': {'강남구': ['테헤란로', '강남대로'], '서초구': ['서초대로', '반포대로'], '송파구': ['올림픽로', '송파대로'], '마포구': ['월드컵북로', '마포대로']},
    '부산': {'해운대구': ['해운대해변로', '센텀중앙로'], '부산진구': ['서전로', '중앙대로'], '동래구': ['충렬대로', '명륜로']},
    '대구': {'수성구': ['동대구로', '달구벌대로'], '중구': ['국채보상로', '동성로'], '달서구': ['월배로', '상인로']},
    '인천': {'연수구': ['컨벤시아대로', '인천타워대로'], '남동구': ['인주대로', '구월로'], '부평구': ['부평대로', '경원대로']},
    '광주': {'서구': ['상무중앙로', '무진대로'], '북구': ['첨단과기로', '동문대로'], '광산구': ['사암로', '첨단중앙로']},
    '대전': {'유성구': ['대덕대로', '대학로'], '서구': ['둔산대로', '대덕대로'], '중구': ['계룡로', '중앙로']},
    '울산': {'남구': ['삼산로', '번영로'], '중구': ['번영로', '학성로'], '동구': ['방어진순환도로', '대학길']},
    '세종특별자치시': {'세종시': ['한누리대로', '가름로', '다솜로', '도움로']},
    '경기': {'성남시 분당구': ['판교역로', '성남대로'], '수원시 영통구': ['광교중앙로', '도청로'], '용인시 수지구': ['포은대로', '수지로'], '고양시 일산동구': ['정발산로', '일산로']},
    '강원특별자치도': {'춘천시': ['중앙로', '퇴계로'], '원주시': ['원일로', '서원대로'], '강릉시': ['경강로', '율곡로']},
    '충북': {'청주시 흥덕구': ['대농로', '가경로'], '충주시': ['국원대로', '예성로'], '제천시': ['의림대로', '청전대로']},
    '충남': {'천안시 서북구': ['불당대로', '충무로'], '아산시': ['온천대로', '충무로'], '당진시': ['당진중앙2로', '원당로']},
    '전북특별자치도': {'전주시 완산구': ['백제대로', '기린대로'], '익산시': ['무왕로', '선화로'], '군산시': ['대학로', '수송로']},
    '전남': {'여수시': ['시청로', '망마로'], '순천시': ['순광로', '백강로'], '목포시': ['백년대로', '영산로']},
    '경북': {'포항시 남구': ['포스코대로', '새천년대로'], '구미시': ['구미대로', '송정대로'], '경주시': ['원화로', '태종로']},
    '경남': {'창원시 성산구': ['창원대로', '중앙대로'], '진주시': ['진주대로', '동진로'], '김해시': ['내외중앙로', '가락로']},
    '제주특별자치도': {'제주시': ['노연로', '도령로', '연북로'], '서귀포시': ['일주동로', '중앙로']}
}

# 상품 ID 범위
MOBILE_IDS = list(range(1, 51))
TAB_WATCH_IDS = list(range(51, 60))
IPTV_IDS = list(range(60, 66))
INTERNET_IDS = list(range(66, 75))
ADDON_IDS = list(range(75, 121))
TETHERING_SUPPORTED_IDS = [1, 2, 3, 4, 5, 6, 8, 13, 14, 18, 23, 27, 29, 30, 32, 34, 37, 39, 43]

# 요금제 매핑 디테일 고도화 (특정 나이/성별 전용 요금제 분류)
SENIOR_PLANS = {15, 17, 20, 26, 31, 37}
YOUTH_PLANS = {36, 38, 39, 42, 50}
KIDS_PLANS = {45, 46, 47, 49}
MILITARY_PLANS = {34, 35}
# 일반 요금제 (특수 요금제를 제외한 나머지)
GENERAL_PLANS = set(MOBILE_IDS) - SENIOR_PLANS - YOUTH_PLANS - KIDS_PLANS - MILITARY_PLANS

os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_random_date(start_date, end_date):
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + timedelta(days=random_number_of_days)

def get_last_12_months():
    today = datetime.now()
    months = []
    for i in range(12):
        d = today - timedelta(days=30 * i)
        months.append(d.strftime('%Y%m'))
    return sorted(months)

# 가입기간(Join Date) 6개 구간으로 세분화
def get_weighted_join_date():
    today = date.today()
    # 6개 구간에 대한 가중치 (총 100%)
    categories = [
        'UNDER_3_MONTHS', 'MONTHS_3_TO_12', 'YEARS_1_TO_2', 
        'YEARS_2_TO_5', 'YEARS_5_TO_10', 'OVER_10_YEARS'
    ]
    weights = [10, 15, 15, 30, 20, 10]
    category = random.choices(categories, weights=weights, k=1)[0]
    
    if category == 'UNDER_3_MONTHS':
        start, end = today - timedelta(days=90), today
    elif category == 'MONTHS_3_TO_12':
        start, end = today - timedelta(days=365), today - timedelta(days=90)
    elif category == 'YEARS_1_TO_2':
        start, end = today - timedelta(days=730), today - timedelta(days=365)
    elif category == 'YEARS_2_TO_5':
        start, end = today - timedelta(days=1825), today - timedelta(days=730)
    elif category == 'YEARS_5_TO_10':
        start, end = today - timedelta(days=3650), today - timedelta(days=1825)
    else: # OVER_10_YEARS
        start, end = today - timedelta(days=5000), today - timedelta(days=3650)
        
    return generate_random_date(start, end)

# 연령대(Birth Date) 8개 구간으로 세분화
def get_weighted_birth_date():
    today = date.today()
    current_year = today.year
    categories = [
        'UNDER_10', 'TEENS', 'TWENTIES', 'THIRTIES', 
        'FORTIES', 'FIFTIES', 'SIXTIES_EARLY', 'OVER_65'
    ]
    weights = [5, 10, 20, 25, 20, 10, 5, 5]
    category = random.choices(categories, weights=weights, k=1)[0]
    
    if category == 'UNDER_10':
        start, end = date(current_year - 10, 1, 1), today
    elif category == 'TEENS':
        start, end = date(current_year - 19, 1, 1), date(current_year - 11, 12, 31)
    elif category == 'TWENTIES':
        start, end = date(current_year - 29, 1, 1), date(current_year - 20, 12, 31)
    elif category == 'THIRTIES':
        start, end = date(current_year - 39, 1, 1), date(current_year - 30, 12, 31)
    elif category == 'FORTIES':
        start, end = date(current_year - 49, 1, 1), date(current_year - 40, 12, 31)
    elif category == 'FIFTIES':
        start, end = date(current_year - 59, 1, 1), date(current_year - 50, 12, 31)
    elif category == 'SIXTIES_EARLY':
        start, end = date(current_year - 64, 1, 1), date(current_year - 60, 12, 31)
    else: # OVER_65
        start, end = date(current_year - 90, 1, 1), date(current_year - 65, 12, 31)
        
    return generate_random_date(start, end)

def run_generation(target_users):
    print(f"[{target_users}명] 데이터 생성 시작...")
    dir_path = os.path.join(OUTPUT_DIR, f"size_{target_users}")
    os.makedirs(dir_path, exist_ok=True)

    # 1. 주소 데이터 생성 (가족 공유를 위해 회원 수의 80% 생성)
    num_addresses = max(1, int(target_users * 0.8))
    seen_address_key = set()  # (province, city, street_address) 유니크 제약 준수
    print(" - 주소 데이터 생성 중...")
    with open(os.path.join(dir_path, 'address.csv'), 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['province', 'city', 'street_address', 'postal_code', 'created_at', 'updated_at'])
        
        for i in range(1, num_addresses + 1):
            while True:
                prov = random.choice(list(ADDRESS_POOL.keys()))
                city = random.choice(list(ADDRESS_POOL[prov].keys()))
                street_base = random.choice(ADDRESS_POOL[prov][city])
                street = f"{street_base} {random.randint(1, 150)}길 {random.randint(1, 99)}"
                key = (prov, city, street)
                if key not in seen_address_key:
                    seen_address_key.add(key)
                    break
            postal = f"{random.randint(10000, 69999)}"
            now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
         
            writer.writerow([prov, city, street, postal, now_str, now_str])

    # 2. 회원 데이터 생성 (암호화 적용)
    print(" - 회원, 가족 결합, 미납/완납 데이터 생성 중...")
    used_emails = set()
    used_phones = set()
    
    subscriptions_to_create = [] # (member_id, [product_ids], start_date)
    # 가족 결합 관리를 위한 변수 추가
    family_id_counter = 1
    open_families = [] # 아직 정원이 덜 찬 가족 그룹 ID 목록 (최대 4인 가정)

    # 💡 파일 오픈 (회원, 가족결합, 청구서 한 번에 처리)
    with open(os.path.join(dir_path, 'member.csv'), 'w', newline='', encoding='utf-8') as f_mem, \
         open(os.path.join(dir_path, 'family_group.csv'), 'w', newline='', encoding='utf-8') as f_fam, \
         open(os.path.join(dir_path, 'billing.csv'), 'w', newline='', encoding='utf-8') as f_bil:
        
        mem_writer = csv.writer(f_mem)
        fam_writer = csv.writer(f_fam)
        bil_writer = csv.writer(f_bil)
        
        # 헤더에 children_count, family_group_id, family_role 추가
        mem_writer.writerow(['address_id', 'provider_id', 'email', 'password', 'name', 'phone', 'birth_date', 'gender', 'join_date', 'created_at', 'updated_at', 'status_updated_at', 'status', 'type', 'role', 'membership', 'children_count', 'family_group_id', 'family_role'])
        fam_writer.writerow(['created_at', 'updated_at'])
        bil_writer.writerow(['member_id', 'yyyymm', 'is_paid', 'created_at', 'updated_at'])
        
        recent_months = get_last_12_months() # 청구서 생성을 위한 최근 12개월
        
        # [추가] 가족을 막 생성해서 최소 2명을 채우기 위해 다음 사람을 강제로 데려와야 하는지 체크
        needs_family_member = False

        for member_id in range(1, target_users + 1):
            # 기본 정보 생성
            raw_name = random.choice(LAST_NAMES) + random.choice(FIRST_NAMES)
            encrypted_name = encrypt_aes(raw_name)
            
            while True:
                email = f"user{member_id}_{random.randint(1000,9999)}@gmail.com"
                if email not in used_emails:
                    used_emails.add(email)
                    break
                    
            now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            join_date = get_weighted_join_date()
            birth_date = get_weighted_birth_date()
            age = date.today().year - birth_date.year
            gender = random.choice(['M', 'F'])

            # 역할(Role) 배분: CUSTOMER 95%, COUNSELOR 5%
            role = random.choices(['CUSTOMER', 'COUNSELOR'], weights=[95, 5], k=1)[0]
            
            # [추가] 고객은 4가지 상태로 나누고, 상담사는 무조건 ACTIVE 고정
            if role == 'CUSTOMER':
                status = random.choices(['ACTIVE', 'BANNED', 'DELETED', 'PROCESSING'], weights=[85, 5, 8, 2], k=1)[0]
            else:
                status = 'ACTIVE'

            # 가입 유형: 무조건 FORM 가입
            signup_type = 'FORM'
            provider_id = '' 
            hashed_password = DEFAULT_PASSWORD_HASH

            while True:
                raw_phone = f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
                if raw_phone not in used_phones:
                    used_phones.add(raw_phone)
                    break
            encrypted_phone = encrypt_aes(raw_phone)
            
            # ---------------------------------------------------------
            # 고객(CUSTOMER) 로직 vs 상담사(COUNSELOR) 로직 분기
            # ---------------------------------------------------------
            
            # [추가 방어 로직] 
            # 만약 마지막 회원인데, 앞에서 누군가 가족을 만들고 짝꿍을 기다리고 있다면?
            # 상담사(COUNSELOR)가 되면 안 되니까 무조건 CUSTOMER로 직업을 고정
            if member_id == target_users and needs_family_member:
                role = 'CUSTOMER'
            
            if role == 'CUSTOMER':
                address_id = random.randint(1, num_addresses)
                membership = random.choices(['VVIP', 'VIP', 'GOLD'], weights=[10, 30, 60], k=1)[0]

                # 자식 수 (나이에 따라 확률 조정)
                if age >= 30 and age <= 60:
                    children_count = random.choices([0, 1, 2, 3], weights=[40, 30, 25, 5])[0]
                else:
                    children_count = 0

                # ==========================================
                # 가족 결합 (최소 2인 보장 로직 적용)
                # ==========================================
                family_group_id = ''
                family_role = ''
                is_last_member = (member_id == target_users)

                # [핵심] 정상(ACTIVE)이거나 정지(BANNED)된 사람만 가족 결합 허용
                if status in ['ACTIVE', 'BANNED']:

                    # 조건: 이전 사람이 방을 파서 짝꿍이 꼭 필요하거나, 20% 확률에 당첨됐을 때
                    if needs_family_member or random.random() < 0.20:
                        
                        if needs_family_member:
                            # [상황 A] 이전 사람이 방을 팠음! 무조건 가장 최근 가족 방에 강제 합류 (최소 2인 달성)
                            target_family = open_families[-1]
                            family_group_id = target_family['id']
                            family_role = 'MEMBER'
                            
                            # 80% 확률로 동거
                            if random.random() < 0.80:
                                address_id = target_family['address_id']
                                
                            target_family['count'] += 1
                            if target_family['count'] >= 4:
                                open_families.remove(target_family)
                                
                            needs_family_member = False # 짝꿍 채우기 임무 완수!
                            
                        elif open_families:
                            # [상황 B] 기존에 열려있는 가족 방들 중 하나에 랜덤으로 합류
                            target_family = random.choice(open_families)
                            family_group_id = target_family['id']
                            family_role = 'MEMBER'
                            
                            if random.random() < 0.80:
                                address_id = target_family['address_id']
                                
                            target_family['count'] += 1
                            if target_family['count'] >= 4:
                                open_families.remove(target_family)
                                
                        elif not is_last_member:
                            # [상황 C] 들어갈 방이 없어서 내가 방을 새로 팜 (단, 마지막 사람은 방 못 팜!)
                            family_group_id = family_id_counter
                            fam_writer.writerow([now_str, now_str]) 
                            open_families.append({'id': family_group_id, 'count': 1, 'address_id': address_id}) 
                            family_role = 'REPRESENTATIVE'
                            family_id_counter += 1
                            
                            needs_family_member = True # "나 방 팠다! 다음 사람 무조건 내 방으로 와!" 플래그 On

                else:
                    # 탈퇴(DELETED)나 가입중(PROCESSING) 회원이 짝꿍을 기다리면 버그 나니까 취소
                    needs_family_member = False

                # [핵심] 가입중(PROCESSING)이 아닌 사람만 요금제 및 청구서 생성
                if status != 'PROCESSING':

                    # 요금제 선택 (나이/성별에 따른 필터링)
                    allowed_plans = list(GENERAL_PLANS)
                    if age >= 65:
                        allowed_plans.extend(SENIOR_PLANS)
                    elif age <= 18:
                        allowed_plans.extend(YOUTH_PLANS)
                        if age <= 12:
                            allowed_plans.extend(KIDS_PLANS)
                            
                    # 남성이며 19~25세 사이인 경우 군인 요금제 선택 가능
                    if gender == 'M' and 19 <= age <= 25:
                        allowed_plans.extend(MILITARY_PLANS)

                    my_products = [random.choice(allowed_plans)] # 깐깐하게 필터링된 모바일 요금제 1개 필수
                    if random.random() < 0.2: my_products.append(random.choice(TAB_WATCH_IDS))
                    if random.random() < 0.2: my_products.append(random.choice(IPTV_IDS))
                    if random.random() < 0.2: my_products.append(random.choice(INTERNET_IDS))
                    my_products.extend(random.sample(ADDON_IDS, random.randint(0, 3)))
                    
                    sub_start = generate_random_date(join_date, date.today())
                    # 나중에 DELETED 처리할 때 쓰기 위해 status도 같이 리스트에 담아줌
                    subscriptions_to_create.append((member_id, my_products, sub_start, status))

                    # 미납/완납(Billing) 청구서 12개월치 생성
                    # 가입일(join_ym)이 아닌 구독 시작일(sub_ym) 기준으로 맞춤
                    sub_ym = sub_start.strftime('%Y%m')
                    valid_billing_months = [m for m in recent_months if m >= sub_ym]

                    for index, yyyymm in enumerate(valid_billing_months):
                        # 과거 청구서는 무조건 완납(True), 맨 마지막(최신 달) 청구서만 5% 확률로 미납
                        if index == len(valid_billing_months) - 1:
                            is_paid = random.random() < 0.95 
                        else:
                            is_paid = True
                            
                        bil_writer.writerow([member_id, yyyymm, is_paid, now_str, now_str])

            else:
                # 상담사(COUNSELOR)는 상품 가입, 멤버십, 가족결합, 청구서 등이 불필요함
                address_id = ''
                membership = ''
                children_count = 0
                family_group_id = ''
                family_role = ''

            # CSV 쓰기
            mem_writer.writerow([
                address_id, provider_id, email, hashed_password, 
                encrypted_name, encrypted_phone, birth_date.strftime('%Y-%m-%d'), gender,
                join_date.strftime('%Y-%m-%d'), now_str, now_str, now_str, status, signup_type, role, membership,
                children_count, family_group_id, family_role
            ])

    # 3. 구독 및 사용량 데이터 생성
    print(" - 구독 및 월별 사용량 데이터 생성 중...")
    sub_id = 1
    
    with open(os.path.join(dir_path, 'subscription.csv'), 'w', newline='', encoding='utf-8') as f_sub, \
         open(os.path.join(dir_path, 'usage_monthly.csv'), 'w', newline='', encoding='utf-8') as f_usage:
         
        sub_writer = csv.writer(f_sub)
        sub_writer.writerow(['member_id', 'product_id', 'start_date', 'end_date', 'status', 'contract_months', 'contract_end_date', 'created_at', 'updated_at'])
        
        usage_writer = csv.writer(f_usage)
        usage_writer.writerow(['subscription_id', 'yyyymm', 'usage_details', 'created_at', 'updated_at'])
        
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        recent_months = get_last_12_months()
        
        # 아까 넘겨준 member_status 같이 받기
        for member_id, p_ids, start_date, member_status in subscriptions_to_create:
            start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
            start_ym = start_date.strftime('%Y%m')
            
            for p_id in p_ids:
                # 3-1. 구독 데이터 작성

                # [핵심] 탈퇴 회원은 구독 상태 False, 해지일은 오늘로 세팅
                sub_is_active = True
                end_date_str = ''
                if member_status == 'DELETED':
                    sub_is_active = False
                    end_date_str = now_str # 탈퇴일을 편의상 데이터 생성일(오늘)로 세팅

                # 약정 로직
                contract_months_val = ''
                contract_end_str = ''

                # 모바일 요금제(MOBILE_IDS)인 경우에만 약정 적용
                if p_id in MOBILE_IDS:
                    # 약정 확률: 무약정(공시지원금/자급제) 30%, 12개월 약정 20%, 24개월 약정 50%
                    contract_type = random.choices([0, 12, 24], weights=[30, 20, 50], k=1)[0]
                    
                    if contract_type > 0:
                        contract_months_val = contract_type
                        # 12개월은 365일, 24개월은 730일 더하기
                        days_to_add = 365 if contract_type == 12 else 730
                        contract_end_date = start_date + timedelta(days=days_to_add)
                        contract_end_str = contract_end_date.strftime('%Y-%m-%d %H:%M:%S')

                # True 였던 자리에 sub_is_active 넣고, 빈칸('') 이었던 자리에 end_date_str 넣기
                sub_writer.writerow([member_id, p_id, start_date_str, end_date_str, sub_is_active, contract_months_val, contract_end_str, now_str, now_str])
                
                # 3-2. 사용량 데이터 작성 (ADDON은 제외)
                if p_id not in ADDON_IDS:
                    # 시작 월부터 이번 달까지의 월 목록 필터링
                    valid_months = [m for m in recent_months if m >= start_ym]
                    
                    for yyyymm in valid_months:
                        usage_details = {}
                        
                        if p_id in MOBILE_IDS:
                            # 1) 공통 모바일 사용량 (데이터, 음성, 문자)
                            usage_details = {
                                "data_gb": round(random.uniform(0.0, 150.0), 1),
                                "voice_min": random.randint(0, 500),
                                "sms_cnt": random.randint(0, 100)
                            }
                            
                            # 2) 테더링/쉐어링 제공 요금제인 경우에만 해당 항목 추가
                            if p_id in TETHERING_SUPPORTED_IDS:
                                usage_details["tethering_sharing_data_gb"] = round(random.uniform(0.0, 50.0), 1)
                                
                        elif p_id in TAB_WATCH_IDS:
                            usage_details = {"data_gb": round(random.uniform(0.5, 30.0), 1)}
                            if p_id == 52:
                                usage_details["voice_min"] = random.randint(0, 50)
                                usage_details["sms_cnt"] = random.randint(0, 250)
                            elif p_id == 59:
                                usage_details["voice_min"] = random.randint(0, 50)
                                usage_details["sms_cnt"] = random.randint(0, 500) # 무제한이므로 랜덤
                        elif p_id in IPTV_IDS:
                            usage_details = {
                                "viewing_hours": random.randint(10, 200),
                                "vod_purchases_cnt": random.randint(0, 10)
                            }
                        elif p_id in INTERNET_IDS:
                            usage_details = {
                                "total_data_gb": round(random.uniform(50.0, 1000.0), 1),
                                "qos_throttled_cnt": random.randint(0, 5)
                            }

                        usage_json = json.dumps(usage_details)
                        usage_writer.writerow([sub_id, yyyymm, usage_json, now_str, now_str])
                        
                sub_id += 1
                
    print(f"[{target_users}명] 데이터 생성 완료!\n")

if __name__ == "__main__":
    for size in SIZES:
        run_generation(size)
    print("모든 더미 데이터 생성이 완료되었습니다.")