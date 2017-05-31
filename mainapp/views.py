from django.shortcuts import render, HttpResponseRedirect
from Parser.settings import DATABASES
import sqlite3
import datetime
import time
import pytz

# Create your views here.
def main(request):
    conn = sqlite3.connect(DATABASES['skype']['NAME'])
    c = conn.cursor()
    c.execute('''
                WITH last AS (SELECT m.id, m.convo_id, m.author, m.from_dispname, m.body_xml, MAX(datetime(m.timestamp, 'unixepoch') )  as dt FROM Messages m GROUP BY m.convo_id)
                SELECT c.displayname, last.from_dispname, last.author, last.dt, last.body_xml, last.convo_id
                FROM conversations c JOIN last ON c.id = last.convo_id
                ORDER BY last.dt DESC
                ''')
    data = c.fetchall()
    c.execute('''
                SELECT skypename FROM Accounts
             ''')
    owners = c.fetchall()
    print(owners)
    conn.close()
    conn = sqlite3.connect(DATABASES['parser']['NAME'])
    c = conn.cursor()
    c.execute("""
                    CREATE TABLE IF NOT EXISTS parser_log (`id`	INTEGER NOT NULL, convo_id INTEGER, comment TEXT, comment_author TEXT, in_archive INTEGER, PRIMARY KEY(id));
                """)
    conn.commit()
    conn.close()
    context = []
    for item in data:
        if item[2] not in owners[0] and item[4]:
            row = {}
            row['author'] = item[1][:30]
            delta = datetime.datetime.now().replace(tzinfo = pytz.timezone("Etc/GMT")) - datetime.datetime.strptime(item[3], '%Y-%m-%d %H:%M:%S').replace(tzinfo = pytz.timezone("Etc/GMT+3"))
            row['datetime'] = '{} д. {} ч. {} м.'.format(delta.days, (delta.seconds//3600),(delta.seconds % 3600)//60)
            row['id'] = item[5]
            row['comment'] = "{}: {}".format(item[1], item[4])
            conn = sqlite3.connect(DATABASES['parser']['NAME'])
            c = conn.cursor()
            c.execute('''
                            SELECT comment, comment_author, in_archive
                            FROM parser_log
                            WHERE convo_id = ?''', (row['id'],)
                      )
            comment = c.fetchone()
            if comment:
                row['comment'] = "{}: {}".format(comment[1], comment[0])
            else:
                row['comment'] = " "
            if not comment or comment[2] != 1:
                context.append(row)
    return render(request, 'index.html', {'context': context})


def add_comment(request):
    if request.method == 'POST':
        comment = request.POST.get('comment')
        comment_author = request.POST.get('comment_author')
        id = request.POST.get('id')
        conn = sqlite3.connect(DATABASES['parser']['NAME'])
        c = conn.cursor()
        c.execute('''
              INSERT INTO parser_log (comment,comment_author, convo_id) VALUES (?,?,?)
             ''', (comment, comment_author, id))
        conn.commit()
        conn.close()
    return HttpResponseRedirect("/")

def archivate(request):
    if request.method == 'POST':
        id = int(request.POST.get('id'))
        print(id, type(id))
        conn = sqlite3.connect(DATABASES['parser']['NAME'])
        c = conn.cursor()
        c.execute('''
                SELECT * FROM parser_log WHERE convo_id = ?
            ''', (id,)
                  )

        data = c.fetchall()
        if data:
            c.execute('''
                    UPDATE parser_log SET in_archive = ?
                    WHERE convo_id = ?
                    ''', (1, id))
        else:
            c.execute('''
                     INSERT INTO parser_log (convo_id,in_archive) VALUES (?,?)
                    ''', (id,1))
        conn.commit()
        conn.close()
    return HttpResponseRedirect("/")