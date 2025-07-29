# 카페 주문 관리 시스템 ☕

Flask 기반의 카페 주문 관리 시스템입니다. 고객의 주문과 관리자의 메뉴 관리 기능을 제공하는 웹 애플리케이션입니다.

## 🚀 주요 기능

### 👤 사용자 기능
- **메뉴 조회**: 카테고리별 메뉴 목록 확인
- **장바구니 관리**: 메뉴 추가/수정/삭제, 수량 조정
- **주문하기**: 고객 정보 입력 및 주문 완료
- **온도 선택**: 음료류 아이스/핫 선택
- **특별 요청**: 개별 메뉴 및 전체 주문 요청사항 입력

### 🛡️ 관리자 기능
- **인증 시스템**: 관리자 로그인/로그아웃
- **대시보드**: 실시간 매출 현황 및 주문 상태 확인
- **매출 관리**: 일/주/월 매출 통계, 주문 목록 조회
- **메뉴 관리**: 메뉴 추가/수정/삭제, 이미지 업로드, 품절 관리
- **카테고리 관리**: 카테고리 추가/삭제, 통계 확인
- **주문 처리**: 주문 상태 변경, 영수증 출력
- **데이터 관리**: Excel 파일 가져오기/내보내기

## 📋 시스템 요구사항

- Python 3.8 이상
- Windows, macOS, Linux 지원
- 웹 브라우저 (Chrome, Firefox, Safari, Edge)

## 🔧 설치 및 실행

### 1. 프로젝트 클론
```bash
git clone <repository-url>
cd cafe_management
```

### 2. 가상환경 생성 및 활성화
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 의존성 패키지 설치
```bash
pip install -r requirements.txt
```

### 4. 데이터베이스 초기화
```bash
python app.py
```
애플리케이션을 처음 실행하면 자동으로 데이터베이스가 생성되고 기본 메뉴 데이터가 삽입됩니다.

### 5. 웹 브라우저에서 접속
```
http://localhost:5000
```

## 🖥️ 사용법

### 고객 주문
1. 메인 페이지에서 "메뉴 보기" 클릭
2. 카테고리별로 메뉴 확인
3. 원하는 메뉴의 "장바구니 추가" 버튼 클릭
4. 온도, 수량, 특별 요청사항 선택 후 추가
5. 장바구니에서 주문 정보 입력 후 주문 완료

### 관리자 기능
1. 메인 페이지에서 "관리자 로그인" 클릭
2. 기본 계정 정보로 로그인
   - **아이디**: admin
   - **비밀번호**: cafe123!
3. 대시보드에서 각종 관리 기능 이용

## 📊 데이터베이스 구조

### Menu (메뉴) 테이블
- `id`: 메뉴 고유 ID
- `name`: 메뉴명
- `category`: 카테고리
- `price`: 가격
- `description`: 설명
- `image`: 이미지 파일명
- `temperature_option`: 온도 옵션 ('ice', 'hot', 'both')
- `display_order`: 표시 순서
- `is_soldout`: 품절 여부

### Order (주문) 테이블
- `id`: 주문 고유 ID
- `order_date`: 주문 일시
- `status`: 주문 상태
- `total_amount`: 총 금액
- `customer_name`: 고객명
- `delivery_location`: 배달 장소
- `delivery_time`: 배달 시간
- `order_request`: 주문 요청사항

### OrderItem (주문항목) 테이블
- `id`: 주문항목 고유 ID
- `order_id`: 주문 ID (외래키)
- `menu_id`: 메뉴 ID (외래키)
- `quantity`: 수량
- `subtotal`: 소계
- `temperature`: 온도
- `special_request`: 특별 요청사항

## 🛠️ 기술 스택

### 백엔드
- **Flask**: 웹 프레임워크
- **SQLAlchemy**: ORM 데이터베이스 관리
- **Flask-Session**: 세션 관리
- **Werkzeug**: 파일 업로드 처리
- **pandas**: Excel 파일 처리

### 프론트엔드
- **Bootstrap 5**: UI 프레임워크
- **jQuery**: JavaScript 라이브러리
- **Font Awesome**: 아이콘
- **Chart.js**: 차트 및 통계

### 데이터베이스
- **SQLite**: 기본 데이터베이스 (개발용)
- **PostgreSQL/MySQL**: 운영 환경 지원 (설정 변경 시)

## 📁 프로젝트 구조

```
cafe_management/
├── app.py                 # 메인 Flask 애플리케이션
├── models.py              # 데이터베이스 모델
├── config.py              # 설정 파일
├── requirements.txt       # 의존성 패키지 목록
├── README.md             # 프로젝트 문서
├── cafe.db               # SQLite 데이터베이스 (자동 생성)
├── static/               # 정적 파일
│   ├── css/
│   │   └── style.css     # 커스텀 스타일
│   ├── js/
│   │   └── main.js       # 메인 JavaScript
│   ├── images/           # 기본 이미지
│   └── uploads/          # 업로드된 메뉴 이미지
├── templates/            # Jinja2 템플릿
│   ├── base.html         # 기본 템플릿
│   ├── index.html        # 메인 페이지
│   ├── user/             # 사용자 페이지
│   │   ├── menu.html
│   │   └── cart.html
│   └── admin/            # 관리자 페이지
│       ├── login.html
│       ├── dashboard.html
│       ├── sales.html
│       ├── menu.html
│       ├── add_menu.html
│       ├── edit_menu.html
│       ├── categories.html
│       ├── import_orders.html
│       └── receipt.html
└── flask_session/        # 세션 파일 저장소 (자동 생성)
```

## ⚙️ 설정 변경

### 데이터베이스 변경
`config.py` 파일에서 데이터베이스 연결 설정을 변경할 수 있습니다.

```python
# SQLite (기본)
SQLALCHEMY_DATABASE_URI = 'sqlite:///cafe.db'

# PostgreSQL
# SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/dbname'

# MySQL
# SQLALCHEMY_DATABASE_URI = 'mysql://user:password@localhost/dbname'
```

### 관리자 계정 변경
보안을 위해 관리자 계정 정보를 변경하세요.

```python
# config.py
ADMIN_USERNAME = 'your_admin_username'
ADMIN_PASSWORD = 'your_secure_password'
```

### 파일 업로드 설정
```python
# config.py
UPLOAD_FOLDER = 'static/uploads'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
```

## 📱 모바일 지원

Bootstrap 5의 반응형 디자인을 활용하여 모바일 기기에서도 최적화된 사용자 경험을 제공합니다.

## 🔒 보안 고려사항

### 운영 환경 배포 시 주의사항
1. **SECRET_KEY 변경**: 강력한 시크릿 키로 변경
2. **DEBUG 모드 비활성화**: `DEBUG = False`
3. **관리자 계정 보안**: 강력한 비밀번호 설정
4. **HTTPS 사용**: SSL/TLS 인증서 적용
5. **파일 업로드 제한**: 허용 파일 형식 및 크기 제한
6. **데이터베이스 보안**: 적절한 권한 설정

## 🐛 문제 해결

### 자주 발생하는 문제

**1. 데이터베이스 연결 오류**
```bash
# 데이터베이스 재초기화
python -c "from app import db; db.create_all()"
```

**2. 세션 문제**
```bash
# 세션 폴더 삭제 후 재시작
rm -rf flask_session/
```

**3. 패키지 설치 오류**
```bash
# pip 업그레이드
pip install --upgrade pip
pip install -r requirements.txt
```

## 📈 성능 최적화

### 권장사항
1. **이미지 최적화**: 메뉴 이미지 크기 및 형식 최적화
2. **캐싱 활용**: Redis 또는 Memcached 활용
3. **데이터베이스 인덱싱**: 자주 조회되는 컬럼에 인덱스 추가
4. **정적 파일 CDN**: CSS, JS, 이미지 파일 CDN 사용

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 지원 및 문의

- **이슈 리포트**: GitHub Issues 활용
- **기능 요청**: GitHub Discussions 활용
- **문서 개선**: Pull Request 환영

## 📝 버전 히스토리

### v1.0.0 (2024-01-xx)
- 초기 릴리스
- 기본 주문 및 관리 기능 구현
- 모바일 반응형 지원
- Excel 데이터 가져오기/내보내기
- 영수증 출력 기능

---

**Made with ❤️ by [Your Name]**

*카페 운영을 더 효율적으로 만들어주는 시스템입니다.* 