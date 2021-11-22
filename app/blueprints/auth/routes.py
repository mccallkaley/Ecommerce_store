from flask import render_template, request, redirect, url_for, flash
from .forms import LoginForm, RegisterForm, EditProfileForm
from app.models import User
from flask_login import login_user, current_user, logout_user, login_required
from .import bp as auth

from app.models import User
from flask import g, make_response, request


from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from app.models import User
from flask import g


basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

@basic_auth.verify_password
def verify_password(email, password):
    # check if user exists
    u = User.query.filter_by(email=email).first()
    if u is None:
        return False
    g.current_user = u
    # check password
    return u.check_hashed_password(password)

@token_auth.verify_token
def verify_token(token):
    u = User.check_token(token) if token else None
    g.current_user = u
    return g.current_user or None

@auth.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        #do Login stuff
        email = request.form.get("email").lower()
        password = request.form.get("password")
                                #Database col = form inputted email
        u = User.query.filter_by(email=email).first()

        if u and u.check_hashed_password(password):
            login_user(u)
            # Give the user Feedback thats you logged in successfully
            flash('You have logged in', 'success')
            return redirect(url_for("main.index"))
        error_string = "Invalid Email password combo"
        return render_template('login.html.j2', error = error_string, form=form)
    return render_template('login.html.j2', form=form)

@auth.route('/logout')
@login_required
def logout():
    if current_user:
        logout_user()
        flash('You have logged out', 'danger')
        return redirect(url_for('auth.login'))



@auth.get('/token')
@basic_auth.login_required()
def get_token():
    user = g.current_user
    token = user.get_token()
    return make_response({"token":token},200)

# makes a user an Admin
# {"id":5}
@auth.put('/admin')
@token_auth.login_required()
def make_admin():
    user_id_to_be_admin = request.get_json().get('id')
    if not user_id_to_be_admin:
        return make_response("Invalid payload", 400)
    if not g.current_user.is_admin:
        return make_response("This action requires Admin privs", 403)
    user = User.query.get(user_id_to_be_admin)
    if not user:
        return make_response("User does not exist!", 404)
    user.is_admin = True
    user.save()
    return make_response(f'{user.first_name} {user.last_name} is now an Admin', 200)

@auth.get('/admin')
@token_auth.login_required()
def get_admin():
    return make_response({"isAdmin":g.current_user.is_admin or False}, 200)



@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST' and form.validate_on_submit():
        try:
            new_user_data = {
                "first_name":form.first_name.data.title(),
                "last_name":form.last_name.data.title(),
                "email":form.email.data.lower(),
                "password": form.password.data,
                "icon":int(form.icon.data)
            }
            #create and empty user
            new_user_object = User()
            # build user with form data
            new_user_object.from_dict(new_user_data)
            # save user to database
            new_user_object.save()
            flash('You have been registered to the system!', 'primary')
        except:
            error_string = "There was an unexpected Error creating your account. Please Try again."
            return render_template('register.html.j2',form=form, error = error_string) #when we had an error creating a user
        return redirect(url_for('auth.login')) # on a post request that successfully creates a new user
    return render_template('register.html.j2', form = form) #the render template on the Get request

@auth.route('/edit_profile', methods=['GET','POST'])
def edit_profile():
    form = EditProfileForm()
    if request.method == 'POST' and form.validate_on_submit():
        new_user_data={
                "first_name":form.first_name.data.title(),
                "last_name":form.last_name.data.title(),
                "email":form.email.data.lower(),
                "password": form.password.data,
                "icon":int(form.icon.data) if int(form.icon.data) != 9000 else current_user.icon
        }
        user=User.query.filter_by(email=form.email.data.lower()).first()
        if user and current_user.email != user.email:
            flash('Email already in use','danger')
            return redirect(url_for('auth.edit_profile'))
        try:
            current_user.from_dict(new_user_data)
            current_user.save()
            flash('Profile Update', 'success')
        except:
            flash('There was an unexpected error', 'danger')
            return redirect(url_for('auth.edit_profile'))
    return render_template('register.html.j2', form = form)