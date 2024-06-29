from collabhub import app, db
from flask import render_template, flash, redirect, url_for
from collabhub.forms import RegisterForm, LoginForm
from collabhub.models import User
from flask_login import login_user, logout_user, current_user, login_required

@app.route("/")
def home_page():
    return render_template("index.html")

@app.route("/register", methods = ["GET","POST"])
def register_page():
    form = RegisterForm()

    if form.validate_on_submit():
        new_role = "influencer" if form.role.data else "sponsor"
        new_user = User(username = form.username.data, email_address = form.email_address.data, password = form.password.data, role = new_role)
        db.session.add(new_user)
        db.session.commit()
        flash("User Registeration Successfull!",category="success")
        login_user(new_user)
        flash(f"Logged in as {new_user.username}",category="success")
        return redirect("/register")

    if form.errors != {}: #checking validation errors
        for ErrMsg in form.errors.values():
            flash(f"ERROR IN USER REGISTERATION: {ErrMsg[0]}",category="danger")

    return render_template("register.html",form=form)

@app.route("/login", methods = ["GET","POST"])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if user.check_password(form.password.data):
                login_user(user)
                flash(f"Login Successful! Welcome,{user.username}",category="success")
                return redirect("/register")
            else:
                flash("ERROR IN LOGIN : Password Does Not Match!",category="danger")
        else:
            flash("ERROR IN LOGIN : No Such Username Exists!",category="danger")

    return render_template("login.html",form=form)
            
        