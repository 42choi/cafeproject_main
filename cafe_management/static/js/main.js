// 메인 JavaScript 파일
// 공통 함수들과 전역 설정

$(document).ready(function() {
    // 페이지 로드 완료 시 초기화
    initializeApp();
});

// 앱 초기화
function initializeApp() {
    // Bootstrap 툴팁 초기화
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // 자동 알림 제거
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);
    
    // 페이지 로딩 애니메이션
    $('.fade-in').addClass('animated');
    
    // 숫자 입력 필드 포맷팅
    $('.number-format').on('input', function() {
        formatNumberInput(this);
    });
    
    // 폼 검증 초기화
    initializeFormValidation();
    
    console.log('카페 주문 관리 시스템이 초기화되었습니다.');
}

// 숫자 포맷팅 함수
function formatNumber(number) {
    if (typeof number === 'string') {
        number = parseFloat(number);
    }
    return number.toLocaleString('ko-KR');
}

// 숫자 입력 필드 포맷팅
function formatNumberInput(input) {
    let value = input.value.replace(/[^\d]/g, '');
    if (value) {
        input.value = formatNumber(parseInt(value));
    }
}

// 가격 포맷팅 (원 단위)
function formatPrice(price) {
    return formatNumber(price) + '원';
}

// 알림 메시지 표시 함수
function showAlert(type, message, duration = 5000) {
    const alertTypes = {
        'success': 'alert-success',
        'error': 'alert-danger',
        'warning': 'alert-warning',
        'info': 'alert-info'
    };
    
    const alertClass = alertTypes[type] || 'alert-info';
    const alertId = 'alert-' + Date.now();
    
    const alertHtml = `
        <div class="alert ${alertClass} alert-dismissible fade show position-fixed" 
             id="${alertId}" 
             style="top: 100px; right: 20px; z-index: 9999; min-width: 300px;" 
             role="alert">
            <i class="fas fa-${getAlertIcon(type)}"></i> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    $('body').append(alertHtml);
    
    // 자동 제거
    setTimeout(function() {
        $('#' + alertId).fadeOut('slow', function() {
            $(this).remove();
        });
    }, duration);
}

// 알림 아이콘 선택
function getAlertIcon(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-triangle',
        'warning': 'exclamation-circle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// 로딩 스피너 표시
function showLoading(element, text = '로딩 중...') {
    const originalContent = element.innerHTML;
    element.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${text}`;
    element.disabled = true;
    
    // 원본 내용 복원 함수 반환
    return function() {
        element.innerHTML = originalContent;
        element.disabled = false;
    };
}

// 확인 대화상자
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// AJAX 요청 래퍼
function ajaxRequest(url, method = 'GET', data = null, successCallback = null, errorCallback = null) {
    const options = {
        url: url,
        method: method,
        dataType: 'json'
    };
    
    if (data) {
        if (method.toLowerCase() === 'get') {
            options.data = data;
        } else {
            options.data = JSON.stringify(data);
            options.contentType = 'application/json';
        }
    }
    
    $.ajax(options)
        .done(function(response) {
            if (successCallback) {
                successCallback(response);
            }
        })
        .fail(function(xhr, status, error) {
            console.error('AJAX 요청 실패:', error);
            if (errorCallback) {
                errorCallback(xhr, status, error);
            } else {
                showAlert('error', '요청 처리 중 오류가 발생했습니다.');
            }
        });
}

// 폼 검증 초기화
function initializeFormValidation() {
    // 필수 입력 필드 검증
    $('form').on('submit', function(e) {
        const form = this;
        let isValid = true;
        
        $(form).find('input[required], select[required], textarea[required]').each(function() {
            const field = $(this);
            const value = field.val().trim();
            
            if (!value) {
                isValid = false;
                field.addClass('is-invalid');
                
                // 에러 메시지 표시
                if (!field.next('.invalid-feedback').length) {
                    field.after('<div class="invalid-feedback">이 필드는 필수입니다.</div>');
                }
            } else {
                field.removeClass('is-invalid');
                field.next('.invalid-feedback').remove();
            }
        });
        
        // 이메일 형식 검증
        $(form).find('input[type="email"]').each(function() {
            const field = $(this);
            const value = field.val().trim();
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            
            if (value && !emailRegex.test(value)) {
                isValid = false;
                field.addClass('is-invalid');
                field.next('.invalid-feedback').remove();
                field.after('<div class="invalid-feedback">올바른 이메일 주소를 입력하세요.</div>');
            }
        });
        
        // 전화번호 형식 검증
        $(form).find('input[type="tel"]').each(function() {
            const field = $(this);
            const value = field.val().trim();
            const phoneRegex = /^[\d\-\s\(\)]+$/;
            
            if (value && !phoneRegex.test(value)) {
                isValid = false;
                field.addClass('is-invalid');
                field.next('.invalid-feedback').remove();
                field.after('<div class="invalid-feedback">올바른 전화번호를 입력하세요.</div>');
            }
        });
        
        if (!isValid) {
            e.preventDefault();
            showAlert('error', '입력 정보를 확인해주세요.');
            
            // 첫 번째 오류 필드로 스크롤
            const firstError = $(form).find('.is-invalid:first');
            if (firstError.length) {
                $('html, body').animate({
                    scrollTop: firstError.offset().top - 100
                }, 500);
                firstError.focus();
            }
        }
    });
    
    // 실시간 검증 (입력 시)
    $('input, select, textarea').on('input change', function() {
        const field = $(this);
        if (field.hasClass('is-invalid')) {
            const value = field.val().trim();
            if (value) {
                field.removeClass('is-invalid');
                field.next('.invalid-feedback').remove();
            }
        }
    });
}

// 장바구니 관련 함수들
const Cart = {
    // 장바구니에 상품 추가
    addItem: function(menuId, quantity = 1, options = {}) {
        const data = {
            menu_id: menuId,
            quantity: quantity,
            ...options
        };
        
        ajaxRequest('/user/add_to_cart', 'POST', data, 
            function(response) {
                if (response.success) {
                    showAlert('success', response.message);
                    Cart.updateCounter(response.cart_count);
                } else {
                    showAlert('error', response.message);
                }
            }
        );
    },
    
    // 장바구니 카운터 업데이트
    updateCounter: function(count) {
        $('.cart-counter').text(count);
        if (count > 0) {
            $('.cart-counter').show();
        } else {
            $('.cart-counter').hide();
        }
    },
    
    // 장바구니 비우기
    clear: function() {
        confirmAction('장바구니를 비우시겠습니까?', function() {
            ajaxRequest('/user/clear_cart', 'POST', null,
                function(response) {
                    if (response.success) {
                        showAlert('success', '장바구니가 비워졌습니다.');
                        location.reload();
                    }
                }
            );
        });
    }
};

// 관리자 기능들
const Admin = {
    // 주문 상태 업데이트
    updateOrderStatus: function(orderId, status) {
        ajaxRequest(`/admin/update_order_status/${orderId}`, 'POST', { status: status },
            function(response) {
                if (response.success) {
                    showAlert('success', '주문 상태가 업데이트되었습니다.');
                } else {
                    showAlert('error', response.message);
                }
            }
        );
    },
    
    // 메뉴 품절 토글
    toggleMenuSoldout: function(menuId) {
        ajaxRequest(`/admin/menu/toggle_soldout/${menuId}`, 'POST', null,
            function(response) {
                if (response.success) {
                    showAlert('success', `메뉴가 ${response.status}로 변경되었습니다.`);
                    setTimeout(() => location.reload(), 1000);
                } else {
                    showAlert('error', response.message);
                }
            }
        );
    },
    
    // 주문 삭제
    deleteOrder: function(orderId) {
        confirmAction('이 주문을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.', function() {
            ajaxRequest(`/admin/delete_order/${orderId}`, 'POST', null,
                function(response) {
                    if (response.success) {
                        showAlert('success', '주문이 삭제되었습니다.');
                        $(`tr[data-order-id="${orderId}"]`).fadeOut('slow', function() {
                            $(this).remove();
                        });
                    } else {
                        showAlert('error', response.message);
                    }
                }
            );
        });
    }
};

// 유틸리티 함수들
const Utils = {
    // 날짜 포맷팅
    formatDate: function(date, format = 'YYYY-MM-DD') {
        if (typeof date === 'string') {
            date = new Date(date);
        }
        
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        const seconds = String(date.getSeconds()).padStart(2, '0');
        
        return format
            .replace('YYYY', year)
            .replace('MM', month)
            .replace('DD', day)
            .replace('HH', hours)
            .replace('mm', minutes)
            .replace('ss', seconds);
    },
    
    // 문자열 자르기
    truncate: function(str, length = 50) {
        if (str.length <= length) {
            return str;
        }
        return str.substr(0, length) + '...';
    },
    
    // 이미지 로드 오류 처리
    handleImageError: function(img) {
        img.src = '/static/images/no-image.png';
        img.alt = '이미지 없음';
    },
    
    // 스크롤 상단 이동
    scrollToTop: function() {
        $('html, body').animate({ scrollTop: 0 }, 'slow');
    },
    
    // 로컬 스토리지 관리
    storage: {
        set: function(key, value) {
            try {
                localStorage.setItem(key, JSON.stringify(value));
            } catch (e) {
                console.warn('로컬 스토리지 저장 실패:', e);
            }
        },
        
        get: function(key, defaultValue = null) {
            try {
                const item = localStorage.getItem(key);
                return item ? JSON.parse(item) : defaultValue;
            } catch (e) {
                console.warn('로컬 스토리지 읽기 실패:', e);
                return defaultValue;
            }
        },
        
        remove: function(key) {
            try {
                localStorage.removeItem(key);
            } catch (e) {
                console.warn('로컬 스토리지 삭제 실패:', e);
            }
        }
    }
};

// 페이지별 초기화
const PageInit = {
    // 메뉴 페이지 초기화
    menu: function() {
        // 메뉴 필터링
        $('.category-filter').on('click', function(e) {
            e.preventDefault();
            const category = $(this).data('category');
            window.location.href = `/user/menu${category ? '?category=' + category : ''}`;
        });
        
        // 메뉴 검색
        $('#menuSearch').on('input', function() {
            const searchTerm = $(this).val().toLowerCase();
            $('.menu-item').each(function() {
                const menuName = $(this).find('.card-title').text().toLowerCase();
                const menuDesc = $(this).find('.card-text').text().toLowerCase();
                
                if (menuName.includes(searchTerm) || menuDesc.includes(searchTerm)) {
                    $(this).parent().show();
                } else {
                    $(this).parent().hide();
                }
            });
        });
    },
    
    // 장바구니 페이지 초기화
    cart: function() {
        // 수량 변경 버튼
        $('.qty-btn').on('click', function() {
            const input = $(this).siblings('input[type="number"]');
            const change = $(this).hasClass('qty-plus') ? 1 : -1;
            const newValue = Math.max(1, parseInt(input.val()) + change);
            input.val(newValue);
            input.trigger('change');
        });
        
        // 자동 총액 계산
        $('.cart-item').each(function() {
            const row = $(this);
            const priceInput = row.find('.item-price');
            const qtyInput = row.find('.item-quantity');
            const subtotalElement = row.find('.item-subtotal');
            
            qtyInput.on('input', function() {
                const price = parseFloat(priceInput.val()) || 0;
                const qty = parseInt(qtyInput.val()) || 0;
                const subtotal = price * qty;
                subtotalElement.text(formatPrice(subtotal));
                
                // 전체 총액 재계산
                updateCartTotal();
            });
        });
    },
    
    // 관리자 대시보드 초기화
    adminDashboard: function() {
        // 실시간 주문 업데이트
        setInterval(function() {
            Admin.refreshOrders();
        }, 30000); // 30초마다
        
        // 통계 차트 초기화
        if (typeof Chart !== 'undefined') {
            initializeCharts();
        }
    }
};

// 차트 초기화 (Chart.js 사용)
function initializeCharts() {
    // 매출 차트
    const salesCtx = document.getElementById('salesChart');
    if (salesCtx) {
        new Chart(salesCtx, {
            type: 'line',
            data: {
                labels: [], // 서버에서 데이터 로드
                datasets: [{
                    label: '일별 매출',
                    data: [],
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
}

// 키보드 단축키
document.addEventListener('keydown', function(e) {
    // Ctrl + / : 도움말
    if (e.ctrlKey && e.key === '/') {
        e.preventDefault();
        showHelp();
    }
    
    // ESC : 모달 닫기
    if (e.key === 'Escape') {
        $('.modal').modal('hide');
    }
    
    // F5 새로고침 확인 (관리자 페이지에서)
    if (e.key === 'F5' && window.location.pathname.includes('/admin/')) {
        if (!confirm('페이지를 새로고침하시겠습니까?')) {
            e.preventDefault();
        }
    }
});

// 도움말 표시
function showHelp() {
    const helpContent = `
        <div class="modal fade" id="helpModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">도움말</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <h6>키보드 단축키</h6>
                        <ul>
                            <li><kbd>Ctrl + /</kbd> : 도움말 표시</li>
                            <li><kbd>ESC</kbd> : 모달 창 닫기</li>
                            <li><kbd>F5</kbd> : 페이지 새로고침</li>
                        </ul>
                        
                        <h6>사용법</h6>
                        <ul>
                            <li>메뉴 페이지에서 상품을 클릭하여 장바구니에 추가</li>
                            <li>장바구니에서 수량 조정 및 주문 완료</li>
                            <li>관리자는 로그인 후 메뉴 및 주문 관리 가능</li>
                        </ul>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">닫기</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // 기존 도움말 모달 제거
    $('#helpModal').remove();
    
    // 새 도움말 모달 추가 및 표시
    $('body').append(helpContent);
    $('#helpModal').modal('show');
}

// 전역 오류 처리
window.addEventListener('error', function(e) {
    console.error('JavaScript 오류:', e.error);
    // 개발 환경에서만 오류 표시
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        showAlert('error', 'JavaScript 오류가 발생했습니다. 콘솔을 확인해주세요.');
    }
});

// 전역 변수로 노출
window.showAlert = showAlert;
window.formatNumber = formatNumber;
window.formatPrice = formatPrice;
window.Cart = Cart;
window.Admin = Admin;
window.Utils = Utils;
window.PageInit = PageInit; 