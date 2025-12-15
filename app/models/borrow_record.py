import pytz

from app import db
from datetime import datetime

class BorrowRecord(db.Model):

    """
    借阅记录表模型
    存储用户借阅图书的详细记录
    """
    __tablename__ = 'borrow_records'  # 数据库表名
    # ========== 主键字段 ==========
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='借阅记录ID，主键，自增长')

    # ========== 外键字段 ==========
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                        nullable=False, index=True, comment='用户ID')
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'),
                        nullable=False, index=True, comment='图书ID')

    # ========== 借阅时间字段 ==========


    borrow_date = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Shanghai')),
                            nullable=False, comment='借书日期')
    due_date = db.Column(db.DateTime, nullable=False, comment='应还日期')
    return_date = db.Column(db.DateTime, comment='实际归还日期')

    # ========== 状态字段 ==========
    status = db.Column(db.Integer, default=0, comment='状态：0-借阅中，1-已归还，2-逾期，3-借阅图书请求,4-拒绝借阅请求')

    # ========== 续借信息字段 ==========
    renew_times = db.Column(db.Integer, default=0, comment='续借次数')
    last_renew_date = db.Column(db.DateTime, comment='最后续借日期')

    # ========== 罚款信息字段 ==========
    fine_amount = db.Column(db.Numeric(10, 2), default=0, comment='罚款金额')
    fine_paid = db.Column(db.Boolean, default=False, comment='罚款是否已支付')
    fine_paid_date = db.Column(db.DateTime, comment='罚款支付日期')

    # ========== 时间字段 ==========
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow, comment='最后更新时间')

    # ========== 计算属性 ==========
    @property
    def is_overdue(self):
        """
        检查是否逾期
        :return: True/False
        """
        if self.return_date:  # 如果已经归还，则不逾期
            return False
        # 未归还且当前时间超过应还日期
        return datetime.utcnow() > self.due_date and self.status == 0

    @property
    def overdue_days(self):
        """
        计算逾期天数
        :return: 逾期天数（如果未逾期返回0）
        """
        if not self.is_overdue:
            return 0
        return (datetime.utcnow() - self.due_date).days

    @property
    def borrow_days(self):
        """
        计算借阅天数
        :return: 借阅天数
        """
        if self.return_date:
            return (self.return_date - self.borrow_date).days
        return (datetime.utcnow() - self.borrow_date).days

    # ========== 业务方法 ==========
    def calculate_fine(self, daily_rate=0.5):
        """
        计算罚款金额
        :param daily_rate: 每日罚款率
        :return: 罚款金额
        """
        if self.is_overdue and not self.fine_paid:
            overdue_days = self.overdue_days
            self.fine_amount = overdue_days * daily_rate
            self.status = 2  # 更新状态为逾期
            return self.fine_amount
        return 0

    def can_renew(self, max_renew_times=2):
        """
        检查是否可以续借
        :param max_renew_times: 最大续借次数
        :return: True/False
        """
        # 条件：借阅中、未逾期、未达到最大续借次数
        return (self.status == 0 and
                not self.is_overdue and
                self.renew_times < max_renew_times)

    def renew(self, renew_days=14):
        """
        执行续借操作
        :param renew_days: 续借天数
        :return: True/False
        """
        if self.can_renew():
            from datetime import timedelta
            self.due_date = self.due_date + timedelta(days=renew_days)
            self.renew_times += 1
            self.last_renew_date = datetime.utcnow()
            return True
        return False

    def return_book(self):
        """
        执行还书操作
        :return: True/False
        """
        if self.status == 0:  # 只有借阅中的记录可以还书
            self.return_date = datetime.utcnow()
            self.status = 1

            # 如果逾期，计算罚款
            if self.is_overdue:
                self.calculate_fine()

            # 更新图书的可用数量
            if self.book:
                self.book.return_book()

            return True
        return False

    def pay_fine(self):
        """
        支付罚款
        :return: True/False
        """
        if self.fine_amount > 0 and not self.fine_paid:
            self.fine_paid = True
            self.fine_paid_date = datetime.utcnow()
            return True
        return False

    def get_status_text(self):
        """
        获取状态文字描述
        :return: 状态描述字符串
        """
        status_map = {
            0: '借阅中',
            1: '已归还',
            2: '逾期'
        }
        return status_map.get(self.status, '未知状态')

    def __repr__(self):
        """对象字符串表示"""
        return f'<BorrowRecord id:{self.id}, user:{self.user_id}, book:{self.book_id}, status:{self.status}>'