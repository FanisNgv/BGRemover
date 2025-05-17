from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse
import base64
from app.api.auth import get_current_user
from app.models.user import User
from app.api.background_removal import remove_background as remove_bg
from app.core.database import get_db
from sqlalchemy.orm import Session
import io

router = APIRouter(prefix="/ml", tags=["ml"])

MODEL_PRICES = {
    "model1": 10,
    "model2": 50,
    "model3": 100
}

@router.post("/remove_background/{model}")
async def remove_background(
    model: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Удаление фона с изображения с использованием выбранной модели
    """
    if model not in MODEL_PRICES:
        raise HTTPException(status_code=400, detail="Неверная модель")
    
    price = MODEL_PRICES[model]
    if current_user.credits < price:
        raise HTTPException(status_code=400, detail="Недостаточно кредитов")
    
    try:
        # Обработка изображения
        result_bytes = await remove_bg(file)
        
        # Конвертация результата в base64
        base64_image = base64.b64encode(result_bytes).decode('utf-8')
        
        # Списание кредитов
        db_user = db.query(User).filter(User.id == current_user.id).first()
        db_user.credits -= price
        db.add(db_user)
        db.commit()
        
        return JSONResponse({
            "image": base64_image,
            "remaining_credits": db_user.credits
        })
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e)) 