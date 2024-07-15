from collabhub import app, db
from flask import render_template, flash, redirect, request, url_for
from flask_login import current_user, login_required
from collabhub.models import User, Transaction, Category, Niche, Influencerdata, Campaign, Sponsordata
from collabhub.forms import money_valiadator
from sqlalchemy import and_
from datetime import date

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

@app.route("/search/influencers", methods=["GET","POST"])
def search_influencers():
    influencers = []
    if request.method == "POST":
        if request.form["content"] == "":
            flash("No Search Query Provided!",category="danger")
        elif request.form["search_by"] == "name":
            influencers = Influencerdata.query.filter(Influencerdata.name.ilike(f"%{request.form['content']}%")).all()
            flash(f"{len(influencers)} Results Found",category="info")
        elif request.form["search_by"] == "category":
            categories = Category.query.filter(Category.title.ilike(f"%{request.form['content']}%")).all()
            if categories:
                cat = [catt.id for catt in categories]
                influes = Influencerdata.query.filter(Influencerdata.category_id.in_(cat)).all()
                if influes:
                    influencers.extend(influes)
                flash(f"{len(influencers)} Result(s) Found",category="info")
            else:
                flash("Category does not exist!",category="danger")
        elif request.form["search_by"] == "niche":
            nichess = Niche.query.filter(Niche.title.ilike(f"%{request.form['content']}%")).all()
            if nichess:
                nic = [nicc.id for nicc in nichess]
                influes = Influencerdata.query.join(Influencerdata.influencer_niches).filter(Niche.id.in_(nic)).all()
                if influes:
                    influencers.extend(influes)
                flash(f"{len(influencers)} Result(s) Found",category="info")
            else:
                flash("Niche does not exist!",category="danger")
    cat_list = [catt.title for catt in Category.query.all()]
    nic_list = [nicc.title for nicc in Niche.query.all()]
    return render_template("search_influencers.html",influencers=influencers,cat_list=cat_list,nic_list=nic_list)

@app.route("/search/campaigns", methods=["GET","POST"])
def search_campaigns():
    campaigns = []
    if request.method == "POST":
        if request.form["content"] == "":
            flash("No Search Query Provided!",category="danger")
        elif request.form["search_by"] == "company_name":
            sponsors = Sponsordata.query.filter(Sponsordata.company_name.ilike(f"%{request.form['content']}%")).all()
            if sponsors:
                spons = [sponsor.id for sponsor in sponsors]
                camps = Campaign.query.filter(and_(
                    Campaign.sponsor_id.in_(spons),
                    Campaign.status == "public",
                    Campaign.is_flagged == False,
                    Campaign.has_ended == False
                    )).all()
                if camps:
                    campaigns.extend(camps)
                flash(f"{len(campaigns)} Results Found",category="info")
            else:
                flash("No Sponsor found",category="danger")
        elif request.form["search_by"] == "category":
            categories = Category.query.filter(Category.title.ilike(f"%{request.form['content']}%")).all()
            if categories:
                cat = [catt.id for catt in categories]
                camps = Campaign.query.filter(and_(
                        Campaign.category_id.in_(cat),
                        Campaign.status == "public",
                        Campaign.is_flagged == False,
                        Campaign.has_ended == False
                        )).all()
                if camps:
                    campaigns.extend(camps)
                flash(f"{len(campaigns)} Result(s) Found",category="info")
            else:
                flash("Category does not exist!",category="danger")
        elif request.form["search_by"] == "niche":
            nichess = Niche.query.filter(Niche.title.ilike(f"%{request.form['content']}%")).all()
            if nichess:
                nic = [nicc.id for nicc in nichess]
                camps = Campaign.query.join(Campaign.campaign_niches).filter(and_(
                Niche.id.in_(nic),
                Campaign.status == "public",
                Campaign.is_flagged == False,
                Campaign.has_ended == False
                )).all()
                if camps:
                    campaigns.extend(camps)
                flash(f"{len(campaigns)} Result(s) Found",category="info")
            else:
                flash("Niche does not exist!",category="danger")
    cat_list = [catt.title for catt in Category.query.all()]
    nic_list = [nicc.title for nicc in Niche.query.all()]
    return render_template("search_campaigns.html",campaigns=campaigns,cat_list=cat_list,nic_list=nic_list,today_date=date.today())