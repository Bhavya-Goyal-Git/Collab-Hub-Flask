from collabhub import app, db
from flask import render_template, flash, redirect, request, url_for
from flask_login import current_user, login_required
from collabhub.models import User, Notification

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