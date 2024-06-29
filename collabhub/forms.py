from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from collabhub.models import User

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
