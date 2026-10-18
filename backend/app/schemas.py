from pydantic import BaseModel, EmailStr, ConfigDict, Field


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class StockOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    symbol: str
    name: str
    current_price: float


class TradeRequest(BaseModel):
    stock_id: int
    quantity: int = Field(gt=0)