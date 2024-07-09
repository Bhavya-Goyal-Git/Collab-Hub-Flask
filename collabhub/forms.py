from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from collabhub.models import User
from flask import flash
from datetime import datetime,date

class RegisterForm(FlaskForm):

    def validate_username(self,username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if(user):
            raise ValidationError("Username Already Exists!")
        
    def validate_email_address(self,email_address_to_check):
        user = User.query.filter_by(email_address=email_address_to_check.data).first() 
        if(user):
            raise ValidationError("Email Address is already registered!")

    role = BooleanField(label="",default="checked") #true for influencer, false for sponsor
    username = StringField(label="Username",validators=[DataRequired(),Length(min=4,max=20)])
    email_address = EmailField(label="Email Address",validators=[DataRequired(),Email(message="Please enter a valid Email Address")])
    password = PasswordField(label="Password",validators=[DataRequired(),Length(min=8)])
    confirm_password = PasswordField(label="Confirm Password",validators=[DataRequired(),EqualTo("password","Confirm Password does not match Password field!")])
    submit = SubmitField(label="Sign Up")


class LoginForm(FlaskForm):
    
    username = StringField(label="Username",validators=[DataRequired(),Length(min=4,max=20)])
    password = PasswordField(label="Password",validators=[DataRequired(),Length(min=8)])
    submit = SubmitField(label="Log in")


def Campaign_form_validator(form):
    strtdate = datetime.strptime(form["start_date"],"%Y-%m-%d").date()
    enddate = datetime.strptime(form["end_date"], "%Y-%m-%d").date()
    if form["name"]=="":
        flash("Campaign name can't be empty",category="danger")
        return False
    if strtdate < date.today():
        flash(f"Start Date can't be older than {date.today}",category="danger")
        return False
    if enddate < date.today():
        flash(f"End Date can't be older than {date.today}",category="danger")
        return False
    if strtdate > enddate:
        flash(f"End Date can't be older than Start date : {strtdate}",category="danger")
        return False
    try:
        if int(form["budget"]) <0:
            flash("Budget needs to be a positive value",category="danger")
            return False
    except:
        flash("Budget needs to be a number",category="danger")
        return False
    
    if form["goal"]=="":
        flash("Atleast One Goal is required",category="danger")
        return False
    if form.getlist("niches") == []:
        flash("Atleast one Niche must be selected",category="danger")
        return False
    return True
    