from collabhub import app, db
from flask import render_template, flash, redirect, request, url_for, abort
from flask_login import current_user, login_required
from collabhub.models import User, Notification, Campaign, Adrequest, Transaction
from sqlalchemy import or_

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