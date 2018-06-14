# coding: UTF-8
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
from db_setup import Base, Location


engine = create_engine('mysql+mysqlconnector://root@localhost/uhcameldb')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
 
DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# location1 = Location(name="חוף השקט", altitude="32.8320354", longitude = "34.9879683")
# session.add(location1)
# session.commit()

location2 = Location(name = "aaa", altitude = "32.8320354", longitude = "34.9879683")
session.add(location2)
session.commit()
