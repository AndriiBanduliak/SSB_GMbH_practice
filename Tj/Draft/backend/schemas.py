from pydantic import BaseModel

class User(BaseModel):
    id: int
    username: str
    class Config:
        from_attributes = True

class APIKeyCreate(BaseModel):
    exchange: str
    api_key: str
    secret_key: str

class APIKey(BaseModel):
    id: int
    exchange: str
    api_key: str
    secret_key: str
    user_id: int
    class Config:
        from_attributes = True

class BalanceCreate(BaseModel):
    user_id: int
    exchange: str
    balance: str

class Balance(BaseModel):
    id: int
    user_id: int
    exchange: str
    balance: str
    class Config:
        from_attributes = True

class DealCreate(BaseModel):
    full_name: str
    password: str
    api_key: str
    platform: str
    crypto_currency: str
    quantity_bought: float
    quantity_sold: float
    exchange_rate: float

class Deal(BaseModel):
    id: int
    full_name: str
    password: str
    api_key: str
    platform: str
    crypto_currency: str
    quantity_bought: float
    quantity_sold: float
    exchange_rate: float
    profit: float
    class Config:
        from_attributes = True
