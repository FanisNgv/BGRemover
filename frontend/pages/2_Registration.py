import streamlit as st
from frontend.utils.api import register_user
from streamlit_local_storage import LocalStorage
import time

st.set_page_config(page_title="Регистрация")

local_storage = LocalStorage()

def registration():
    st.title("Регистрация")
    
    email = st.text_input("Email")
    password = st.text_input("Пароль", type="password")
    password_confirm = st.text_input("Подтвердите пароль", type="password")

    _, col2, _ = st.columns([1.5, 1, 1])

    with col2:
        if st.button("Зарегистрироваться"):
            if not email or not password:
                st.error("Заполните все поля!")
                return
                
            if password != password_confirm:
                st.error("Пароли не совпадают!")
                return
                
            try:
                register_user(email=email, password=password)
                st.success(f"Пользователь {email} успешно зарегистрирован!")
                st.session_state.clear()
    
                local_storage.deleteAll(key="logout_cleanup")
                time.sleep(2)
                
                st.switch_page("pages/1_Login.py")
            except Exception as e:
                st.error(f"Ошибка: {str(e)}")

registration()
