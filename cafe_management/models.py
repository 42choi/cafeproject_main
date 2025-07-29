from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

db = SQLAlchemy()

class Menu(db.Model):
    """메뉴 테이블"""
    __tablename__ = 'cafe_menu'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    image = db.Column(db.String(255))
    temperature_option = db.Column(db.String(20), default='both')  # 'ice', 'hot', 'both'
    display_order = db.Column(db.Integer, default=9999)
    is_soldout = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 관계 설정
    order_items = db.relationship('OrderItem', backref='menu', lazy=True)
    
    def __repr__(self):
        return f'<Menu {self.name}>'
    
    def to_dict(self):
        """객체를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'price': self.price,
            'description': self.description,
            'image': self.image,
            'temperature_option': self.temperature_option,
            'display_order': self.display_order,
            'is_soldout': self.is_soldout,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class Order(db.Model):
    """주문 테이블"""
    __tablename__ = 'cafe_order'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, preparing, ready, completed, cancelled
    total_amount = db.Column(db.Integer, nullable=False)
    customer_name = db.Column(db.String(50), nullable=False)
    delivery_location = db.Column(db.String(100), nullable=False)
    delivery_time = db.Column(db.String(50), nullable=True)
    order_request = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 관계 설정
    order_items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Order {self.id} - {self.customer_name}>'
    
    def to_dict(self):
        """객체를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'order_date': self.order_date.strftime('%Y-%m-%d %H:%M:%S') if self.order_date else None,
            'status': self.status,
            'total_amount': self.total_amount,
            'customer_name': self.customer_name,
            'delivery_location': self.delivery_location,
            'delivery_time': self.delivery_time,
            'order_request': self.order_request,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
            'items': [item.to_dict() for item in self.order_items]
        }


class OrderItem(db.Model):
    """주문항목 테이블"""
    __tablename__ = 'cafe_order_item'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('cafe_order.id'), nullable=False)
    menu_id = db.Column(db.Integer, db.ForeignKey('cafe_menu.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    special_request = db.Column(db.Text)
    temperature = db.Column(db.String(10), default='ice')  # 'ice', 'hot'
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<OrderItem {self.menu.name} x {self.quantity}>'
    
    def to_dict(self):
        """객체를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'menu_id': self.menu_id,
            'menu_name': self.menu.name if self.menu else None,
            'quantity': self.quantity,
            'subtotal': self.subtotal,
            'special_request': self.special_request,
            'temperature': self.temperature,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


def init_db(app):
    """데이터베이스 초기화"""
    db.init_app(app)
    
    with app.app_context():
        # 테이블 생성
        db.create_all()
        
        # 기본 메뉴 데이터 삽입 (메뉴가 없는 경우에만)
        if Menu.query.count() == 0:
            sample_menus = [
                Menu(name='아메리카노', category='커피', price=4000, description='깔끔하고 진한 아메리카노', temperature_option='both', display_order=1),
                Menu(name='카페라떼', category='커피', price=4500, description='부드러운 우유와 에스프레소의 조화', temperature_option='both', display_order=2),
                Menu(name='카푸치노', category='커피', price=4500, description='풍부한 거품과 에스프레소', temperature_option='both', display_order=3),
                Menu(name='바닐라라떼', category='커피', price=5000, description='달콤한 바닐라 시럽이 들어간 라떼', temperature_option='both', display_order=4),
                Menu(name='초콜릿라떼', category='음료', price=5500, description='진한 초콜릿과 우유의 만남', temperature_option='both', display_order=5),
                Menu(name='딸기라떼', category='음료', price=5500, description='상큼한 딸기와 우유', temperature_option='both', display_order=6),
                Menu(name='녹차라떼', category='음료', price=5000, description='고소한 녹차와 우유', temperature_option='both', display_order=7),
                Menu(name='아이스티', category='음료', price=3500, description='시원한 아이스티', temperature_option='ice', display_order=8),
                Menu(name='치즈케이크', category='디저트', price=6000, description='부드러운 뉴욕 스타일 치즈케이크', display_order=9),
                Menu(name='초콜릿케이크', category='디저트', price=6500, description='진한 초콜릿 케이크', display_order=10),
                Menu(name='크로아상', category='베이커리', price=3000, description='바삭한 프랑스식 크로아상', display_order=11),
            ]
            
            for menu in sample_menus:
                db.session.add(menu)
            
            db.session.commit()
            print('기본 메뉴 데이터가 삽입되었습니다.')


def get_categories():
    """모든 카테고리 반환"""
    categories = db.session.query(Menu.category).distinct().all()
    return [category[0] for category in categories]


def get_menu_by_category(category=None):
    """카테고리별 메뉴 조회"""
    query = Menu.query.order_by(Menu.display_order.asc(), Menu.id.asc())
    
    if category:
        query = query.filter_by(category=category)
    
    return query.all()


def get_sales_data(start_date=None, end_date=None):
    """매출 데이터 조회"""
    query = db.session.query(Order).filter(Order.status.in_(['completed', 'ready']))
    
    if start_date:
        query = query.filter(Order.order_date >= start_date)
    if end_date:
        query = query.filter(Order.order_date <= end_date)
    
    orders = query.all()
    
    total_sales = sum(order.total_amount for order in orders)
    total_orders = len(orders)
    
    return {
        'orders': orders,
        'total_sales': total_sales,
        'total_orders': total_orders
    } 