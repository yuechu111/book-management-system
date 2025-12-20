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
from app.forms.user import ProfileForm
from app.models import User,Admin,Book,Category,BorrowRecord,Favorite

users_bp = Blueprint('users', __name__,template_folder='templates/users')

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

@users_bp.route('/dashboard',methods=['POST','GET'])
@login_required
def dashboard():

    soon_book = 0

    user = get_current_user()
    active_borrows = user.get_active_borrows()
    #获取我的收藏数量
    my_favorites_count = Favorite.query.filter_by(user_id=user.id,is_active=True).count()
    all_users_count = User.query.count()
    all_books_count = Book.query.count()

    now = datetime.utcnow()
    for borrow in active_borrows:
        if borrow.due_date - now < timedelta(7):
            soon_book += 1

    return render_template('users/dashboard.html',
                            all_users_count=all_users_count,
                            all_books_count=all_books_count,
                            active_borrows=active_borrows,
                           borrow_record=BorrowRecord,
                           my_favorites_count=my_favorites_count,
                           soon_book=soon_book
                           )

@users_bp.route('/borrowing',methods=['POST','GET'])
@login_required
def borrowing():
    user = User.query.get(session.get('user_id'))
    borrow_history = user.get_borrow_history()
    active_borrows = user.get_active_borrows()

    return render_template('users/borrowing.html',
                           active_borrows=active_borrows,
                           borrow_history=borrow_history
                           )

@users_bp.route('/search',methods=['POST','GET'])
@login_required
def search():
    user_id = get_current_user().id
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
                           selected_category=category_id,
                           user_id=user_id
                           )

@users_bp.route('/favorites',methods=['POST','GET'])
@login_required
def favorites():
    user = get_current_user()
    if not user:
        return redirect(url_for('users.login'))

    user_id = user.id

    # 获取所有分类
    categories = Category.query.all()

    # 获取查询参数
    query = request.args.get('q', '').strip()
    category_id = request.args.get('category', '-1')

    # 基础查询：获取用户的所有收藏记录
    favorites_query = Favorite.query.filter_by(user_id=user_id)

    # 如果有搜索条件，需要先过滤收藏记录对应的图书
    if query or category_id != '-1':
        # 先获取符合条件的图书ID
        book_query = Book.query

        # 分类筛选
        if category_id and category_id != '-1':
            try:
                category_id_int = int(category_id)
                book_query = book_query.filter_by(category_id=category_id_int)
            except ValueError:
                pass

        # 关键词搜索
        if query:
            book_query = book_query.filter(
                or_(
                    Book.title.ilike(f'%{query}%'),
                    Book.author.ilike(f'%{query}%'),
                    Book.isbn.ilike(f'%{query}%'),
                    Book.description.ilike(f'%{query}%')
                )
            )

        # 获取符合条件的图书ID
        filtered_books = book_query.all()
        filtered_book_ids = [book.id for book in filtered_books]

        # 过滤收藏记录，只保留符合条件的图书
        if filtered_book_ids:
            favorites_query = favorites_query.filter(Favorite.book_id.in_(filtered_book_ids))
        else:
            # 如果没有符合条件的图书，返回空结果
            return render_template('users/favorites.html',
                                   favorites_books=[],
                                   categories=categories,
                                   query=query,
                                   selected_category=category_id)

    # 获取收藏记录
    favorites_books = favorites_query.all()
    borrow_query = BorrowRecord.query
    return render_template('users/favorites.html',
                           favorites_books=favorites_books,
                           categories=categories,
                           query=query,
                           selected_category=category_id,
                           borrow_query=borrow_query,
                           user_id=user_id
                           )

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

        user = get_current_user()
        if len(user.get_active_borrows()) > 5:
            return jsonify({'success': False, 'message': '个人借阅图书数量最大为5'}), 200

        # 7. 创建借阅记录
        print("【8. 创建借阅记录】")
        new_borrow_record = BorrowRecord(
            user_id=user_id,
            book_id=book_id,
            status=3
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

@users_bp.route('/continue_borrow_book', methods=['POST'])
def continue_borrow_book():

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

        # 2. 接收borrow_id
        borrow_id = request.form.get('borrow_id')

        if not borrow_id:
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
            borrow_id = int(borrow_id)
        except ValueError as e:
            print(f"❌ ID转换失败: {e}")
            return jsonify({'success': False, 'message': '无效的ID格式'}), 400

        borrow_record = BorrowRecord.query.get(borrow_id)
        print(borrow_record.renew_times)
        borrow_record.due_date += timedelta(days=15)

        if borrow_record.renew_times >= 3:
            return jsonify({'success': False, 'message': '续借次数已达上限'}), 200

        try:
            borrow_record.renew_times += 1
            db.session.commit()
            print("✅ 数据库提交成功！")
        except Exception as commit_error:
            print(f"❌ 数据库提交失败: {str(commit_error)}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            raise

        return jsonify({
            'success': True,
            'message': '成功续借',
            'new_due_date': borrow_record.due_date.strftime('%Y-%m-%d %H:%M')
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

        return jsonify({'success': False,'message': f'借阅失败: {str(e)}',}), 500

@users_bp.route('/return_book', methods=['POST'])
def return_book():
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

        user = get_current_user()
        borrow_id = request.form.get('borrow_id')
        borrow_record = BorrowRecord.query.get(borrow_id)

        if not borrow_record or borrow_record.user_id != user.id:
            return jsonify({'success': False, 'message': '无效的借阅记录'}), 400

        if borrow_record.return_book():
            book = Book.query.get(borrow_record.book_id)
            book.available_copies += 1

            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return jsonify({'success': False, 'message': '还书失败，请稍后重试'}), 500

            return jsonify({'success': True, 'message': f'成功归还《{book.title}》'})

    except ValueError as e:
        print(f"❌ 数值错误: {str(e)}")
        return jsonify({'success': False, 'message': '无效的图书ID'}), 200

    return jsonify({'success': False, 'message': '还书操作失败'}), 400

@users_bp.route('/my_favorite', methods=['POST'])
def my_favorite():
    """切换收藏状态（收藏/取消收藏）"""
    try:
        # 1. CSRF验证
        csrf_token = request.form.get('csrf_token')
        if csrf_token:
            try:
                validate_csrf(csrf_token)
                print("✅ CSRF验证通过")
            except ValidationError as e:
                print(f"❌ CSRF验证失败: {str(e)}")
                return jsonify({'success': False, 'message': '安全验证失败'}), 400

        # 2. 获取用户ID
        user_id = session.get('user_id')
        if not user_id:
            print("❌ 用户未登录")
            return jsonify({'success': False, 'message': '请先登录'}), 401

        print(f"用户ID: {user_id}")

        # 3. 获取图书ID
        book_id = request.form.get('book_id')
        if not book_id:
            print("❌ 缺少book_id参数")
            return jsonify({'success': False, 'message': '缺少图书ID'}), 400

        try:
            book_id = int(book_id)
        except ValueError:
            print(f"❌ 图书ID格式错误: {book_id}")
            return jsonify({'success': False, 'message': '无效的图书ID格式'}), 400

        # 4. 查询图书
        book = Book.query.get(book_id)
        if not book:
            print(f"❌ 图书不存在: book_id={book_id}")
            return jsonify({'success': False, 'message': '图书不存在'}), 404

        # 5. 查询是否已收藏
        existing_favorite = Favorite.query.filter_by(
            user_id=user_id,
            book_id=book_id
        ).first()

        operation = ""  # 记录操作类型
        try:
            if existing_favorite:
                # 取消收藏
                operation = "cancel"
                print(f"执行取消收藏: user_id={user_id}, book_id={book_id}")

                db.session.delete(existing_favorite)
                db.session.commit()

                return jsonify({
                    'success': True,
                    'operation': 'cancel',  # 操作类型
                    'message': f'已取消收藏《{book.title}》',
                    'is_favorite': False,  # 当前状态
                    'book_title': book.title
                })

            else:
                # 添加收藏
                operation = "add"
                print(f"执行添加收藏: user_id={user_id}, book_id={book_id}")

                favorite = Favorite(
                    user_id=user_id,
                    book_id=book_id,
                    created_at=datetime.utcnow()
                )

                db.session.add(favorite)

                db.session.commit()

                return jsonify({
                    'success': True,
                    'operation': 'add',  # 操作类型
                    'message': f'成功收藏《{book.title}》',
                    'is_favorite': True,  # 当前状态
                    'book_title': book.title,
                    'favorite_id': favorite.id
                })

        except Exception as e:
            db.session.rollback()
            print(f"❌ {operation}收藏操作失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'操作失败，请稍后重试',
                'error': str(e)
            }), 500

    except Exception as e:
        print(f"❌ 收藏功能异常: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'操作失败: {str(e)}'
        }), 500

@users_bp.route('/my_profile', methods=['POST','GET'])
@login_required
def my_profile():
    profile_form = ProfileForm()
    current_user = get_current_user()
    if request.method == 'GET':
        profile_form.username.data = current_user.username  # 这里设置默认值
        profile_form.email.data = current_user.email
        profile_form.phone.data = current_user.phone
        profile_form.address.data = current_user.address if current_user.address else ''

        # POST 请求时的处理逻辑
    if profile_form.validate_on_submit():
        current_user.username = profile_form.username.data
        current_user.email = profile_form.email.data
        current_user.phone = profile_form.phone.data
        current_user.address = profile_form.address.data
        # 处理密码修改
        if profile_form.new_password.data:
            if not current_user.verify_password(profile_form.current_password.data):
                flash('当前密码错误，无法修改密码', 'danger')
                return render_template('users/my_profile.html',profile_form=profile_form)
            flash('密码修改成功，请使用新密码登录', 'success')
            current_user.password = profile_form.new_password.data  # 使用属性设置器自动哈希密码
            db.session.commit()
            return redirect(url_for('auth.login'))
        flash("个人资料更新成功", "success")
        db.session.commit()
    return render_template('users/my_profile.html',profile_form=profile_form)

@users_bp.route('/delete_book', methods=['POST','GET'])
def delete_book():
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
    borrow_id = request.form.get('borrow_id')
    borrow_record = BorrowRecord.query.get(borrow_id)
    from app import db
    db.session.delete(borrow_record)
    db.session.commit()
    return jsonify({'success':True,'message':'删除成功'})

def get_current_user():
    return User.query.get(session.get('user_id'))