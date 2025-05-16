import time
import streamlit as st
import io
import base64
import logging
import random
from frontend.utils.api import get_user_info, add_credits, remove_background
from datetime import datetime, timedelta
from streamlit_local_storage import LocalStorage


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

local_storage = LocalStorage()


st.set_page_config(page_title="Личный кабинет", layout="wide")

if 'game_active' not in st.session_state:
    st.session_state.game_active = False
if 'target_number' not in st.session_state:
    st.session_state.target_number = random.randint(1, 10)
if 'game_attempts' not in st.session_state:
    st.session_state.game_attempts = 0
if 'game_message' not in st.session_state:
    st.session_state.game_message = "Угадайте число от 1 до 10"

def init_game_state():
    """Инициализация состояния игры"""
    st.session_state.update({
        "target_number": random.randint(1, 10),
        "game_attempts": 0,
        "game_message": "Угадайте число от 1 до 10",
        "game_active": True
    })

def logout_user():
    st.session_state.clear()
    
    local_storage.deleteAll(key="logout_cleanup")
    time.sleep(2)
    
    st.switch_page("pages/1_Login.py")

def play_number_game():
    """Игра для пополнения баланса"""
    st.write("### Пополнение баланса")
    st.write(st.session_state.game_message)

    with st.form("number_guess_form"):
        number = st.number_input("Введите число", min_value=1, max_value=10, step=1)
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("Проверить")
        with col2:
            if st.form_submit_button("Закрыть"):
                st.session_state.game_active = False
                st.rerun()

        if submit:
            st.session_state.game_attempts += 1
            if number == st.session_state.target_number:
                st.session_state.game_message = "Поздравляем! Вы угадали число!"
                st.session_state.game_active = False
                try:
                    result = add_credits(
                        st.session_state.token_type,
                        st.session_state.access_token,
                        100
                    )
                    st.session_state.credits = result["current_credits"]
                    st.success("Баланс пополнен на 100 кредитов!")
                    time.sleep(2)
                    st.rerun()
                except Exception as e:
                    st.error(f"Ошибка при пополнении баланса: {str(e)}")
            else:
                direction = "больше" if number < st.session_state.target_number else "меньше"
                st.session_state.game_message = f"Загаданное число {direction}!"
                st.rerun()

def show_user_dashboard():
    """Отображение основной информации пользователя"""
    st.title("Личный кабинет")
    
    try:
        user_data = get_user_info(st.session_state.token_type, st.session_state.access_token)
        
        # Обновляем данные сессии
        st.session_state.update({
            "user_id": user_data["id"],
            "user_email": user_data["email"],
            "credits": user_data["credits"],
            "logged_in": True
        })

        # Информация о пользователе
        with st.container():
            st.subheader("Информация о пользователе")
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**Email:** {user_data['email']}")
                st.write(f"**Баланс:** {st.session_state.credits} кредитов")
            with col2:
                if st.button("Выйти", type="primary", use_container_width=True):
                    logout_user()

        st.markdown("---")
        if st.button("Пополнить баланс"):
            init_game_state()

        if st.session_state.game_active:
            play_number_game()

        # Основной функционал
        st.markdown("---")
        st.subheader("Удаление фона")
        
        model_choice = st.radio(
            "Выберите модель:",
            ["Модель 1 (10 кредитов)", "Модель 2 (50 кредитов)", "Модель 3 (100 кредитов)"],
            horizontal=True
        )

        model_mapping = {
            "Модель 1 (10 кредитов)": "model1",
            "Модель 2 (50 кредитов)": "model2",
            "Модель 3 (100 кредитов)": "model3"
        }

        uploaded_file = st.file_uploader("Загрузите изображение", type=["jpg", "jpeg", "png"])

        if uploaded_file is not None:
            col1, col2 = st.columns(2)
            with col1:
                st.image(uploaded_file, caption="Исходное изображение")
            with col2:
                if st.button("Удалить фон", type="primary"):
                    with st.spinner("Обработка изображения..."):
                        try:
                            result = remove_background(
                                st.session_state.token_type,
                                st.session_state.access_token,
                                uploaded_file.getvalue(),
                                model_mapping[model_choice]
                            )

                            image_bytes = base64.b64decode(result["image"])
                            result_img = io.BytesIO(image_bytes)
                            
                            st.image(result_img, caption="Результат")
                            st.download_button(
                                "Скачать результат",
                                data=result_img,
                                file_name="no_bg.png",
                                mime="image/png"
                            )
                            st.session_state.credits = result["remaining_credits"]
                            st.success(f"Готово! Осталось кредитов: {st.session_state.credits}")
                        except Exception as e:
                            st.error(f"Ошибка: {str(e)}")

    except Exception as e:
        st.error(f"Ошибка при загрузке данных: {str(e)}")
        time.sleep(2)
        logout_user()

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

def main():
    if not check_auth():
        st.warning("Требуется авторизация")
        time.sleep(1)
        st.switch_page("pages/1_Login.py")
    
    show_user_dashboard()

if __name__ == "__main__":
    main()