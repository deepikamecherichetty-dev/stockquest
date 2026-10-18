import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import models, market
from app.database import Base, engine, get_db
from app.routers import auth, stocks, trades
from app.routers import market as market_router
from app.seed import seed_stocks

Base.metadata.create_all(bind=engine)
seed_stocks()


@asynccontextmanager
async def lifespan(app: FastAPI):
    market.ensure_baseline()
    task = asyncio.create_task(market.market_loop())
    yield
    task.cancel()


app = FastAPI(title="StockQuest API", lifespan=lifespan)
app.include_router(auth.router)
app.include_router(stocks.router)
app.include_router(trades.router)
app.include_router(market_router.router)


@app.get("/")
def home():
    return {"message": "StockQuest API is running"}


@app.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"database": "connected"}