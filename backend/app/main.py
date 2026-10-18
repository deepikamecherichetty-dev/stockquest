from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import models
from app.database import Base, engine, get_db
from app.routers import auth, stocks, trades
from app.seed import seed_stocks

Base.metadata.create_all(bind=engine)
seed_stocks()

app = FastAPI(title="StockQuest API")
app.include_router(auth.router)
app.include_router(stocks.router)
app.include_router(trades.router)

@app.get("/")
def home():
    return {"message": "StockQuest API is running"}


@app.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"database": "connected"}