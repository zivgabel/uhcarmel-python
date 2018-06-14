import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context
import random, string
from itsdangerous import(TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

Base  = declarative_base();
secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))



class City(Base):
    __tablename__ = 'city'
    id = Column(Integer, primary_key = True)
    name =Column(String(250), nullable = False)
    
class User(Base):
    __tablename__ = 'user'
    __table_args__ = {'mysql_engine':'InnoDB', 'mysql_charset':'utf8'}
    
    
    id = Column(Integer, primary_key = True)
    username = Column(String(10), nullable=False)
    password_hash = Column(String(100), nullable=False)
    first_name =Column(String(50), nullable = False)
    last_name =Column(String(50), nullable = False)
    
    def hash_password(self,password):
        self.password_hash = pwd_context.encrypt(password)
    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(secret_key, expires_in = expiration)
        return s.dumps({'id': self.id })
    
    @staticmethod
    def verify_auth_token(token):
        print secret_key
        s = Serializer(secret_key)
        try:
            data = s.loads(token)
        except SignatureExpired:
            print 'Valid Token, but expired'
            return None
        except BadSignature:
            print 'Invalid Token'
            return None
        user_id = data['id']
        return user_id
    
class Location(Base):
    __tablename__ = 'location'

    id = Column(Integer, primary_key = True)
    name =Column(String(250), nullable = False)
    altitude = Column(String(250), nullable = False)
    longitude = Column(String(250), nullable = False)
    
    @property
    def serialize(self):
        return {
           'id' : self.id,
           'name' : self.name,
           'altitude' : self.altitude,
           'longitude' : self.longitude
        }
    
    

engine = create_engine('mysql+mysqlconnector://root@localhost/uhcameldb?charset=utf8')
Base.metadata.create_all(engine)