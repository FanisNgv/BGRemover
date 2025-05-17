from fastapi import APIRouter, UploadFile, File
from fastapi.responses import Response
import torch
import numpy as np
from torchvision import transforms
from torchvision.models.segmentation import deeplabv3_resnet101
from PIL import Image
import io
import gc

router = APIRouter(prefix="/api/background", tags=["background"])

# Максимальный размер стороны изображения
MAX_IMAGE_SIZE = 1920

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"PyTorch Version: {torch.__version__}")
print(f"CUDA Available: {torch.cuda.is_available()}")
print(f"Using device: {device}")
if torch.cuda.is_available():
    print(f"CUDA Version: {torch.version.cuda}")
    print(f"Current GPU: {torch.cuda.get_device_name()}")
    print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
    # Включаем оптимизации CUDA
    torch.backends.cudnn.benchmark = True
    torch.backends.cudnn.enabled = True

model = deeplabv3_resnet101(weights=None, weights_backbone=None)
weights_path = "background_removal/models/deeplabv3_resnet101.pth"
state_dict = torch.load(weights_path, map_location=device)
model.load_state_dict(state_dict, strict=False)
model.to(device)
model.eval()

# Константы для нормализации
IMAGENET_MEAN = torch.tensor([0.485, 0.456, 0.406]).view(-1, 1, 1)
IMAGENET_STD = torch.tensor([0.229, 0.224, 0.225]).view(-1, 1, 1)

# Предобработка изображения
preprocess = transforms.Compose([
    transforms.ToTensor(),
])

def resize_if_needed(image: Image.Image) -> tuple[Image.Image, tuple[int, int], bool]:
    """
    Масштабирует изображение, если оно слишком большое
    Возвращает: (масштабированное изображение, оригинальный размер, было ли масштабирование)
    """
    original_size = image.size
    w, h = original_size
    was_resized = False
    
    # Проверяем, нужно ли масштабировать
    if max(w, h) > MAX_IMAGE_SIZE:
        # Вычисляем новый размер, сохраняя пропорции
        ratio = MAX_IMAGE_SIZE / max(w, h)
        new_size = (int(w * ratio), int(h * ratio))
        image = image.resize(new_size, Image.Resampling.LANCZOS)
        was_resized = True
        print(f"Resized image from {original_size} to {new_size}")
    
    return image, original_size, was_resized

@torch.cuda.amp.autocast()
async def remove_background(file: UploadFile) -> bytes:
    """
    Удаляет фон с изображения и возвращает результат в виде байтов
    """
    try:
        # Чтение изображения
        contents = await file.read()
        input_image = Image.open(io.BytesIO(contents)).convert("RGB")
        
        # Масштабируем изображение если нужно
        input_image, original_size, was_resized = resize_if_needed(input_image)
        
        # Предобработка
        input_tensor = preprocess(input_image)
        
        # Нормализация
        input_tensor = ((input_tensor.to(device) - IMAGENET_MEAN.to(device)) / IMAGENET_STD.to(device)).unsqueeze(0)
        
        # Сегментация
        with torch.no_grad():
            output = model(input_tensor)["out"][0]
            predicted_mask = output.argmax(0)  # [H, W]
            
            # Создаем маску на GPU
            foreground_mask = (predicted_mask != 0).to(torch.float32)  # [H, W]
            
            # Получаем оригинальное изображение как тензор на GPU
            original_tensor = preprocess(input_image).to(device)  # [3, H, W]
            
            # Применяем маску
            foreground_mask = foreground_mask.unsqueeze(0).expand_as(original_tensor)  # [3, H, W]
            result = original_tensor * foreground_mask
            
            # Переносим на CPU и конвертируем в numpy
            result_np = (result.cpu().numpy() * 255).astype(np.uint8)
            mask_np = foreground_mask[0].cpu().numpy().astype(np.uint8)
            
            # Очищаем память GPU
            del input_tensor, output, predicted_mask, foreground_mask, original_tensor, result
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()
            
            # Создаем RGBA изображение
            result_image = Image.fromarray(result_np.transpose(1, 2, 0))
            result_rgba = Image.new("RGBA", result_image.size)
            result_rgba.paste(result_image)
            
            # Создаем и применяем альфа-канал
            alpha = Image.fromarray((mask_np * 255).astype(np.uint8), 'L')
            result_rgba.putalpha(alpha)
            
            # Возвращаем к оригинальному размеру если было масштабирование
            if was_resized:
                result_rgba = result_rgba.resize(original_size, Image.Resampling.LANCZOS)
            
            # Сохранение в буфер
            img_byte_arr = io.BytesIO()
            result_rgba.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            
            return img_byte_arr.getvalue()
            
    except Exception as e:
        print(f"Error in remove_background: {str(e)}")
        raise Exception(str(e)) 