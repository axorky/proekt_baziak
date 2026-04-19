# импортирую библиотеки для работы
import streamlit as st      # основная библиотека для работы
from requests import get        # Библиотека для запросов данных
from xml.etree.ElementTree import fromstring    # библиотека для обработки xml файлов
from datetime import datetime
from json import load
from ssl import create_default_context
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from certifi import where

def get_rate_cbr(x):    # САМАЯ ГЛАВНАЯ ФУНКЦИЯ для получения отношения валюты к рублю, от неё идет общая работа с действием: "Валюта"
    url = "http://www.cbr.ru/scripts/XML_daily.asp"
    try:
        response = get(url)
        response.encoding = 'windows-1251'
        root = fromstring(response.text)

        for valute in root.findall('Valute'):
            if valute.find('CharCode').text == x:    # проверка требуемой валюты для конвертизации
                value = valute.find('Value').text
                rate = float(value.replace(',', '.'))
                return rate
    except Exception as e:
        print(f"Ошибка при получении данных: {e}")
        return None

params = urlencode(
    {
        "start": "1",
        "limit": "30",
        "convert": "RUB",
    }
)
request = Request(
    f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?{params}",
    headers={
        "Accept": "application/json",
        "X-CMC_PRO_API_KEY": "dc37e8804ae847fd965f3f473be59451",
    },
)
context = create_default_context(cafile=where())
with urlopen(request, context=context) as response:
    data = load(response)

crypto_list = data.get('data', [])

info = []
data = []
crypt_names = []

for crypto in crypto_list:
        price = float(f'{crypto['quote']['RUB']['price']:.2f}')
        if price != 1.00 and price != 0.00:
            crypt_names.append(crypto['name'])
            data.append(crypto['name'])
            data.append(f"{price:.2f}")
            info.append(data)
        data = []


def all_valutes():      # функция для создания списка со всеми валютами, находящихся в доступе на сайте центрального банка России
        url = "http://www.cbr.ru/scripts/XML_daily.asp"    # ссылка для обращение к xml файлу сайта ЦБР
        try:
            response = get(url)
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

all_valutes = all_valutes()

def get_date():
    url = "http://www.cbr.ru/scripts/XML_daily.asp" 
    response = get(url)
    response.encoding = 'windows-1251'     # Важно для правильного отображения русских букв
    root = fromstring(response.text)     # Проверка текста для получения данных

    date_header = response.headers.get('Date')
    if date_header:
        date_obj = datetime.strptime(date_header, '%a, %d %b %Y %H:%M:%S %Z') # Преобразуем строку заголовка (например, "Tue, 24 Mar 2026 12:34:56 GMT") в datetime
    formatted_date = date_obj.strftime('%d.%m.%Y') # Форматируем для вывода на сайт (например, "24.03.2026")
    return formatted_date

def rate_to_another_rate(x, y):   # функция перевода валюты НЕ рубля, к другой валюты НЕ рубля
    rate = get_rate_cbr(y[0:3]) / get_rate_cbr(x[0:3])
    return rate

def rub_to_another_rate_rub(x):   # функция перевода валюты НЕ рубля, к другой валюты НЕ рубля
    rate = 1 / get_rate_cbr(x[0:3])
    return rate

def swap_values():  # понадобиться в будущем для изменения значений ввода и вывода
    st.session_state.x, st.session_state.y = st.session_state.y, st.session_state.x

def fast_crypt_x(pair):
    for valute in all_valutes:
        if pair[-3:] in valute:
            return valute


def crypt_price_rub(x):
    for i in info:
        if x == i[0]:
            return float(i[1])

def crypt_price_valute(x, y):
    if y[0:3] == "RUB":
        for i in info:
            if x == i[0]:
                return 1 / float(i[1])
    return get_rate_cbr(y[0:3]) / crypt_price_rub(x)

def valute_price_crypt(x, y):
    if x[0:3] == "RUB":
        for i in info:
            if y == i[0]:
                return float(i[1])
    return crypt_price_rub(y) / get_rate_cbr(x[0:3])

def crypt_to_crypt(x, y):
    price = crypt_price_rub(x) / crypt_price_rub(y)
    return price

def combined_list(names):
    combined_valutes_list = []
    rev_combined_valutes_list = []
    combined_valutes_list.extend(all_valutes)
    combined_valutes_list.extend(names)
    rev_combined_valutes_list.extend(names)
    rev_combined_valutes_list.extend(all_valutes)
    return combined_valutes_list, rev_combined_valutes_list


def fast_valute_y(pair):
    val_name = pair.split(" - ")[0].strip()
    
    for valute in combined_list(crypt_names)[0]:
        if val_name in valute:
            return valute
        
def fast_valute_x(pair):
    val_name = pair.split(" - ")[1].strip()
    
    for valute in combined_list(crypt_names)[1]:
        if val_name in valute:
            return valute

def update_pair(pair):
    st.session_state.y = fast_valute_y(pair)
    st.session_state.x = fast_valute_x(pair)

def set_amount(quant):
    st.session_state.quanty = quant

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

col4, col5 = st.columns([1, 1]) 

with col4:
    st.write(f"Последнее обновление курса ЦБР: {get_date()}") ## вывод актуальной даты курса для конвертизации

st.divider() # информационное разделение, для более удобного и приятного вида

col1, col2, col3 = st.columns([7, 1, 7]) # настраиваем размеры кнопок


if "x" and "y" and "quanty" not in st.session_state:
    st.session_state.x = None
    st.session_state.y = None
    st.session_state.quanty = 1

    
    # количество требуемой валюты
quanty = st.number_input("Введите количество", 1, key="quanty")

with col1:
    y = st.selectbox(   # выбор
        "Валюта:",
        options = combined_list(crypt_names)[1],
        index = None,
        placeholder = "Тут строка поиска/выбора",
        label_visibility="visible",
        key = 'y'
        )
    st.write("")

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.button("↔",
        use_container_width = True,
        on_click = swap_values,
        key = "swap_button"
        )

with col3:
    x = st.selectbox(   # в какую валюту конвертизирует
        "Вывод в:",
        options = combined_list(crypt_names)[0],
        index = None,
        placeholder = "Тут строка поиска/выбора",
        label_visibility="visible",
        key = "x"
        )

st.divider()

if x == y:    # проверка if, если валюты равны, то следовательно - значение 1
    try:
        if y != None or x != None:
            st.info(f"{y} {"  =  "} {1} {f"{x}"}")
        else:
            st.info("Ожидание ввода...")  
    except:
        st.info("Ожидание ввода...")    # пока не выберется валюта данные не появится, предотвращая ошибку
elif x != y:     # проверка elif, так как иначе выводит ошибку и предотвращает работу программы
    try:
        if x in crypt_names and y in crypt_names:    # в остальных случаях проводится конвертизация через деление двух криптовалют
            st.info(f"{quanty} {y} {"  =  "} {quanty * crypt_to_crypt(y, x):.4f} {f"{x}"}")
        elif x in crypt_names:
            st.info(f"{quanty} {y} {"  =  "} {quanty * crypt_price_valute(x, y):.8f} {f"{x}"}")
        elif y in crypt_names:    # если валюта - рубль - то производиться обычная конвертизация из xml файла сайта цбр
            st.info(f"{quanty} {y} {"  =  "} {quanty * valute_price_crypt(x, y):.2f} {f"{x}"}")
        else:
            if x == y:    # проверка if, если валюты равны, то следовательно - значение 1
                try:
                    st.info(f"{y} {"  =  "} {1} {f"{x[0:3]}"}")
                except:
                    st.info("Ожидание ввода...")    # пока не выберется валюта данные не появится, предотвращая ошибку
            elif x != "":     # проверка elif, так как иначе выводит ошибку и предотвращает работу программы
                try:
                    if x[0:3] == "RUB":    # если валюта - рубль - то производиться обычная конвертизация из xml файла сайта цбр
                        st.info(f"{quanty} {y} {"  =  "} {quanty * get_rate_cbr(y[0:3]):.2f} {f"{x}"}")
                    elif y[0:3] == "RUB":
                        st.info(f"{quanty} {y} {"  =  "} {quanty * rub_to_another_rate_rub(x):.4f} {f"{x}"}")
                    else:    # в остальных случаях проводится конвертизация через деление двух НЕ рублёвых валют
                        st.info(f"{quanty} {y} {"  =  "} {(quanty * rate_to_another_rate(x, y)):.4f} {f"{x}"}")
                except: 
                    st.info("Ожидание ввода...")

    except: 
        st.info("Ожидание ввода...")    # пока не выберется валюта данные не появится, предотвращая ошибку

st.divider()   

col_left, col_right = st.columns([4, 1])

with col_left:
    st.write("Часто выбираемые пары:")
    
    popular_pairs = [
        "USD - RUB", "Tether USDt - RUB", "Bitcoin - Ethereum",
        "RUB - KZT", "EUR - Toncoin", "USD - Toncoin",
        "Bitcoin - RUB", "BYN - RUB", "EUR - USD"

    ]
    
    inner_cols = st.columns(3)
    for i, pair in enumerate(popular_pairs):
        with inner_cols[i % 3]:
            st.button(
            pair, 
            use_container_width=True, 
            on_click=update_pair, 
            args=(pair,)
        )

with col_right:
    st.write("Количество:")
    
    amounts = [100, 500, 1000]
    
    for val in amounts:
        st.button(
        f"{val}", 
        key=f"btn_{val}", 
        use_container_width=True, 
        on_click=set_amount, 
        args=(val,)
    )