from functools import wraps
from flask import request, jsonify
from app.models import SolarPlant
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from app.models import User
from app import db
from app.auth import auth

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user is None or not user.check_password(request.form['password']):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('login.html')

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        user = User(username=request.form['username'], email=request.form['email'])
        user.set_password(request.form['password'])
        user.role = 'user'  # Set default role
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    return render_template('register.html')




def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.args.get('api_key')
        if not api_key:
            return jsonify({"error": "No API key provided"}), 401
        
        plant = SolarPlant.query.filter_by(api_key=api_key).first()
        
        if not plant:
            return jsonify({"error": "Invalid API key"}), 401
        
        if plant.api_status != 'enabled':
            return jsonify({"error": "API access is not enabled for this plant"}), 403
        
        kwargs['plant_id'] = plant.id
        return f(*args, **kwargs)
    return decorated_function

    


#this is for the create admin role
@auth.route('/create_admin', methods=['GET', 'POST'])
def create_admin():
    if request.method == 'POST':
        admin = User(username=request.form['username'], email=request.form['email'], role='admin')
        admin.set_password(request.form['password'])
        db.session.add(admin)
        db.session.commit()
        flash('Admin user created successfully!')
        return redirect(url_for('auth.login'))
    return render_template('create_admin.html')

