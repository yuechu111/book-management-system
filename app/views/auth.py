from flask import Blueprint, render_template, flash, url_for, session
from werkzeug.utils import redirect

from app.forms import LoginForm,RegisterForm
from app.models import User,Admin

auth_bp = Blueprint('auth', __name__,template_folder='templates/auth')

@auth_bp.route('/login',methods=['POST','GET'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user_account = login_form.account.data
        user_password = login_form.password.data
        user_type = login_form.user_type.data

        #普通用户登录逻辑
        if user_type == 'user':
            user = User.query.filter_by(username=user_account).first()
            if user and user.verify_password(user_password):
                session.permanent = True
                session['user_id'] = user.id
                session['username'] = user.username
                session['user_type'] = 'user'
                # 登录成功逻辑
                return redirect(url_for('users.dashboard'))
            else:
                # 登录失败逻辑
                flash('用户账号或密码错误', 'danger')
        #管理员登录逻辑
        elif user_type == 'admin':
            admin = Admin.query.filter_by(username=user_account, status=1,role='admin').first() or Admin.query.filter_by(username=user_account, status=1,role='super_admin').first()
            if admin and admin.verify_password(user_password):
                if admin.role == 'super_admin':
                    # 超级管理员登录成功逻辑
                    return "超级管理员登录成功"
                elif admin.role == 'admin':
                    # 普通管理员登录成功逻辑
                    return "普通管理员登录成功"
            else:
                # 登录失败逻辑
                flash('管理员账号或密码错误', 'danger')

    return render_template('auth/login.html', login_form=login_form)

@auth_bp.route('/register',methods=['POST','GET'])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        # 获取表单数据
        username = register_form.username.data
        email = register_form.email.data
        password = register_form.password.data
        phone = register_form.phone.data
        address = register_form.address.data

        # 创建新用户对象
        new_user = User(
            username=username,
            email=email,
            phone=phone,
            address=address,
            status=2  # 新注册用户状态为待审核
        )
        new_user.password = password  # 使用属性设置器自动哈希密码

        # 保存到数据库
        from app import db
        db.session.add(new_user)
        db.session.commit()
        # 延迟跳转
        return render_template('auth/register_success.html',
                               username=username,
                               redirect_url=url_for('auth.login'),
                               delay_time=3)
    return render_template('auth/register.html',register_form=register_form)


