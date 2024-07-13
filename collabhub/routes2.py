from collabhub import app, db
from flask import render_template, flash, redirect, request, url_for
from flask_login import current_user, login_required
from collabhub.models import User
from collabhub.forms import money_valiadator

@app.route("/<int:user_id>/addmoney", methods=["GET","POST"])
def addMoneyToWallet(user_id):
    user = User.query.get(user_id)
    if request.method == "POST":
        if money_valiadator(request.form):
            amount = int(request.form["amount"])
            user.walletbalance +=amount
            db.session.add(user)
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
                db.session.add(user)
                db.session.commit()
                flash(f"${amount}/- were withdrawn from wallet!",category="info")
                if user.role == "influencer":
                    return redirect(url_for("influencer_homepage",user_id=user.id))
                elif user.role == "sponsor":
                    return redirect(url_for("sponsor_homepage",user_id=user.id))
    return render_template("withdraw_money.html",user=user)