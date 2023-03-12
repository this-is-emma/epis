from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from foundation_app.models import User
from foundation_app.auth.forms import SignUpForm, LoginForm
from foundation_app.extensions import app, db, bcrypt

auth = Blueprint('auth', __name__)

# Create your routes here.
@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            username=form.username.data,
            phone_number = form.phone_number.data,
            first_name = form.first_name.data,
            email = form.email.data,
            password=hashed_password,
            date_joined = datetime.now()
        )

        db.session.add(user)
        db.session.commit()
        flash('New account Created.')
        return redirect(url_for('auth.login'))
    return render_template('signup.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        login_user(user, remember=True)
        next_page = request.args.get('next')
        print(f'{user.first_name} is admin? {user.is_admin}')
        return redirect(next_page if next_page else url_for('auth.user_account'))
    return render_template('login.html', form=form)

@auth.route('/user_account', methods=['GET', 'POST'])
def user_account():
    user = current_user
    id = current_user.id
    user1 = User.query.get(id)
    print(f'user1 is: {user1}')
    print(f'donations are : {user1.donations}')
    #gather all users:
    all_users = User.query.all()
    return render_template('user_account.html', user = user, all_users=all_users)



@auth.route('/logout')
def logout():
    logout_user()
    flash('Successfully logged out!')
    return redirect(url_for('main.homepage'))

@auth.route('/set_admin')
def set_admin():
    user = User.query.filter_by(id=1).first()
    user.is_admin = True
    db.session.commit()
    flash('User 1 is now admin!')
    return redirect(url_for('main.homepage'))