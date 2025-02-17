from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from enum import Enum
from typing import List
from demurrage_calculator import ContainerType, ContainerSize, calculate_demurrage

app = FastAPI(title="Demurrage Calculator API")

class DemurrageRequest(BaseModel):
    container_type: ContainerType
    container_size: ContainerSize
    days: int

class ChargeBreakdown(BaseModel):
    days: int
    rate: float
    subtotal: float

class DemurrageResponse(BaseModel):
    total_charge: float
    breakdown: List[ChargeBreakdown]

@app.post("/calculate-demurrage", response_model=DemurrageResponse)
async def calculate_demurrage_charge(request: DemurrageRequest):
    if request.days < 0:
        raise HTTPException(status_code=400, detail="Days cannot be negative")
    
    total, breakdown = calculate_demurrage(
        request.container_type,
        request.container_size,
        request.days
    )
    
    charge_breakdown = [
        ChargeBreakdown(
            days=details['days'],
            rate=details['rate'],
            subtotal=details['charge']
        )
        for details in breakdown.values()
    ]
    
    return DemurrageResponse(
        total_charge=total,
        breakdown=charge_breakdown
    )

