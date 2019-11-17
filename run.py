import os
from flask import Flask, render_template, url_for, redirect, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from forms import RegistrationForm, LoginForm
import env  # delete this line when deploying to heroku.

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config["MONGO_URI"] = os.getenv('MONGO_URI')

mongo = PyMongo(app)


@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html', users=mongo.db.users.find())


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        users = mongo.db.users
        users.insert_one({'username': form.username.data,
                          'email': form.email.data,
                          'password': form.password.data})
        flash(f'Account created for {form.username.data}!', 'alert_success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'test@login.com' and form.password.data == 'password':
            flash('Login succesfull!', 'alert_success')
            return redirect(url_for('home'))
        else:
            flash('Login failed, please check your email and/or password!', 'alert_fail')
    return render_template('login.html', title='Login', form=form)


if __name__ == '__main__':
    app.run(host=os.environ.get('IP', '0.0.0.0'),
            port=int(os.environ.get('PORT', 5000)),
            debug=True)
