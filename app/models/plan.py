from typing import Optional, List
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, JSON

class Plan(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(unique=True, index=True) # Ej: 'TRIAL', 'MONTHLY', 'ANNUAL'
    name: str
    description: str
    price: float
    duration_days: int # 7, 30, 365
    
    is_trial: bool = False
    is_active: bool = True
    
    # Guardamos la lista de características como un JSON array en Postgres
    features: List[str] = Field(default=[], sa_column=Column(JSON))
    
    display_order: int = 0