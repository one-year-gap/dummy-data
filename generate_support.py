import csv
import random
import os
from datetime import timedelta, date

# --- 설정 및 상수 ---
SIZES = [10, 100, 1000, 10000, 50000, 100000]
OUTPUT_DIR = "dummy_data"

# --- 상담(Support) 템플릿용 재료 ---
GREETINGS = {
    'POLITE': ['안녕하세요.', '수고 많으십니다.', '상담원님 수고하십니다~', '문의 하나 드릴게요.'],
    'ANGRY': ['아니 진짜 짜증나네요.', '도대체 일 처리를 어떻게 하는 건가요?', '빠른 해결 안되면 그냥 해지합니다.', '장난하나요 지금?'],
    'NEUTRAL': ['문의드립니다.', '확인 부탁드립니다.', '질문 있습니다.', '']
}
ENDINGS_Q = {
    'POLITE': ['감사합니다.', '좋은 하루 보내세요~', '확인해주시면 감사하겠습니다.', '부탁드려요!'],
    'ANGRY': ['빨리 확인해서 연락주세요.', '당장 환불해주세요.', '진짜 실망스럽네요.', '어떻게 보상할건가요?'],
    'NEUTRAL': ['어떻게 해야 하나요?', '알려주세요.', '답변 바랍니다.', '확인 요망.']
}
ANSWERS = ['이용에 불편을 드려 대단히 죄송합니다.', '문의하신 내용에 대해 안내해 드립니다.', '친절히 모시겠습니다.']

# 제목과 내용의 연관성을 위해, 카테고리별로 사용할 상품 풀을 명확히 분리
MOB_PRODUCTS = ['5G 프리미어', 'LTE 무제한', '다이렉트 65', '키즈 29']
HOM_PRODUCTS = ['기가 인터넷', 'U+ tv', '스마트홈']
APP_NAMES = ['당신의 U+ 앱', '홈페이지', '고객센터 앱']

# {product}와 {app} 변수를 통일하여 제목, 질문, 답변이 일치하도록 템플릿 고도화
SUPPORT_TEMPLATES = {
    'MOB_001': [
        {"title": "{product} 가입/해지 문의", "q": "{greeting} {product} 요금제로 바꾸고 싶은데 {app}에서 안 넘어가져요. {ending_q}", "a": "{answer_start} 해당 증상은 {app} 일시적 오류로 보입니다. 앱 업데이트 후 다시 시도해 주시기 바랍니다."}
    ],
    'MOB_002': [
        {"title": "{product} 요금 납부 방법 변경", "q": "{greeting} {product} 요금을 카드로 내고 싶은데 {app} 어디서 하나요? {ending_q}", "a": "{answer_start} {app} 내 [마이페이지] - [요금납부] 메뉴에서 카드 결제로 변경 가능합니다."}
    ],
    'HOM_007': [
        {"title": "{product} 자꾸 끊깁니다", "q": "{greeting} 어제부터 {product} 신호가 계속 죽네요. 미치겠습니다. {ending_q}", "a": "{answer_start} 해당 지역 통신망 점검을 위해 AS 기사 방문을 접수해 드렸습니다."}
    ],
    'MEM_001': [
        {"title": "VIP 영화예매 포인트 차감", "q": "{greeting} 영화 예매했는데 포인트만 깎이고 예매번호가 안 와요. {ending_q}", "a": "{answer_start} 포인트 차감 후 예매가 실패한 건은 영업일 기준 1~2일 내로 자동 환급 처리됩니다."}
    ]
}

def generate_random_date(start_date, end_date):
    time_between_dates = end_date - start_date
    return start_date + timedelta(days=random.randrange(time_between_dates.days))

def run_support_generation(target_users):
    dir_path = os.path.join(OUTPUT_DIR, f"size_{target_users}")
    member_file = os.path.join(dir_path, 'member.csv')
    
    if not os.path.exists(member_file):
        print(f"⚠️ [size_{target_users}] member.csv 파일이 없습니다. 먼저 메인 스크립트를 실행해주세요.")
        return

    print(f"[{target_users}명 기준] 상담 데이터 생성 시작...")

    # ---------------------------------------------------------
    # 1. member.csv를 읽어서 가상 ID(줄 번호) 매핑하기
    # ---------------------------------------------------------
    customer_ids = []
    counselor_ids = []
    
    with open(member_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader) # 헤더 건너뛰기
        role_idx = header.index('role') # 'role' 컬럼이 몇 번째인지 찾기
        
        # 줄 번호(row_num)가 곧 DB에 들어갈 ID(PK)가 됩니다!
        for row_num, row in enumerate(reader, start=1):
            role = row[role_idx]
            if role == 'CUSTOMER':
                customer_ids.append(row_num)
            elif role == 'COUNSELOR':
                counselor_ids.append(row_num)

    # ---------------------------------------------------------
    # 2. 상담(support_case) 데이터 생성 (PK 없이)
    # ---------------------------------------------------------
    num_cases = int(len(customer_ids) * 0.6) # 고객의 약 60%가 문의를 남겼다고 가정

    with open(os.path.join(dir_path, 'support_case.csv'), 'w', newline='', encoding='utf-8') as f_support:
        support_writer = csv.writer(f_support)
        
        # 헤더 작성 (이 테이블은 ID 자동생성이므로 case_id는 헤더에서 뻄)
        support_writer.writerow(['member_id', 'counselor_id', 'category_code', 'status', 'title', 'question_text', 'answer_text', 'satisfaction_score', 'customer_modified_at', 'support_started_at', 'resolved_at', 'created_at', 'updated_at'])
        
        for _ in range(num_cases):
            # [A] 상담 티켓 기본 정보 세팅
            customer_id = random.choice(customer_ids) if customer_ids else 1
            category_code = random.choice(list(SUPPORT_TEMPLATES.keys()))
            template = random.choice(SUPPORT_TEMPLATES[category_code])
            
            # 카테고리에 맞는 상품군(모바일 vs 홈)을 한 번만 미리 뽑습니다.
            if category_code.startswith('MOB'):
                selected_product = random.choice(MOB_PRODUCTS)
            elif category_code.startswith('HOM'):
                selected_product = random.choice(HOM_PRODUCTS)
            else:
                selected_product = "서비스" # 멤버십 등 기타 카테고리용
                
            selected_app = random.choice(APP_NAMES)
            emotion = random.choice(['POLITE', 'ANGRY', 'NEUTRAL'])

            # 미리 뽑아둔 똑같은 selected_product, selected_app을 제목, 질문, 답변에 동시에 주입합니다.
            title = template['title'].format(product=selected_product)
            question = template['q'].format(
                greeting=random.choice(GREETINGS[emotion]), 
                product=selected_product, 
                app=selected_app, 
                ending_q=random.choice(ENDINGS_Q[emotion])
            )
            answer_text_temp = template['a'].format(
                answer_start=random.choice(ANSWERS),
                app=selected_app,
                product=selected_product
            )

            # [B] 상담 진행 날짜 및 상태 세팅
            status = random.choices(['CLOSED', 'SUPPORTING', 'OPEN'], weights=[75, 15, 10], k=1)[0]
            created_at = generate_random_date(date(2025, 1, 1), date.today())
            created_str = created_at.strftime('%Y-%m-%d %H:%M:%S')
            
            counselor_id, answer_text, satisfaction_score, support_started_str, resolved_str = '', '', '', '', ''
            
            if status in ['SUPPORTING', 'CLOSED']:
                counselor_id = random.choice(counselor_ids) if counselor_ids else ''
                support_started_at = created_at + timedelta(hours=random.randint(1, 24))
                support_started_str = support_started_at.strftime('%Y-%m-%d %H:%M:%S')
                
                if status == 'CLOSED':
                    answer_text = answer_text_temp
                    resolved_at = support_started_at + timedelta(hours=random.randint(1, 48))
                    resolved_str = resolved_at.strftime('%Y-%m-%d %H:%M:%S')
                    
                    if emotion == 'ANGRY':
                        satisfaction_score = random.choices([0, 1, 2, 3, 4, 5], weights=[40, 30, 20, 10, 0, 0], k=1)[0]
                    else:
                        satisfaction_score = random.choices([0, 1, 2, 3, 4, 5], weights=[2, 3, 5, 20, 30, 40], k=1)[0]

            updated_str = resolved_str if resolved_str else (support_started_str if support_started_str else created_str)

            # case_id를 제외하고 데이터를 쓴다
            support_writer.writerow([
                customer_id, counselor_id, category_code, status, title, 
                question, answer_text, satisfaction_score, '', 
                support_started_str, resolved_str, created_str, updated_str
            ])

    print(f"[{target_users}명 기준] 상담 및 분석 데이터 생성 완료!\n")

if __name__ == "__main__":
    for size in SIZES:
        run_support_generation(size)
    print("모든 상담 더미 데이터 생성이 완료되었습니다.")