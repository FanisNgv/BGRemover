from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.transaction import Transaction, TransactionType
from app.api.auth import get_current_user
from pydantic import BaseModel

router = APIRouter(
    prefix="/user",
    tags=["user"]
)

class CreditsAdd(BaseModel):
    amount: int

@router.post("/add_credits")
async def add_credits(
    credits_data: CreditsAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Добавляет указанное количество кредитов пользователю и создает запись о транзакции
    """
    if credits_data.amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Количество кредитов должно быть положительным числом"
        )
    
    # Обновляем баланс пользователя
    current_user.credits = (current_user.credits or 0) + credits_data.amount
    
    # Создаем запись о транзакции
    transaction = Transaction(
        user_id=current_user.id,
        type=TransactionType.CREDIT_ADD,
        amount=credits_data.amount,
        balance_after=current_user.credits
    )
    
    db.add(transaction)
    db.commit()
    
    return {
        "status": "success",
        "message": f"Добавлено {credits_data.amount} кредитов",
        "current_credits": current_user.credits,
        "transaction_id": str(transaction.id)
    }

@router.get("/transactions")
async def get_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получает историю транзакций текущего пользователя
    """
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).order_by(Transaction.created_at.desc()).all()
    
    return transactions
