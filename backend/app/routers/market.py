from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import models, market
from app.database import get_db

router = APIRouter(prefix="/market", tags=["market"])


@router.get("/history/{stock_id}")
def price_history(
    stock_id: int,
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(models.PriceHistory)
        .filter(models.PriceHistory.stock_id == stock_id)
        .order_by(models.PriceHistory.created_at.desc())
        .limit(limit)
        .all()
    )
    return [{"price": float(r.price), "time": r.created_at} for r in reversed(rows)]


@router.post("/tick")
def force_tick():
    """Dev helper: run one market tick now. Remove before deploying."""
    market.tick()
    return {"message": "tick done"}