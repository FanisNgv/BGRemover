from fastapi import APIRouter, UploadFile, File
from fastapi.responses import Response
import torch
import numpy as np
from torchvision import transforms
from torchvision.models.segmentation import deeplabv3_resnet101
from PIL import Image
import io

router = APIRouter(prefix="/api/background", tags=["background"])

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

model = deeplabv3_resnet101(weights=None, weights_backbone=None)
weights_path = "background_removal/models/deeplabv3_resnet101.pth"
state_dict = torch.load(weights_path, map_location=device)
model.load_state_dict(state_dict, strict=False)
model.to(device)  # Перемещаем модель на GPU если доступно
model.eval()

# Предобработка изображения
preprocess = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                       std=[0.229, 0.224, 0.225]),
])

async def remove_background(file: UploadFile) -> bytes:
    """
    Удаляет фон с изображения и возвращает результат в виде байтов
    """
    # Чтение изображения
    contents = await file.read()
    input_image = Image.open(io.BytesIO(contents)).convert("RGB")
    
    # Предобработка
    input_tensor = preprocess(input_image).unsqueeze(0)
    input_tensor = input_tensor.to(device)  # Перемещаем тензор на GPU если доступно
    
    # Сегментация
    with torch.no_grad():
        output = model(input_tensor)["out"][0]
        predicted_mask = output.argmax(0).byte().cpu().numpy()
    
    # Создание маски и применение
    foreground_mask = (predicted_mask != 0).astype(np.uint8)
    foreground_mask_3ch = np.stack([foreground_mask]*3, axis=-1)
    input_np = np.array(input_image)
    foreground = input_np * foreground_mask_3ch
    
    # Конвертация результата в PNG с прозрачностью
    result_image = Image.fromarray(foreground)
    # Создаем новое изображение с альфа-каналом
    result_rgba = Image.new("RGBA", result_image.size)
    # Копируем RGB каналы
    result_rgba.paste(result_image)
    # Устанавливаем альфа-канал на основе маски
    alpha = Image.fromarray((foreground_mask * 255).astype(np.uint8), 'L')
    result_rgba.putalpha(alpha)
    
    # Сохранение в буфер
    img_byte_arr = io.BytesIO()
    result_rgba.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    return img_byte_arr.getvalue() 