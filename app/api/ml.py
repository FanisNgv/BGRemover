from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse
import base64
from app.api.auth import get_current_user
from app.models.user import User
from app.models.transaction import Transaction, TransactionType
from app.api.background_removal import remove_background as remove_bg
from app.core.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/ml", tags=["ml"])

MODEL_PRICES = {
    "deeplabv3": 10,
    "rmbg": 50,
    "rmbg2": 100
}

@router.post("/remove_background/{model}")
async def remove_background(
    model: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    if model not in MODEL_PRICES:
        raise HTTPException(
            status_code=400, 
            detail=f"Неверная модель. Доступные модели: {', '.join(MODEL_PRICES.keys())}"
        )
    
    price = MODEL_PRICES[model]
    if current_user.credits < price:
        raise HTTPException(
            status_code=400, 
            detail=f"Недостаточно кредитов. Необходимо: {price}, доступно: {current_user.credits}"
        )
    
    try:
        result_bytes = await remove_bg(file, model)
        
        base64_image = base64.b64encode(result_bytes).decode('utf-8')
        
        current_user.credits -= price
        
        transaction = Transaction(
            user_id=current_user.id,
            type=TransactionType.CREDIT_USE,
            amount=-price,
            balance_after=current_user.credits
        )
        
        db.add(transaction)
        db.commit()
        
        return JSONResponse({
            "image": base64_image,
            "remaining_credits": current_user.credits
        })
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e)) 