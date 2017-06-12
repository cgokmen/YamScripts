from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime, Float
from models import Base, Account
from sqlalchemy.orm import relationship
from datetime import datetime

# STOCK EXCHANGE
class Company(Base):
    __tablename__ = 'companies'

    code = Column(String(4), primary_key=True)
    name = Column(Text, nullable=False)
    submission_id = Column(Text, nullable=False)

    value_points = relationship('ValuePoint', back_populates="company", cascade="all, delete, delete-orphan")
    owned_stocks = relationship('Stock', back_populates="company", cascade="all, delete, delete-orphan")

    def __repr__(self):
        return '<Company %r (%r)>' % (self.name, self.code)

class ValuePoint(Base):
    __tablename__ = 'valuepoints'

    id = Column(Integer, primary_key=True)
    datetime = Column(DateTime, nullable=False, default=datetime.utcnow)
    value = Column(Float, nullable=False)

    company_code = Column(String(4), ForeignKey('companies.code'), nullable=False)
    company = relationship(Company, back_populates="value_points")

    def __repr__(self):
        return '<Value of %r at %r: $%.2f>' % (self.company.name, self.datetime, self.value)

class Stock(Base):
    __tablename__ = 'stocks'

    id = Column(Integer, primary_key=True)
    count = Column(Integer, nullable=False)
    value_per_stock_at_purchase = Column(Float, nullable=False)

    owner_number = Column(Integer, ForeignKey('accounts.number'), nullable=False)
    owner = relationship(Account, back_populates="owned_stocks")

    company_code = Column(String(4), ForeignKey('companies.code'), nullable=False)
    company = relationship(Company, back_populates="owned_stocks")

Account.owned_stocks = relationship('Stock', back_populates="owner", cascade="all, delete, delete-orphan")