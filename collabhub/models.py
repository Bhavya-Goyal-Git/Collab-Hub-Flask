from collabhub import db
from sqlalchemy import CheckConstraint, ForeignKey, String, Column
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from typing import List
from datetime import date



class User(db.Model):
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

class Category(db.Model) :
   id:Mapped[int] = mapped_column(primary_key=True)
   title:Mapped[str] = mapped_column(String(20),nullable=False,unique=True)

class Niche(db.Model) :
   id:Mapped[int] = mapped_column(primary_key=True)
   title:Mapped[str] = mapped_column(String(20),nullable=False,unique=True)

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

   influencer_category:Mapped['Category'] = relationship()
   social_links:Mapped[List['Socials']] = relationship()
   influencer_niches:Mapped[List['Niche']] = relationship(secondary=influencerniche)
   ads:Mapped[List['Adrequest']] = relationship(back_populates="ad_influencer")

class Sponsordata(db.Model):
   id:Mapped[int] = mapped_column(primary_key=True)
   user_id:Mapped[int] = mapped_column(ForeignKey("user.id"),unique=True)
   company_name:Mapped[str] = mapped_column(nullable=False)

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
      CheckConstraint("status IN ('pending', 'accepted', 'rejected', 'negotiation')", name='check_ad_status_valid'),
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