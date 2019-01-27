from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from DB import Brand, Base, ProdactName, User

# connect with DB

engine = create_engine('sqlite:///brand.db?check_same_thread=False')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create User
user1 = User(name="admin", email="topics.of.computer@gmail.com")
session.add(user1)
session.commit()
# create random brand  1
brand1 = Brand(name=" Brand1", user_id="1")
session.add(brand1)
session.commit()

# Create prodact names for funny brand
prodactName1 = ProdactName(
    name=" forever primer",
    description="STEP1 Skin Equalizer triples the power of your foundation: easier application, optimized makeup result, improved wear.",
    price="10",
    brand=brand1,
    user_id="1")
session.add(prodactName1)
session.commit()

prodactName2 = ProdactName(
    name="BABY LIPS  COLOR BALM CRAYON",
    description="Baby Lips Color Balm Crayon delivers easy application for bold bursts of bright, juicy color. ",
    price="15",
    brand=brand1,
    user_id="1")
session.add(prodactName2)
session.commit()

# create  brand  2

# create random brand
brand1 = Brand(name=" Brand  2", user_id="2")
session.add(brand1)
session.commit()

# Create prodact names for funny brand
prodactName1 = ProdactName(
    name="ULTRA HD CONCEALER",
    description="the first* self-setting concealer that instantly and lastingly brightens the eye contour by capturing light: from every possible angle the eye area appears flawless and luminous....",
    price="10",
    brand=brand1,
    user_id="2")
session.add(prodactName1)
session.commit()

prodactName2 = ProdactName(
    name="GUERLAIN",
    description="A travel version of the legendary pearls to color-correct, mattify, and delicately brighten the complexion.",
    price="7",
    brand=brand1,
    user_id="2")
session.add(prodactName2)
session.commit()

print "test prodact names is added!"
