""" OpenWeatherMap (экспорт)

Сделать скрипт, экспортирующий данные из базы данных погоды, 
созданной скриптом openweather.py. Экспорт происходит в формате CSV или JSON.

Скрипт запускается из командной строки и получает на входе:
    export_openweather.py --csv filename [<город>]
    export_openweather.py --json filename [<город>]
    export_openweather.py --html filename [<город>]

При выгрузке в html можно по коду погоды (weather.id) подтянуть
соответствующие картинки отсюда:  http://openweathermap.org/weather-conditions

Экспорт происходит в файл filename.

Опционально можно задать в командной строке город. В этом случае
экспортируются только данные по указанному городу. Если города нет в базе -
выводится соответствующее сообщение.

"""

from dominate import document
from dominate.tags import *
import urllib.request
import sys
import sqlite3

db_filename = 'db_weather.sqlite'
#print(sys.argv)
try:
    filename = sys.argv[1]
    country = sys.argv[2]

except IndexError:
    print("Задан неверный параметр. Файл должен быть запущен с указанием параметров: export_openweather.py filename [<город>]")

city = sys.argv[3]

with sqlite3.connect(db_filename) as conn:
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute('''
        select distinct id_города, Город, Страна, Дата, Температура, id_погоды, Значок
        from weather
        where Страна = ?''', (country,))
    db_rows = cur.fetchall()
    cities = list(db_rows)
    html_string = ''
    html_string += '''
<!DOCTYPE html>
<html>
<head>
    <title>Weather</title>
</head>'''
    html_string += '''
    <body>
    <h1>Погода на момент актуализации базы данных</h1>
    <table border = "1">
      <tbody>
        <tr>
            <th align="center" width="auto">id_города</th>
            <th align="center" width="auto">Город</th>
            <th align="center" width="auto">Страна</th>
            <th align="center" width="auto">Дата</th>
            <th align="center" width="auto">Температура</th>
            <th align="center" width="auto">id_погоды</th>
            <th align="center" width="auto">Значок</th>
        </tr>
    '''
    for city in cities:
        #print(list(city))
        if city:
            #print(city)
            #print(list(city))
            html_string += '\t<tr>\n'
            for k in list(city):
                if k == list(city)[-1]:
                    path = "http://openweathermap.org/img/w/" + str(k) + ".png"
                    html_string += '\t\t<td align="center" width="auto"><img src=' + path + '></td>\n'
                else:
                    html_string += '\t\t<td align="center" width="auto">' + str(k) + '</td>\n'
            html_string += '\t</tr>\n'
        else:
            print("Города указанной страны отсутствуют в базе")

    html_string += '''
            </tbody>
        </table>
    </body>
 </html>'''

print(html_string)
with open(filename, 'w', encoding='UTF-8') as f:
    f.write(html_string)







