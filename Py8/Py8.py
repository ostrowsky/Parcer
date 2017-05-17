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

db_filename = 'db_weather'
conn = sqlite3.connect(db_filename)
conn.close()
#os.remove(db_filename)
"""
with sqlite3.connect(db_filename) as conn:
    conn.execute('''
        create table weather (
        id_города   INTEGER PRIMARY KEY,
        Город       VARCHAR(255),
        Дата        DATE,
        Температура INTEGER,
        id_погоды   INTEGER
        );
    ''')
"""

with open('city.list.json', 'rb') as json_file:
    for line in json_file:
        encoded_line = json_file.readline()
        decoded_line = encoded_line.decode('utf-8')
        city = json.loads(decoded_line)
        city_id = city['_id']
        name = city['name']
        print(city['country'])
        date = datetime.date.today()
        query = 'http://api.openweathermap.org/data/2.5/weather?id={}&units=metric&appid={}'.format(city['_id'], app_id)
        request = urllib.request.urlopen(query)
        response = request.read()
        response_decoded = response.decode('utf-8')
        json_line = json.loads(response_decoded)
        temp = json_line['main']['temp']
        temp_id = json_line['weather'][0]['id']

        """
        with sqlite3.connect(db_filename) as conn:
            conn.execute('''
                insert into weather (id_города, Город, Дата, Температура, id_погоды) VALUES (?,?,?,?,?)''', (
                city_id, name, date, temp, temp_id
            )
        )

        """



       # g = Grab()
       # g.go('http://api.openweathermap.org/data/2.5/weather?id=524901&units=metric&appid=5ed63d7796f30a5f84cf735eed9af7e1')
        #print(g.response, g.response.body)





