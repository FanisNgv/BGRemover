import streamlit as st
import requests
from typing import Optional

def get_auth_header() -> dict:
    """
    Получает заголовок авторизации из сессии
    """
    token = st.session_state.get('access_token')
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}

def check_auth() -> bool:
    """
    Проверяет авторизацию пользователя
    """
    if 'access_token' not in st.session_state:
        return False
    
    try:
        response = requests.get(
            "http://localhost:8000/auth/me",
            headers=get_auth_header()
        )
        return response.status_code == 200
    except:
        return False

def get_current_user() -> Optional[dict]:
    """
    Получает данные текущего пользователя
    """
    if not check_auth():
        return None
    
    try:
        response = requests.get(
            "http://localhost:8000/auth/me",
            headers=get_auth_header()
        )
        if response.status_code == 200:
            return response.json()
    except:
        pass
    
    return None

def login(email: str, password: str) -> tuple[bool, str]:
    """
    Авторизует пользователя
    """
    try:
        response = requests.post(
            "http://localhost:8000/auth/login",
            json={"email": email, "password": password}
        )
        
        if response.status_code == 200:
            data = response.json()
            st.session_state['access_token'] = data['access_token']
            return True, ""
        
        return False, "Неверный email или пароль"
    except Exception as e:
        return False, f"Ошибка при авторизации: {str(e)}"

def logout():
    """
    Выход из системы
    """
    if 'access_token' in st.session_state:
        del st.session_state['access_token']
    
    try:
        requests.post("http://localhost:8000/auth/logout")
    except:
        pass 