"""
图书馆管理系统数据库模型定义
使用Flask-SQLAlchemy ORM框架
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from app.models.book import Book
from app.models.borrow_record import BorrowRecord
from app import db

class User(db.Model):
    """
    用户表模型
    存储图书馆普通用户信息
    """
    __tablename__ = 'users'  # 数据库表名

    # ========== 字段定义 ==========
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='用户ID，主键，自增长')
    username = db.Column(db.String(50), unique=True, nullable=False, index=True, comment='用户名，唯一，不可为空')
    email = db.Column(db.String(100), unique=True, nullable=False, index=True, comment='邮箱地址，唯一，不可为空')
    password_hash = db.Column(db.String(255), nullable=False, comment='密码哈希值，存储加密后的密码')
    phone = db.Column(db.String(20), comment='联系电话')
    address = db.Column(db.String(200), comment='联系地址')
    status = db.Column(db.Integer, default=1, comment='用户状态：0-禁用，1-正常，2-待审核,3-审核未通过')
    last_login_at = db.Column(db.DateTime, comment='最后登录时间')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow, comment='最后更新时间，自动更新')

    # ========== 关系定义 ==========
    # 一个用户可以有多条借阅记录
    # backref='user' 会在BorrowRecord模型中创建user属性
    # lazy='dynamic' 返回查询对象而不是直接加载所有记录
    # cascade='all, delete-orphan' 设置级联删除
    borrow_records = db.relationship('BorrowRecord', backref='user',
                                     lazy='dynamic', cascade='all, delete-orphan'
                                     )

    # 添加收藏关系（多对多）
    # 通过Favorite表建立与Book的关联
    favorite_books = db.relationship(
        'Book',
        secondary='favorites',
        primaryjoin="and_(User.id==Favorite.user_id, Favorite.is_active==True)",
        secondaryjoin="Book.id==Favorite.book_id",
        backref=db.backref('favorited_users', lazy='dynamic'),
        lazy='dynamic'
    )


    # ========== 新增业务方法：收藏相关 ==========
    def add_favorite(self, book_id, note=None):
        """
        用户收藏图书
        :param book_id: 图书ID
        :param note: 收藏备注
        :return: 收藏记录对象
        """
        from app.models.favorite import Favorite
        return Favorite.add_favorite(self.id, book_id, note)

    def remove_favorite(self, book_id):
        """
        用户取消收藏
        :param book_id: 图书ID
        :return: True/False
        """
        from app.models.favorite import Favorite
        return Favorite.remove_favorite(self.id, book_id)

    def is_favorited(self, book_id):
        """
        检查用户是否收藏了某本书
        :param book_id: 图书ID
        :return: True/False
        """
        from app.models.favorite import Favorite
        return Favorite.is_favorited(self.id, book_id) is not None

    def get_favorites(self, page=1, per_page=20):
        """
        获取用户的收藏列表（分页）
        :param page: 页码
        :param per_page: 每页数量
        :return: 分页查询对象
        """
        from app.models.favorite import Favorite
        return Favorite.get_user_favorites(self.id, page, per_page)

    def get_favorite_count(self):
        """
        获取用户的收藏数量
        :return: 收藏数量
        """
        from app.models.favorite import Favorite
        return Favorite.query.filter_by(
            user_id=self.id,
            is_active=True
        ).count()

    def get_favorite_books_by_category(self, category_id=None):
        """
        按分类获取收藏图书
        :param category_id: 分类ID，None表示所有分类
        :return: 图书列表
        """
        query = self.favorite_books

        if category_id:
            query = query.filter_by(category_id=category_id)

        return query.order_by(Book.title).all()

    # ========== 属性方法 ==========
    @property
    def password(self):
        """
        密码属性获取器
        防止直接读取密码哈希值
        """
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """
        密码属性设置器
        自动对密码进行哈希加密
        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """
        验证密码
        :param password: 待验证的明文密码
        :return: 验证结果 True/False
        """
        return check_password_hash(self.password_hash, password)

    # ========== 业务方法 ==========
    def get_active_borrows(self):
        """
        获取用户当前正在借阅的图书
        :return: 借阅中的记录查询对象
        """
        return self.borrow_records.filter(
            BorrowRecord.status.in_([0, 3,4])).all()

    def has_overdue_books(self):
        """
        检查用户是否有逾期未还的图书
        :return: True/False
        """
        active_borrows = self.get_active_borrows()
        for record in active_borrows:
            if record.is_overdue:
                return True
        return False

    def get_borrow_history(self):
        """
        获取用户的借阅历史
        :return: 所有借阅记录列表（包括已归还）
        """
        return self.borrow_records.filter(
            BorrowRecord.status != 4,
            BorrowRecord.status != 3
        ).order_by(
            BorrowRecord.borrow_date.desc()
        ).all()

    def __repr__(self):
        """对象字符串表示，便于调试"""
        return f'<User id:{self.id}, username:{self.username}>'