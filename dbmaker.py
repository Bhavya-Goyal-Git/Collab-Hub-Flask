from collabhub import app, db
from collabhub.models import User, Category,Niche

print("\n\n----------- Welcome to initial Database setup! ------------\n")

with app.app_context():
    try:
        db.drop_all()
    except:
        print("No Previously SetUp Database Found!\n")

    print("----------------- Creating Database ----------------------------\n")
    db.create_all()
    print("----------------- Database Created! ----------------------------\n")

    print("----------------- Adding some data ----------------------------\n")
    main_user = User(username="admin",email_address="admin11@gmail.com",password="12345678",role="admin")
    user1 = User(username="influence11",email_address="influence11@gmail.com",password="12345678",role="influencer")
    user2 = User(username="sponsor11",email_address="sponsor11@gmail.com",password="12345678",role="sponsor")

    cat1 = Category(title="Fashion", niches = [
        Niche(title="Sustainable Fashion"),
        Niche(title="Men's Fashion"),
        Niche(title="Women's Fashion"),
        Niche(title="Kids Fashion"),
        Niche(title="Plus Size Fashion"),
        Niche(title="Enthic Wear"),
        Niche(title="Western Wear")
    ])
    cat2 = Category(title="Lifestyle",niches = [
        Niche(title="Home Decor"),
        Niche(title="Furniture"),
        Niche(title="Blogging"),
        Niche(title="Minimalism")
    ])
    cat3 = Category(title="Travel",niches =[
        Niche(title="Travel Gear"),
        Niche(title="Travel Luggage"),
        Niche(title="Accomodations"),
        Niche(title="Adventure Sports"),
    ])
    cat4 = Category(title="Beauty",niches = [
        Niche(title="Makeup Products"),
        Niche(title="Skin Care Products"),
        Niche(title="Hair Care Products"),
        Niche(title="Men's Grooming"),
        Niche(title="Natural Beauty"),
    ])
    cat5 = Category(title="Food",niches=[
        Niche(title="Healthy Eating"),
        Niche(title="Baking and Desserts"),
        Niche(title="International Cuisine"),
        Niche(title="Vegan Eating"),
        Niche(title="Low Budget Foods")
    ])
    cat6 = Category(title="Fitness",niches=[
        Niche(title="Gym Gear"),
        Niche(title="Home Equipments"),
        Niche(title="Supplements"),
        Niche(title="Yoga Gear"),
    ])
    cat7 = Category(title="Gaming",niches=[
        Niche(title="PC Builds"),
        Niche(title="GPU's"),
        Niche(title="Accessories"),
        Niche(title="Desk decor"),
    ])
    cat8 = Category(title="Tech",niches=[
        Niche(title="Monitors"),
        Niche(title="Laptops"),
        Niche(title="Headphones"),
        Niche(title="Speakers"),
        Niche(title="Printers"),
        Niche(title="Smartphones"),
        Niche(title="Tablets"),
        Niche(title="Cable Management"),
        Niche(title="Cleaning kits"),
        Niche(title="TV's")
    ])
    cat9 = Category(title="Electricals",niches=[
        Niche(title="Refrigirator"),
        Niche(title="Air Conditioners"),
        Niche(title="Fans and Lights"),
        Niche(title="Daily Appliances")
    ])
    cat10 = Category(title="Finance",niches=[
        Niche(title="Investing"),
        Niche(title="Crypto Currency"),
    ])
    cat11 = Category(title="Pets",niches=[
        Niche(title="Pets grooming"),
        Niche(title="Pet Food"),
    ])

    db.session.add_all([main_user,user1,user2,cat1,cat2,cat3,cat4,cat5,cat6,cat7,cat8,cat9,cat10,cat11])
    db.session.commit()
    print("----------------- Entries Added! ----------------------------\n")

print("----------------- Procedure completed! ----------------------\n\n")