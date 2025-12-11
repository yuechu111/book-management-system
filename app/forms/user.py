from flask_wtf import FlaskForm
from wtforms.fields.simple import StringField, TextAreaField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp, Email, Optional, EqualTo, ValidationError


class ProfileForm(FlaskForm):
        """修改个人资料表单"""

        # 用户名 - 在修改时需要特殊验证（排除当前用户）
        username = StringField('用户名', validators=[
            DataRequired(message='用户名不能为空'),
            Length(min=2, max=50, message='用户名长度必须在2-50个字符之间'),
        ], render_kw={"placeholder": "请输入用户名", "class": "form-control"})

        # 邮箱 - 在修改时需要特殊验证（排除当前用户）
        email = StringField('邮箱地址', validators=[
            DataRequired(message='邮箱地址不能为空'),
            Email(message='请输入有效的邮箱地址'),
            Length(max=100, message='邮箱地址长度不能超过100个字符')
        ], render_kw={"placeholder": "请输入邮箱地址", "class": "form-control", "type": "email"})

        # 电话号码 - 可选
        phone = StringField('联系电话', validators=[
            Optional(),
            Length(max=20, message='电话号码长度不能超过20个字符'),
            Regexp(r'^[\d\-\+\(\)\s]+$', message='请输入有效的电话号码')
        ], render_kw={"placeholder": "请输入联系电话", "class": "form-control"})

        # 地址 - 可选
        address = TextAreaField('联系地址', validators=[
            Optional(),
            Length(max=200, message='地址长度不能超过200个字符')
        ], render_kw={"placeholder": "请输入联系地址", "class": "form-control", "rows": 3})

        # 当前密码 - 用于验证身份（修改敏感信息时需要）
        current_password = PasswordField('当前密码', validators=[
            Optional()  # 如果只修改基本信息，可能不需要验证密码
        ], render_kw={"placeholder": "请输入当前密码以确认修改", "class": "form-control"})

        # 新密码 - 可选，只有想修改密码时才填写
        new_password = PasswordField('新密码', validators=[
            Optional(),
            Length(min=8, max=30, message='密码长度必须在8-30个字符之间'),
            EqualTo('confirm_password', message='两次输入的密码不一致')
        ], render_kw={"placeholder": "如需修改密码，请输入新密码", "class": "form-control"})

        # 确认新密码
        confirm_password = PasswordField('确认新密码', validators=[
            Optional()
        ], render_kw={"placeholder": "请再次输入新密码", "class": "form-control"})

        submit = SubmitField('保存更改')
        # 用户状态 - 如果是管理员编辑用户，可能需要这个字段
        # 如果是用户自己修改资料，这个字段不应该显示
        # status = SelectField('用户状态', choices=[
        #     (1, '正常'),
        #     (0, '禁用'),
        #     (2, '待审核')
        # ], coerce=int, validators=[Optional()])

        # def validate_username(self, field):
        #     """自定义验证：用户名唯一性（排除当前用户）"""
        #     from app.models import User  # 需要导入您的User模型
        #     from flask_login import current_user
        #
        #     # 检查用户名是否已存在（排除当前用户自己）
        #     user = User.query.filter_by(username=field.data).first()
        #     if user and user.id != current_user.id:
        #         raise ValidationError('该用户名已被使用，请选择其他用户名')

        # def validate_email(self, field):
        #     """自定义验证：邮箱唯一性（排除当前用户）"""
        #     from app.models import User  # 需要导入您的User模型
        #     from flask_login import current_user
        #
        #     # 检查邮箱是否已存在（排除当前用户自己）
        #     user = User.query.filter_by(email=field.data).first()
        #     if user and user.id != current_user.id:
        #         raise ValidationError('该邮箱已被注册，请使用其他邮箱')