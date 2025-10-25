from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base
import datetime

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    balance = Column(Float, default=0.0)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer)
    amount = Column(Float)
    type = Column(String)  # "credit" or "debit"
    date = Column(DateTime, default=datetime.datetime.utcnow)

class Loan(Base):
    __tablename__ = "loans"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer)
    amount = Column(Float)
    status = Column(String)  # "approved", "pending", "rejected"
