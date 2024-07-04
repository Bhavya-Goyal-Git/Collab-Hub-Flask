from collabhub import app, db, list_of_countries
from flask import render_template, flash, redirect, request, url_for
from collabhub.forms import RegisterForm, LoginForm
from collabhub.models import User, Category, Niche, Influencerdata
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
import os
import uuid

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
        if new_user.role == "influencer":
            return redirect(f"/influencer/updateprofile/{new_user.id}")
        else:
            pass #redirect to sponsor updateprofile

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
                flash(f"Login Successful! Welcome, {user.username}",category="success")
                if user.role == "influencer":
                    return redirect(f"/influencer/{user.id}/home")
                elif user.role == "sponsor":
                    pass
                else:
                    pass #admin
            else:
                flash("ERROR IN LOGIN : Password Does Not Match!",category="danger")
        else:
            flash("ERROR IN LOGIN : No Such Username Exists!",category="danger")

    return render_template("login.html",form=form)
            
@app.route("/logout")
def logout_page():
    logout_user()
    flash("You have been logged out!",category="info")
    return redirect(url_for("home_page"))

@app.route("/influencer/updateprofile/<int:user_id>", methods = ["GET","POST"])
def influencer_completeprofile_page(user_id):
    user = User.query.get(user_id)
    if request.method=="POST":
        if request.form["name"]=="":
            flash("ERROR IN DATA UPDATION! No Name Given",category="danger")
            return redirect(f"/influencer/updateprofile/{user_id}")
        elif request.form.getlist("niches") == []:
            flash("ERROR IN DATA UPDATION! No Niches Selected",category="danger")
            return redirect(f"/influencer/updateprofile/{user_id}")
        if user.infludata:
            user.infludata.name = request.form["name"]
            user.infludata.country = request.form["country"]
            user.infludata.about = request.form["about"]
            user.infludata.influencer_category = Category.query.get(int(request.form["category"]))
            while len(user.infludata.influencer_niches)!=0:
                user.infludata.influencer_niches.pop()
            nichelist = []
            for element in request.form.getlist("niches"):
                nichelist.append(Niche.query.get(int(element)))
            for niche in nichelist:
                user.infludata.influencer_niches.append(niche)
            db.session.add(user)
            db.session.commit()
            flash("Data Updated SuccessFully!!",category="success")
            return redirect(f"/influencer/{user.id}/home")
        else:
            data = Influencerdata(user_id=user_id,name=request.form["name"],country=request.form["country"],about=request.form["about"])
            category = Category.query.get(int(request.form["category"]))
            data.influencer_category = category
            nichelist = []
            for element in request.form.getlist("niches"):
                nichelist.append(Niche.query.get(int(element)))
            for niche in nichelist:
                data.influencer_niches.append(niche)
            db.session.add(data)
            db.session.commit()
            flash("Data Uploaded Successfully!!",category="success")
            return redirect(f"/influencer/{user.id}/home")

    categories = Category.query.all()
    niches = Niche.query.all()
    return render_template("influencer_updateprofile.html",categories=categories,niches=niches,list_of_countries=list_of_countries,user=user)

@app.route("/influencer/<int:user_id>") #profile page (publically visible)
def influencer_profilepage(user_id):
    user = User.query.get(user_id)
    return render_template("influencer_profilepage.html",user=user)

@app.route("/influencer/<int:user_id>/home") #home page with links
def influencer_homepage(user_id):
    user = User.query.get(user_id)
    return render_template("influencer_homepage.html",user=user)

@app.route("/<int:user_id>/updateprofilepic", methods=["GET","POST"])
def update_profilepic(user_id):
    user = User.query.get(user_id)
    if request.method =="POST":
        myfile = request.files["profile_pic"]
        if myfile:
            extension = os.path.splitext(myfile.filename)[-1]
            if extension in app.config["ALLOWED_EXTENSIONS"]:
                name = str(uuid.uuid1()) + "_" + secure_filename(myfile.filename)
                myfile.save(os.path.join(app.root_path, app.config["UPLOAD_FOLDER"],"profile_pics/",name))
                if(user.role=="influencer"):
                    user.infludata.profile_photo = name
                else:
                    user.sponsdata.profile_photo = name
                db.session.add(user)
                db.session.commit()
                flash("Profile Picture Updated Successfully!",category="success")
                if(user.role=="influencer"):
                    return redirect(f"/influencer/{user.id}/home")
                else:
                    pass #return to sponsors home page
            else:
                flash("ERROR IN UPLOADING FILE: Extention not allowed!",category="danger")
        else:
            flash("ERROR IN UPLOADING FILE: No file selected",category="danger")
    return render_template("updateprofilepic.html",user=user)