from collabhub import db, bcrypt, login_manager
from sqlalchemy import CheckConstraint, ForeignKey, String, Column
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from typing import List
from datetime import date
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model,UserMixin):
   id:Mapped[int] = mapped_column(primary_key=True)
   username:Mapped[str] = mapped_column(String(20),nullable=False,unique=True)
   email_address:Mapped[str] = mapped_column(nullable=False,unique=True)
   password_hash:Mapped[str] = mapped_column(nullable=False)
   role:Mapped[str] = mapped_column(nullable=False)
   is_flagged:Mapped[bool] = mapped_column(default=False)

   __table_args__ =(
      CheckConstraint("role IN ('influencer', 'sponsor','admin')", name='check_role_valid'),
   )

   infludata:Mapped['Influencerdata'] = relationship(uselist=False)
   sponsdata:Mapped['Sponsordata'] =  relationship(uselist=False)

   @property
   def password(self):
      raise AttributeError("Non Accessible attribute")
   
   @password.setter
   def password(self,password_to_set):
      self.password_hash = bcrypt.generate_password_hash(password_to_set).decode("utf-8")

   def check_password(self,attempted_password):
      return bcrypt.check_password_hash(self.password_hash,attempted_password)


class Category(db.Model) :
   id:Mapped[int] = mapped_column(primary_key=True)
   title:Mapped[str] = mapped_column(String(20),nullable=False,unique=True)

   niches:Mapped[List['Niche']] = relationship()

class Niche(db.Model) :
   id:Mapped[int] = mapped_column(primary_key=True)
   title:Mapped[str] = mapped_column(String(20),nullable=False,unique=True)
   associated_category:Mapped[int] = mapped_column(ForeignKey("category.id"))

class Socials(db.Model) :
   id:Mapped[int] = mapped_column(primary_key=True)
   owner:Mapped[int] = mapped_column(ForeignKey("influencerdata.id"))
   handle:Mapped[str] = mapped_column(nullable=False)
   link:Mapped[str] = mapped_column(nullable=False,unique=True)

influencerniche = db.Table(
    "influencerniche",
    Column("influencer_id", ForeignKey("influencerdata.id"), primary_key=True),
    Column("niche_id", ForeignKey("niche.id"), primary_key=True),
)
campaignniche = db.Table(
   "campaignniche",
   Column("ad_id", ForeignKey("campaign.id"), primary_key=True),
   Column("niche_id", ForeignKey("niche.id"), primary_key=True),
)

class Influencerdata(db.Model):
   id:Mapped[int] = mapped_column(primary_key=True)
   user_id:Mapped[int] = mapped_column(ForeignKey("user.id"),unique=True)
   name:Mapped[str] = mapped_column(nullable=False)
   country:Mapped[str] = mapped_column(nullable=True)
   category_id:Mapped[int] = mapped_column(ForeignKey("category.id"))
   about:Mapped[str]
   cover_photo:Mapped[str] = mapped_column(unique=True,nullable=True) #stores filename
   profile_photo:Mapped[str] = mapped_column(unique=True,nullable=True) 

   influencer_category:Mapped['Category'] = relationship()
   social_links:Mapped[List['Socials']] = relationship()
   influencer_niches:Mapped[List['Niche']] = relationship(secondary=influencerniche)
   ads:Mapped[List['Adrequest']] = relationship(back_populates="ad_influencer")

class Sponsordata(db.Model):
   id:Mapped[int] = mapped_column(primary_key=True)
   user_id:Mapped[int] = mapped_column(ForeignKey("user.id"),unique=True)
   company_name:Mapped[str] = mapped_column(nullable=False)
   profile_photo:Mapped[str] = mapped_column(unique=True,nullable=True)
   
   campaigns:Mapped[List['Campaign']] = relationship(back_populates="sponsor")
   

class Campaign(db.Model):
   id:Mapped[int] = mapped_column(primary_key=True)
   sponsor_id:Mapped[int] = mapped_column(ForeignKey("sponsordata.id"))
   name:Mapped[str] = mapped_column(nullable=False)
   description:Mapped[str]
   start_date:Mapped[date] = mapped_column(nullable=False)
   end_date:Mapped[date] = mapped_column(nullable=False)
   budget:Mapped[int] = mapped_column(nullable=False)
   status:Mapped[str] = mapped_column(nullable=False)
   goal:Mapped[str] = mapped_column(nullable=False)
   category_id:Mapped[int] = mapped_column(ForeignKey("category.id"))
   is_flagged:Mapped[bool] = mapped_column(default=False)
   has_ended:Mapped[bool] = mapped_column(default=False)
   campaign_pic:Mapped[str] = mapped_column(unique=True,nullable=True)

   __table_args__ =(
      CheckConstraint("status IN ('public', 'private')", name='check_status_valid'),
   )

   sponsor:Mapped['Sponsordata'] = relationship(back_populates="campaigns")
   campaign_category:Mapped['Category'] = relationship()
   ad_requests:Mapped[List['Adrequest']] = relationship(back_populates="ad_campaign")
   campaign_niches:Mapped[List['Niche']] = relationship(secondary=campaignniche)


class Adrequest(db.Model):
   id:Mapped[int] = mapped_column(primary_key=True)
   campaign_id:Mapped[int] = mapped_column(ForeignKey("campaign.id"))
   influencer_id:Mapped[int] = mapped_column(ForeignKey("influencerdata.id"))
   requirements:Mapped[str] = mapped_column(nullable=False)
   payment_amount:Mapped[int] = mapped_column(nullable=False)
   status:Mapped[str] = mapped_column(nullable=False)

   __table_args__ =(
      CheckConstraint("status IN ('pending', 'accepted', 'rejected', 'negotiation', 'completed')", name='check_ad_status_valid'),
   )

   ad_campaign:Mapped['Campaign'] = relationship(back_populates="ad_requests")
   ad_influencer:Mapped['Influencerdata'] = relationship(back_populates="ads")
   messages:Mapped[List['Admessages']] = relationship()

class Admessages(db.Model):
   id:Mapped[int] = mapped_column(primary_key=True)
   message:Mapped[str] = mapped_column(nullable=False)
   adrequest_id:Mapped[int] = mapped_column(ForeignKey("adrequest.id"))
   sender:Mapped[str] = mapped_column(nullable=False)

   __table_args__ =(
      CheckConstraint("sender IN ('influencer', 'sponsor')", name='check_sender_valid'),
   )