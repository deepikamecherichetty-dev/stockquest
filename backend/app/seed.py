from app.database import SessionLocal
from app import models

STOCKS = [
    ("RELIANCE", "Reliance Industries", 2900.00),
    ("TCS", "Tata Consultancy Services", 3900.00),
    ("INFY", "Infosys", 1500.00),
    ("HDFCBANK", "HDFC Bank", 1650.00),
    ("ICICIBANK", "ICICI Bank", 1200.00),
    ("SBIN", "State Bank of India", 800.00),
    ("ITC", "ITC Limited", 430.00),
    ("WIPRO", "Wipro", 480.00),
    ("LT", "Larsen & Toubro", 3500.00),
    ("BHARTIARTL", "Bharti Airtel", 1500.00),
]


def seed_stocks():
    db = SessionLocal()
    try:
        for symbol, name, price in STOCKS:
            exists = db.query(models.Stock).filter(models.Stock.symbol == symbol).first()
            if not exists:
                db.add(models.Stock(symbol=symbol, name=name, current_price=price))
        db.commit()
    finally:
        db.close()