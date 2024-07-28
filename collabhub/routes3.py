from collabhub import app, db
from flask import render_template, flash, redirect, request, url_for, abort
from flask_login import current_user, login_required
from collabhub.models import User, Notification, Campaign, Adrequest, Transaction, Influencerdata, Category, Sponsordata
from sqlalchemy import or_, func, and_

@app.route("/<int:user_id>/notifications")
@login_required
def notifications_page(user_id):
    user = User.query.get(user_id)
    if not user:
        abort(400)
    if current_user.id != user_id:
        abort(403)
    return render_template("notification_center.html",user=user)

@app.route("/<int:user_id>/notifications/clear")
@login_required
def clearnotifications_page(user_id):
    user = User.query.get(user_id)
    if not user:
        abort(400)
    if current_user.id != user_id:
        abort(403)
    try:
        count = Notification.query.filter(Notification.reciever==user.id).delete()
        db.session.commit()
        flash(f"{count} Notifications cleared successfully!",category="success")
    except:
        db.session.rollback()
        flash("Something went wrong!!",category="danger")
    return redirect(request.referrer)

@app.route("/sponsor/endCampaign/<int:campaign_id>")
@login_required
def endCampaign(campaign_id):
    if current_user.role != "sponsor":
        abort(403)
    camp = Campaign.query.get(campaign_id)
    if camp:
        if camp.sponsor_id != current_user.sponsdata.id:
            abort(403)
        for adreq in camp.ad_requests:
            if adreq.status in ["accepted","negotiation","unsettled"]:
                flash("Campaign has running Ad requests and can't be ended!",category="danger")
                return redirect(request.referrer)
        notifs = []
        for adreq in camp.ad_requests:
            if adreq.status in ["unapproved","pending"]:
                adreq.status = "rejected"
                notif = Notification(reciever=adreq.ad_influencer.user_id)
                notif.content = f"Ad request for the Campaign <strong>{adreq.ad_campaign.name}</strong> to <strong>{adreq.ad_campaign.sponsor.company_name}</strong> has been <strong>REJECTED</strong> by the Sponsor, as the Campaign is ending."
                notifs.append(notif)
        try:
            if notifs:
                db.session.add_all(notifs)
            camp.has_ended = True
            db.session.add(camp)
            db.session.commit()
            flash(f"Campaign {camp.name} has been ended Successfully!!",category="success")
        except:
            db.session.rollback()
            flash("Something went wrong!!",category="danger")
    else:
        flash("Invalid Request",category="danger")
    return redirect(request.referrer)

@app.route("/sponsor/deleteCampaign/<int:campaign_id>")
@login_required
def deleteCampaign(campaign_id):
    if current_user.role != "sponsor":
        abort(403)
    camp = Campaign.query.get(campaign_id)
    if camp:
        if camp.sponsor_id != current_user.sponsdata.id:
            abort(403)
        for adreq in camp.ad_requests:
            if adreq.status not in ["unapproved","pending","rejected"]:
                flash("Campaign has running Ad requests and can't be deleted!",category="danger")
                return redirect(request.referrer)
        notifs = []
        for adreq in camp.ad_requests:
            if adreq.status in ["unapproved","pending"]:
                notif = Notification(reciever=adreq.ad_influencer.user_id)
                notif.content = f"Ad request to <strong>{adreq.ad_campaign.sponsor.company_name}</strong> for the Campaign <strong>{adreq.ad_campaign.name}</strong> has been <strong>DELETED</strong> by the Sponsor."
                notifs.append(notif)
        try:
            if notifs:
                db.session.add_all(notifs)
            Adrequest.query.filter(Adrequest.campaign_id==camp.id).delete()
            db.session.delete(camp)
            db.session.commit()
            flash(f"Campaign {camp.name} has been deleted Successfully!!",category="success")
        except:
            db.session.rollback()
            flash("Something went wrong!!",category="danger")
    else:
        flash("Invalid Request",category="danger")
    return redirect(request.referrer)

@app.route("/transactions/<int:user_id>")
@login_required
def user_transactionspage(user_id):
    user = User.query.get(user_id)
    if not user:
        abort(400)
    if current_user.id != user_id:
        abort(403)
    transacts = Transaction.query.filter(or_(
        Transaction.sender == user_id,
        Transaction.reciever == user_id
    )).order_by(Transaction.dateoftransaction).all()
    return render_template("transactions.html",transacts = transacts)

@app.route("/admin")
@login_required
def admin_page():
    user = User.query.get(1)
    if current_user.role!="admin" or current_user.id != 1:
        abort(403)

    user_roles = db.session.query(User.role,func.count(User.id)).group_by(User.role).all()
    user_roles = {value[0].capitalize() : value[1] for value in user_roles}

    total_users = sum(user_roles.values())

    user_growth = db.session.query(User.dateofjoining,func.count(User.id)).group_by(User.dateofjoining).all()
    user_growth = {value[0].strftime('%Y-%m-%d') : value[1] for value in user_growth}

    campaign_stats = db.session.query(Campaign.has_ended,func.count(Campaign.id)).group_by(Campaign.has_ended).all()
    campaign_stats = {value[0] : value[1] for value in campaign_stats}

    total_campaigns = sum(campaign_stats.values())

    campaigncatcounts = db.session.query(Category.title,func.count(Campaign.id)).filter(Campaign.category_id == Category.id).group_by(Category.title).all()
    campaigncatcounts = {value[0] : value[1] for value in campaigncatcounts}

    influencercatcounts = db.session.query(Category.title,func.count(Influencerdata.id)).filter(Influencerdata.category_id == Category.id).group_by(Category.title).all()
    influencercatcounts = {value[0] : value[1] for value in influencercatcounts}

    transactions = db.session.query(func.count(Transaction.id),func.sum(Transaction.amount)).filter(and_(Transaction.sender!=None, Transaction.reciever!=None)).one_or_none()
    if transactions:
        total_transactions = transactions[0]
        if transactions[1]:
            transactions_worth = transactions[1]
        else:
            transactions_worth = 0
    else:
        total_transactions = 0
        transactions_worth = 0
    transactions_worth = f"{transactions_worth:,}"

    total_funds = db.session.query(func.sum(User.walletbalance)).scalar()
    if total_funds:
        total_funds = f"{total_funds:,}"
    else:
        total_funds = 0

    flagged_inf = db.session.query(func.count(Influencerdata.id)).filter(Influencerdata.is_flagged==True).scalar()
    flagged_spons = db.session.query(func.count(Sponsordata.id)).filter(Sponsordata.is_flagged==True).scalar()
    flagged_users = 0
    if flagged_inf:
        flagged_users+=flagged_inf
    if flagged_spons:
        flagged_users+=flagged_spons
    
    if total_users == 0:
        flagged_users_percent = 0
    else:
        flagged_users_percent = round((flagged_users/total_users)*100,2)

    flagged_campaigns = db.session.query(func.count(Campaign.id)).filter(Campaign.is_flagged==True).scalar()
    if flagged_campaigns == None:
        flagged_campaigns = 0
    if total_campaigns == 0:
        flagged_campaigns_percent = 0
    else:
        flagged_campaigns_percent = round((flagged_campaigns/total_campaigns)*100,2)

    influencer_demograpic = db.session.query(Influencerdata.country,func.count(Influencerdata.id)).group_by(Influencerdata.country).all()
    influencer_demograpic = {value[0] : value[1] for value in influencer_demograpic}

    adreqs = db.session.query(Adrequest.status,func.count(Adrequest.id)).group_by(Adrequest.status).all()
    adreqs = {value[0].capitalize() : value[1] for value in adreqs}
    total_ads = sum(adreqs.values())

    admin_notifs = db.session.query(func.count(Notification.id)).filter(Notification.reciever == current_user.id).scalar()
    if admin_notifs == None:
        admin_notifs = 0

    return render_template("admin_home.html",user=user,total_users=total_users,user_roles=user_roles, user_growth=user_growth,campaign_stats=campaign_stats, total_campaigns=total_campaigns,campaigncatcounts=campaigncatcounts,influencercatcounts=influencercatcounts,total_transactions=total_transactions,transactions_worth=transactions_worth,total_funds=total_funds,flagged_users_percent=flagged_users_percent,flagged_campaigns_percent=flagged_campaigns_percent,influencer_demograpic=influencer_demograpic,adreqs=adreqs,total_ads=total_ads,admin_notifs=admin_notifs)

@app.route("/admin/users")
@login_required
def admin_userspage():
    if current_user.role!="admin" or current_user.id != 1:
        abort(403)
    users = User.query.all()
    return render_template("admin_users.html",users= users)

@app.route("/admin/campaigns")
@login_required
def admin_campaignspage():
    if current_user.role!="admin" or current_user.id != 1:
        abort(403)
    camps = Campaign.query.order_by(Campaign.has_ended).all()
    return render_template("admin_campaigns.html",campaigns=camps)

@app.route("/admin/flaguser/<int:user_id>")
@login_required
def toggleflag(user_id):
    user = User.query.get(user_id)
    if not user:
        abort(400)
    if current_user.role !="admin" or user_id == 1:
        abort(403)
    if user.role == "influencer":
        user.infludata.is_flagged = not user.infludata.is_flagged
        nowstat = user.infludata.is_flagged
    else:
        user.sponsdata.is_flagged = not user.sponsdata.is_flagged
        nowstat = user.sponsdata.is_flagged
    if nowstat:
        flash(f"Flagged User @{user.username} !!",category="info")
        notif = Notification(reciever=user_id)
        notif.content = "<strong>ADMIN MESSAGE : </strong> Your profile has been <strong>FLAGGED</strong> by Admin due to suspicious activity! Contact at admincollabhub@12.com to resolve or your Account shall be Terminated."
    else:
        flash(f"Unflagged User @{user.username} !!",category="info")
        notif = Notification(reciever=user_id)
        notif.content = "<strong>ADMIN MESSAGE : </strong> Your profile has been <strong>UNFLAGGED</strong> by Admin. Sorry for the inconvinience. Happy Collaborating :)"
    db.session.add_all([user,notif])
    db.session.commit()
    return redirect(url_for('admin_userspage'))

@app.route("/admin/notifyUser/<int:user_id>",methods=["POST"])
@login_required
def notify_a_user(user_id):
    user = User.query.get(user_id)
    if not user:
        abort(400)
    if current_user.role != "admin":
        abort(403)
    if request.form["content"]:
        notif = Notification(reciever=user_id)
        notif.content = "<strong>ADMIN MESSAGE : </strong>"+request.form["content"]
        db.session.add(notif)
        db.session.commit()
        flash(f"Notification sent to @{user.username} successfully!!",category="success")
    else:
        flash("No notification body provided!!",category="danger")
    return redirect(request.referrer)

@app.route("/admin/flagcampaign/<int:campaign_id>")
@login_required
def toggleflagcampaign(campaign_id):
    camp = Campaign.query.get(campaign_id)
    if not camp:
        abort(400)
    if current_user.role !="admin":
        abort(403)
    camp.is_flagged = not camp.is_flagged
    nowstat = camp.is_flagged
    if nowstat:
        flash(f"Flagged Campaign {camp.name} !!",category="info")
        notif = Notification(reciever=camp.sponsor.user_id)
        notif.content = f"<strong>ADMIN MESSAGE : </strong> Your Campign <strong>{camp.name}</strong> has been <strong>FLAGGED</strong> by Admin due to suspicious activity! Contact at admincollabhub@12.com to resolve or your Campaign shall be Terminated."
    else:
        flash(f"Unflagged Campaign {camp.name} !!",category="info")
        notif = Notification(reciever=camp.sponsor.user_id)
        notif.content = f"<strong>ADMIN MESSAGE : </strong> Your Campign <strong>{camp.name}</strong> has been <strong>UNFLAGGED</strong> by Admin. Sorry for the inconvinience. Happy Collaborating :)"
    db.session.add_all([camp,notif])
    db.session.commit()
    return redirect(url_for('admin_campaignspage'))

@app.route("/influencer/<int:influencer_id>/stats")
def influencer_stats(influencer_id):
    influencer = Influencerdata.query.get(influencer_id)
    if not influencer:
        abort(400)
    if current_user.role != "influencer" or current_user.infludata.id!=influencer_id:
        abort(403)

    social_handles =[sociallink.handle.capitalize() for sociallink in influencer.social_links]
    social_handles_reach = [sociallink.reach for sociallink in influencer.social_links]
    total_reach = sum(social_handles_reach)
    if total_reach != 0:
        average_reach = int(total_reach/len(social_handles))
    else:
        average_reach = 0
    total_reach = f"{total_reach:,}"
    average_reach = f"{average_reach:,}"

    ad_stats = db.session.query(Adrequest.status,func.count(Adrequest.id)).filter(Adrequest.influencer_id == influencer_id).group_by(Adrequest.status).all()
    ad_stats = {value[0].capitalize() : value[1] for value in ad_stats}
    successful_ads =0
    for key in ad_stats:
        if key in ["Completed","Accepted","Unsettled"]:
            successful_ads += ad_stats[key]
    total_ads = sum(ad_stats.values())
    if total_ads == 0:
        successful_ads = 0
    else:
        successful_ads = round((successful_ads/total_ads)*100,2)

    payment_per_adreq = db.session.query(Adrequest.payment_amount).filter(and_(Adrequest.influencer_id == influencer_id,Adrequest.status.in_(["completed","accepted","unsettled"]))).all()
    payment_per_adreq = [value[0] for value in payment_per_adreq]

    total_earning = db.session.query(func.sum(Transaction.amount)).filter(and_(Transaction.reciever==current_user.id, Transaction.sender!=None)).scalar()
    if total_earning == None:
        total_earning = 0
    total_earning = f"{total_earning:,}"

    camp_ids = [adreq.campaign_id for adreq in influencer.ads]
    catcounts = db.session.query(Category.title,func.count(Campaign.id)).filter(and_(Campaign.id.in_(camp_ids),Campaign.category_id == Category.id)).group_by(Category.title).all()
    catcounts = {value[0] : value[1] for value in catcounts}


    return render_template("influencer_stats.html",social_handles=social_handles,social_handles_reach=social_handles_reach,total_reach=total_reach,average_reach = average_reach,ad_stats=ad_stats,total_ads=total_ads, payment_per_adreq = payment_per_adreq, total_earning = total_earning,success_percent=successful_ads,categories_participated=catcounts)

@app.route("/sponsor/<int:sponsor_id>/stats")
def sponsor_stats(sponsor_id):
    sponsor = Sponsordata.query.get(sponsor_id)
    if not sponsor:
        abort(400)
    if current_user.role != "sponsor" or current_user.sponsdata.id!=sponsor_id:
        abort(403)

    budget_among_camps = db.session.query(Campaign.name,Campaign.budget).filter(Campaign.sponsor_id==sponsor_id).all()
    budget_among_camps = {value[0]:value[1] for value in budget_among_camps}
    total_campaigns = len(budget_among_camps)
    if total_campaigns == 0:
        avg_camp_budget = 0
    else:
        avg_camp_budget = round(sum(budget_among_camps.values())/total_campaigns,2)
    avg_camp_budget = f"{avg_camp_budget:,}"

    adreq_per_camp = db.session.query(Campaign.name,func.count(Adrequest.id)).filter(and_(Campaign.sponsor_id==sponsor_id,Campaign.id==Adrequest.campaign_id)).group_by(Campaign.name).all()
    adreq_per_camp = {value[0]:value[1] for value in adreq_per_camp}

    budgetVsSpend_perCamp = db.session.query(Campaign.name,Campaign.budget,func.sum(Adrequest.payment_amount)).filter(and_(Adrequest.status.in_(["accepted","unsettled","completed"]),Campaign.id==Adrequest.campaign_id, Campaign.sponsor_id==sponsor_id)).group_by(Campaign.name).all()
    budgetVsSpend_perCamp_names = [value[0] for value in budgetVsSpend_perCamp]
    budgetVsSpend_perCamp_budgets = [value[1] for value in budgetVsSpend_perCamp]
    budgetVsSpend_perCamp_spends = [value[2] for value in budgetVsSpend_perCamp]

    total_money_spent = db.session.query(func.sum(Transaction.amount)).filter(and_(Transaction.sender==current_user.id, Transaction.reciever!=None)).scalar()
    if total_money_spent == None:
        total_money_spent = 0
    total_money_spent = f"{total_money_spent:,}"

    catcounts = db.session.query(Category.title,func.count(Campaign.id)).filter(and_(Campaign.sponsor_id==sponsor_id,Campaign.category_id == Category.id)).group_by(Category.title).all()
    catcounts = {value[0] : value[1] for value in catcounts}

    camps = db.session.query(Campaign.id).filter(Campaign.sponsor_id==sponsor_id).all()
    camps = [v[0] for v in camps]
    ad_stats = db.session.query(Adrequest.status,func.count(Adrequest.id)).filter(Adrequest.campaign_id.in_(camps)).group_by(Adrequest.status).all()
    ad_stats = {value[0].capitalize() : value[1] for value in ad_stats}
    total_adreqs = sum(ad_stats.values())

    successful_ads =0
    for key in ad_stats:
        if key in ["Completed","Accepted","Unsettled"]:
            successful_ads += ad_stats[key]
    if total_adreqs!=0:
        successful_ads = round((successful_ads/total_adreqs)*100,2)

    return render_template("sponsor_stats.html",total_campaigns=total_campaigns,budget_among_camps=budget_among_camps,adreq_per_camp=adreq_per_camp,total_adreqs=total_adreqs,avg_camp_budget=avg_camp_budget,budgetVsSpend_perCamp_names=budgetVsSpend_perCamp_names,budgetVsSpend_perCamp_budgets=budgetVsSpend_perCamp_budgets,budgetVsSpend_perCamp_spends=budgetVsSpend_perCamp_spends,total_money_spent=total_money_spent,catcounts=catcounts,ad_stats=ad_stats,successful_ads=successful_ads)