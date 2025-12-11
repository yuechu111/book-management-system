from time import sleep

from alembic.util import status
from flask import Blueprint, render_template, jsonify, request, flash, url_for
from sqlalchemy.sql.elements import or_
from werkzeug.utils import redirect

from app.models import Book, User, BorrowRecord, Category
from app.views.users import borrow_book
from app.forms import BookForm

admin_bp = Blueprint('admin', __name__,template_folder='templates/admin')

@admin_bp.route('/dashboard',methods=['POST','GET'])
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
def book_information(book_id):
    book = Book.query.get(book_id)
    borrow_book_count = BorrowRecord.query.filter_by(book_id=book_id).count()
    borrow_records = BorrowRecord.query.filter_by(book_id=book_id).all()
    return render_template('admin/book_information.html',
                            book=book,
                           borrow_book_count=borrow_book_count,
                            borrow_records=borrow_records
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


