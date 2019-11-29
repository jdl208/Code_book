from codebook import app, mongo, bcrypt, mail
from flask import render_template, url_for, redirect, flash, request, abort
from codebook.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                            PostForm, RequestResetForm, ResetPasswordForm)
from codebook.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime
import os
import secrets
from PIL import Image
from bson.objectid import ObjectId
from flask_mail import Message


@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html', users=mongo.db.users.find(),
                           posts=mongo.db.posts.find(),
                           modals=mongo.db.posts.find(),
                           title="Home")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data,
                        email=form.email.data,
                        password=hashed_password,
                        profile_pic='default.jpg')
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
            user_obj = User(user['username'], user['email'], user['password'], user['profile_pic'])
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


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/prof_img', picture_fn)
    #  Resize uploaded profile picture to 150 by 150 px
    output_size = (150, 150)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            old_value = mongo.db.users.find_one({'username': current_user.username})
            new_pic = {'$set': {'profile_pic': picture_file}}
            mongo.db.users.update_one(old_value, new_pic)
        old_value = mongo.db.users.find_one({'username': current_user.username})
        new_value = {'$set': {'username': form.username.data, 'email': form.email.data}}
        mongo.db.users.update_one(old_value, new_value)
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    else:
        flash('Error updating account. Please try again', 'fail')
    profile_pic = url_for('static', filename='prof_img/' + current_user.profile_pic)
    return render_template('account.html', title='Account', profile_pic=profile_pic, form=form)


@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data,
                    short_desc=form.short_desc.data,
                    content=form.content.data,
                    author=current_user.username,
                    date_posted=datetime.utcnow())
        posts = mongo.db.posts
        posts.insert_one(post.__dict__)
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('new_post.html', title='New Post', form=form)


@app.route('/post/<post_id>')
def post(post_id):
    post = mongo.db.posts.find_one({'_id': ObjectId(post_id)})
    return render_template('post.html', title=post["title"], post=post)


@app.route('/post/<post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = mongo.db.posts.find_one({'_id': ObjectId(post_id)})
    if post['author'] != current_user.username:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        new_value = {'$set': {'title': form.title.data,
                              'short_desc': form.short_desc.data,
                              'content': form.content.data}}
        mongo.db.posts.update_one(post, new_value)
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post['_id']))
    elif request.method == 'GET':
        form.title.data = post['title']
        form.short_desc.data = post['short_desc']
        form.content.data = post['content']
    return render_template('new_post.html', title='Update Post', form=form)


@app.route('/post/<post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = mongo.db.posts.find_one({'_id': ObjectId(post_id)})
    if post['author'] != current_user.username:
        abort(403)
    mongo.db.posts.delete_one(post)
    flash('Your post has been deleted', 'success')
    return redirect(url_for('home'))
