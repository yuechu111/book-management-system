from functools import wraps
from time import sleep


from flask import Blueprint, render_template, jsonify, request, flash, url_for, session
from sqlalchemy.sql.elements import or_
from werkzeug.utils import redirect

from app.models import Book, User, BorrowRecord, Category
from app.views.users import borrow_book
from app.forms import BookForm

admin_bp = Blueprint('admin', __name__,template_folder='templates/admin')

def login_required(f):
    """
    简单的登录验证装饰器
    仅检查session中是否有user_id
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查session中是否有user_id
        if 'user_id' not in session:
            # 重定向到登录页面，并传递当前URL作为next参数
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard',methods=['POST','GET'])
@login_required
def dashboard():
    book_query = Book.query
    user_query = User.query
    borrow_query = BorrowRecord.query
    return render_template('admin/dashboard.html',
                            book_query=book_query,
                           user_query=user_query,
                           borrow_query=borrow_query
                           )

@admin_bp.route('/book_management',methods=['POST','GET'])
@login_required
def book_management():
    book_query = Book.query
    if request.method == 'GET':
        # 获取所有分类
        categories = Category.query.all()
        # 获取查询参数
        query = request.args.get('q', '').strip()  # 搜索关键词（GET方式）
        category_id = request.args.get('category', '').strip()  # 分类ID（GET方式）

        # 初始化查询
        books_query = Book.query
        # 定义是否是查询

        # 处理分类筛选
        if category_id:
            try:
                category_id_int = int(category_id)
                # 验证分类是否存在
                category = Category.query.get(category_id_int)
                if category:
                    books_query = books_query.filter_by(category_id=category_id_int)
            except ValueError:
                # 无效的分类ID，忽略
                pass

        # 处理关键词搜索
        if query:
            # 多字段模糊搜索：书名、作者、ISBN、描述
            books_query = books_query.filter(
                or_(
                    Book.title.ilike(f'%{query}%'),
                    Book.author.ilike(f'%{query}%'),
                    Book.isbn.ilike(f'%{query}%'),
                    Book.description.ilike(f'%{query}%')
                )
            )

        # 执行查询并获取结果
        books = books_query
        return render_template('admin/book_management.html',
                               categories=categories,
                               book_query=books,
                               current_query=query,
                               selected_category=category_id,
                               )
    return render_template('admin/book_management.html',
                           book_query=book_query
                           )

@admin_bp.route('/add_book',methods=['POST','GET'])
@login_required
def add_book():
    book_form = BookForm()
    # 动态设置分类选择字段的选项
    if book_form.validate_on_submit():
        # 获取表单数据
        title = book_form.title.data
        author = book_form.author.data
        isbn = book_form.isbn.data
        publisher = book_form.publisher.data
        publish_date = book_form.publish_date.data
        edition = book_form.edition.data
        language = book_form.language.data
        pages = book_form.pages.data
        price = book_form.price.data
        total_copies = book_form.total_copies.data
        status = book_form.status.data
        description = book_form.description.data
        category_id = book_form.category_id.data

        if isbn in [book.isbn for book in Book.query.all()]:
            flash('该ISBN号的图书已存在，不能重复添加！', 'danger')
            return render_template('admin/add_book.html',
                                   book_form=book_form)

        # 创建新图书对象
        new_book = Book(
            title=title,
            author=author,
            isbn=isbn,
            description=description,
            category_id=category_id,
            total_copies=total_copies,
            available_copies=total_copies,  # 初始可用副本数等于总副本数
            publisher=publisher,
            publish_date=publish_date,
            edition=edition,
            language=language,
            pages=pages,
            price=price,
            status=status,
        )

        # 保存到数据库
        from app import db
        db.session.add(new_book)
        db.session.commit()
        flash('图书添加成功！', 'success')
        return redirect(url_for('admin.book_management'))
    return render_template('admin/add_book.html',
                           book_form=book_form)

@admin_bp.route('/book_information/<int:book_id>',methods=['POST','GET'])
@login_required
def book_information(book_id):
    book = Book.query.get(book_id)
    borrow_book_count = BorrowRecord.query.filter_by(book_id=book_id).count()
    borrow_records = BorrowRecord.query.filter_by(book_id=book_id).all()
    return render_template('admin/book_information.html',
                            book=book,
                           borrow_book_count=borrow_book_count,
                            borrow_records=borrow_records
                           )

@admin_bp.route('/user_management)',methods=['POST','GET'])
@login_required
def user_management():
    user_query = User.query

    if request.method == 'GET':
        query = request.args.get('q', '').strip()
        status = request.args.get('status', '').strip()
        # 初始化查询
        user_query = User.query
        if query:
            # 多字段模糊搜索:用户名、邮箱、电话、地址
            user_query = user_query.filter(
                or_(
                    User.username.ilike(f'%{query}%'),
                    User.email.ilike(f'%{query}%'),
                    User.phone.ilike(f'%{query}%'),
                    User.address.ilike(f'%{query}%')
                )
            )
        if status:
            try:
                status_int = int(status)
                user_query = user_query.filter_by(status=status_int)
            except ValueError:
                pass
        return render_template('admin/user_management.html',
                               user_query=user_query,
                               current_query=query,
                               selected_status=status
                               )

    return render_template('admin/user_management.html',
                           user_query=user_query
                           )

@admin_bp.route('/user_profile/<int:user_id>',methods=['POST','GET'])
@login_required
def user_profile(user_id):
    user_id = int(user_id)
    user = User.query.get(user_id)
    borrow_records = BorrowRecord.query.filter_by(user_id=user_id).all()
    current_borrow_count = BorrowRecord.query.filter_by(user_id=user_id,status=0).count()
    borrow_overdue_count = BorrowRecord.query.filter_by(user_id=user_id,status=2).count()
    return render_template('admin/user_profile.html',
                           user=user,
                           borrow_records=borrow_records,
                           current_borrow_count=current_borrow_count,
                           borrow_overdue_count=borrow_overdue_count
                           )

@admin_bp.route('/request_management',methods=['POST','GET'])
@login_required
def request_management():
    user_query = User.query
    user_register_count = User.query.filter_by(status=2).count()
    user_borrow_request_count = BorrowRecord.query.filter_by(status=3).count()
    user_return_request_count = BorrowRecord.query.filter_by(status=4).count()
    user_register_requests = User.query.filter_by(status=2).all()
    user_borrow_requests = BorrowRecord.query.filter_by(status=3).all()
    user_return_requests = BorrowRecord.query.filter_by(status=4).all()
    return render_template('admin/request_management.html',
                           user_query=user_query,
                           user_register_requests=user_register_requests,
                           user_register_count=user_register_count,
                           user_borrow_request_count=user_borrow_request_count,
                           user_borrow_requests=user_borrow_requests,
                           )

@admin_bp.route('/delete_book',methods=['POST'])
def delete_book():
    book_id = int(request.form.get('book_id'))
    if not book_id:
        return jsonify({'success':False,'message':'无效的图书ID'})
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'success':False,'message':'图书不存在'})
    # 删除图书
    from app import db
    db.session.delete(book)
    db.session.commit()
    return jsonify({'success':True})

@admin_bp.route('/delete_user',methods=['POST'])
def delete_user():
    user_id = int(request.form.get('user_id'))
    if not user_id:
        return jsonify({'success':False,'message':'无效的用户ID'})
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success':False,'message':'用户不存在'})
    # 删除用户
    from app import db
    db.session.delete(user)
    db.session.commit()
    return jsonify({'success':True})

@admin_bp.route('/set_user_active',methods=['POST'])
def set_user_active():
    user_id = int(request.form.get('user_id'))
    status = int(request.form.get('status'))
    if not user_id:
        return jsonify({'success':False,'message':'无效的用户ID'})
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success':False,'message':'用户不存在'})
    # 设置用户为激活状态
    user.status = status
    from app import db
    db.session.commit()
    return jsonify({'success':True})

@admin_bp.route('/process_register',methods=['POST'])
def process_register():
    user_id = int(request.form.get('request_id'))
    action = request.form.get('action')
    if not user_id:
        return jsonify({'success':False,'message':'无效的用户ID'})
    user = User.query.get(user_id)
    if not user:
        return jsonify({'success':False,'message':'用户不存在'})
    if action == 'approve':
        user.status = 1  # 激活用户
    elif action == 'reject':
        user.status = 3  # 拒绝注册，设置为未激活
    else:
        return jsonify({'success':False,'message':'无效的操作'})
    from app import db
    db.session.commit()
    return jsonify({'success':True})

@admin_bp.route('/bulk_process_register',methods=['POST'])
def bulk_process_register():
    user_ids = request.form.getlist('request_ids[]')
    action = request.form.get('action')
    if not user_ids:
        return jsonify({'success':False,'message':'无效的用户ID列表'})
    from app import db
    for user_id in user_ids:
        user = User.query.get(int(user_id))
        if not user:
            continue
        if action == 'approve':
            user.status = 1  # 激活用户
        elif action == 'reject':
            user.status = 3  # 拒绝注册，设置为未激活
        else:
            continue
    db.session.commit()
    return jsonify({'success':True})

@admin_bp.route('/process_borrow_book',methods=['POST'])
def process_borrow_book():
    request_id = int(request.form.get('request_id'))
    action = request.form.get('action')
    if not request_id:
        return jsonify({'success':False,'message':'无效的请求ID'})
    borrow_record = BorrowRecord.query.get(request_id)
    if not borrow_record:
        return jsonify({'success':False,'message':'借阅请求不存在'})
    if action == 'approve':
        from app import db
        borrow_record.status = 0
        db.session.commit()
    elif action == 'reject':
        # 直接删除借阅请求记录
        from app import db
        borrow_record.status = 4
        db.session.commit()
    else:
        return jsonify({'success':False,'message':'无效的操作'})
    return jsonify({'success':True})


@admin_bp.route('/change-book-status', methods=['POST'])
def change_book_status():
    """更改图书状态"""
    try:
        # 获取参数
        book_id = request.form.get('book_id')
        status = request.form.get('status')

        print(f"收到请求 - book_id: {book_id} (类型: {type(book_id)}), status: {status} (类型: {type(status)})")

        # 验证参数
        if not book_id or book_id.strip() == '':
            return jsonify({'success': False, 'message': "无效的图书ID"})

        if status is None or status == '':
            return jsonify({'success': False, 'message': "无效的状态"})

        # 将book_id转换为整数
        try:
            book_id_int = int(book_id)
        except ValueError:
            return jsonify({'success': False, 'message': "图书ID必须是数字"})

        # 将status转换为整数
        try:
            status_int = int(status)
        except ValueError:
            return jsonify({'success': False, 'message': "状态必须是数字"})

        # 验证状态值是否有效
        if status_int not in [0, 1, 2]:
            return jsonify({'success': False, 'message': "状态值无效，必须是0、1或2"})

        # 查找图书
        book = Book.query.get(book_id_int)
        if not book:
            return jsonify({'success': False, 'message': "图书不存在"})

        print(f"找到图书: {book.title}, 当前状态: {book.status}, 新状态: {status_int}")

        # 更新状态
        book.status = status_int
        from app import db
        db.session.commit()

        print(f"状态更新成功: {book.title} -> 状态: {status_int}")

        return jsonify({
            'success': True,
            'message': "修改成功",
            'new_status': status_int
        })

    except Exception as e:
        print(f"更改图书状态错误: {e}")
        return jsonify({
            'success': False,
            'message': f"修改失败: {str(e)}"
        }), 500
