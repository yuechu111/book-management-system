from flask import Blueprint, render_template, flash, url_for, session
from werkzeug.utils import redirect

from app.forms import LoginForm
from app.models import User,Admin

books_bp = Blueprint('books', __name__,template_folder='templates/books')

@books_bp.route('/homepage',methods=['POST','GET'])
def homepage():
    return render_template('books/homepage.html')