from collabhub import app, db
from flask import render_template, flash, redirect, request, url_for
from flask_login import current_user, login_required
from collabhub.models import User, Transaction, Category, Niche, Influencerdata
from collabhub.forms import money_valiadator

@app.route("/<int:user_id>/addmoney", methods=["GET","POST"])
def addMoneyToWallet(user_id):
    user = User.query.get(user_id)
    if request.method == "POST":
        if money_valiadator(request.form):
            amount = int(request.form["amount"])
            user.walletbalance +=amount
            trans = Transaction(sender=None,reciever=user_id,amount=amount)
            db.session.add(user)
            db.session.add(trans)
            db.session.commit()
            flash(f"${amount}/- were added to wallet successfully!",category="success")
            if user.role == "influencer":
                return redirect(url_for("influencer_homepage",user_id=user.id))
            elif user.role == "sponsor":
                return redirect(url_for("sponsor_homepage",user_id=user.id))
    return render_template("add_money.html",user=user)

@app.route("/<int:user_id>/withdrawmoney", methods=["GET","POST"])
def withdrawMoneyFromWallet(user_id):
    user = User.query.get(user_id)
    if request.method == "POST":
        if money_valiadator(request.form):
            amount = int(request.form["amount"])
            if amount>user.walletbalance:
                flash("TRANSACTION FAILED: Insufficient Money in wallet",category="danger")
            else:
                user.walletbalance -=amount
                trans = Transaction(sender=user_id,reciever=None,amount=amount)
                db.session.add(user)
                db.session.add(trans)
                db.session.commit()
                flash(f"${amount}/- were withdrawn from wallet!",category="info")
                if user.role == "influencer":
                    return redirect(url_for("influencer_homepage",user_id=user.id))
                elif user.role == "sponsor":
                    return redirect(url_for("sponsor_homepage",user_id=user.id))
    return render_template("withdraw_money.html",user=user)

@app.route("/create/category", methods=["GET","POST"])
def create_category():
    if request.method == "POST":
        if request.form["category_title"]:
            try:
                cat = Category(title=request.form["category_title"].capitalize())
                db.session.add(cat)
                db.session.commit()
                flash("Category Added Successfully!",category="success")
            except:
                flash("Category Already exists or is too long",category="danger")
        else:
            flash("Category field cannot be left blank!",category="danger")
        return redirect(request.referrer)
    return render_template("create_category.html")

@app.route("/add/niche", methods=["GET","POST"])
def create_niche():
    if request.method == "POST":
        if request.form["niche_title"]:
            cat = Category.query.get(request.form["category"])
            try:
                niche = Niche(title=request.form["niche_title"])
                cat.niches.append(niche)
                db.session.add(cat)
                db.session.commit()
                flash("Niche Added Successfully!",category="success")
            except:
                flash("Niche Already exists or is too long",category="danger")
        else:
            flash("Niche field cannot be left blank!",category="danger")
        return redirect(request.referrer)
    categories = Category.query.all()
    return render_template("create_niche.html",categories=categories)

def have_common_element(list1, list2):
    return not set(list1).isdisjoint(list2)

@app.route("/search/influencers", methods=["GET","POST"])
def search_influencers():
    influencers = []
    if request.method == "POST":
        if request.form["content"] == "":
            influencers = Influencerdata.query.all()
        elif request.form["search_by"] == "name":
            influencers = Influencerdata.query.filter(Influencerdata.name.ilike(f"%{request.form['content']}%")).all()
            flash(f"{len(influencers)} Results Found",category="info")
        elif request.form["search_by"] == "category":
            categories = Category.query.filter(Category.title.ilike(f"%{request.form['content']}%")).all()
            if categories:
                for cat in categories:
                    influes = Influencerdata.query.filter_by(category_id=cat.id).all()
                    if influes:
                        influencers.extend(influes)
                flash(f"{len(influencers)} Result(s) Found",category="info")
            else:
                flash("Category does not exist!",category="danger")
        elif request.form["search_by"] == "niche":
            nichess = Niche.query.filter(Niche.title.ilike(f"%{request.form['content']}%")).all()
            if nichess:
                for nic in nichess:
                    influes = Influencerdata.query.join(Influencerdata.influencer_niches).filter(Niche.id == nic.id).all()
                    if influes:
                        influencers.extend(influes)
                flash(f"{len(influencers)} Result(s) Found",category="info")
            else:
                flash("Niche does not exist!",category="danger")
    cat_list = [catt.title for catt in Category.query.all()]
    nic_list = [nicc.title for nicc in Niche.query.all()]
    return render_template("search_influencers.html",influencers=influencers,cat_list=cat_list,nic_list=nic_list)