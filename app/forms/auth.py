from flask_wtf import FlaskForm
from wtforms.fields.choices import RadioField
from wtforms.fields.simple import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo, Optional, ValidationError


class LoginForm(FlaskForm):
    #用户输入字段
    account = StringField(label="账号",validators=[DataRequired(),Length(min=2,max=12)])
    user_type = RadioField('用户类型', choices=[
        ('user', '用户'),
        ('admin', '管理员')
    ], default='user')
    #密码输入字段
    password = PasswordField(label="密&emsp;码",validators=[DataRequired()])
    #提交按钮
    login = SubmitField(label="登录")


class RegisterForm(FlaskForm):
    """
    用户注册表单
    与User数据库模型对应
    """

    # ========== 用户信息字段 ==========
    username = StringField(
        label="用户名",
        validators=[
            DataRequired(message="用户名不能为空"),
            Length(min=2, max=50, message="用户名长度必须在2-50个字符之间")
        ],
        description="请输入2-50个字符的用户名",
        render_kw={"placeholder": "请输入用户名", "class": "form-control"}
    )

    email = StringField(
        label="邮箱地址",
        validators=[
            DataRequired(message="邮箱地址不能为空"),
            Length(min=5, max=100, message="邮箱地址长度必须在5-100个字符之间"),
            Email(message="请输入有效的邮箱地址格式")
        ],
        description="请输入有效的邮箱地址，用于账号验证和通知",
        render_kw={"placeholder": "example@domain.com", "class": "form-control"}
    )

    # ========== 密码相关字段 ==========
    password = PasswordField(
        label="密码",
        validators=[
            DataRequired(message="密码不能为空"),
            Length(min=6, message="密码长度至少6位"),
            Regexp(
                r'^(?=.*[a-zA-Z])(?=.*\d)',
                message="密码必须包含字母和数字"
            )
        ],
        description="密码至少6位，且包含字母和数字",
        render_kw={"placeholder": "请输入密码", "class": "form-control"}
    )

    confirm_password = PasswordField(
        label="确认密码",
        validators=[
            DataRequired(message="请确认密码"),
            EqualTo('password', message="两次输入的密码不一致")
        ],
        description="请再次输入密码",
        render_kw={"placeholder": "请再次输入密码", "class": "form-control"}
    )

    # ========== 可选信息字段 ==========
    phone = StringField(
        label="联系电话",
        validators=[
            Optional(),
            Length(max=20, message="联系电话不能超过20个字符"),
            Regexp(
                r'^[0-9+\-\s()]+$',
                message="请输入有效的电话号码格式"
            )
        ],
        description="可选：用于接收图书馆通知",
        render_kw={"placeholder": "请输入联系电话", "class": "form-control"}
    )

    address = StringField(
        label="联系地址",
        validators=[
            Optional(),
            Length(max=200, message="地址不能超过200个字符")
        ],
        description="可选：用于图书邮寄服务",
        render_kw={"placeholder": "请输入联系地址", "class": "form-control"}
    )

    # ========== 协议同意 ==========
    agree_terms = BooleanField(
        label="我已阅读并同意",
        validators=[DataRequired(message="请阅读并同意用户协议")],
        description="《用户协议》和《隐私政策》"
    )

    # ========== 提交按钮 ==========
    submit = SubmitField(
        label="立即注册",
        render_kw={"class": "btn btn-primary btn-block"}
    )

    # ========== 自定义验证方法 ==========
    def validate_username(self, field):
        """
        验证用户名是否已存在
        """
        from app.models import User
        user = User.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError("该用户名已被注册，请选择其他用户名")

    def validate_email(self, field):
        """
        验证邮箱是否已存在
        """
        from app.models import User
        user = User.query.filter_by(email=field.data).first()
        if user:
            raise ValidationError("该邮箱已被注册，请使用其他邮箱或尝试找回密码")