/**
 * 登录页面交互脚本
 */

// 等待DOM加载完成
document.addEventListener('DOMContentLoaded', function() {
    initLoginPage();
});

/**
 * 初始化登录页面
 */
function initLoginPage() {
    // 初始化所有功能
    initUserTypeSelection();
    initPasswordToggle();
    initFormSubmission();
    initAutoFocus();
}

/**
 * 初始化用户类型选择
 */
function initUserTypeSelection() {
    const btnStudent = document.getElementById('btnStudent');
    const btnTeacher = document.getElementById('btnTeacher');
    const userTypeInput = document.getElementById('user_type');
    const idInput = document.querySelector('input[name="id"]');

    if (!btnStudent || !btnTeacher || !userTypeInput) {
        console.warn('用户类型选择元素未找到');
        return;
    }

    /**
     * 选择用户类型
     *
     */
    function selectUserType(type) {
        // 更新按钮样式
        if (type === 'user' ) {
            btnStudent.classList.add('active');
            btnTeacher.classList.remove('active');
            if (idInput) {
                idInput.placeholder = '请输入用户账号';
            }
        } else {
            btnStudent.classList.remove('active');
            btnTeacher.classList.add('active');
            if (idInput) {
                idInput.placeholder = '请输入管理员账号';
            }
        }

        // 更新隐藏输入框的值
        userTypeInput.value = type;
    }

    // 绑定点击事件
    btnStudent.addEventListener('click', () => selectUserType('user'));
    btnTeacher.addEventListener('click', () => selectUserType('admin'));

    // 根据当前值初始化状态
    if (userTypeInput.value === 'admin') {
        selectUserType('admin');
    } else {
        selectUserType('user'); // 默认选择学生
    }
}

/**
 * 初始化密码显示/隐藏切换
 */
function initPasswordToggle() {
    const toggleBtn = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('passwordInput');

    if (!toggleBtn || !passwordInput) {
        console.warn('密码切换元素未找到');
        return;
    }

    toggleBtn.addEventListener('click', function() {
        const type = passwordInput.type === 'password' ? 'text' : 'password';
        passwordInput.type = type;

        // 切换图标
        const icon = this.querySelector('i');
        icon.classList.toggle('fa-eye');
        icon.classList.toggle('fa-eye-slash');
    });
}

/**
 * 初始化表单提交
 */
function initFormSubmission() {
    const loginForm = document.getElementById('loginForm');
    const loginBtn = document.getElementById('loginBtn');

    if (!loginForm || !loginBtn) {
        console.warn('表单元素未找到');
        return;
    }

    // 表单提交前检查必填字段
    loginForm.addEventListener('submit', function(e) {
        const userTypeInput = document.getElementById('user_type');
        const idInput = document.querySelector('input[name="id"]');
        const passwordInput = document.getElementById('passwordInput');

        // 简单检查必填字段
        if (!userTypeInput.value || !idInput?.value.trim() || !passwordInput?.value.trim()) {
            e.preventDefault();
            showToast('请填写完整信息', 'warning');
            return;
        }

        // 显示加载状态
        showLoadingState(true);
    });
}

/**
 * 显示/隐藏登录加载状态
 * @param {boolean} show - 是否显示加载状态
 */
function showLoadingState(show) {
    const customBtn = document.getElementById('customLoginBtn');
    const originalBtn = document.getElementById('originalLoginBtn');

    if (!customBtn || !originalBtn) return;

    if (show) {
        // 保存原始按钮内容
        if (!customBtn.dataset.originalHtml) {
            customBtn.dataset.originalHtml = customBtn.innerHTML;
        }

        // 设置加载状态
        customBtn.disabled = true;
        customBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 登录中...';
        customBtn.classList.add('disabled');

        // 同时禁用原始表单字段
        originalBtn.disabled = true;

    } else {
        // 恢复原始状态
        const originalHtml = customBtn.dataset.originalHtml ||
                            '<i class="fas fa-sign-in-alt"></i> 登录';

        customBtn.disabled = false;
        customBtn.innerHTML = originalHtml;
        customBtn.classList.remove('disabled');

        originalBtn.disabled = false;
    }
}

// 绑定自定义按钮点击事件
document.addEventListener('DOMContentLoaded', function() {
    const customBtn = document.getElementById('customLoginBtn');
    const originalBtn = document.getElementById('originalLoginBtn');
    const loginForm = document.getElementById('loginForm');

    if (customBtn && originalBtn && loginForm) {
        customBtn.addEventListener('click', function() {
            // 触发隐藏的原始按钮
            originalBtn.click();
        });

        // 表单提交时显示加载状态
        loginForm.addEventListener('submit', function() {
            showLoadingState(true);
        });
    }
});
/**
 * 初始化自动聚焦
 */
function initAutoFocus() {
    // 如果存在错误信息，则不自动聚焦
    const errorAlert = document.querySelector('.alert-danger');
    if (errorAlert) return;

    const idInput = document.querySelector('input[name="id"]');
    if (idInput) {
        setTimeout(() => {
            idInput.focus();
        }, 100);
    }
}

/**
 * 显示提示消息
 * @param {string} message - 消息内容
 * @param {string} type - 消息类型: 'success', 'warning', 'error'
 */
function showToast(message, type = 'success') {
    // 检查是否已存在Toast容器，不存在则创建
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '1055';
        document.body.appendChild(toastContainer);
    }

    // 创建Toast
    const toastId = 'toast-' + Date.now();
    const toast = document.createElement('div');
    toast.id = toastId;
    toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type === 'warning' ? 'warning' : 'success'} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');

    // 图标映射
    const icons = {
        'success': 'check-circle',
        'warning': 'exclamation-triangle',
        'error': 'exclamation-circle'
    };
    const icon = icons[type] || 'info-circle';

    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="fas fa-${icon} me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="关闭"></button>
        </div>
    `;

    toastContainer.appendChild(toast);

    // 使用Bootstrap Toast
    const bsToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: 3000
    });

    bsToast.show();

    // Toast隐藏后移除元素
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

// 页面加载完成后恢复表单按钮状态
window.addEventListener('pageshow', function(event) {
    // 如果是从缓存加载（浏览器后退），重置按钮状态
    if (event.persisted) {
        showLoadingState(false);
    }
});

// 导出函数供其他模块使用（如果需要）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initLoginPage,
        showToast
    };
}