#from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from backend.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    date_of_birth = Column(Date, nullable=False) 

class APIKey(Base):
    __tablename__ = "api_keys"
    id = Column(Integer, primary_key=True, index=True)
    exchange = Column(String, index=True)
    api_key = Column(String)
    secret_key = Column(String)
    passphrase = Column(String, nullable=True)   # новое поле
    user_id = Column(Integer, ForeignKey("users.id"))


class Balance(Base):
    __tablename__ = "balances"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    exchange = Column(String, index=True)
    balance = Column(String)

class Deal(Base):
    __tablename__ = "deals"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    password = Column(String)
    api_key = Column(String)
    platform = Column(String, index=True)
    crypto_currency = Column(String, index=True)
    quantity_bought = Column(String)
    quantity_sold = Column(String)
    exchange_rate = Column(String)
    profit = Column(String)
