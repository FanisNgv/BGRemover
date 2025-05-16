import streamlit as st
import requests
import time
from datetime import datetime
from frontend.utils.api import get_user_transactions
from streamlit_local_storage import LocalStorage

local_storage = LocalStorage()

st.set_page_config(
    page_title="История транзакций - Remooovy",
    layout="wide"
)

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

if not check_auth():
    st.warning("Пожалуйста, войдите в систему")
    st.stop()

st.title("История транзакций 💰")

try:
    transactions = get_user_transactions(st.session_state.token_type, st.session_state.access_token)
except Exception as e:
    st.error(f"Ошибка при получении истории транзакций: {str(e)}")
    st.stop()

# Функция для форматирования типа транзакции
def format_transaction_type(type_str):
    types = {
        "credit_add": "Пополнение",
        "credit_use": "Использование",
        "credit_refund": "Возврат"
    }
    return types.get(type_str, type_str)

# Функция для форматирования даты
def format_date(date_str):
    date = datetime.fromisoformat(date_str)
    return date.strftime("%d.%m.%Y %H:%M")

# Отображение баланса
if transactions:
    current_balance = transactions[0]["balance_after"]
    st.metric("Текущий баланс", f"{current_balance} кредитов")

# Создание таблицы транзакций
if transactions:
    # Подготовка данных для таблицы
    table_data = []
    for t in transactions:
        amount_str = f"+{t['amount']}" if t['type'] == 'credit_add' else f"-{t['amount']}"
        table_data.append({
            "Дата": format_date(t["created_at"]),
            "Тип": format_transaction_type(t["type"]),
            "Сумма": amount_str,
            "Баланс после": t["balance_after"],
        })
    
    st.dataframe(
        table_data,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Дата": st.column_config.DatetimeColumn(
                "Дата",
                format="DD.MM.YYYY HH:mm"
            ),
            "Сумма": st.column_config.TextColumn(
                "Сумма",
                help="+ пополнение, - списание"
            ),
            "Баланс после": st.column_config.NumberColumn(
                "Баланс после",
                help="Баланс после проведения операции"
            )
        }
    )
else:
    st.info("У вас пока нет транзакций") 