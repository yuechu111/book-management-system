from datetime import datetime, timedelta
from functools import wraps
from threading import active_count

from flask import Blueprint, render_template, flash, url_for, session, request, jsonify
from flask_wtf.csrf import validate_csrf
from sqlalchemy.dialects.oracle.dictionary import all_users
from werkzeug.routing import ValidationError
from werkzeug.utils import redirect
from sqlalchemy import or_

from app import db
from app.forms import LoginForm
from app.models import User,Admin,Book,Category,BorrowRecord

users_bp = Blueprint('users', __name__,template_folder='templates/users')

@users_bp.route('/dashboard',methods=['POST','GET'])
def dashboard():
    user = User.query.get(session.get('user_id'))
    active_borrows = user.get_active_borrows()

    all_users_count = User.query.count()
    all_books_count = Book.query.count()
    return render_template('users/dashboard.html',
                            all_users_count=all_users_count,
                            all_books_count=all_books_count,
                            active_borrows=active_borrows
                           )

@users_bp.route('/borrowing',methods=['POST','GET'])
def borrowing():
    user = User.query.get(session.get('user_id'))
    borrow_history = user.get_borrow_history()
    active_borrows = user.get_active_borrows()

    return render_template('users/borrowing.html',
                           active_borrows=active_borrows,
                           borrow_history=borrow_history

                           )

@users_bp.route('/search',methods=['POST','GET'])
def search():
    # 获取所有分类
    categories = Category.query.all()

    # 获取查询参数
    query = request.args.get('q', '').strip()  # 搜索关键词（GET方式）
    category_id = request.args.get('category', '').strip()  # 分类ID（GET方式）

    # 初始化查询
    books_query = Book.query

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
    books = books_query.all()

    return render_template('users/search.html',
                           categories=categories,
                           books=books,
                           current_query=query,
                           selected_category=category_id
                           )

@users_bp.route('/favorites',methods=['POST','GET'])
def favorites():

    return render_template('users/favorites.html')


@users_bp.route('/borrow_book', methods=['POST'])
def borrow_book():
    try:
        # 1. 接收CSRF token并验证
        csrf_token = request.form.get('csrf_token')
        print(f"【1. CSRF验证】csrf_token: {csrf_token}")

        if csrf_token:
            try:
                validate_csrf(csrf_token)
                print("✅ CSRF验证通过")
            except ValidationError as e:
                print(f"❌ CSRF验证失败: {str(e)}")
                return jsonify({'success': False, 'message': '安全验证失败'}), 400
        else:
            print("⚠️ 未提供CSRF token，跳过验证")

        # 2. 接收book_id
        book_id = request.form.get('book_id')
        print(f"【2. 获取图书ID】book_id: {book_id}")

        if not book_id:
            print("❌ 缺少图书ID")
            return jsonify({'success': False, 'message': '缺少图书ID'}), 400

        # 3. 获取用户ID
        user_id = session.get("user_id")
        print(f"【3. 获取用户ID】user_id: {user_id}")

        if not user_id:
            print("❌ 用户未登录")
            return jsonify({'success': False, 'message': '请先登录'}), 401

        # 转换ID
        try:
            user_id = int(user_id)
            book_id = int(book_id)
            print(f"【4. 转换ID】user_id: {user_id}, book_id: {book_id}")
        except ValueError as e:
            print(f"❌ ID转换失败: {e}")
            return jsonify({'success': False, 'message': '无效的ID格式'}), 400

        # 4. 检查图书是否存在
        book = Book.query.get(book_id)
        print(f"【5. 检查图书】book: {book}")

        if not book:
            print("❌ 图书不存在")
            return jsonify({'success': False, 'message': '图书不存在'}), 404

        # 5. 检查图书是否可借
        print(f"【6. 检查库存】当前库存: {book.available_copies}")
        if book.available_copies <= 0:
            print("❌ 库存不足")
            return jsonify({'success': False, 'message': '该图书已借完'}), 400

        # 6. 检查用户是否已借阅该书且未归还
        existing_borrow = BorrowRecord.query.filter_by(
            user_id=user_id,
            book_id=book_id,
            return_date=None  # 未归还的记录
        ).first()

        print(f"【7. 检查重复借阅】existing_borrow: {existing_borrow}")
        if existing_borrow:
            print("❌ 已借阅未归还")
            return jsonify({'success': False, 'message': '您已借阅该书，请先归还'}), 200

        # 7. 创建借阅记录
        print("【8. 创建借阅记录】")
        new_borrow_record = BorrowRecord(
            user_id=user_id,
            book_id=book_id,
        )

        # 8. 设置应还日期
        due_date = datetime.utcnow() + timedelta(days=30)
        new_borrow_record.due_date = due_date
        print(f"【9. 设置应还日期】due_date: {due_date}")

        # 9. 更新图书库存
        book.available_copies -= 1
        print(f"【10. 更新库存】新库存: {book.available_copies}")

        # 打印借阅记录详情
        print(f"【11. 借阅记录详情】")
        print(f"   ID: {new_borrow_record.id}")
        print(f"   user_id: {new_borrow_record.user_id}")
        print(f"   book_id: {new_borrow_record.book_id}")
        print(f"   borrow_date: {new_borrow_record.borrow_date}")
        print(f"   due_date: {new_borrow_record.due_date}")
        print(f"   return_date: {new_borrow_record.return_date}")

        # 10. 保存到数据库
        print("【12. 开始提交到数据库】")
        db.session.add(new_borrow_record)

        try:
            db.session.commit()
            print("✅ 数据库提交成功！")
            print(f"✅ 借阅记录ID: {new_borrow_record.id}")
        except Exception as commit_error:
            print(f"❌ 数据库提交失败: {str(commit_error)}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            raise

        return jsonify({
            'success': True,
            'message': f'成功借阅《{book.title}》',
            'due_date': new_borrow_record.due_date.strftime('%Y-%m-%d'),
            'borrow_id': new_borrow_record.id
        })

    except ValidationError as e:
        print(f"❌ 验证错误: {str(e)}")
        return jsonify({'success': False, 'message': '安全验证失败'}), 200
    except ValueError as e:
        print(f"❌ 数值错误: {str(e)}")
        return jsonify({'success': False, 'message': '无效的图书ID'}), 200
    except Exception as e:
        print(f"\n" + "❌" * 20)
        print(f"【未捕获的异常】")
        print(f"异常类型: {type(e).__name__}")
        print(f"异常信息: {str(e)}")
        import traceback
        traceback.print_exc()
        print("❌" * 20 + "\n")

        try:
            db.session.rollback()
            print("已回滚数据库事务")
        except:
            pass

        return jsonify({'success': False, 'message': f'借阅失败: {str(e)}'}), 500
