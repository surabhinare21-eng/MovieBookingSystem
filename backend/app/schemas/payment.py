from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


# Base schema: shared payment fields
class PaymentBase(BaseModel):
    final_amount: Decimal = Field(
        ...,
        gt=0,
        max_digits=10,
        decimal_places=2,
    )

    payment_type: str = Field(
        ...,
        min_length=1,
        max_length=50,
    )


# Schema for creating a payment
class PaymentCreate(PaymentBase):
    booking_id: int = Field(..., gt=0)


# Schema for updating payment status
class PaymentUpdate(BaseModel):
    payment_status: PaymentStatus


# Schema for returning payment details
class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    payment_id: int
    booking_id: int
    final_amount: Decimal
    payment_type: str
    payment_status: PaymentStatus
    transaction_reference: str | None = None
    paid_at: datetime | None = None
    created_at: datetime