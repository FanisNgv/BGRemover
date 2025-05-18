import requests
from typing import Dict, Any
from frontend.config import API_URL, REQUEST_TIMEOUT
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def make_request(
    method: str,
    endpoint: str,
    data: Dict[str, Any] = None,
    params: Dict[str, Any] = None,
    headers: Dict[str, Any] = None,
    files: Dict[str, Any] = None
) -> requests.Response:
    """
    Общая функция для выполнения HTTP-запросов к API
    """
    url = f"{API_URL}{endpoint}"
    logger.info(f"Making {method} request to {url}")
    
    # Добавляем заголовок для работы с JSON если нет файлов
    if headers is None:
        headers = {}
    if files is None and "Content-Type" not in headers:
        headers["Content-Type"] = "application/json"
    
    try:
        logger.info(f"Request data: {data}")
        response = requests.request(
            method=method,
            url=url,
            json=data if files is None and headers.get("Content-Type") == "application/json" else None,
            data=data if files is None and headers.get("Content-Type") != "application/json" else None,
            params=params,
            headers=headers,
            files=files,
            timeout=REQUEST_TIMEOUT,
            cookies=requests.cookies.RequestsCookieJar()
        )
        logger.info(f"Response status: {response.status_code}")
        
        # Пытаемся получить данные ответа
        try:
            response_data = response.json()
            logger.info(f"Response data: {response_data}")
        except:
            logger.info(f"Raw response: {response.text}")
            response_data = {"detail": response.text}

        # Если статус ошибки, выбрасываем исключение с данными от сервера
        if response.status_code >= 400:
            error_message = response_data.get("detail", "Unknown error occurred")
            raise Exception(error_message)
            
        return response
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error to {url}")
        raise Exception(f"Не удалось подключиться к серверу. Пожалуйста, проверьте, что сервер запущен и доступен.")
    except requests.exceptions.Timeout:
        logger.error(f"Timeout error to {url}")
        raise Exception("Превышено время ожидания ответа от сервера.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        if hasattr(e, "response") and e.response is not None:
            try:
                error_detail = e.response.json().get("detail", str(e))
                logger.error(f"API Error detail: {error_detail}")
                raise Exception(error_detail)
            except:
                pass
        raise Exception(str(e))
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        raise Exception(str(e))

def register_user(email: str, password: str) -> Dict[str, Any]:
    """
    Регистрация нового пользователя
    """
    data = {
        "email": email,
        "password": password
    }
    response = make_request("POST", "/auth/register", data=data)
    return response.json()

def login_user(email: str, password: str) -> Dict[str, Any]:
    """
    Аутентификация пользователя
    """
    data = {
        "email": email,
        "password": password
    }
    response = make_request("POST", "/auth/login", data=data)
    return response.json()

def get_user_info(token_type: str, access_token: str) -> Dict[str, Any]:
    """
    Получение информации о пользователе
    """
    headers = {"Authorization": f"{token_type} {access_token}"}
    response = make_request("GET", "/auth/me", headers=headers)
    return response.json()

def get_user_transactions(token_type: str, access_token: str) -> Dict[str, Any]:
    headers = {"Authorization": f"{token_type} {access_token}"}
    response = make_request("GET", "/user/transactions", headers=headers)
    return response.json()

def add_credits(token_type: str, access_token: str, amount: int) -> Dict[str, Any]:
    """
    Пополнение баланса пользователя
    """
    headers = {"Authorization": f"{token_type} {access_token}"}
    data = {"amount": amount}
    response = make_request("POST", "/user/add_credits", data=data, headers=headers)
    return response.json()

def remove_background(token_type: str, access_token: str, file: bytes, model: str) -> Dict[str, Any]:
    headers = {"Authorization": f"{token_type} {access_token}"}
    files = {"file": file}
    response = make_request("POST", f"/ml/remove_background/{model}", files=files, headers=headers)
    return response.json() 