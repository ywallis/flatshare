from fastapi import APIRouter, Depends
from sqlmodel import Session

from src.models import (
    Transaction,
    TransactionCreate,
    TransactionPublicWithUsers,
)
from src.utils import get_session

router = APIRouter()

@router.post("/transactions/", response_model=TransactionPublicWithUsers)
def add_transaction(
    *, session: Session = Depends(get_session), transaction: TransactionCreate
):
    db_transaction = Transaction.model_validate(transaction)
    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)
    return db_transaction
