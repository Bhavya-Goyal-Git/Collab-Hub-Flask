from collabhub import app, db
from flask import render_template, flash, redirect, request, url_for
from flask_login import current_user, login_required
from collabhub.models import User, Notification, Campaign, Adrequest, Admessages

@app.route("/<int:user_id>/notifications")
def notifications_page(user_id):
    user = User.query.get(user_id)
    return render_template("notification_center.html",user=user)

@app.route("/<int:user_id>/notifications/clear")
def clearnotifications_page(user_id):
    user = User.query.get(user_id)
    count = Notification.query.filter(Notification.reciever==user.id).delete()
    db.session.commit()
    flash(f"{count} Notifications cleared successfully!",category="success")
    return redirect(request.referrer)

@app.route("/sponsor/endCampaign/<int:campaign_id>")
def endCampaign(campaign_id):
    camp = Campaign.query.get(campaign_id)
    if camp:
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
        if notifs:
            db.session.add_all(notifs)
        camp.has_ended = True
        db.session.add(camp)
        db.session.commit()
        flash(f"Campaign {camp.name} has been ended Successfully!!",category="success")
    else:
        flash("Invalid Request",category="danger")
    return redirect(request.referrer)

@app.route("/sponsor/deleteCampaign/<int:campaign_id>")
def deleteCampaign(campaign_id):
    camp = Campaign.query.get(campaign_id)
    if camp:
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
        if notifs:
            db.session.add_all(notifs)
        Adrequest.query.filter(Adrequest.campaign_id==camp.id).delete()
        db.session.delete(camp)
        db.session.commit()
        flash(f"Campaign {camp.name} has been deleted Successfully!!",category="success")
    else:
        flash("Invalid Request",category="danger")
    return redirect(request.referrer)