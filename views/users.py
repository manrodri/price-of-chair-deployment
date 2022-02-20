from flask import Blueprint, request, session, url_for, render_template, redirect
# from models.user import User, UserErrors
from models.user_dynamo import User, UserErrors

user_blueprint = Blueprint('users', __name__)


@user_blueprint.route('/login', methods=['GET', 'POST'])
def login_user():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            if User.is_login_valid(email, password):
                session['email'] = email
                return redirect(url_for('alerts.index'))
        except UserErrors.UserError as e:
            return e.message

    return render_template("users/login.html")  # Send the user an error if their login was invalid


@user_blueprint.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            if User.register_user(email, password):
                session['email'] = email
                return redirect(url_for('alerts.index'))
        except UserErrors.UserError as e:
            return e.message

    return render_template("users/register.html")  # Send the user an error if their login was invalid


@user_blueprint.route('/logout')
def logout_user():
    if session.get('email'):
        session['email'] = None
    return redirect(url_for('users.login_user'))
