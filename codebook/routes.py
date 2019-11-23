from codebook import app, mongo, bcrypt
from flask import render_template, url_for, redirect, flash, request
from codebook.forms import RegistrationForm, LoginForm
from codebook.models import User
from flask_login import login_user, current_user, logout_user, login_required
# from bson.objectid import ObjectId


@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html', users=mongo.db.users.find(), title="Home")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        users = mongo.db.users
        users.insert_one(new_user.__dict__)
        flash(f'Account for {form.username.data} has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = mongo.db.users.find_one({'email': form.email.data})
        if user and bcrypt.check_password_hash(user['password'], form.password.data):
            user_obj = User(user['username'], user['email'], user['password'])
            login_user(user_obj, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login unsuccesful, please check your email and/or password!', 'fail')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/account')
@login_required
def account():
    return render_template('account.html', title='Account')
