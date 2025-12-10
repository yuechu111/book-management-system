from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

from config import Config
from datetime import datetime
db = SQLAlchemy()
import app.models

migrate = Migrate()
#初始化用户
def create_default_admins():
    """创建默认的管理员账户"""
    from app.models import Admin

    # 默认管理员列表
    default_admins = [
        {
            'username': 'superadmin',
            'email': 'superadmin@library.com',
            'password': '123456',
            'real_name': '系统超级管理员',
            'role': 'super_admin'
        },
        {
            'username': 'libadmin',
            'email': 'admin@library.com',
            'password': '123456',
            'real_name': '图书管理员',
            'role': 'admin'
        }
    ]

    for admin_data in default_admins:
        # 检查是否已存在
        existing_admin = Admin.query.filter_by(username=admin_data['username']).first()
        if not existing_admin:
            try:
                new_admin = Admin(
                    username=admin_data['username'],
                    email=admin_data['email'],
                    real_name=admin_data['real_name'],
                    role=admin_data['role'],
                    status=1
                )
                new_admin.password = admin_data['password']  # 使用属性设置器自动哈希

                db.session.add(new_admin)
                db.session.commit()
                print(f"✅ 管理员 {admin_data['username']} 创建成功")
            except Exception as e:
                db.session.rollback()
                print(f"❌ 创建管理员 {admin_data['username']} 失败: {e}")
        else:
            print(f"⏭️  管理员 {admin_data['username']} 已存在，跳过")
#初始化管理员
def create_default_users():
    """创建默认的用户账户"""
    from app.models import User

    # 默认用户列表
    default_users = [
        {
            'username': 'student1',
            'email': 'student1@example.com',
            'password': 'Student123',
            'phone': '13800138001',
            'address': '计算机科学学院 2020级1班'
        },
        {
            'username': 'student2',
            'email': 'student2@example.com',
            'password': 'Student456',
            'phone': '13800138002',
            'address': '信息工程学院 2021级2班'
        },
        {
            'username': 'teacher1',
            'email': 'teacher1@example.com',
            'password': 'Teacher789',
            'phone': '13900139001',
            'address': '文学院 教授办公室'
        },
        {
            'username': 'staff1',
            'email': 'staff1@example.com',
            'password': 'Staff123',
            'phone': '13700137001',
            'address': '图书馆办公室'
        },
        {
            'username': 'testuser',
            'email': 'test@library.com',
            'password': 'Test123456',
            'phone': '13600136001',
            'address': '测试用户地址'
        }
    ]

    created_count = 0

    for user_data in default_users:
        # 检查用户名是否已存在
        existing_user = User.query.filter_by(username=user_data['username']).first()
        if existing_user:
            print(f"⏭️  用户 '{user_data['username']}' 已存在，跳过")
            continue

        # 检查邮箱是否已存在
        existing_email = User.query.filter_by(email=user_data['email']).first()
        if existing_email:
            print(f"⏭️  邮箱 '{user_data['email']}' 已被使用，跳过用户 '{user_data['username']}'")
            continue

        try:
            # 创建新用户
            new_user = User(
                username=user_data['username'],
                email=user_data['email'],
                phone=user_data['phone'],
                address=user_data['address'],
                status=1  # 默认启用状态
            )

            # 使用属性设置器自动哈希密码
            new_user.password = user_data['password']

            db.session.add(new_user)
            db.session.commit()

            print(f"✅ 用户 '{user_data['username']}' 创建成功")
            created_count += 1

        except Exception as e:
            db.session.rollback()
            print(f"❌ 创建用户 '{user_data['username']}' 失败: {e}")

    print(f"✅ 用户初始化完成，共创建 {created_count} 个用户")
    return created_count
#初始化数据库图书分类信息
def create_default_categories():
    """创建默认的图书分类（支持多级）"""
    from app.models.category import Category

    # 默认分类列表 - 按照层级结构
    default_categories = [
        # 顶级分类
        {'id': 1, 'name': '文学艺术', 'parent_id': 0, 'description': '小说、散文、诗歌等文学作品', 'sort_order': 1},
        {'id': 2, 'name': '科学技术', 'parent_id': 0, 'description': '自然科学、工程技术等专业书籍', 'sort_order': 2},
        {'id': 3, 'name': '社会科学', 'parent_id': 0, 'description': '经济、管理、法律等社会科学书籍', 'sort_order': 3},
        {'id': 4, 'name': '教育学习', 'parent_id': 0, 'description': '教材、教辅、学习方法类书籍', 'sort_order': 4},
        {'id': 5, 'name': '生活休闲', 'parent_id': 0, 'description': '生活、健康、旅游、美食等休闲类书籍',
         'sort_order': 5},

        # 文学艺术 - 子分类
        {'id': 6, 'name': '中国文学', 'parent_id': 1, 'description': '中国作家创作的文学作品', 'sort_order': 1},
        {'id': 7, 'name': '外国文学', 'parent_id': 1, 'description': '外国作家创作的文学作品', 'sort_order': 2},
        {'id': 8, 'name': '科幻奇幻', 'parent_id': 1, 'description': '科幻、奇幻、魔幻等类型小说', 'sort_order': 3},
        {'id': 9, 'name': '历史小说', 'parent_id': 1, 'description': '以历史为背景的小说作品', 'sort_order': 4},

        # 科学技术 - 子分类
        {'id': 10, 'name': '计算机科学', 'parent_id': 2, 'description': '编程、算法、软件开发等计算机相关书籍',
         'sort_order': 1},
        {'id': 11, 'name': '数学物理', 'parent_id': 2, 'description': '数学、物理学等基础科学书籍', 'sort_order': 2},
        {'id': 12, 'name': '工程技术', 'parent_id': 2, 'description': '电子、机械、建筑等工程技术书籍', 'sort_order': 3},
        {'id': 13, 'name': '医学健康', 'parent_id': 2, 'description': '医学、健康、养生类书籍', 'sort_order': 4},

        # 社会科学 - 子分类
        {'id': 14, 'name': '经济管理', 'parent_id': 3, 'description': '经济学、管理学、金融等商业类书籍',
         'sort_order': 1},
        {'id': 15, 'name': '历史地理', 'parent_id': 3, 'description': '历史、地理、文化类书籍', 'sort_order': 2},
        {'id': 16, 'name': '哲学心理', 'parent_id': 3, 'description': '哲学、心理学、社会学类书籍', 'sort_order': 3},
        {'id': 17, 'name': '政治法律', 'parent_id': 3, 'description': '政治学、法律、国际关系类书籍', 'sort_order': 4},

        # 计算机科学 - 孙子分类
        {'id': 18, 'name': '编程语言', 'parent_id': 10, 'description': '各种编程语言学习书籍', 'sort_order': 1},
        {'id': 19, 'name': '算法与数据结构', 'parent_id': 10, 'description': '算法、数据结构、计算机理论',
         'sort_order': 2},
        {'id': 20, 'name': '人工智能', 'parent_id': 10, 'description': '机器学习、深度学习、人工智能', 'sort_order': 3},
        {'id': 21, 'name': '软件开发', 'parent_id': 10, 'description': '软件工程、系统设计、项目管理', 'sort_order': 4},
    ]

    created_count = 0

    for cat_data in default_categories:
        # 检查分类是否已存在（按名称）
        existing_cat = Category.query.filter_by(name=cat_data['name']).first()
        if existing_cat:
            print(f"⏭️  分类 '{cat_data['name']}' 已存在，跳过")
            continue

        try:
            # 创建分类
            category = Category(
                name=cat_data['name'],
                parent_id=cat_data['parent_id'],
                description=cat_data['description'],
                sort_order=cat_data['sort_order']
            )

            # 如果需要指定ID（例如为了外键关联），可以使用以下方法
            # 但通常不推荐指定ID，除非有特殊需求
            db.session.add(category)

            # 刷新以获取ID（如果不指定ID，由数据库自增）
            db.session.flush()

            print(f"✅ 分类 '{cat_data['name']}' 创建成功")
            print(f"   父分类ID: {cat_data['parent_id']}")
            print(f"   描述: {cat_data['description'][:30]}...")
            print()

            created_count += 1

        except Exception as e:
            db.session.rollback()
            print(f"❌ 创建分类 '{cat_data['name']}' 失败: {e}")

    db.session.commit()
    print(f"✅ 分类初始化完成，共创建 {created_count} 个分类")

    # 返回分类映射字典，方便图书初始化时使用
    categories = Category.query.all()
    category_map = {cat.name: cat.id for cat in categories}

    return category_map
#初始化数据库图书信息
def create_default_books():
    """创建默认的图书数据"""
    from app.models import Book
    from app.models import Category
    # 获取分类映射
    categories = Category.query.all()
    category_map = {cat.name: cat.id for cat in categories}

    # 默认图书列表 - 关联到具体的分类
    default_books = [
        {
            'isbn': '9787020002207',
            'title': '红楼梦',
            'author': '曹雪芹',
            'publisher': '人民文学出版社',
            'publish_date': datetime(2008, 7, 1),
            'edition': '第3版',
            'language': '中文',
            'pages': 1606,
            'price': 59.70,
            'cover_image': '',
            'description': '中国古典小说巅峰之作，以贾、史、王、薛四大家族的兴衰为背景，描绘了一批举止见识出于须眉之上的闺阁佳人的人生百态。',
            'total_copies': 10,
            'available_copies': 8,
            'category_id': category_map.get('中国文学'),
            'status': 1
        },
        {
            'isbn': '9787020002208',
            'title': '三国演义',
            'author': '罗贯中',
            'publisher': '人民文学出版社',
            'publish_date': datetime(1998, 5, 1),
            'edition': '第2版',
            'language': '中文',
            'pages': 990,
            'price': 39.50,
            'cover_image': '',
            'description': '中国第一部长篇章回体历史演义小说，描写了从东汉末年到西晋初年之间近百年的历史风云。',
            'total_copies': 8,
            'available_copies': 6,
            'category_id': category_map.get('历史小说'),
            'status': 1
        },
        {
            'isbn': '9787530216714',
            'title': '活着',
            'author': '余华',
            'publisher': '作家出版社',
            'publish_date': datetime(2012, 8, 1),
            'edition': '第1版',
            'language': '中文',
            'pages': 191,
            'price': 28.00,
            'cover_image': '',
            'description': '讲述在大时代背景下，徐福贵的人生和家庭不断经受着苦难，到了最后所有亲人都先后离他而去。',
            'total_copies': 15,
            'available_copies': 12,
            'category_id': category_map.get('中国文学'),
            'status': 1
        },
        {
            'isbn': '9787532760298',
            'title': '三体',
            'author': '刘慈欣',
            'publisher': '重庆出版社',
            'publish_date': datetime(2008, 1, 1),
            'edition': '第1版',
            'language': '中文',
            'pages': 302,
            'price': 23.00,
            'cover_image': '',
            'description': '讲述了地球人类文明和三体文明的信息交流、生死搏杀及两个文明在宇宙中的兴衰历程。',
            'total_copies': 12,
            'available_copies': 9,
            'category_id': category_map.get('科幻奇幻'),
            'status': 1
        },
        {
            'isbn': '9787544253994',
            'title': '百年孤独',
            'author': '加西亚·马尔克斯',
            'publisher': '南海出版公司',
            'publish_date': datetime(2011, 6, 1),
            'edition': '第1版',
            'language': '中文',
            'pages': 360,
            'price': 39.50,
            'cover_image': '',
            'description': '魔幻现实主义文学的代表作，描写了布恩迪亚家族七代人的传奇故事。',
            'total_copies': 9,
            'available_copies': 7,
            'category_id': category_map.get('外国文学'),
            'status': 1
        },
        {
            'isbn': '9787111126768',
            'title': 'C程序设计语言',
            'author': 'Brian W. Kernighan, Dennis M. Ritchie',
            'publisher': '机械工业出版社',
            'publish_date': datetime(2004, 1, 1),
            'edition': '第2版',
            'language': '中文',
            'pages': 258,
            'price': 30.00,
            'cover_image': '',
            'description': 'C语言程序设计的经典教材，全面、系统地讲述了C语言的各个特性及程序设计的基本方法。',
            'total_copies': 20,
            'available_copies': 18,
            'category_id': category_map.get('编程语言'),
            'status': 1
        },
        {
            'isbn': '9787302272064',
            'title': 'Python编程：从入门到实践',
            'author': 'Eric Matthes',
            'publisher': '人民邮电出版社',
            'publish_date': datetime(2016, 7, 1),
            'edition': '第1版',
            'language': '中文',
            'pages': 459,
            'price': 89.00,
            'cover_image': '',
            'description': '一本针对所有层次的Python读者而作的Python入门书，从最基础的概念开始，逐步引导读者完成复杂的项目。',
            'total_copies': 25,
            'available_copies': 22,
            'category_id': category_map.get('编程语言'),
            'status': 1
        },
        {
            'isbn': '9787121318020',
            'title': '机器学习',
            'author': '周志华',
            'publisher': '清华大学出版社',
            'publish_date': datetime(2016, 1, 1),
            'edition': '第1版',
            'language': '中文',
            'pages': 425,
            'price': 88.00,
            'cover_image': '',
            'description': '机器学习领域经典教材，系统全面地介绍了机器学习的基础概念、经典方法和前沿进展。',
            'total_copies': 15,
            'available_copies': 12,
            'category_id': category_map.get('人工智能'),
            'status': 1
        },
        {
            'isbn': '9787544291170',
            'title': '经济学原理',
            'author': 'N. Gregory Mankiw',
            'publisher': '北京大学出版社',
            'publish_date': datetime(2015, 5, 1),
            'edition': '第7版',
            'language': '中文',
            'pages': 850,
            'price': 128.00,
            'cover_image': '',
            'description': '世界上最流行的经济学入门教材，以浅显易懂的语言和生动有趣的案例介绍了经济学的基本原理。',
            'total_copies': 18,
            'available_copies': 15,
            'category_id': category_map.get('经济管理'),
            'status': 1
        },
        {
            'isbn': '9787510840984',
            'title': '人类简史：从动物到上帝',
            'author': '尤瓦尔·赫拉利',
            'publisher': '中信出版社',
            'publish_date': datetime(2014, 11, 1),
            'edition': '第1版',
            'language': '中文',
            'pages': 440,
            'price': 68.00,
            'cover_image': '',
            'description': '讲述了人类从石器时代至21世纪的演化与发展史，并将人类历史分为四个阶段。',
            'total_copies': 14,
            'available_copies': 11,
            'category_id': category_map.get('历史地理'),
            'status': 1
        },
        {
            'isbn': '9787108041531',
            'title': '中国哲学简史',
            'author': '冯友兰',
            'publisher': '北京大学出版社',
            'publish_date': datetime(2013, 1, 1),
            'edition': '第1版',
            'language': '中文',
            'pages': 320,
            'price': 38.00,
            'cover_image': '',
            'description': '系统介绍中国哲学发展历史的经典著作，从先秦诸子到近现代思想家的哲学思想。',
            'total_copies': 12,
            'available_copies': 10,
            'category_id': category_map.get('哲学心理'),
            'status': 1
        },
        {
            'isbn': '9787301217076',
            'title': '高等数学',
            'author': '同济大学数学系',
            'publisher': '高等教育出版社',
            'publish_date': datetime(2014, 7, 1),
            'edition': '第7版',
            'language': '中文',
            'pages': 456,
            'price': 42.80,
            'cover_image': '',
            'description': '高等学校理工科专业高等数学课程的经典教材，内容全面，讲解清晰。',
            'total_copies': 30,
            'available_copies': 25,
            'category_id': category_map.get('数学物理'),
            'status': 1
        }
    ]

    created_count = 0

    for book_data in default_books:
        # 检查ISBN是否已存在
        existing_book = Book.query.filter_by(isbn=book_data['isbn']).first()
        if existing_book:
            print(f"⏭️  图书 ISBN '{book_data['isbn']}' 已存在，跳过")
            continue

        # 检查分类是否存在
        if not book_data['category_id']:
            print(f"⚠️  图书 '{book_data['title']}' 的分类不存在，跳过")
            continue

        try:
            # 创建新图书
            new_book = Book(
                isbn=book_data['isbn'],
                title=book_data['title'],
                author=book_data['author'],
                publisher=book_data['publisher'],
                publish_date=book_data['publish_date'],
                edition=book_data['edition'],
                language=book_data['language'],
                pages=book_data['pages'],
                price=book_data['price'],
                cover_image=book_data['cover_image'],
                description=book_data['description'],
                total_copies=book_data['total_copies'],
                available_copies=book_data['available_copies'],
                category_id=book_data['category_id'],
                status=book_data['status']
            )

            db.session.add(new_book)
            db.session.commit()

            print(f"✅ 图书 '{book_data['title']}' 创建成功")
            print(f"   作者: {book_data['author']}")
            print(f"   分类: {Category.query.get(book_data['category_id']).name}")
            print(f"   库存: {book_data['total_copies']} 本")
            print()

            created_count += 1

        except Exception as e:
            db.session.rollback()
            print(f"❌ 创建图书 '{book_data['title']}' 失败: {e}")

    print(f"✅ 图书初始化完成，共创建 {created_count} 本图书")
    return created_count

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    #初始化
    db.init_app(app)
    migrate.init_app(app, db)
    csrf = CSRFProtect(app)

    with app.app_context():
        db.create_all()
        create_default_admins()
        create_default_users()
        create_default_categories()
        create_default_books()

    from app.views.auth import auth_bp
    from app.views.users import users_bp
    app.register_blueprint(auth_bp)  # 注册蓝图
    app.register_blueprint(users_bp)  # 注册蓝图
    return app