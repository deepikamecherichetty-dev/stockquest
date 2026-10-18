from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Numeric, DateTime, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    cash_balance = Column(Numeric(14, 2), nullable=False, default=100000)
    created_at = Column(DateTime, default=datetime.utcnow)

    trades = relationship("Trade", back_populates="user")
    holdings = relationship("Holding", back_populates="user")


class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(120), nullable=False)
    current_price = Column(Numeric(12, 2), nullable=False)


class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    side = Column(String(4), nullable=False)  # "BUY" or "SELL"
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(12, 2), nullable=False)
    realized_pnl = Column(Numeric(12, 2), nullable=False, default=0)  # profit on SELL
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="trades")
    stock = relationship("Stock")


class Holding(Base):
    __tablename__ = "holdings"
    __table_args__ = (UniqueConstraint("user_id", "stock_id"),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    avg_price = Column(Numeric(12, 2), nullable=False, default=0)

    user = relationship("User", back_populates="holdings")
    stock = relationship("Stock")