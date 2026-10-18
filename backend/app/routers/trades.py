from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(tags=["trading"])

CENT = Decimal("0.01")


def _locked_user(db: Session, user_id: int) -> models.User:
    # row lock: two trades at the same moment can't overspend the wallet
    return (
        db.query(models.User)
        .filter(models.User.id == user_id)
        .with_for_update()
        .one()
    )


@router.post("/trade/buy")
def buy(
    req: schemas.TradeRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    stock = db.get(models.Stock, req.stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    user = _locked_user(db, current_user.id)
    price = Decimal(stock.current_price)
    cost = price * req.quantity
    if user.cash_balance < cost:
        raise HTTPException(status_code=400, detail="Insufficient cash balance")

    user.cash_balance -= cost

    holding = (
        db.query(models.Holding)
        .filter_by(user_id=user.id, stock_id=stock.id)
        .first()
    )
    if holding:
        total_qty = holding.quantity + req.quantity
        holding.avg_price = (
            (holding.avg_price * holding.quantity + cost) / total_qty
        ).quantize(CENT)
        holding.quantity = total_qty
    else:
        db.add(models.Holding(
            user_id=user.id, stock_id=stock.id,
            quantity=req.quantity, avg_price=price,
        ))

    db.add(models.Trade(
        user_id=user.id, stock_id=stock.id, side="BUY",
        quantity=req.quantity, price=price, realized_pnl=0,
    ))
    db.commit()
    return {
        "message": f"Bought {req.quantity} x {stock.symbol} at {price}",
        "cash_balance": float(user.cash_balance),
    }


@router.post("/trade/sell")
def sell(
    req: schemas.TradeRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    stock = db.get(models.Stock, req.stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    user = _locked_user(db, current_user.id)
    holding = (
        db.query(models.Holding)
        .filter_by(user_id=user.id, stock_id=stock.id)
        .first()
    )
    if not holding or holding.quantity < req.quantity:
        raise HTTPException(status_code=400, detail="Not enough shares to sell")

    price = Decimal(stock.current_price)
    pnl = ((price - holding.avg_price) * req.quantity).quantize(CENT)
    user.cash_balance += price * req.quantity

    holding.quantity -= req.quantity
    if holding.quantity == 0:
        db.delete(holding)

    db.add(models.Trade(
        user_id=user.id, stock_id=stock.id, side="SELL",
        quantity=req.quantity, price=price, realized_pnl=pnl,
    ))
    db.commit()
    return {
        "message": f"Sold {req.quantity} x {stock.symbol} at {price}",
        "realized_pnl": float(pnl),
        "cash_balance": float(user.cash_balance),
    }


@router.get("/portfolio")
def portfolio(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    rows = (
        db.query(models.Holding, models.Stock)
        .join(models.Stock, models.Stock.id == models.Holding.stock_id)
        .filter(models.Holding.user_id == current_user.id)
        .all()
    )

    positions = []
    holdings_value = Decimal(0)
    for h, s in rows:
        price = Decimal(s.current_price)
        value = price * h.quantity
        holdings_value += value
        positions.append({
            "stock_id": s.id,
            "symbol": s.symbol,
            "quantity": h.quantity,
            "avg_price": float(h.avg_price),
            "current_price": float(price),
            "value": float(value),
            "unrealized_pnl": float((price - h.avg_price) * h.quantity),
        })

    cash = Decimal(current_user.cash_balance)
    return {
        "cash_balance": float(cash),
        "holdings_value": float(holdings_value),
        "total_value": float(cash + holdings_value),
        "positions": positions,
    }