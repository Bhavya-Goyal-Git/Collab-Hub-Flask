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
            if current_user.role=="admin":
                try:
                    cat = Category(title=request.form["category_title"].capitalize())
                    db.session.add(cat)
                    db.session.commit()
                    flash("Category Added Successfully!",category="success")
                except:
                    flash("Category Already exists or is too long",category="danger")
            else:
                notif = Notification(reciever=1)
                notif.content = f"Request from <strong>@{current_user.user_name}</strong> for creation of Category: <strong>{request.form['category_title']}</strong>. Kindly add the category (or not if inappropriate) and notify the User."
                db.session.add(notif)
                db.session.commit()
                flash("Request for adding of category sent to ADMIN, until then please use given categories, change later.",category="success")
        else:
            flash("Category field cannot be left blank!",category="danger")
        return redirect(request.referrer)
    return render_template("create_category.html")

@app.route("/add/niche", methods=["GET","POST"])
def create_niche():
    if request.method == "POST":
        if request.form["niche_title"]:
            cat = Category.query.get(request.form["category"])
            if current_user.role=="admin":
                try:
                    niche = Niche(title=request.form["niche_title"])
                    cat.niches.append(niche)
                    db.session.add(cat)
                    db.session.commit()
                    flash("Niche Added Successfully!",category="success")
                except:
                    flash("Niche Already exists or is too long",category="danger")
            else:
                notif = Notification(reciever=1)
                notif.content = f"Request from <strong>@{current_user.user_name}</strong> for creation of Niche: <strong>{request.form['niche_title']}</strong> under the Category:<strong>{cat.name}</strong>. Kindly add the Niche (or not if inappropriate) and notify the User."
                db.session.add(notif)
                db.session.commit()
                flash("Request for adding of Niche sent to ADMIN, until then please use given niches, change later.",category="success")
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
                Influencerdata.name.ilike(f"{request.form['content']}%"),
                Influencerdata.is_flagged ==False
                )).all()
            flash(f"{len(influencers)} Results Found",category="info")
        elif request.form["search_by"] == "category":
            categories = Category.query.filter(Category.title.ilike(f"{request.form['content']}%")).all()
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
            nichess = Niche.query.filter(Niche.title.ilike(f"{request.form['content']}%")).all()
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
            sponsors = Sponsordata.query.filter(Sponsordata.company_name.ilike(f"{request.form['content']}%")).all()
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
            categories = Category.query.filter(Category.title.ilike(f"{request.form['content']}%")).all()
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
            nichess = Niche.query.filter(Niche.title.ilike(f"{request.form['content']}%")).all()
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
    if camp and (camp.has_ended or camp.is_flagged or camp.end_date<date.today()):
        flash("Campaign is restricted/expired and can't have Ad requests",category="danger")
        return redirect(request.referrer) 
    influencer = Influencerdata.query.get(int(iid))
    return render_template("adrequest_form.html",camp=camp,influencer=influencer)

@app.route("/create/adrequest",methods=["POST"])
def create_adrequest():
    if ad_req_validator(request.form,True):
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
            notif.content = f"You have recieved an Ad request from <strong>{current_user.infludata.name}</strong> for the Campaign <strong>{adreq.ad_campaign.name}</strong>. Kindly Edit/Approve or Reject the request to proceed further."
            db.session.add(notif)
            db.session.commit()
            return redirect(url_for("influencer_homepage",user_id=current_user.id))
        elif current_user.role == "sponsor":
            notif = Notification(reciever=adreq.ad_influencer.user_id)
            notif.content = f"You have recieved an Ad request from <strong>{current_user.sponsdata.company_name}</strong> for the campaign <strong>{adreq.ad_campaign.name}</strong>. Kindly Accept/Reject the request or Negotitate to proceed further."
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
        notif.content = f"Your Ad request to <strong>{current_user.infludata.name}</strong> for the Campaign <strong>{adreq.ad_campaign.name}</strong> has been <strong>ACCEPTED</strong> by the Influencer."
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
        notif.content = f"Your Ad request to <strong>{current_user.infludata.name}</strong> for the Campaign <strong>{adreq.ad_campaign.name}</strong> has been <strong>REJECTED</strong> by the Influencer."
        db.session.add_all([adreq,notif])
        db.session.commit()
        flash(f"Ad Request for Campaign {adreq.ad_campaign.name} has been rejected!",category="info")
    elif adreq and (adreq.status == "unapproved" or adreq.status == "negotiation") and current_user.role=="sponsor":
        adreq.status = "rejected"
        notif = Notification(reciever=adreq.ad_influencer.user_id)
        notif.content = f"Your Ad request to <strong>{adreq.ad_campaign.sponsor.company_name}</strong> for the Campaign <strong>{adreq.ad_campaign.name}</strong> has been <strong>REJECTED</strong> by the Sponsor."
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
        notif.content = f"Ad request from <strong>{current_user.infludata.name}</strong> for the Campaign <strong>{adreq.ad_campaign.name}</strong> has been <strong>DELETED</strong> by the Influencer."
        flash(f"Ad Request for Campaign {adreq.ad_campaign.name} has been deleted!",category="info")
        db.session.delete(adreq)
        db.session.add(notif)
        db.session.commit()
    elif adreq and (adreq.status == "pending" or adreq.status == "rejected") and current_user.role=="sponsor":
        notif = Notification(reciever=adreq.ad_influencer.user_id)
        notif.content = f"Ad request to <strong>{adreq.ad_campaign.sponsor.company_name}</strong> for the Campaign <strong>{adreq.ad_campaign.name}</strong> has been <strong>DELETED</strong> by the Sponsor."
        flash(f"Influencer {adreq.ad_influencer.name}'s Ad Request for the Campaign {adreq.ad_campaign.name} has been Deleted!",category="info")
        db.session.delete(adreq)
        db.session.add(notif)
        db.session.commit()
    else:
        flash("Invalid Request",category="danger")
    return redirect(request.referrer)

@app.route("/influencer/negotitateAdReq/<int:ad_request_id>",methods=["POST"])
def negotitateadreq_page(ad_request_id):
    adreq = Adrequest.query.get(int(ad_request_id))
    if adreq and adreq.status == "pending":
        adreq.status = "negotiation"
        admsg = Admessages(sender="influencer",message=request.form["ad_message"])
        adreq.messages.append(admsg)
        notif = Notification(reciever=adreq.ad_campaign.sponsor.user_id)
        notif.content = f"Your Ad request to <strong>{current_user.infludata.name}</strong> for the Campaign <strong>{adreq.ad_campaign.name}</strong> has been put under <strong>NEGOTIATION</strong> by the Influencer. The changes requested can be found in dedicated Ad-Chat window. Kindly Update/Approve the changes or Reject the request to proceed further."
        db.session.add_all([adreq,notif])
        db.session.commit()
        flash(f"Ad Request for Campaign {adreq.ad_campaign.name} has been sent back to Sponsor {adreq.ad_campaign.sponsor.company_name} for Negotiation!",category="success")
    else:
        flash("Invalid Request",category="danger")
    return redirect(request.referrer)


@app.route("/sponsor/editAdRequest/<int:ad_request_id>",methods=["GET","POST"])
def edit_adrequestpage(ad_request_id):
    adreq = Adrequest.query.get(int(ad_request_id))
    if request.method == "POST":
        if ad_req_validator(request.form,False):
            isreqchanged = False if adreq.requirements == request.form["requirements"] else True
            ispaychanged = False if int(adreq.payment_amount) == int(request.form["payment_amount"]) else True
            adreq.requirements = request.form["requirements"]
            adreq.payment_amount = request.form["payment_amount"]
            if request.form["ad_message"] != "":
                adreq.messages.append(Admessages(message=request.form["ad_message"],sender="sponsor"))
                db.session.add(adreq)
            notif = Notification(reciever=adreq.ad_influencer.user_id)
            msg=""
            if adreq.status == "unapproved":
                msg = f"Your Ad Request for the Campaign <strong>{adreq.ad_campaign.name}</strong> to <strong>{adreq.ad_campaign.sponsor.company_name}</strong> has been approved by the Sponsor. Requirements for the ad request have been added."
                if(ispaychanged):
                    msg+= " Payment Amount however, is not kept at expected value, it has been changed."
            elif adreq.status == "negotiation":
                msg = f"Your Negotiation in Ad Request for the Campaign <strong>{adreq.ad_campaign.name}</strong> to <strong>{adreq.ad_campaign.sponsor.company_name}</strong> has been approved by the Sponsor."
                if(ispaychanged):
                    msg+=" Payment Amount for the ad request has been changed."
                if(isreqchanged):
                    msg+=" Requirements for the ad request have been changed."
            msg+= " Kindly Accept/Reject the Ad request or Negotiate it to proceed further."
            notif.content = msg
            adreq.status = "pending"
            db.session.add_all([adreq,notif])
            db.session.commit()
            flash(f"Ad request to {adreq.ad_influencer.name} for the Campaign {adreq.ad_campaign.name} has been Edited & Approved successfully!",category="success")
            return redirect(url_for("sponsor_adrequests",sponsor_id=current_user.sponsdata.id))
    return render_template("edit_adrequest.html",adreq=adreq)

@app.route("/adRequest/<int:ad_request_id>/markCompleted")
def markcompleted_adreq(ad_request_id):
    adreq = Adrequest.query.get(int(ad_request_id))
    if adreq.status == "accepted":
        adreq.status = "unsettled"
        notif = Notification(reciever=adreq.ad_campaign.sponsor.user_id)
        notif.content = f"Ad Contract for the Campaign <strong>{adreq.ad_campaign.name}</strong> with <strong>{adreq.ad_influencer.name}</strong> has been marked <strong>DONE</strong> by the Influencer. The status has been set to unsettled. Kindly <strong>Make the due payment</strong> to the influencer to complete the Ad request."
        db.session.add_all([adreq,notif])
        db.session.commit()
        flash(f"Ad Request for the campaign {adreq.ad_campaign.name} has been marked DONE successfully",category="success")
    else:
        flash("Invalid Request",category="danger")
    return redirect(request.referrer)

@app.route("/adRequest/<int:ad_request_id>/makePayment")
def makeadreq_payment(ad_request_id):
    adreq = Adrequest.query.get(int(ad_request_id))
    if adreq.status == "unsettled":
        ad_sponsor = adreq.ad_campaign.sponsor.user_data
        ad_influ = adreq.ad_influencer.user_data
        if ad_sponsor.walletbalance < adreq.payment_amount:
            flash("Insufficient Money in wallet! Couldn't make payment for ad campaign!",category="danger")
        else:
            ad_sponsor.walletbalance -= adreq.payment_amount
            ad_influ.walletbalance +=adreq.payment_amount
            newTrans = Transaction(sender=ad_sponsor.id,reciever=ad_influ.id,amount=adreq.payment_amount)
            notif = Notification(reciever=adreq.ad_influencer.user_id)
            notif.content = f"Payment of <strong>${adreq.prettypayment}/-</strong> regarding Completed Ad request for Campaign <strong>{adreq.ad_campaign.name}</strong> by Sponsor <strong>{adreq.ad_campaign.sponsor.company_name}</strong> has been recieved in the wallet."
            adreq.status = "completed"
            db.session.add_all([adreq,notif,newTrans])
            db.session.commit()
            flash(f"Payment for the Ad Request made successfully!",category="success")
    else:
        flash("Invalid Request",category="danger")
    return redirect(request.referrer)