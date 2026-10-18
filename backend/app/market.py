import asyncio
import json
import math
import random
from decimal import Decimal
from pathlib import Path

from app import models
from app.database import SessionLocal

PARAMS_FILE = Path(__file__).parent / "market_params.json"
DEFAULT_MU = 0.12      # 12% yearly drift
DEFAULT_SIGMA = 0.25   # 25% yearly volatility
TRADING_DAYS = 252
TICK_SECONDS = 10      # one tick = one simulated trading day


def load_params() -> dict:
    if PARAMS_FILE.exists():
        return json.loads(PARAMS_FILE.read_text())
    return {}


def gbm_step(price: float, mu: float, sigma: float) -> float:
    dt = 1 / TRADING_DAYS
    z = random.gauss(0, 1)
    return price * math.exp((mu - 0.5 * sigma ** 2) * dt + sigma * math.sqrt(dt) * z)


def ensure_baseline():
    """Give every stock a first history point so charts have a start."""
    db = SessionLocal()
    try:
        for stock in db.query(models.Stock).all():
            exists = db.query(models.PriceHistory.id).filter_by(stock_id=stock.id).first()
            if not exists:
                db.add(models.PriceHistory(stock_id=stock.id, price=stock.current_price))
        db.commit()
    finally:
        db.close()


def tick():
    params = load_params()
    db = SessionLocal()
    try:
        for stock in db.query(models.Stock).all():
            p = params.get(stock.symbol, {})
            mu = p.get("mu", DEFAULT_MU)
            sigma = p.get("sigma", DEFAULT_SIGMA)
            new_price = max(round(gbm_step(float(stock.current_price), mu, sigma), 2), 1.0)
            stock.current_price = Decimal(str(new_price))
            db.add(models.PriceHistory(stock_id=stock.id, price=stock.current_price))
        db.commit()
    finally:
        db.close()


async def market_loop():
    while True:
        await asyncio.sleep(TICK_SECONDS)
        try:
            await asyncio.to_thread(tick)
        except Exception as e:
            print("market tick failed:", e)