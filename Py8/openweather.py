""" OpenWeatherMap
OpenWeatherMap — онлайн-сервис, который предоставляет бесплатный API для доступа к данным о текущей погоде, прогнозам, для web-сервисов и мобильных приложений. Архивные данные доступны только на коммерческой основе. В качестве источника данных используются официальные метеорологические службы, данные из метеостанций аэропортов, и данные с частных метеостанций.

Необходимо решить следующие задачи:

== Получение APPID ==
    Чтобы получать данные о погоде необходимо получить бесплатный APPID.
    
    Предлагается 2 варианта (по желанию):
    - получить APPID вручную
    - автоматизировать процесс получения APPID, используя дополнительную библиотеку GRAB (pip install grab)

        Необходимо зарегистрироваться на сайте openweathermap.org:
        https://home.openweathermap.org/users/sign_up

        Войти на сайт по ссылке:
        https://home.openweathermap.org/users/sign_in

        Свой ключ вытащить со страницы отсюда:
        https://home.openweathermap.org/api_keys
        
        Ключ имеет смысл сохранить в локальный файл, например, "app.id"

        
== Получение списка городов ==
    Список городов может быть получен по ссылке: http://bulk.openweathermap.org/sample/city.list.json.gz
    
    Далее снова есть несколько вариантов (по желанию):
    - скачать и распаковать список вручную
    - автоматизировать скачивание (ulrlib) и распаковку списка 
        (воспользоваться модулем gzip или вызвать распаковку через создание процесса архиватора через модуль subprocess)
    
    Список достаточно большой. Представляет собой JSON-строки:
    {"_id":707860,"name":"Hurzuf","country":"UA","coord":{"lon":34.283333,"lat":44.549999}}
    {"_id":519188,"name":"Novinki","country":"RU","coord":{"lon":37.666668,"lat":55.683334}}
    
    
== Получение погоды ==
    На основе списка городов можно делать запрос к сервису по id города. И тут как раз понадобится APPID.
        By city ID
        Examples of API calls:
        http://api.openweathermap.org/data/2.5/weather?id=2172797&appid=b1b15e88fa797225412429c1c50c122a

    Для получения температуры по Цельсию:
    http://api.openweathermap.org/data/2.5/weather?id=520068&units=metric&appid=b1b15e88fa797225412429c1c50c122a

    Для запроса по нескольким городам сразу:
    http://api.openweathermap.org/data/2.5/group?id=524901,703448,2643743&units=metric&appid=b1b15e88fa797225412429c1c50c122a


    Данные о погоде выдаются в JSON-формате
    {"coord":{"lon":38.44,"lat":55.87},"weather":[{"id":803,"main":"Clouds","description":"broken clouds","icon":"04n"}],"base":"cmc stations","main":{"temp":280.03,"pressure":1006,"humidity":83,"temp_min":273.15,"temp_max":284.55},"wind":{"speed":3.08,"deg":265,"gust":7.2},"rain":{"3h":0.015},"clouds":{"all":76},"dt":1465156452,"sys":{"type":3,"id":57233,"message":0.0024,"country":"RU","sunrise":1465087473,"sunset":1465149961},"id":520068,"name":"Noginsk","cod":200}    


== Сохранение данных в локальную БД ==    
Программа должна позволять:
1. Создавать файл базы данных SQLite с следующей структурой данных (если файла 
   базы данных не существует):

    Погода
        id_города           INTEGER PRIMARY KEY
        Город               VARCHAR(255)
        Дата                DATE
        Температура         INTEGER
        id_погоды           INTEGER                 # weather.id из JSON-данных

2. Выводить список стран из файла и предлагать пользователю выбрать страну 
(ввиду того, что список городов и стран весьма велик имеет смысл запрашивать у пользователя имя города или страны
 и искать данные в списке доступных городов/стран (регуляркой))

3. Скачивать JSON (XML) файлы погоды в городах выбранной страны
4. Парсить последовательно каждый из файлов и добавлять данные о погоде в базу
   данных. Если данные для данного города и данного дня есть в базе - обновить
   температуру в существующей записи.


При повторном запуске скрипта:
- используется уже скачанный файл с городами
- используется созданная база данных, новые данные добавляются и обновляются



При работе с XML-файлами:

Доступ к данным в XML файлах происходит через пространство имен:
<forecast ... xmlns="http://weather.yandex.ru/forecast ...>

Чтобы работать с пространствами имен удобно пользоваться такими функциями:

    # Получим пространство имен из первого тега:
    def gen_ns(tag):
        if tag.startswith('{'):
            ns, tag = tag.split('}')
            return ns[1:]
        else:
            return ''

    tree = ET.parse(f)
    root = tree.getroot()

    # Определим словарь с namespace
    namespaces = {'ns': gen_ns(root.tag)}

    # Ищем по дереву тегов
    for day in root.iterfind('ns:day', namespaces=namespaces):
        ...

"""

from grab import Grab
from lxml import html
import urllib.request
import gzip
import json
import sqlite3
import os
import datetime

db_filename = 'db_weather_2912.sqlite'
date = datetime.date.today()
NUM = 20

"""
username = input("Введите имя пользователя для регистрации на openweather\n")
email = input("Введите e-mail для регистрации\n")
password = password_confirmation = input("Введите пароль для регистрации\n")


g = Grab()
g.go('https://home.openweathermap.org/users/sign_up')
g.set_input_by_id('user_username', username)
g.set_input_by_id('user_email', email)
g.set_input_by_id('user_password', password)
g.set_input_by_id('user_password_confirmation', password_confirmation)
g.set_input_by_id('user_agreement', 'True')
g.submit()
print(g.response, g.response.body)

g = Grab()
g.go('https://home.openweathermap.org/api_keys')
g.set_input_by_id('user_email', email)
g.set_input_by_id('user_password', password)
g.set_input_by_id('user_remember_me', 'True')
g.submit()
app_id = g.xpath_text('/html/body/div[3]/div[5]/div[3]/div[1]/table/tbody/tr/td[1]/pre')
with open('app.id', 'w', encoding='UTF-8') as f:
    f.write(app_id)


f = urllib.request.urlopen('http://bulk.openweathermap.org/sample/city.list.json.gz')
s = f.read()
with open('city.list.json.gz', 'wb') as arch:
    arch.write(s)

with gzip.open('city.list.json.gz', 'r') as arch:
    archive_content = arch.read()


with open('city.list.json', 'wb') as json_content:
    json_content.write(archive_content)

with open('app.id', 'r', encoding='UTF-8') as f:
    app_id = f.read()


"""

conn = sqlite3.connect(db_filename)

# os.remove(db_filename)
conn.executescript('drop table if exists weather')

with sqlite3.connect(db_filename) as conn:
    conn.execute('''
        create table weather (
        id_города   INTEGER PRIMARY KEY,
        Город       VARCHAR(255),
        Страна      VARCHAR(8),
        Дата        DATE,
        Температура INTEGER,
        id_погоды   INTEGER,
        Значок      VARCHAR(8)
        );
    ''')

with open('app.id', 'r', encoding='UTF-8') as f:
    app_id = f.read()

with open('city.list.json', 'rb') as json_file:
    for line in json_file:
        encoded_line = json_file.readline()
        decoded_line = encoded_line.decode('utf-8')
        city = json.loads(decoded_line)
        city_id = city['_id']
        name = city['name']
        country = city['country']
        query = 'http://api.openweathermap.org/data/2.5/weather?id={}&units=metric&appid={}'.format(city['_id'], app_id)
        print(query)
        request = urllib.request.urlopen(query)
        response = request.read()
        response_decoded = response.decode('utf-8')
        json_line = json.loads(response_decoded)
        temp = json_line['main']['temp']
        temp_id = json_line['weather'][0]['id']
        icon = json_line['weather'][0]['icon']
        with sqlite3.connect(db_filename) as conn:
            conn.execute('''
                insert into weather (id_города, Город, Страна, Дата, Температура, id_погоды, Значок) VALUES (?,?,?,?,?,?,?)''',
                         (
                             city_id, name, country, date, temp, temp_id, icon

                         )
                         )
        print("добавляю:  ", city_id, name, country, date, temp, temp_id, icon)
conn.close()
print("закрываю соединение")

user_country = input("Введите обозначение страны\n")
query = 'http://api.openweathermap.org/data/2.5/group?id='
with sqlite3.connect(db_filename) as conn:
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute('''
        select distinct Страна, id_города
        from weather
        where Страна =?''', (user_country,))
    cities_id = cur.fetchmany(NUM)
    for row in cities_id:
        query += str(row['id_города']) + ','
    query2 = query[:-1] + '&units=metric&appid=' + app_id
    print(query2)
    request2 = urllib.request.urlopen(query2)
    response2 = request2.read()
    response_decoded2 = response2.decode('utf-8')

    date = datetime.datetime.today()
    json_line2 = json.loads(response_decoded2)
    # print(json_line2)

    for item in json_line2['list']:
        temp = item['main']['temp']
        temp_id = item['weather'][0]['id']
        icon = item['weather'][0]['icon']
        city_id = item['id']
        country = item['sys']['country']
        name = item['name']
        with sqlite3.connect(db_filename) as conn:
            cur = conn.cursor()
            cur.execute("""select id_города from weather where id_города = ?""", (city_id,))
            if cur.fetchall():
                conn.execute(
                    """update weather set Дата = ?, Температура = ?, id_погоды = ?, Значок = ? where id_города = ?""",
                    (date, temp, temp_id, icon, city_id))
                print('updated succesfully:  ', date, temp, temp_id, icon, name, country)
            else:
                conn.execute(
                    """insert into weather (id_города, Город, Страна, Дата, Температура, id_погоды, Значок) VALUES (?,?,?,?,?,?)""",
                    (city_id, name, country, date, temp, temp_id, icon))
                print('inserted succesfully:  ', city_id, name, country, date, temp, temp_id, icon)

conn.close()
print("закрываю соединение")
