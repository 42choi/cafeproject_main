from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from flask_session import Session
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import pandas as pd
from io import BytesIO
import json

# 로컬 모듈 import
from models import db, Menu, Order, OrderItem, init_db, get_categories, get_menu_by_category, get_sales_data
import config

app = Flask(__name__)

# 설정 로드
app.config.from_object(config)

# 확장 초기화
Session(app)
init_db(app)

# 업로드 폴더 생성
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    """허용된 파일 확장자 확인"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def login_required(f):
    """관리자 로그인 필요 데코레이터"""
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# ============================================================================
# 메인 라우트
# ============================================================================

@app.route('/')
def index():
    """메인 페이지 (사용자/관리자 선택)"""
    return render_template('index.html')

@app.route('/init_db')
def init_database():
    """데이터베이스 초기화"""
    try:
        db.create_all()
        flash('데이터베이스가 초기화되었습니다.', 'success')
    except Exception as e:
        flash(f'데이터베이스 초기화 중 오류가 발생했습니다: {str(e)}', 'error')
    return redirect(url_for('index'))

@app.route('/update_db_schema')
def update_db_schema():
    """데이터베이스 스키마 업데이트"""
    try:
        db.create_all()
        flash('데이터베이스 스키마가 업데이트되었습니다.', 'success')
    except Exception as e:
        flash(f'스키마 업데이트 중 오류가 발생했습니다: {str(e)}', 'error')
    return redirect(url_for('index'))

# ============================================================================
# 사용자 라우트
# ============================================================================

@app.route('/user/menu')
def user_menu():
    """메뉴 조회"""
    category = request.args.get('category')
    categories = get_categories()
    menus = get_menu_by_category(category)
    
    # 장바구니 항목 수 계산
    cart = session.get('cart', {})
    cart_count = sum(item['quantity'] for item in cart.values())
    
    return render_template('user/menu.html', 
                         menus=menus, 
                         categories=categories, 
                         selected_category=category,
                         cart_count=cart_count)

@app.route('/user/add_to_cart', methods=['POST'])
def add_to_cart():
    """장바구니에 추가"""
    try:
        menu_id = int(request.form.get('menu_id'))
        quantity = int(request.form.get('quantity', 1))
        temperature = request.form.get('temperature', 'ice')
        special_request = request.form.get('special_request', '')
        
        menu = Menu.query.get_or_404(menu_id)
        
        if menu.is_soldout:
            return jsonify({'success': False, 'message': '품절된 상품입니다.'})
        
        # 세션에 장바구니 초기화
        if 'cart' not in session:
            session['cart'] = {}
        
        cart_key = f"{menu_id}_{temperature}_{special_request}"
        
        if cart_key in session['cart']:
            session['cart'][cart_key]['quantity'] += quantity
        else:
            session['cart'][cart_key] = {
                'menu_id': menu_id,
                'menu_name': menu.name,
                'price': menu.price,
                'quantity': quantity,
                'temperature': temperature,
                'special_request': special_request,
                'subtotal': menu.price * quantity
            }
        
        # subtotal 재계산
        session['cart'][cart_key]['subtotal'] = menu.price * session['cart'][cart_key]['quantity']
        session.modified = True
        
        cart_count = sum(item['quantity'] for item in session['cart'].values())
        
        return jsonify({
            'success': True, 
            'message': '장바구니에 추가되었습니다.',
            'cart_count': cart_count
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'오류: {str(e)}'})

@app.route('/user/view_cart')
def view_cart():
    """장바구니 조회"""
    cart = session.get('cart', {})
    total_amount = sum(item['subtotal'] for item in cart.values())
    
    return render_template('user/cart.html', cart=cart, total_amount=total_amount)

@app.route('/user/update_cart', methods=['POST'])
def update_cart():
    """장바구니 수정"""
    try:
        cart_key = request.form.get('cart_key')
        quantity = int(request.form.get('quantity', 1))
        
        if 'cart' in session and cart_key in session['cart']:
            if quantity <= 0:
                del session['cart'][cart_key]
            else:
                session['cart'][cart_key]['quantity'] = quantity
                menu_price = session['cart'][cart_key]['price']
                session['cart'][cart_key]['subtotal'] = menu_price * quantity
            
            session.modified = True
            flash('장바구니가 업데이트되었습니다.', 'success')
        
        return redirect(url_for('view_cart'))
        
    except Exception as e:
        flash(f'장바구니 업데이트 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('view_cart'))

@app.route('/user/place_order', methods=['POST'])
def place_order():
    """주문하기"""
    try:
        cart = session.get('cart', {})
        if not cart:
            flash('장바구니가 비어있습니다.', 'error')
            return redirect(url_for('view_cart'))
        
        customer_name = request.form.get('customer_name')
        delivery_location = request.form.get('delivery_location')
        delivery_time = request.form.get('delivery_time')
        order_request = request.form.get('order_request')
        
        if not customer_name or not delivery_location:
            flash('고객명과 배달 장소는 필수입니다.', 'error')
            return redirect(url_for('view_cart'))
        
        # 주문 생성
        total_amount = sum(item['subtotal'] for item in cart.values())
        
        order = Order(
            customer_name=customer_name,
            delivery_location=delivery_location,
            delivery_time=delivery_time,
            order_request=order_request,
            total_amount=total_amount,
            status='pending'
        )
        
        db.session.add(order)
        db.session.flush()  # order.id를 얻기 위해
        
        # 주문 항목 생성
        for cart_item in cart.values():
            order_item = OrderItem(
                order_id=order.id,
                menu_id=cart_item['menu_id'],
                quantity=cart_item['quantity'],
                subtotal=cart_item['subtotal'],
                temperature=cart_item['temperature'],
                special_request=cart_item['special_request']
            )
            db.session.add(order_item)
        
        db.session.commit()
        
        # 장바구니 비우기
        session.pop('cart', None)
        session.modified = True
        
        flash(f'주문이 완료되었습니다. 주문번호: {order.id}', 'success')
        return redirect(url_for('user_menu'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'주문 처리 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('view_cart'))

@app.route('/user/clear_cart', methods=['POST'])
def clear_cart():
    """장바구니 비우기"""
    session.pop('cart', None)
    session.modified = True
    flash('장바구니가 비워졌습니다.', 'success')
    return redirect(url_for('view_cart'))

# ============================================================================
# 관리자 라우트
# ============================================================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """관리자 로그인"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == app.config['ADMIN_USERNAME'] and password == app.config['ADMIN_PASSWORD']:
            session['admin_logged_in'] = True
            session.permanent = True
            flash('관리자로 로그인되었습니다.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('아이디 또는 비밀번호가 올바르지 않습니다.', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    """관리자 로그아웃"""
    session.pop('admin_logged_in', None)
    flash('로그아웃되었습니다.', 'success')
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_dashboard():
    """관리자 대시보드"""
    # 오늘 매출 통계
    today = datetime.now().date()
    today_orders = Order.query.filter(
        Order.order_date >= today,
        Order.status.in_(['completed', 'ready'])
    ).all()
    
    today_sales = sum(order.total_amount for order in today_orders)
    today_order_count = len(today_orders)
    
    # 최근 주문
    recent_orders = Order.query.order_by(Order.order_date.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html',
                         today_sales=today_sales,
                         today_order_count=today_order_count,
                         recent_orders=recent_orders)

@app.route('/admin/sales')
@login_required
def admin_sales():
    """매출 관리"""
    # 기본적으로 오늘부터 일주일 전까지의 데이터
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=7)
    
    sales_data = get_sales_data(start_date, end_date)
    
    return render_template('admin/sales.html',
                         sales_data=sales_data,
                         start_date=start_date,
                         end_date=end_date)

@app.route('/admin/sales/filter', methods=['POST'])
@login_required
def filter_sales():
    """매출 필터링"""
    try:
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
        
        sales_data = get_sales_data(start_date, end_date)
        
        return render_template('admin/sales.html',
                             sales_data=sales_data,
                             start_date=start_date,
                             end_date=end_date)
    except Exception as e:
        flash(f'날짜 필터링 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('admin_sales'))

@app.route('/admin/export_all_orders')
@login_required
def export_all_orders():
    """전체 주문 내역 내보내기"""
    try:
        orders = Order.query.order_by(Order.order_date.desc()).all()
        
        # Excel 데이터 준비
        data = []
        for order in orders:
            for item in order.order_items:
                data.append({
                    '주문번호': order.id,
                    '주문일시': order.order_date.strftime('%Y-%m-%d %H:%M:%S'),
                    '고객명': order.customer_name,
                    '배달장소': order.delivery_location,
                    '배달시간': order.delivery_time or '',
                    '상태': order.status,
                    '메뉴명': item.menu.name,
                    '수량': item.quantity,
                    '온도': item.temperature,
                    '특별요청': item.special_request or '',
                    '소계': item.subtotal,
                    '총액': order.total_amount
                })
        
        df = pd.DataFrame(data)
        
        # Excel 파일 생성
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='주문내역', index=False)
        output.seek(0)
        
        return send_file(
            output,
            as_attachment=True,
            download_name=f'전체_주문내역_{datetime.now().strftime("%Y%m%d")}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        flash(f'내보내기 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('admin_sales'))

@app.route('/admin/export_period_orders', methods=['POST'])
@login_required
def export_period_orders():
    """기간별 주문 내역 내보내기"""
    try:
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
        
        query = Order.query.order_by(Order.order_date.desc())
        
        if start_date:
            query = query.filter(Order.order_date >= start_date)
        if end_date:
            query = query.filter(Order.order_date <= end_date + timedelta(days=1))
        
        orders = query.all()
        
        # Excel 데이터 준비
        data = []
        for order in orders:
            for item in order.order_items:
                data.append({
                    '주문번호': order.id,
                    '주문일시': order.order_date.strftime('%Y-%m-%d %H:%M:%S'),
                    '고객명': order.customer_name,
                    '배달장소': order.delivery_location,
                    '배달시간': order.delivery_time or '',
                    '상태': order.status,
                    '메뉴명': item.menu.name,
                    '수량': item.quantity,
                    '온도': item.temperature,
                    '특별요청': item.special_request or '',
                    '소계': item.subtotal,
                    '총액': order.total_amount
                })
        
        df = pd.DataFrame(data)
        
        # Excel 파일 생성
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='주문내역', index=False)
        output.seek(0)
        
        period_str = f"{start_date_str}_{end_date_str}" if start_date_str and end_date_str else datetime.now().strftime("%Y%m%d")
        
        return send_file(
            output,
            as_attachment=True,
            download_name=f'주문내역_{period_str}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        flash(f'내보내기 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('admin_sales'))

# ============================================================================
# 메뉴 관리 라우트
# ============================================================================

@app.route('/admin/menu')
@login_required
def admin_menu():
    """메뉴 관리"""
    category = request.args.get('category')
    categories = get_categories()
    menus = get_menu_by_category(category)
    
    return render_template('admin/menu.html',
                         menus=menus,
                         categories=categories,
                         selected_category=category)

@app.route('/admin/menu/add', methods=['GET', 'POST'])
@login_required
def add_menu():
    """메뉴 추가"""
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            category = request.form.get('category')
            price = float(request.form.get('price'))
            description = request.form.get('description')
            temperature_option = request.form.get('temperature_option', 'both')
            
            # 이미지 업로드 처리
            image_filename = None
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # 유니크한 파일명 생성
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    name_part = ''.join(name.split())[:10]  # 메뉴명의 일부 사용
                    image_filename = f"{timestamp}_{name_part}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
            
            # 디스플레이 순서 설정 (마지막 순서 +1)
            max_order = db.session.query(db.func.max(Menu.display_order)).scalar() or 0
            display_order = max_order + 1
            
            menu = Menu(
                name=name,
                category=category,
                price=price,
                description=description,
                image=image_filename,
                temperature_option=temperature_option,
                display_order=display_order
            )
            
            db.session.add(menu)
            db.session.commit()
            
            flash('메뉴가 추가되었습니다.', 'success')
            return redirect(url_for('admin_menu'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'메뉴 추가 중 오류가 발생했습니다: {str(e)}', 'error')
    
    categories = get_categories()
    return render_template('admin/add_menu.html', categories=categories)

@app.route('/admin/menu/edit/<int:menu_id>', methods=['GET', 'POST'])
@login_required
def edit_menu(menu_id):
    """메뉴 수정"""
    menu = Menu.query.get_or_404(menu_id)
    
    if request.method == 'POST':
        try:
            menu.name = request.form.get('name')
            menu.category = request.form.get('category')
            menu.price = float(request.form.get('price'))
            menu.description = request.form.get('description')
            menu.temperature_option = request.form.get('temperature_option', 'both')
            
            # 이미지 업로드 처리
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename != '' and allowed_file(file.filename):
                    # 기존 이미지 삭제
                    if menu.image:
                        old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], menu.image)
                        if os.path.exists(old_image_path):
                            os.remove(old_image_path)
                    
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    name_part = ''.join(menu.name.split())[:10]
                    image_filename = f"{timestamp}_{name_part}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
                    menu.image = image_filename
            
            menu.updated_at = datetime.now()
            db.session.commit()
            
            flash('메뉴가 수정되었습니다.', 'success')
            return redirect(url_for('admin_menu'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'메뉴 수정 중 오류가 발생했습니다: {str(e)}', 'error')
    
    categories = get_categories()
    return render_template('admin/edit_menu.html', menu=menu, categories=categories)

@app.route('/admin/menu/delete/<int:menu_id>')
@login_required
def delete_menu(menu_id):
    """메뉴 삭제"""
    try:
        menu = Menu.query.get_or_404(menu_id)
        
        # 이미지 파일 삭제
        if menu.image:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], menu.image)
            if os.path.exists(image_path):
                os.remove(image_path)
        
        db.session.delete(menu)
        db.session.commit()
        
        flash('메뉴가 삭제되었습니다.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'메뉴 삭제 중 오류가 발생했습니다: {str(e)}', 'error')
    
    return redirect(url_for('admin_menu'))

@app.route('/admin/menu/toggle_soldout/<int:menu_id>', methods=['POST'])
@login_required
def toggle_soldout(menu_id):
    """품절 상태 토글"""
    try:
        menu = Menu.query.get_or_404(menu_id)
        menu.is_soldout = not menu.is_soldout
        menu.updated_at = datetime.now()
        db.session.commit()
        
        status = '품절' if menu.is_soldout else '판매중'
        return jsonify({'success': True, 'status': status, 'is_soldout': menu.is_soldout})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@app.route('/admin/menu/update_order', methods=['POST'])
@login_required
def update_menu_order():
    """메뉴 순서 변경"""
    try:
        order_data = request.json.get('order', [])
        
        for item in order_data:
            menu_id = item['id']
            new_order = item['order']
            
            menu = Menu.query.get(menu_id)
            if menu:
                menu.display_order = new_order
                menu.updated_at = datetime.now()
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

# ============================================================================
# 카테고리 관리 라우트
# ============================================================================

@app.route('/admin/categories', methods=['GET', 'POST'])
@login_required
def admin_categories():
    """카테고리 관리"""
    if request.method == 'POST':
        try:
            category_name = request.form.get('category_name')
            
            if category_name:
                # 중복 체크
                existing = Menu.query.filter_by(category=category_name).first()
                if existing:
                    flash('이미 존재하는 카테고리입니다.', 'error')
                else:
                    # 샘플 메뉴로 카테고리 생성
                    sample_menu = Menu(
                        name=f'{category_name} 샘플',
                        category=category_name,
                        price=0,
                        description='카테고리 생성용 임시 메뉴입니다. 삭제해주세요.',
                        is_soldout=True
                    )
                    db.session.add(sample_menu)
                    db.session.commit()
                    flash('카테고리가 추가되었습니다.', 'success')
            else:
                flash('카테고리명을 입력해주세요.', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'카테고리 추가 중 오류가 발생했습니다: {str(e)}', 'error')
    
    categories = get_categories()
    # 각 카테고리별 메뉴 수 계산
    category_counts = {}
    for category in categories:
        count = Menu.query.filter_by(category=category).count()
        category_counts[category] = count
    
    return render_template('admin/categories.html', 
                         categories=categories, 
                         category_counts=category_counts)

@app.route('/admin/categories/delete/<category>', methods=['POST'])
@login_required
def delete_category(category):
    """카테고리 삭제"""
    try:
        # 해당 카테고리의 모든 메뉴 삭제
        menus = Menu.query.filter_by(category=category).all()
        
        for menu in menus:
            # 이미지 파일 삭제
            if menu.image:
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], menu.image)
                if os.path.exists(image_path):
                    os.remove(image_path)
            db.session.delete(menu)
        
        db.session.commit()
        flash(f'카테고리 "{category}"와 관련 메뉴들이 삭제되었습니다.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'카테고리 삭제 중 오류가 발생했습니다: {str(e)}', 'error')
    
    return redirect(url_for('admin_categories'))

# ============================================================================
# 주문 관리 라우트
# ============================================================================

@app.route('/admin/import_orders', methods=['GET', 'POST'])
@login_required
def import_orders():
    """주문 데이터 가져오기"""
    if request.method == 'POST':
        try:
            if 'file' not in request.files:
                flash('파일이 선택되지 않았습니다.', 'error')
                return redirect(request.url)
            
            file = request.files['file']
            if file.filename == '':
                flash('파일이 선택되지 않았습니다.', 'error')
                return redirect(request.url)
            
            if file and file.filename.endswith(('.xlsx', '.xls')):
                # Excel 파일 읽기
                df = pd.read_excel(file)
                
                imported_count = 0
                for _, row in df.iterrows():
                    # 주문 데이터 처리 (실제 컬럼명에 맞게 수정 필요)
                    order = Order(
                        customer_name=row.get('고객명', ''),
                        delivery_location=row.get('배달장소', ''),
                        delivery_time=row.get('배달시간', ''),
                        total_amount=int(row.get('총액', 0)),
                        status=row.get('상태', 'pending'),
                        order_request=row.get('주문요청', '')
                    )
                    db.session.add(order)
                    imported_count += 1
                
                db.session.commit()
                flash(f'{imported_count}개의 주문이 가져왔습니다.', 'success')
            else:
                flash('Excel 파일만 업로드 가능합니다.', 'error')
                
        except Exception as e:
            db.session.rollback()
            flash(f'파일 처리 중 오류가 발생했습니다: {str(e)}', 'error')
    
    return render_template('admin/import_orders.html')

@app.route('/admin/print_receipt/<int:order_id>')
@login_required
def print_receipt(order_id):
    """영수증 출력"""
    order = Order.query.get_or_404(order_id)
    return render_template('admin/receipt.html', order=order)

@app.route('/admin/get_recent_orders')
@login_required
def get_recent_orders():
    """최근 주문 조회 (AJAX)"""
    try:
        orders = Order.query.order_by(Order.order_date.desc()).limit(20).all()
        orders_data = [order.to_dict() for order in orders]
        return jsonify({'success': True, 'orders': orders_data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/admin/update_order_status/<int:order_id>', methods=['POST'])
@login_required
def update_order_status(order_id):
    """주문 상태 업데이트 (AJAX)"""
    try:
        order = Order.query.get_or_404(order_id)
        new_status = request.json.get('status')
        
        if new_status in ['pending', 'preparing', 'ready', 'completed', 'cancelled']:
            order.status = new_status
            order.updated_at = datetime.now()
            db.session.commit()
            
            return jsonify({'success': True, 'status': new_status})
        else:
            return jsonify({'success': False, 'message': '잘못된 상태값입니다.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@app.route('/admin/delete_order/<int:order_id>', methods=['POST'])
@login_required
def delete_order(order_id):
    """주문 삭제 (AJAX)"""
    try:
        order = Order.query.get_or_404(order_id)
        db.session.delete(order)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

# ============================================================================
# 에러 핸들러
# ============================================================================

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# ============================================================================
# 템플릿 컨텍스트 프로세서
# ============================================================================

@app.context_processor
def inject_globals():
    """모든 템플릿에서 사용할 전역 변수들"""
    cart_count = 0
    if 'cart' in session:
        cart_count = sum(item['quantity'] for item in session['cart'].values())
    
    return {
        'cart_count': cart_count,
        'admin_logged_in': session.get('admin_logged_in', False),
        'current_year': datetime.now().year
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 