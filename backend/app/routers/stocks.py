from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.get("", response_model=List[schemas.StockOut])
def list_stocks(db: Session = Depends(get_db)):
    return db.query(models.Stock).order_by(models.Stock.symbol).all()


@router.get("/{symbol}", response_model=schemas.StockOut)
def get_stock(symbol: str, db: Session = Depends(get_db)):
    stock = db.query(models.Stock).filter(models.Stock.symbol == symbol.upper()).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock