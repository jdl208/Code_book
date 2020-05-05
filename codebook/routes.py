import smtplib, ssl, os, secrets
from codebook import app, mongo, bcrypt, mail
from flask import render_template, url_for, redirect, flash, request, abort
from codebook.forms import (
    RegistrationForm,
    LoginForm,
    UpdateAccountForm,
    PostForm,
    SearchForm,
    RequestResetForm,
    ResetPasswordForm,
)
from codebook.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime
from PIL import Image
from bson.objectid import ObjectId
from flask_mail import Message


@app.route("/", methods=["GET", "POST"])
@app.route("/home", methods=["GET", "POST"])
def home():
    """
    Check if a user is signed in and then direct him to his own notes or to the frontpage.
    If not signed in You can sign in on the page directly
    """
    if current_user.is_authenticated:
        return redirect(url_for("my_notes"))
    form = LoginForm()
    if form.validate_on_submit():
        user = mongo.db.users.find_one({"email": form.email.data})
        if user and bcrypt.check_password_hash(user["password"], form.password.data):
            user_obj = User(user["username"], user["email"], user["password"], user["profile_pic"])
            login_user(user_obj, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("my_notes"))
        else:
            flash("Login unsuccesful, please check your email and/or password!", "danger")
    posts = mongo.db.posts.find({"$query": {"public": True}, "$orderby": {"date_posted": -1}}).limit(3)
    return render_template("index.html", posts=posts, title="Home", form=form)


@app.route("/public", methods=["GET", "POST"])
def public():
    """
    Route to all the public notes with a search bar that searches through all the public notes.
    """
    form = SearchForm()
    if form.validate_on_submit():
        result = mongo.db.posts.find({"$and": [{"$text": {"$search": form.query.data}}, {"public": True}]})
        return render_template("notes.html", posts=result, title="Search results", form=form)
    posts = mongo.db.posts.find({"$query": {"public": True}, "$orderby": {"date_posted": -1}})
    return render_template(
        "notes.html", posts=posts, title="Public notes", form=form, placeholder="Search public notes"
    )


@app.route("/my_notes", methods=["GET", "POST"])
@login_required
def my_notes():
    """
    View to your personal notes. If you haven't got a note yet,
    it wil direct you to the page to make a note.
    """
    form = SearchForm()
    if current_user.is_authenticated:
        if form.validate_on_submit():
            result = mongo.db.posts.find(
                {"$and": [{"$text": {"$search": form.query.data}}, {"author": current_user.username}]}
            )
            return render_template("notes.html", posts=result, title="Search results", form=form)
        if mongo.db.posts.count({"author": current_user.username}) == 0:
            flash("You have no notes yet. Make your first note here.", "info")
            return redirect(url_for("new_post"))
        return render_template(
            "notes.html",
            posts=mongo.db.posts.find({"$query": {"author": current_user.username}, "$orderby": {"date_posted": -1}}),
            title="My notes",
            form=form,
            placeholder="Search my notes",
        )


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    View to register page and create a user with a hashed password.
    It will set a default profile image.
    """
    if current_user.is_authenticated:
        return redirect(url_for("my_notes"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        new_user = User(
            username=form.username.data, email=form.email.data, password=hashed_password, profile_pic="default.png"
        )
        users = mongo.db.users
        users.insert_one(new_user.__dict__)
        flash(f"Account for {form.username.data} has been created! You can now log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    View to the login page.
    Checks if submitted values are correct or it will return an error
    """
    if current_user.is_authenticated:
        return redirect(url_for("my_notes"))
    form = LoginForm()
    if form.validate_on_submit():
        user = mongo.db.users.find_one({"email": form.email.data})
        if user and bcrypt.check_password_hash(user["password"], form.password.data):
            user_obj = User(user["username"], user["email"], user["password"], user["profile_pic"])
            login_user(user_obj, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("my_notes"))
        else:
            flash("Login unsuccesful, please check your email and/or password!", "danger")
    return render_template("login.html", title="Login", form=form)


@app.route("/logout")
def logout():
    """
    Log user out
    """
    logout_user()
    return redirect(url_for("home"))


def save_picture(form_picture):
    """
    Save a picture the user sets as a profile image.
    It will be resized to 150 by 150 pixels
    """
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, "static/prof_img", picture_fn)
    #  Resize uploaded profile picture to 150 by 150 px
    output_size = (150, 150)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    """
    View to update account information.
    When a user updates his profile image or username.
    This will also be adjusted in all the notes from user.
    """
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            old_value = mongo.db.users.find_one({"username": current_user.username})
            new_pic = {"$set": {"profile_pic": picture_file}}
            mongo.db.users.update_one(old_value, new_pic)
            mongo.db.posts.update_many({"author": current_user.username}, {"$set": {"avatar": picture_file}})
        if current_user.username != form.username.data:
            mongo.db.posts.update_many({"author": current_user.username}, {"$set": {"author": form.username.data}})
        old_value = mongo.db.users.find_one({"username": current_user.username})
        new_value = {"$set": {"username": form.username.data, "email": form.email.data}}
        mongo.db.users.update_one(old_value, new_value)
        flash("Your account has been updated!", "success")
        return redirect(url_for("account"))
    #  Fill the formfields with the current data
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    else:
        flash("Error updating account. Please try again", "danger")
    profile_pic = url_for("static", filename="prof_img/" + current_user.profile_pic)
    return render_template("account.html", title="Account", profile_pic=profile_pic, form=form)


@app.route("/post/new", methods=["GET", "POST"])
@login_required
def new_post():
    """
    Make a new post and submit it to mongodb
    """
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            short_desc=form.short_desc.data,
            content=form.content.data,
            author=current_user.username,
            date_posted=datetime.utcnow(),
            public=form.public.data,
            avatar=current_user.profile_pic,
        )
        mongo.db.posts.insert_one(post.__dict__)
        flash("Your post has been created!", "success")
        return redirect(url_for("home"))
    return render_template("new_post.html", title="New Note", form=form)


@app.route("/post/<post_id>")
def post(post_id):
    """
    View to a single note
    """
    post = mongo.db.posts.find_one({"_id": ObjectId(post_id)})
    return render_template("post.html", title=post["title"], post=post)


@app.route("/post/<post_id>/update", methods=["GET", "POST"])
@login_required
def update_post(post_id):
    """
    View to update notes.
    When a user tries to reach a note from another user. He will get a 403 error
    """
    post = mongo.db.posts.find_one({"_id": ObjectId(post_id)})
    if post["author"] != current_user.username:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        new_value = {
            "$set": {
                "title": form.title.data,
                "short_desc": form.short_desc.data,
                "content": form.content.data,
                "public": form.public.data,
                "date_posted": datetime.utcnow(),
            }
        }
        mongo.db.posts.update_one(post, new_value)
        flash("Your post has been updated!", "success")
        return redirect(url_for("post", post_id=post["_id"]))
    #  Fill form with current data from database
    elif request.method == "GET":
        form.title.data = post["title"]
        form.short_desc.data = post["short_desc"]
        form.content.data = post["content"]
        form.public.data = post["public"]
    return render_template("new_post.html", title="Update Post", form=form)


@app.route("/post/<post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    """
    View to delete your posts
    When an unauthorized user tries ot delete a post it will get a 403 error
    """
    post = mongo.db.posts.find_one({"_id": ObjectId(post_id)})
    if post["author"] != current_user.username:
        abort(403)
    mongo.db.posts.delete_one(post)
    flash("Your post has been deleted", "success")
    return redirect(url_for("home"))


def send_reset_email(user):
    reset_user = User(
        username=user["username"], email=user["email"], password=user["password"], profile_pic=user["profile_pic"]
    )
    token = reset_user.get_reset_token()
    msg = Message("Password Reset Request", sender="johandeleeuw@gmail.com", recipients=[reset_user.email])
    msg.body = f"""To reset your password, visit the following link:

{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
"""
    mail.send(msg)


@app.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = mongo.db.users.find_one({"email": form.email.data})
        send_reset_email(user)
        flash("An email has been sent with instructions to reset your password.", "info")
        return redirect(url_for("login"))
    return render_template("reset_request.html", title="Reset Password", form=form)


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    user = User.verify_reset_token(token)
    if user is None:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for("reset_request"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user.password = hashed_password
        mongo.db.users.update_one({"email": user["email"]}, {"$set": {"password": hashed_password}})
        flash("Your password has been updated! You are now able to log in", "success")
        return redirect(url_for("login"))
    return render_template("reset_token.html", title="Reset Password", form=form)
