from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, IntegerField, DecimalField, DateField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, NumberRange, Regexp
from datetime import date
from decimal import Decimal


class BookForm(FlaskForm):
    """图书表单"""

    # ========== 基本信息字段 ==========
    title = StringField('*图书标题', validators=[
        DataRequired(message='图书标题不能为空'),
        Length(min=1, max=200, message='标题长度在1-200个字符之间')
    ])

    isbn = StringField('*ISBN号', validators=[
        DataRequired(message='ISBN不能为空'),
        Length(min=10, max=20, message='ISBN长度在10-20个字符之间')
    ])

    author = StringField('*作者', validators=[
        DataRequired(message='作者不能为空'),
        Length(min=1, max=100, message='作者姓名长度在1-100个字符之间')
    ])

    publisher = StringField('出版社', validators=[
        Optional(),
        Length(max=100, message='出版社名称长度不能超过100个字符')
    ])

    publish_date = DateField('出版日期', validators=[
        Optional()
    ], format='%Y-%m-%d')

    edition = StringField('版次', validators=[
        Optional(),
        Length(max=50, message='版次长度不能超过50个字符')
    ])

    language = SelectField('语言', choices=[
        ('中文', '中文'),
        ('英文', '英文'),
        ('日文', '日文'),
        ('其他', '其他')
    ], default='中文')

    pages = IntegerField('页数', validators=[
        Optional(),
        NumberRange(min=1, message='页数必须大于0')
    ])

    price = DecimalField('价格', validators=[
        Optional(),
        NumberRange(min=0, message='价格不能为负数')
    ], places=2)

    # ========== 分类和库存 ==========
    category_id = SelectField('分类', validators=[
        DataRequired(message='请选择分类')
    ], coerce=int, choices=[(1, "文学小说"),
    (2, "科幻奇幻"),
    (3, "计算机科学"),
    (4, "历史传记"),
    (5, "经济管理"),
    (6, "教育心理"),
    (7, "科学技术"),
    (8, "艺术设计"),
    (9, "中国文学"),
    (10, "外国文学"),
    (11, "编程语言"),
    (12, "数据科学"),
    (13, "网络技术"),
    (14, "文学艺术"),
    (15, "社会科学"),
    (16, "教育学习"),
    (17, "生活休闲"),
    (18, "历史小说"),
    (19, "数学物理"),
    (20, "工程技术"),
    (21, "医学健康"),
    (22, "历史地理"),
    (23, "哲学心理"),
    (24, "政治法律"),
    (25, "算法与数据结构"),
    (26, "人工智能"),
    (27, "软件开发")])

    total_copies = IntegerField('总副本数', validators=[
        DataRequired(message='总副本数不能为空'),
        NumberRange(min=1, message='总副本数至少为1')
    ], default=1)

    available_copies = IntegerField('可用副本数', validators=[
        DataRequired(message='可用副本数不能为空'),
        NumberRange(min=0, message='可用副本数不能为负数')
    ], default=1)

    status = SelectField('状态', choices=[
        (1, '正常'),
        (0, '下架'),
        (2, '维护中')
    ], coerce=int, default=1)

    # ========== 描述和封面 ==========
    description = TextAreaField('图书描述', validators=[
        Optional(),
        Length(max=2000, message='图书描述不能超过2000个字符')
    ])

    cover_image = FileField('封面图片', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], '只允许上传图片文件')
    ])

    # 提交按钮
    submit = SubmitField('保存图书')