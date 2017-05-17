from grab import Grab
from lxml import html
import urllib.request
import gzip
import json
import sqlite3
import os
import datetime

username = 'ostrowsky'
email = 'ostrowskyi@gmail.com'
password = password_confirmation = 'want_to_get_weather'
NUM = 20
db_filename = 'db_weather.sqlite'
date = datetime.date.today()
'''
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
'''

with open('app.id', 'r', encoding='UTF-8') as f:
    app_id = f.read()




conn = sqlite3.connect(db_filename)

#os.remove(db_filename)
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

with open('city.list.json', 'rb') as json_file:
    for line in json_file:
        encoded_line = json_file.readline()
        decoded_line = encoded_line.decode('utf-8')
        city = json.loads(decoded_line)
        city_id = city['_id']
        name = city['name']
        country = city['country']
        query = 'http://api.openweathermap.org/data/2.5/weather?id={}&units=metric&appid={}'.format(city['_id'], app_id)
        request = urllib.request.urlopen(query)
        response = request.read()
        response_decoded = response.decode('utf-8')
        json_line = json.loads(response_decoded)
        temp = json_line['main']['temp']
        temp_id = json_line['weather'][0]['id']
        icon = json_line['weather'][0]['icon']
        with sqlite3.connect(db_filename) as conn:
            conn.execute('''
                insert into weather (id_города, Город, Страна, Дата, Температура, id_погоды, Значок) VALUES (?,?,?,?,?,?,?)''', (
                city_id, name, country, date, temp, temp_id, icon
            )
        )
        conn.close()


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
        query += str(row['id_города'])+','
    query2 = query[:-1] + '&units=metric&appid=' + app_id
    request2 = urllib.request.urlopen(query2)
    print(query2)
    response2 = request2.read()
    response_decoded2 = response2.decode('utf-8')

    date = datetime.datetime.today()
    json_line2 = json.loads(response_decoded2)
    #print(json_line2)

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
                conn.execute("""update weather set Дата = ?, Температура = ?, id_погоды = ?, Значок = ? where id_города = ?""",
                     (date, temp, temp_id, icon, city_id))
                print('updated succesfully:  ', date, temp, temp_id, icon, name, country)
            else:
                conn.execute("""insert into weather (id_города, Город, Страна, Дата, Температура, id_погоды, Значок) VALUES (?,?,?,?,?,?)""",
                         (city_id, name, country, date, temp, temp_id, icon))
                print('inserted succesfully:  ', city_id, name, country, date, temp, temp_id, icon )

    conn.close()






