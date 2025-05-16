import streamlit as st
from streamlit_local_storage import LocalStorage
from frontend.utils.api import login_user, get_user_info
import time

st.set_page_config(page_title="Авторизация")

local_storage = LocalStorage()

def save_auth_data(token_type, access_token):
    st.session_state.token_type = token_type
    st.session_state.access_token = access_token
    
    auth_data = {
        "token_type": token_type,
        "access_token": access_token,
        "timestamp": int(time.time())
    }
    
    local_storage.setItem("auth_data", auth_data)

def check_auth():
    if "access_token" in st.session_state:
        return True
    
    auth_data = local_storage.getItem("auth_data")
    
    if auth_data and isinstance(auth_data, dict):
        if (time.time() - auth_data.get("timestamp", 0)) < 604800:
            st.session_state.token_type = auth_data["token_type"]
            st.session_state.access_token = auth_data["access_token"]
            return True
    
    return False

def login():
    st.title("Авторизация")

    if check_auth():
        st.switch_page("pages/3_MainPage.py")
        return

    email = st.text_input("Email")
    password = st.text_input("Пароль", type="password")

    if st.button("Войти"):
        if not email or not password:
            st.error("Введите email и пароль!")
            return

        try:
            token_data = login_user(email, password)
            
            save_auth_data(token_data["token_type"], token_data["access_token"])
            
            user_data = get_user_info(
                token_data["token_type"],
                token_data["access_token"]
            )
            
            st.session_state.user_id = user_data["id"]
            st.session_state.user_email = user_data["email"]
            st.session_state.credits = user_data["credits"]
            st.session_state.logged_in = True

            st.success("Успешный вход! Перенаправляем...")
            time.sleep(1)

            st.switch_page("pages/3_MainPage.py")
        except Exception as e:
            st.error(f"Ошибка: {str(e)}")

login()