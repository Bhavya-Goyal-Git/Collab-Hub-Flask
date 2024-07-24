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

@app.route("/admin")
@login_required
def admin_page():
    user = User.query.get(1)
    if current_user.role!="admin" or current_user.id != 1:
        abort(403)
    return render_template("admin_home.html",user=user)

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