from fastapi import APIRouter, UploadFile
import torch
import torch.nn.functional as F
import numpy as np
from torchvision import transforms
from torchvision.models.segmentation import deeplabv3_resnet101
from transformers import pipeline, AutoModelForImageSegmentation
from torchvision.transforms.functional import normalize
from PIL import Image
import io

router = APIRouter(prefix="/api/background", tags=["background"])

MAX_IMAGE_SIZE = 1920

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"PyTorch Version: {torch.__version__}")
print(f"CUDA Available: {torch.cuda.is_available()}")
print(f"Using device: {device}")
if torch.cuda.is_available():
    print(f"CUDA Version: {torch.version.cuda}")
    print(f"Current GPU: {torch.cuda.get_device_name()}")
    print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
    torch.backends.cudnn.benchmark = True
    torch.backends.cudnn.enabled = True

deeplabv3 = deeplabv3_resnet101(weights=None, weights_backbone=None)
weights_path = "background_removal/models/DeepLabV3/deeplabv3_resnet101.pth"
state_dict = torch.load(weights_path, map_location=device)
deeplabv3.load_state_dict(state_dict, strict=False)
deeplabv3.to(device)
deeplabv3.eval()

rmbg_pipeline = pipeline(
    "image-segmentation",
    model="background_removal/models/RMBG-1.4",
    device=0 if torch.cuda.is_available() else -1,
    trust_remote_code=True
)

rmbg2_model = AutoModelForImageSegmentation.from_pretrained(
    "background_removal/models/RMBG-2.0",
    trust_remote_code=True
).to(device).eval()

DEEPLABV3_MEAN = torch.tensor([0.485, 0.456, 0.406]).view(-1, 1, 1)
DEEPLABV3_STD = torch.tensor([0.229, 0.224, 0.225]).view(-1, 1, 1)

preprocess = transforms.Compose([
    transforms.ToTensor(),
])

def resize_if_needed(image: Image.Image) -> tuple[Image.Image, tuple[int, int], bool]:
    original_size = image.size
    w, h = original_size
    was_resized = False
    
    if max(w, h) > MAX_IMAGE_SIZE:
        ratio = MAX_IMAGE_SIZE / max(w, h)
        new_size = (int(w * ratio), int(h * ratio))
        image = image.resize(new_size, Image.Resampling.LANCZOS)
        was_resized = True
        print(f"Resized image from {original_size} to {new_size}")
    
    return image, original_size, was_resized

def preprocess_deeplabv3(image: Image.Image) -> torch.Tensor:
    tensor = transforms.ToTensor()(image)
    tensor = ((tensor.to(device) - DEEPLABV3_MEAN.to(device)) / DEEPLABV3_STD.to(device)).unsqueeze(0)
    return tensor

def process_deeplabv3_output(output: torch.Tensor, image: Image.Image) -> Image.Image:
    predicted_mask = output.argmax(0)
    foreground_mask = (predicted_mask != 0).to(torch.float32)
    
    original_tensor = transforms.ToTensor()(image).to(device)
    foreground_mask = foreground_mask.unsqueeze(0).expand_as(original_tensor)
    result = original_tensor * foreground_mask
    
    result_np = (result.cpu().numpy() * 255).astype(np.uint8)
    mask_np = foreground_mask[0].cpu().numpy().astype(np.uint8)
    
    result_image = Image.fromarray(result_np.transpose(1, 2, 0))
    result_rgba = Image.new("RGBA", result_image.size)
    result_rgba.paste(result_image)
    
    alpha = Image.fromarray((mask_np * 255).astype(np.uint8), 'L')
    result_rgba.putalpha(alpha)
    
    return result_rgba

def process_rmbg_image(contents: bytes) -> Image.Image:
    temp_file = io.BytesIO(contents)
    image = Image.open(temp_file).convert("RGB")
    
    result_image = rmbg_pipeline(image)
    
    if result_image.mode != "RGBA":
        result_image = result_image.convert("RGBA")
    
    return result_image

def process_rmbg2_image(contents: bytes) -> Image.Image:
    temp_file = io.BytesIO(contents)
    image = Image.open(temp_file).convert("RGB")
    original_size = image._size
    
    transform_image = transforms.Compose([
        transforms.Resize((1024, 1024)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    input_tensor = transform_image(image).unsqueeze(0).to(device)
    
    with torch.no_grad():
        output = rmbg2_model(input_tensor)

        if isinstance(output, (list, tuple)):
            output = output[-1]
        mask = output.sigmoid().cpu()
    
    mask = mask[0].squeeze(0)
    mask_pil = transforms.ToPILImage()(mask)
    mask_pil = mask_pil.resize(original_size, resample=Image.LANCZOS)
    image.putalpha(mask_pil)
    
    return image


@torch.amp.autocast('cuda' if torch.cuda.is_available() else 'cpu')
async def remove_background(file: UploadFile, model: str = "deeplabv3") -> bytes:
    try:
        contents = await file.read()
        
        if model == "deeplabv3":
            input_image = Image.open(io.BytesIO(contents)).convert("RGB")
            input_image, original_size, was_resized = resize_if_needed(input_image)
            
            with torch.no_grad():
                input_tensor = preprocess_deeplabv3(input_image)
                output = deeplabv3(input_tensor)["out"][0]
                result_rgba = process_deeplabv3_output(output, input_image)
            
            if was_resized:
                result_rgba = result_rgba.resize(original_size, Image.Resampling.LANCZOS)
            
        elif model == "rmbg":
            result_rgba = process_rmbg_image(contents)
            
        elif model == "rmbg2":
            result_rgba = process_rmbg2_image(contents)
            
        else:
            raise ValueError(f"Неизвестная модель: {model}")
        
        img_byte_arr = io.BytesIO()
        result_rgba.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        return img_byte_arr.getvalue()
            
    except Exception as e:
        print(f"Error in remove_background: {str(e)}")
        import traceback
        traceback.print_exc()
        raise Exception(str(e))

def preprocess_image(im: np.ndarray, model_input_size: list) -> torch.Tensor:
    if len(im.shape) < 3:
        im = im[:, :, np.newaxis]

    im_tensor = torch.tensor(im, dtype=torch.float32).permute(2, 0, 1)
    im_tensor = F.interpolate(im_tensor.unsqueeze(0), size=model_input_size, mode='bilinear')
    image = im_tensor / 255.0
    image = normalize(image, [0.5, 0.5, 0.5], [1.0, 1.0, 1.0])
    return image

def postprocess_image(result: torch.Tensor, im_size: list) -> np.ndarray:
    result = torch.squeeze(F.interpolate(result, size=im_size, mode='bilinear'), 0)
    probs = torch.sigmoid(result)
    mask = (probs > 0.5).to(torch.uint8) * 255
    mask_np = mask.cpu().numpy()

    if mask_np.ndim == 3:
        mask_np = mask_np[0]

    return mask_np


transform_image_rmbg2 = transforms.Compose([
    transforms.Resize((1024, 1024)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])