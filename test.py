import streamlit as st
import requests
from xml.etree.ElementTree import *


x = "USD"
def get_rate_cbr(x):
    url = "http://www.cbr.ru/scripts/XML_daily.asp"
    try:
        response = requests.get(url)
        response.encoding = 'windows-1251'  # Важно для правильного отображения русских букв
        root = fromstring(response.text)

        for valute in root.findall('Valute'):
            if valute.find('CharCode').text == x:
                value = valute.find('Value').text
                rate = float(value.replace(',', '.'))
                return rate
        return None
    except Exception as e:
        print(f"Ошибка при получении данных: {e}")
        return None


st.title("Конвертер валют и криптовалют")

# x = st.multiselect(
#     'Какую валюту вы предпочитаете?',
#     ['USD', 'AMD', 'BYN'],
# )
# st.write('Вы выбрали:', *x)

# x = st.select_slider(
#     'Выберите валюту:',
#     options=['USD', 'AMD', 'BYN']
# )
# st.write('Вы выбрали:', x)

# x = st.radio(
#     "Выберите валюту",
#    ['USD', 'AMD', 'BYN']
# )
# st.write('Вы выбрали:', x)


def all_valutes():
    url = "http://www.cbr.ru/scripts/XML_daily.asp"
    try:
        response = requests.get(url)
        response.encoding = 'windows-1251'  # Важно для правильного отображения русских букв
        root = fromstring(response.text)

        valutes = []
        for valute in root.findall('Valute'):
            valnames = ""
            valnames += valute.find('CharCode').text
            valnames += " - "
            valnames += valute.find('Name').text
            valutes.append(valnames)
        return valutes
        
    except Exception as e:
        print(f"Ошибка при получении данных: {e}")
        return None

quanty = st.number_input("Введите количество", 1)

x = st.selectbox('Выберите валюту:', all_valutes())
st.write(f"{quanty} {x} {"  =  "} {quanty * get_rate_cbr(x[0:3]):.2f} {"RUB"}")


