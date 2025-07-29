import os
from datetime import timedelta

# 기본 설정
SECRET_KEY = os.environ.get('SECRET_KEY') or 'cafe-management-secret-key-2024'
DEBUG = True

# 데이터베이스 설정
SQLALCHEMY_DATABASE_URI = 'sqlite:///cafe.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# 파일 업로드 설정
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

# 세션 설정
PERMANENT_SESSION_LIFETIME = timedelta(days=1)
SESSION_TYPE = 'filesystem'
SESSION_FILE_DIR = './flask_session'

# 관리자 인증 설정
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'cafe123!'

# 페이지네이션 설정
ITEMS_PER_PAGE = 20

# 날짜/시간 형식
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DATE_FORMAT = '%Y-%m-%d'

# 기본 카테고리
DEFAULT_CATEGORIES = [
    '커피',
    '음료',
    '디저트',
    '베이커리',
    '샐러드',
    '샌드위치'
]

# 온도 옵션
TEMPERATURE_OPTIONS = {
    'ice': '아이스',
    'hot': '핫',
    'both': '아이스/핫'
}

# 주문 상태
ORDER_STATUS = {
    'pending': '대기중',
    'preparing': '준비중',
    'ready': '준비완료',
    'completed': '완료',
    'cancelled': '취소'
} 