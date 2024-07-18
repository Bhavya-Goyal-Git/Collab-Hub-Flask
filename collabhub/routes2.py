from collabhub import app, db
from flask import render_template, flash, redirect, request, url_for
from flask_login import current_user, login_required
from collabhub.models import User, Transaction, Category, Niche, Influencerdata, Campaign, Sponsordata, Adrequest, Admessages, Notification
from collabhub.forms import money_valiadator, ad_req_validator
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
            influencers = Influencerdata.query.filter(and_(
                Influencerdata.name.ilike(f"%{request.form['content']}%"),
                Influencerdata.is_flagged ==False
                )).all()
            flash(f"{len(influencers)} Results Found",category="info")
        elif request.form["search_by"] == "category":
            categories = Category.query.filter(Category.title.ilike(f"%{request.form['content']}%")).all()
            if categories:
                cat = [catt.id for catt in categories]
                influes = Influencerdata.query.filter(and_(
                    Influencerdata.category_id.in_(cat),
                    Influencerdata.is_flagged ==False
                    )).all()
                if influes:
                    influencers.extend(influes)
                flash(f"{len(influencers)} Result(s) Found",category="info")
            else:
                flash("Category does not exist!",category="danger")
        elif request.form["search_by"] == "niche":
            nichess = Niche.query.filter(Niche.title.ilike(f"%{request.form['content']}%")).all()
            if nichess:
                nic = [nicc.id for nicc in nichess]
                influes = Influencerdata.query.join(Influencerdata.influencer_niches).filter(and_(
                    Niche.id.in_(nic),
                    Influencerdata.is_flagged ==False
                )).all()
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

@app.route("/create/adrequest/form",methods=["POST"])
def adrequest_formpage():
    cid = request.form.get("cid")
    iid = request.form.get("iid")
    if not iid:
        flash("Something went wrong!",category="danger")
        return redirect(request.referrer)
    camp = Campaign.query.get(int(cid)) if cid else None
    influencer = Influencerdata.query.get(int(iid))
    return render_template("adrequest_form.html",camp=camp,influencer=influencer)

@app.route("/create/adrequest",methods=["POST"]) #register request in DB and redirect
def create_adrequest():
    if ad_req_validator(request.form):
        adreq = Adrequest(campaign_id=int(request.form["campaign"]), influencer_id=int(request.form["influencer"]))
        adreq.requirements = "To be filled by Sponsor" if current_user.role == "influencer" else request.form["requirements"]
        adreq.payment_amount = request.form["payment_amount"]
        adreq.status = "unapproved" if current_user.role == "influencer" else "pending"
        if request.form["ad_message"] != "":
            adreq.messages.append(Admessages(message=request.form["ad_message"],sender=current_user.role))
        db.session.add(adreq)
        db.session.commit()
        flash("Ad Request Made Successfully!!",category="success")
        if current_user.role == "influencer":
            notif = Notification(reciever=adreq.ad_campaign.sponsor.user_id)
            notif.content = f"You have recieved an Ad request from {current_user.infludata.name} for the Campaign {adreq.ad_campaign.name}. Kindly Edit/Approve or Reject the request to proceed further."
            db.session.add(notif)
            db.session.commit()
            return redirect(url_for("influencer_homepage",user_id=current_user.id))
        elif current_user.role == "sponsor":
            notif = Notification(reciever=adreq.ad_influencer.user_id)
            notif.content = f"You have recieved an Ad request from {current_user.sponsdata.company_name} for the campaign {adreq.ad_campaign.name}. Kindly Accept/Reject the request or Negotitate to proceed further."
            db.session.add(notif)
            db.session.commit()
            return redirect(url_for("sponsor_homepage",user_id=current_user.id))

@app.route("/influencer/<int:influencer_id>/myAdRequests")
def influencer_adrequests(influencer_id):
    influencer = Influencerdata.query.get(influencer_id)
    return render_template("influencer_myads.html",influencer=influencer)

@app.route("/sponsor/<int:sponsor_id>/myAdRequests")
def sponsor_adrequests(sponsor_id):
    sponsor = None
    campg = request.args.get("campaign")
    if campg:
        campg = Campaign.query.get(int(campg))
        flash(f"Found {len(campg.ad_requests)} Ad request(s) for the Campaign: {campg.name}",category="info")
    else:
        sponsor = Sponsordata.query.get(sponsor_id)
    return render_template("sponsor_myads.html",sponsor=sponsor, campg=campg)

@app.route("/influencer/AcceptAdReq/<int:ad_request_id>")
def acceptadreq_page(ad_request_id):
    adreq = Adrequest.query.get(int(ad_request_id))
    if adreq and adreq.status == "pending":
        adreq.status = "accepted"
        notif = Notification(reciever=adreq.ad_campaign.sponsor.user_id)
        notif.content = f"Your Ad request to {current_user.infludata.name} for the Campaign {adreq.ad_campaign.name} has been ACCEPTED by the Influencer."
        db.session.add_all([adreq,notif])
        db.session.commit()
        flash(f"Ad Request for Campaign {adreq.ad_campaign.name} has been accepted!",category="success")
    else:
        flash("Invalid Request",category="danger")
    return redirect(url_for('influencer_adrequests',influencer_id=adreq.influencer_id))

@app.route("/rejectAdReq/<int:ad_request_id>")
def rejectadreq_page(ad_request_id):
    adreq = Adrequest.query.get(int(ad_request_id))
    if adreq and adreq.status == "pending" and current_user.role=="influencer" :
        adreq.status = "rejected"
        notif = Notification(reciever=adreq.ad_campaign.sponsor.user_id)
        notif.content = f"Your Ad request to {current_user.infludata.name} for the Campaign {adreq.ad_campaign.name} has been REJECTED by the Influencer."
        db.session.add_all([adreq,notif])
        db.session.commit()
        flash(f"Ad Request for Campaign {adreq.ad_campaign.name} has been rejected!",category="info")
    elif adreq and (adreq.status == "unapproved" or adreq.status == "negotiation") and current_user.role=="sponsor":
        adreq.status = "rejected"
        notif = Notification(reciever=adreq.ad_influencer.user_id)
        notif.content = f"Your Ad request to {adreq.ad_campaign.sponsor.company_name} for the Campaign {adreq.ad_campaign.name} has been REJECTED by the Sponsor."
        db.session.add_all([adreq,notif])
        db.session.commit()
        flash(f"Influencer {adreq.ad_influencer.name}'s Ad Request for the Campaign {adreq.ad_campaign.name} has been rejected!",category="info")
    else:
        flash("Invalid Request",category="danger")
    return redirect(request.referrer)

@app.route("/deleteAdReq/<int:ad_request_id>")
def deleteadreq_page(ad_request_id):
    adreq = Adrequest.query.get(int(ad_request_id))
    if adreq and adreq.status == "unapproved" and current_user.role=="influencer" :
        notif = Notification(reciever=adreq.ad_campaign.sponsor.user_id)
        notif.content = f"Ad request from {current_user.infludata.name} for the Campaign {adreq.ad_campaign.name} has been DELETED by the Influencer."
        flash(f"Ad Request for Campaign {adreq.ad_campaign.name} has been deleted!",category="info")
        db.session.delete(adreq)
        db.session.add(notif)
        db.session.commit()
    elif adreq and (adreq.status == "pending" or adreq.status == "rejected") and current_user.role=="sponsor":
        notif = Notification(reciever=adreq.ad_influencer.user_id)
        notif.content = f"Ad request to {adreq.ad_campaign.sponsor.company_name} for the Campaign {adreq.ad_campaign.name} has been DELETED by the Sponsor."
        flash(f"Influencer {adreq.ad_influencer.name}'s Ad Request for the Campaign {adreq.ad_campaign.name} has been Deleted!",category="info")
        db.session.delete(adreq)
        db.session.add(notif)
        db.session.commit()
    else:
        flash("Invalid Request",category="danger")
    return redirect(request.referrer)