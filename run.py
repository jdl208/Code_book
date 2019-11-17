import os
from flask import Flask, render_template, url_for

app = Flask(__name__)


@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'alert_success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)
    

if __name__ == '__main__':
    app.run(debug=True)
