import pytz
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from datetime import datetime

class Admin(db.Model):
    """
    管理员表模型
    存储图书馆管理员信息
    """
    __tablename__ = 'admins'  # 数据库表名

    # ========== 字段定义 ==========
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='管理员ID，主键，自增长')
    username = db.Column(db.String(50), unique=True, nullable=False, index=True, comment='管理员用户名')
    email = db.Column(db.String(100), unique=True, nullable=False, index=True, comment='管理员邮箱')
    password_hash = db.Column(db.String(255), nullable=False, comment='密码哈希值')
    real_name = db.Column(db.String(50), comment='真实姓名')

    role = db.Column(db.String(20), default='admin', comment='角色：admin-普通管理员，super_admin-超级管理员')
    status = db.Column(db.Integer, default=1, comment='状态：0-禁用，1-正常')
    last_login_at = db.Column(db.DateTime, comment='最后登录时间')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Shanghai')), comment='创建时间')
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Shanghai')),
                           onupdate=lambda: datetime.now(pytz.timezone('Asia/Shanghai')), comment='最后更新时间')

    # ========== 属性方法 ==========
    @property
    def password(self):
        """密码属性获取器"""
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """密码属性设置器"""
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)

    # ========== 业务方法 ==========
    def is_super_admin(self):
        """
        检查是否是超级管理员
        :return: True/False
        """
        return self.role == 'super_admin'

    def can_manage_users(self):
        """
        检查是否有管理用户的权限
        :return: True/False
        """
        return self.role in ['super_admin', 'admin']

    def can_manage_books(self):
        """
        检查是否有管理图书的权限
        :return: True/False
        """
        return self.role in ['super_admin', 'admin']

    def __repr__(self):
        """对象字符串表示"""
        return f'<Admin id:{self.id}, username:{self.username}, role:{self.role}>'