from app import db
from datetime import datetime

from app.models.borrow_record import BorrowRecord


class Book(db.Model):
    """
    图书表模型
    存储图书详细信息
    """
    __tablename__ = 'books'  # 数据库表名

    # ========== 基本信息字段 ==========
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='图书ID，主键，自增长')
    isbn = db.Column(db.String(20), unique=True, nullable=False, index=True, comment='ISBN号，国际标准书号')
    title = db.Column(db.String(200), nullable=False, index=True, comment='图书标题')
    author = db.Column(db.String(100), nullable=False, comment='作者')
    publisher = db.Column(db.String(100), comment='出版社')
    publish_date = db.Column(db.Date, comment='出版日期')
    edition = db.Column(db.String(50), comment='版次')
    language = db.Column(db.String(20), default='中文', comment='语言')
    pages = db.Column(db.Integer, comment='页数')
    price = db.Column(db.Numeric(10, 2), comment='价格')
    cover_image = db.Column(db.String(255), comment='封面图片URL')
    description = db.Column(db.Text, comment='图书描述')

    # ========== 库存信息字段 ==========
    total_copies = db.Column(db.Integer, default=1, comment='总副本数')
    available_copies = db.Column(db.Integer, default=1, comment='可用副本数')

    # ========== 外键关联 ==========
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'),
                            nullable=False, index=True, comment='分类ID')

    # ========== 状态字段 ==========
    status = db.Column(db.Integer, default=1, comment='状态：0-下架，1-正常，2-维护中')

    # ========== 时间字段 ==========
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow, comment='最后更新时间')

    # ========== 关系定义 ==========
    # 一本书可以有多条借阅记录
    borrow_records = db.relationship('BorrowRecord', backref='book',
                                     lazy='dynamic', cascade='all, delete-orphan'
                                     )

    # ========== 计算属性 ==========
    @property
    def is_available(self):
        """
        检查图书是否可借
        :return: True/False
        """
        return self.status == 1 and self.available_copies > 0

    @property
    def borrowed_count(self):
        """
        计算已借出数量
        :return: 已借出的副本数
        """
        return self.total_copies - self.available_copies

    @property
    def current_borrowers(self):
        """
        获取当前借阅该书的用户列表
        :return: 当前借阅记录列表
        """
        return self.borrow_records.filter_by(status=0).all()

    # ========== 业务方法 ==========
    def borrow(self):
        """
        借书操作
        减少可用副本数
        :return: True-成功，False-失败
        """
        if self.available_copies > 0:
            self.available_copies -= 1
            return True
        return False

    def return_book(self):
        """
        还书操作
        增加可用副本数
        :return: True-成功，False-失败
        """
        if self.available_copies < self.total_copies:
            self.available_copies += 1
            return True
        return False

    def is_borrowed_by_user(self, user_id):
        """
        检查指定用户是否正在借阅本书
        :param user_id: 用户ID
        :return: True/False
        """
        record = self.borrow_records.filter_by(
            user_id=user_id,
            status=0
        ).first()
        return record is not None

    def get_borrow_history(self):
        """
        获取本书的借阅历史
        :return: 借阅记录列表
        """
        return self.borrow_records.order_by(BorrowRecord.borrow_date.desc()).all()

    def get_favorite_count(self):
        """
        获取本书的收藏数量
        :return: 收藏数量
        """
        from app.models.favorite import Favorite
        return Favorite.query.filter_by(
            book_id=self.id,
            is_active=True
        ).count()

    def is_favorited_by_user(self, user_id):
        """
        检查指定用户是否收藏了本书
        :param user_id: 用户ID
        :return: True/False
        """
        from app.models.favorite import Favorite
        return Favorite.is_favorited(user_id, self.id) is not None

    def get_favorited_users(self):
        """
        获取收藏本书的用户列表
        :return: 用户列表
        """
        return [record.user for record in self.favorited_by_records.filter_by(is_active=True).all()]

    def __repr__(self):
        """对象字符串表示"""
        return f'<Book id:{self.id}, title:{self.title}, isbn:{self.isbn}>'