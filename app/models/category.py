from app import db
from datetime import datetime

class Category(db.Model):
    """
    分类表模型
    存储图书分类信息，支持多级分类
    """
    __tablename__ = 'categories'  # 数据库表名

    # ========== 字段定义 ==========
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='分类ID，主键，自增长')
    name = db.Column(db.String(100), nullable=False, unique=True, index=True, comment='分类名称')
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'), default=0, comment='父分类ID，0表示顶级分类')
    description = db.Column(db.Text, comment='分类描述')
    sort_order = db.Column(db.Integer, default=0, comment='排序序号，数字越小越靠前')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow, comment='最后更新时间')

    # ========== 关系定义 ==========
    # 自关联关系：一个分类可以有多个子分类，一个分类只能属于一个父分类
    # remote_side=[id] 指定关联的远程端是当前表的id字段
    parent = db.relationship('Category', remote_side=[id],
                             backref=db.backref('children', lazy='dynamic'),
                             comment='父分类关系')

    # 一个分类可以包含多本图书
    books = db.relationship('Book', backref='category', lazy='dynamic',
                            cascade='all, delete-orphan', comment='该分类下的图书')

    # ========== 业务方法 ==========
    def get_all_children(self):
        """
        递归获取所有子分类（包括孙子分类等）
        :return: 所有子分类ID列表
        """
        children_ids = []
        for child in self.children:
            children_ids.append(child.id)
            children_ids.extend(child.get_all_children())
        return children_ids

    def get_full_path(self):
        """
        获取分类的完整路径（如：计算机科学/编程语言/Python）
        :return: 分类路径字符串
        """
        if self.parent_id == 0:
            return self.name
        parent = Category.query.get(self.parent_id)
        return f"{parent.get_full_path()}/{self.name}"

    def is_root(self):
        """检查是否是顶级分类"""
        return self.parent_id == 0

    def get_book_count(self):
        """获取该分类下的图书数量"""
        return self.books.count()

    def __repr__(self):
        """对象字符串表示"""
        return f'<Category id:{self.id}, name:{self.name}, parent_id:{self.parent_id}>'