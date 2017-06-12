# -*- coding: utf-8 -*-
from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime, Float
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Account(Base):
    __tablename__ = 'accounts'

    number = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(20), unique=True, nullable=True)
    bank_in_cents = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)

    owner_flair_text = Column(Text, nullable=True)
    owner_flair_css = Column(Text, nullable=True)
    owner_flair_expiration = Column(DateTime, nullable=True)

    deposited_posts = relationship('Post', back_populates="owner")

    def __repr__(self):
        return '<Account %r ($%.2f in bank)>' % (self.number, self.bank_in_cents / float(100))

class Post(Base):
    __tablename__ = 'posts'

    id = Column(String(20), primary_key=True, autoincrement=False)
    owner_number = Column(Integer, ForeignKey('accounts.number'), nullable=True)
    owner = relationship(Account, back_populates="deposited_posts")

#import yamsdaq_models

if __name__ == "__main__":
    engine = create_engine('sqlite:///yamecon.db')
    Base.metadata.create_all(engine)