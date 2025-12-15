"""
收藏关联表模型
存储用户收藏图书的关系
"""
import pytz

from app import db
from datetime import datetime


class Favorite(db.Model):
    """
    用户收藏表模型
    存储用户收藏图书的关联关系
    """
    __tablename__ = 'favorites'  # 数据库表名

    # ========== 主键字段 ==========
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='收藏记录ID，主键，自增长')

    # ========== 外键字段 ==========
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                        nullable=False, index=True, comment='用户ID')
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'),
                        nullable=False, index=True, comment='图书ID')

    # ========== 收藏信息字段 ==========
    note = db.Column(db.String(200), comment='收藏备注，用户可自行填写')
    sort_order = db.Column(db.Integer, default=0, comment='排序序号，用于自定义排序')

    # ========== 状态字段 ==========
    is_active = db.Column(db.Boolean, default=True, comment='是否有效收藏：True-有效，False-已取消')

    # ========== 时间字段 ==========
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Shanghai')), comment='收藏时间')
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Shanghai')),
                           onupdate=lambda: datetime.now(pytz.timezone('Asia/Shanghai')), comment='最后更新时间')

    # ========== 表级约束 ==========
    # 复合唯一约束：一个用户不能重复收藏同一本书
    __table_args__ = (
        db.UniqueConstraint('user_id', 'book_id',
                            name='uix_user_book_favorite'),
    )

    # ========== 关系定义 ==========
    # 关联到User和Book模型
    user = db.relationship('User', backref=db.backref('favorite_records', lazy='dynamic'))
    book = db.relationship('Book', backref=db.backref('favorited_by_records', lazy='dynamic'))

    # ========== 业务方法 ==========
    @property
    def is_valid(self):
        """
        检查收藏是否有效
        :return: True/False
        """
        return self.is_active

    def toggle_active(self):
        """
        切换收藏状态（收藏/取消收藏）
        :return: 新的状态
        """
        self.is_active = not self.is_active
        self.updated_at = datetime.utcnow()
        return self.is_active

    def set_note(self, note_text):
        """
        设置收藏备注
        :param note_text: 备注内容
        :return: None
        """
        self.note = note_text
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        """
        转换为字典格式，便于API返回
        :return: 字典格式的收藏信息
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'book_title': self.book.title if self.book else '',
            'book_author': self.book.author if self.book else '',
            'book_cover': self.book.cover_image if self.book else '',
            'book_available': self.book.is_available if self.book else False,
            'note': self.note,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def is_favorited(cls, user_id, book_id):
        """
        检查用户是否已收藏某本书
        :param user_id: 用户ID
        :param book_id: 图书ID
        :return: 收藏记录对象（如果存在），否则None
        """
        return cls.query.filter_by(
            user_id=user_id,
            book_id=book_id,
            is_active=True
        ).first()

    @classmethod
    def add_favorite(cls, user_id, book_id, note=None):
        """
        添加收藏
        :param user_id: 用户ID
        :param book_id: 图书ID
        :param note: 收藏备注
        :return: 收藏记录对象
        """
        # 检查是否已收藏
        existing = cls.query.filter_by(
            user_id=user_id,
            book_id=book_id
        ).first()

        if existing:
            # 如果存在但已取消收藏，重新激活
            if not existing.is_active:
                existing.is_active = True
                existing.note = note or existing.note
                existing.updated_at = datetime.utcnow()
        else:
            # 创建新的收藏记录
            existing = cls(
                user_id=user_id,
                book_id=book_id,
                note=note,
                is_active=True
            )
            db.session.add(existing)

        db.session.commit()
        return existing

    @classmethod
    def remove_favorite(cls, user_id, book_id):
        """
        移除收藏（软删除，将is_active设为False）
        :param user_id: 用户ID
        :param book_id: 图书ID
        :return: True/False
        """
        favorite = cls.query.filter_by(
            user_id=user_id,
            book_id=book_id,
            is_active=True
        ).first()

        if favorite:
            favorite.is_active = False
            favorite.updated_at = datetime.utcnow()
            db.session.commit()
            return True
        return False

    @classmethod
    def get_user_favorites(cls, user_id, page=1, per_page=20, only_active=True):
        """
        获取用户的收藏列表（分页）
        :param user_id: 用户ID
        :param page: 页码
        :param per_page: 每页数量
        :param only_active: 是否只返回有效收藏
        :return: 分页查询对象
        """
        query = cls.query.filter_by(user_id=user_id)

        if only_active:
            query = query.filter_by(is_active=True)

        return query.order_by(
            cls.sort_order.desc(),
            cls.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)

    def __repr__(self):
        """对象字符串表示"""
        return f'<Favorite id:{self.id}, user:{self.user_id}, book:{self.book_id}, active:{self.is_active}>'