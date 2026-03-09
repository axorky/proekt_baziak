# импортирую библиотеки для работы
import streamlit as st      # основная библиотека для работы
import requests         # Библиотека для запросов данных
from xml.etree.ElementTree import fromstring    # библиотека для обработки xml файлов

def all_valutes():      # функция для создания списка со всеми валютами, находящихся в доступе на сайте центрального банка России
        url = "http://www.cbr.ru/scripts/XML_daily.asp"    # ссылка для обращение к xml файлу сайта ЦБР
        try:
            response = requests.get(url)
            response.encoding = 'windows-1251'     # Важно для правильного отображения русских букв
            root = fromstring(response.text)     # Проверка текста для получения данных

            valutes = []
            for valute in root.findall('Valute'):    # проверка по валютам, сбор данных в отдельный список
                valnames = ""
                valnames += valute.find('CharCode').text
                valnames += " - "
                valnames += valute.find('Name').text
                valutes.append(valnames)
            valutes.append("RUB - Россиийский рубль")    # добавляем отдельно, так как в информации не предоставлена валюта российского рубля
            return valutes    # возвращаем полный список доступных валют
            
        except Exception as e:    # в случае ошибки данных, для предотвращениия отказа работы приложения добавлена except
            print(f"Ошибка при получении данных: {e}")
            return None

def get_rate_cbr(x):    # САМАЯ ГЛАВНАЯ ФУНКЦИЯ для получения отношения валюты к рублю, от неё идет общая работа с действием: "Валюта"
    url = "http://www.cbr.ru/scripts/XML_daily.asp"
    try:
        response = requests.get(url)
        response.encoding = 'windows-1251'
        root = fromstring(response.text)

        for valute in root.findall('Valute'):
            if valute.find('CharCode').text == x:    # проверка требуемой валюты для конвертизации
                value = valute.find('Value').text
                rate = float(value.replace(',', '.'))
                return rate
        return None
    except Exception as e:
        print(f"Ошибка при получении данных: {e}")
        return None

def rub_to_another_rate(x, y):   # функция перевода валюты НЕ рубля, к другой валюты НЕ рубля
    rate = get_rate_cbr(y[0:3]) / get_rate_cbr(x[0:3])
    return rate

# В streamlit есть несколько способов выбора варианта ответа, multiselect - Для выбора нескольких значений, select_slider - для ползунка выбора,
# radio - для выбора пунктов, лучше всего для не более чем 6 вариантов ответа

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

st.title("Конвертер валют и криптовалют")  # задаем титул - главная фраза на сайте, название программы

move = st.radio(   # выбор действия - Валюта и Криптовалюта, для отделения разных функций
    "Выберите что вы хотиите перевести",
   ['Валюта', 'Криптовалюта']
)

if move == "Валюта":  # действие ВАЛЮТА
    quanty = st.number_input("Введите количество", 1)  # количество требуемой валюты

    y = st.selectbox(   # выбор валюты для конвертизации
        'Валюта:',
        all_valutes(),
        index = None,
        placeholder="Тут строка поиска/выбора")

    x = st.selectbox(   # в какую валюту конвертизирует
        'Вывод в:',
        all_valutes(),
        index = None,
        placeholder="Тут строка поиска/выбора")

    if x == y:    # проверка if, если валюты равны, то следовательно - значение 1
        try:
            st.write(f"{y} {"  =  "} {1} {f"{x[0:3]}"}")
        except:
            st.write("Ожидание ввода...")    # пока не выберется валюта данные не появится, предотвращая ошибку
    elif x != "":     # проверка elif, так как иначе выводит ошибку и предотвращает работу программы
        try:
            if x[0:3] == "RUB":    # если валюта - рубль - то производиться обычная конвертизация из xml файла сайта цбр
                st.write(f"{quanty} {y} {"  =  "} {quanty * get_rate_cbr(y[0:3]):.2f} {f"{x[0:3]}"}")
            else:    # в остальных случаях проводится конвертизация через деление двух НЕ рублёвых валют
                st.write(f"{quanty} {y} {"  =  "} {(quanty * rub_to_another_rate(x, y)):.4f} {f"{x[0:3]}"}")
        except: 
            st.write("Ожидание ввода...")    # пока не выберется валюта данные не появится, предотвращая ошибку


















if move == "Криптовалюта":
    st.title("В разработке...")
