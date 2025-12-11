// 等待DOM加载完成
document.addEventListener('DOMContentLoaded', function() {
    // 初始化所有下拉菜单
    const dropdownTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="dropdown"]'));
    dropdownTriggerList.map(function(dropdownTriggerEl) {
        return new bootstrap.Dropdown(dropdownTriggerEl);
    });

    // 侧边栏功能
    const sidebar = document.getElementById('sidebar');
    const toggleSidebarBtn = document.getElementById('toggleSidebarBtn');
    const mainContent = document.getElementById('mainContent');
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');

    if (toggleSidebarBtn) {
        toggleSidebarBtn.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            mainContent.classList.toggle('expanded');

            // 切换按钮图标
            const icon = this.querySelector('i');
            if (sidebar.classList.contains('collapsed')) {
                icon.classList.remove('fa-chevron-left');
                icon.classList.add('fa-chevron-right');
            } else {
                icon.classList.remove('fa-chevron-right');
                icon.classList.add('fa-chevron-left');
            }

            // 保存状态到localStorage
            localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
        });
    }

    // 加载侧边栏状态
    if (localStorage.getItem('sidebarCollapsed') === 'true') {
        sidebar.classList.add('collapsed');
        mainContent.classList.add('expanded');
        const icon = toggleSidebarBtn?.querySelector('i');
        if (icon) {
            icon.classList.remove('fa-chevron-left');
            icon.classList.add('fa-chevron-right');
        }
    }

    // 移动端菜单按钮
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function() {
            sidebar.classList.toggle('show');
        });
    }

    // 点击主内容区域时，在移动端关闭侧边栏
    mainContent.addEventListener('click', function() {
        if (window.innerWidth <= 992 && sidebar.classList.contains('show')) {
            sidebar.classList.remove('show');
        }
    });

    // 通知功能
    const notificationItems = document.querySelectorAll('.notification-item');
    const markAllReadBtn = document.getElementById('markAllRead');
    const notificationBadge = document.querySelector('.notification-badge');

    // 标记单个通知为已读
    notificationItems.forEach(item => {
        item.addEventListener('click', function() {
            if (this.classList.contains('notification-unread')) {
                const notificationId = this.getAttribute('data-id');
                markNotificationAsRead(notificationId, this);
            }
        });
    });

    // 全部标记为已读
    if (markAllReadBtn) {
        markAllReadBtn.addEventListener('click', function(e) {
            e.preventDefault();
            markAllNotificationsAsRead();
        });
    }

    // 标记通知为已读的函数
    function markNotificationAsRead(notificationId, element) {
        // 这里应该发送AJAX请求到服务器
        fetch(`/api/notifications/${notificationId}/read`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                element.classList.remove('notification-unread');
                updateNotificationBadge();
            }
        })
        .catch(error => console.error('Error:', error));
    }

    // 标记所有通知为已读
    function markAllNotificationsAsRead() {
        fetch('/api/notifications/read-all', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.querySelectorAll('.notification-unread').forEach(item => {
                    item.classList.remove('notification-unread');
                });
                updateNotificationBadge();
            }
        })
        .catch(error => console.error('Error:', error));
    }

    // 更新通知徽章
    function updateNotificationBadge() {
        const unreadCount = document.querySelectorAll('.notification-unread').length;

        if (notificationBadge) {
            if (unreadCount > 0) {
                notificationBadge.textContent = unreadCount;
                notificationBadge.style.display = 'flex';
            } else {
                notificationBadge.style.display = 'none';
            }
        }
    }

    // 表单提交确认
    const confirmForms = document.querySelectorAll('form[data-confirm]');
    confirmForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const message = this.getAttribute('data-confirm');
            if (message && !confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // 自动关闭警告框
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // 动态加载页面内容（如果需要）
    if (typeof window.loadPage === 'function') {
        window.addEventListener('popstate', function(event) {
            if (event.state && event.state.page) {
                window.loadPage(event.state.page);
            }
        });
    }

    // 处理回车键搜索
    const searchInputs = document.querySelectorAll('input[type="search"], input[data-search]');
    searchInputs.forEach(input => {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const searchForm = this.closest('form');
                if (searchForm) {
                    searchForm.submit();
                }
            }
        });
    });

    // 工具提示初始化
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // 调整页面高度以适应内容
    function adjustPageHeight() {
        const sidebar = document.getElementById('sidebar');
        const mainContent = document.getElementById('mainContent');
        const pageContainer = document.querySelector('.page-container');

        if (sidebar && mainContent && pageContainer) {
            const windowHeight = window.innerHeight;
            const navbarHeight = 70;
            const contentHeight = windowHeight - navbarHeight - 40; // 减去padding

            pageContainer.style.minHeight = contentHeight + 'px';
        }
    }

    // 初始调整和窗口调整时重新调整
    adjustPageHeight();
    window.addEventListener('resize', adjustPageHeight);
});

// 全局AJAX请求函数
function makeRequest(url, method = 'GET', data = null) {
    const headers = {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    };

    const config = {
        method: method,
        headers: headers
    };

    if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
        config.body = JSON.stringify(data);
    }

    return fetch(url, config)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        });
}

// 显示加载动画
function showLoading() {
    const loadingEl = document.createElement('div');
    loadingEl.className = 'loading-overlay';
    loadingEl.innerHTML = `
        <div class="loading-spinner">
            <div class="spinner-border" role="status">
                <span class="visually-hidden">加载中...</span>
            </div>
        </div>
    `;
    document.body.appendChild(loadingEl);
}

// 隐藏加载动画
function hideLoading() {
    const loadingEl = document.querySelector('.loading-overlay');
    if (loadingEl) {
        loadingEl.remove();
    }
}

// 显示成功消息
function showSuccess(message) {
    showAlert('success', message);
}

// 显示错误消息
function showError(message) {
    showAlert('danger', message);
}

// 显示警告消息
function showWarning(message) {
    showAlert('warning', message);
}

// 显示信息消息
function showInfo(message) {
    showAlert('info', message);
}

// 显示警告框
function showAlert(type, message) {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;

    // 在页面顶部插入警告
    const mainContent = document.getElementById('mainContent');
    if (mainContent) {
        const pageContainer = mainContent.querySelector('.page-container');
        if (pageContainer) {
            pageContainer.insertAdjacentHTML('afterbegin', alertHtml);

            // 自动关闭
            setTimeout(() => {
                const alert = pageContainer.querySelector('.alert');
                if (alert) {
                    const bsAlert = new bootstrap.Alert(alert);
                    bsAlert.close();
                }
            }, 5000);
        }
    }
}

// 确认对话框
function confirmDialog(message, callback) {
    if (confirm(message)) {
        if (typeof callback === 'function') {
            callback();
        }
        return true;
    }
    return false;
}