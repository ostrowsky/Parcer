from django.shortcuts import render, HttpResponseRedirect
from django.template.context_processors import csrf
from django.http import Http404, JsonResponse
from Parser.settings import DATABASES
import sqlite3
import datetime
import time
import pytz

# Create your views here.
color = {"Максим":"#614999", "Егор":"#357336", "Лада":"#07faf2", "Ангел":"#ff00a2"}

def form_row(item):
    row = {}
    row['id'] = item[6]
    row['author'] = item[1][:30]
    delta = datetime.datetime.now().replace(tzinfo=pytz.timezone("Etc/GMT")) - datetime.datetime.strptime(item[3],
                                                                                                          '%Y-%m-%d %H:%M:%S').replace(
        tzinfo=pytz.timezone("Etc/GMT+3"))
    row['datetime'] = '{} д. {} ч. {} м.'.format(delta.days, (delta.seconds // 3600), (delta.seconds % 3600) // 60)
    row['login'] = item[6]
    row['avatar'] = item[7]
    conn = sqlite3.connect(DATABASES['parser']['NAME'])
    c = conn.cursor()
    c.execute("""
                                SELECT comment, comment_author, color
                                FROM parser_log
                                WHERE identity = ?""", (row['id'],)
              )
    comments = c.fetchall()
    conn.commit()
    conn.close()
    row['comment'] = []
    if comments:
        if comments[0][2]:
            row['color'] = comments[0][2]
        else:
            row['color'] = "#FFFFFF"
        for comment in comments:
            row['comment'].append("{}:{}".format(comment[1], comment[0]))

    if not comments:
        row['comment'] = " "
    return row

def main(request):
    context = []
    conn = sqlite3.connect(DATABASES['skype']['NAME'])
    c = conn.cursor()
    c.execute('''
                WITH last AS (SELECT m.id, m.convo_id, m.author, m.from_dispname, m.body_xml, MAX(datetime(m.timestamp, 'unixepoch') )  as dt FROM Messages m GROUP BY m.convo_id)
                SELECT c.displayname, last.from_dispname, last.author, last.dt, last.body_xml, last.convo_id, c.identity, ct.avatar_url
                FROM conversations c
                JOIN last ON c.id = last.convo_id
                JOIN contacts ct ON c.identity = ct.skypename
                WHERE last.author NOT IN (SELECT skypename FROM Accounts)
                ORDER BY last.dt
                ''')
    data = c.fetchall()
    conn.close()
    for item in data:
        if item[2] and item[4]:
            conn = sqlite3.connect(DATABASES['parser']['NAME'])
            c = conn.cursor()
            message_date = datetime.datetime.strptime(item[3], '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.timezone("Etc/GMT+3"))
            c.execute("""
                                SELECT in_archive, archive_date
                                FROM archive
                                WHERE identity = ?""", (item[6],)
              )
            in_archive = c.fetchone()
            conn.close()
            if in_archive and in_archive[0] == 1:
                archive_date = datetime.datetime.strptime(in_archive[1][:-7], '%Y-%m-%d %H:%M:%S').replace(
                tzinfo=pytz.timezone("Etc/GMT"))
                if archive_date <= message_date:
                    conn = sqlite3.connect(DATABASES['parser']['NAME'])
                    c = conn.cursor()
                    c.execute("""
                                            UPDATE archive SET in_archive = ?
                                            WHERE identity = ?
                                            """, (0, item[6])
                          )
                    conn.commit()
                    conn.close()
                    new_row = form_row(item)
                    context.append(new_row)
                else:
                    continue
            elif not in_archive or not in_archive[0]:
                new_row = form_row(item)
                context.append(new_row)

    return render(request, 'index.html', {'context': context})


def add_comment(request):
    print('принято', request)
    if request.method == 'POST':
        context = {}

        id = request.POST.get('id')
        comment = request.POST.get('comment')
        comment_author = request.POST.get('comment_author')
        print(comment, comment_author, id)
        curr_color = color.get(comment_author, "#FFFFFF")
        conn = sqlite3.connect(DATABASES['parser']['NAME'])
        c = conn.cursor()
        c.execute('''
                                  INSERT INTO parser_log (comment,comment_author, identity, color) VALUES (?,?,?,?)
                                 ''', (comment, comment_author, id, curr_color))
        conn.commit()

        c = conn.cursor()
        c.execute('''
                                         SELECT comment, comment_author, color
                                         FROM parser_log
                                         WHERE identity = ?''', (id,)
                  )
        comments = c.fetchall()
        conn.commit()
        conn.close()
        row = {}
        context = []
        row['comment'] = []
        if comments:
            if comments[0][2]:
                row['color'] = comments[0][2]
            else:
                row['color'] = "#FFFFFF"
            for comment in comments:
                row['comment'].append("{}:{}".format(comment[1], comment[0]))

        if not comments:
            row['comment'] = " "
        context.append(row)
    return HttpResponseRedirect("/")


def users(request, user):
    conn = sqlite3.connect(DATABASES['parser']['NAME'])
    c = conn.cursor()
    c.execute('''
                            SELECT p.id, p.identity FROM (SELECT MIN(p.id) as id, p.identity
                            FROM parser_log p
                            LEFT JOIN archive a ON p.identity = a.identity
                            WHERE a.in_archive ISNULL OR a.in_archive = 0
                            GROUP BY 2) as first_comment
                            JOIN parser_log p ON p.id = first_comment.id
                            WHERE p.comment_author = ?''', (user,)
                          )
    res = c.fetchall()
    conn.close()
    context = []
    if res:
        for item in res:
            client = item[1]
            id = item[0]
            conn = sqlite3.connect(DATABASES['skype']['NAME'])
            c = conn.cursor()
            c.execute('''
                WITH last AS (SELECT m.id, m.convo_id, m.author, m.from_dispname, m.body_xml, MAX(datetime(m.timestamp, 'unixepoch') )  as dt FROM Messages m GROUP BY m.convo_id)
                SELECT c.displayname, last.from_dispname, last.author, last.dt, last.body_xml, last.convo_id, c.identity, ct.avatar_url
                FROM conversations c
                JOIN last ON c.id = last.convo_id
                JOIN contacts ct ON c.identity = ct.skypename
                WHERE c.identity = ?
                ORDER BY last.dt ASC
                    ''', (client,))
            data = c.fetchone()
            conn.close()
            if data:
                new_row = form_row(data)
                context.append(new_row)

    return render(request, 'user.html', {'user':user, 'context': context})



def archivate(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        date = datetime.datetime.now()
        conn = sqlite3.connect(DATABASES['parser']['NAME'])
        c = conn.cursor()
        c.execute('''
                SELECT * FROM archive WHERE identity = ?
            ''', (id,)
                  )
        data = c.fetchall()
        if data:
            conn = sqlite3.connect(DATABASES['parser']['NAME'])
            c = conn.cursor()
            c.execute('''
                    UPDATE archive SET in_archive = ?, archive_date = ?
                    WHERE identity = ?
                    ''', (1, date, id))
        else:
            conn = sqlite3.connect(DATABASES['parser']['NAME'])
            c = conn.cursor()
            c.execute('''
                     INSERT INTO archive (identity,in_archive, archive_date) VALUES (?,?,?)
                    ''', (id,1, date))
        conn.commit()
        conn.close()
    return HttpResponseRedirect("/")

def dearchivate(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        conn = sqlite3.connect(DATABASES['parser']['NAME'])
        c = conn.cursor()
        c.execute('''
                SELECT * FROM archive WHERE identity = ?
            ''', (id,)
                  )

        data = c.fetchone()
        c.execute('''
                    UPDATE archive SET in_archive = ?
                    WHERE identity = ?
                    ''', (0, id))
        conn.commit()
        conn.close()
    return HttpResponseRedirect("/")

def archive(request):
    conn = sqlite3.connect(DATABASES['parser']['NAME'])
    c = conn.cursor()
    c.execute('''
                                SELECT p.id, p.identity FROM (SELECT MIN(p.id) as id, p.identity
                                FROM parser_log p
                                LEFT JOIN archive a ON p.identity = a.identity
                                WHERE a.in_archive ISNULL OR a.in_archive = 0
                                GROUP BY 2) as first_comment
                                JOIN parser_log p ON p.id = first_comment.id
                                WHERE p.comment_author = ?''', (user,)
              )
    res = c.fetchall()
    conn.close()
    context = []
    if res:
        for item in res:
            client = item[1]
            id = item[0]
            conn = sqlite3.connect(DATABASES['skype']['NAME'])
            c = conn.cursor()
            c.execute('''
                    WITH last AS (SELECT m.id, m.convo_id, m.author, m.from_dispname, m.body_xml, MAX(datetime(m.timestamp, 'unixepoch') )  as dt FROM Messages m GROUP BY m.convo_id)
                    SELECT c.displayname, last.from_dispname, last.author, last.dt, last.body_xml, last.convo_id, c.identity, ct.avatar_url
                    FROM conversations c
                    JOIN last ON c.id = last.convo_id
                    JOIN contacts ct ON c.identity = ct.skypename
                    WHERE c.identity = ?
                    ORDER BY last.dt ASC
                        ''', (client,))
            data = c.fetchone()
            conn.close()
            if data:
                new_row = form_row(data)
                context.append(new_row)


    """
    conn = sqlite3.connect(DATABASES['skype']['NAME'])
    c = conn.cursor()
    c.execute('''
                   WITH last AS (SELECT m.id, m.convo_id, m.author, m.from_dispname, m.body_xml, MAX(datetime(m.timestamp, 'unixepoch') )  as dt FROM Messages m GROUP BY m.convo_id)
                   SELECT c.displayname, last.from_dispname, last.author, last.dt, last.body_xml, last.convo_id, c.identity, ct.avatar_url
                   FROM conversations c
                   JOIN last ON c.id = last.convo_id
                   JOIN contacts ct ON c.identity = ct.skypename
                   ORDER BY last.dt
                   ''')
    data = c.fetchall()
    c.execute('''
                   SELECT skypename FROM Accounts
                ''')
    owners = c.fetchall()
    conn.commit()
    conn.close()
    context = []
    for item in data:
        row = {}
        row['id'] = item[6]
        conn = sqlite3.connect(DATABASES['parser']['NAME'])
        c = conn.cursor()
        message_date = datetime.datetime.strptime(item[3], '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.timezone("Etc/GMT+3"))
        c.execute('''
                               SELECT in_archive, archive_date
                               FROM archive
                               WHERE identity = ?''', (row['id'],)
                  )
        in_archive = c.fetchone()
        if in_archive:
            archive_date = datetime.datetime.strptime(in_archive[1][:-7], '%Y-%m-%d %H:%M:%S').replace(tzinfo = pytz.timezone("Etc/GMT"))
            if in_archive[0] and (archive_date > message_date):
                row['author'] = item[1][:30]

                delta = datetime.datetime.now().replace(tzinfo=pytz.timezone("Etc/GMT")) - datetime.datetime.strptime(
                    item[3], '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.timezone("Etc/GMT+3"))
                row['datetime'] = '{} д. {} ч. {} м.'.format(delta.days, (delta.seconds // 3600),
                                                            (delta.seconds % 3600) // 60)
                row['login'] = item[6]
                row['avatar'] = item[7]
                conn = sqlite3.connect(DATABASES['parser']['NAME'])
                c = conn.cursor()
                c.execute('''
                               SELECT comment, comment_author, color
                               FROM parser_log
                               WHERE identity = ?''', (row['id'],)
                          )
                comments = c.fetchall()
                conn.commit()
                conn.close()
                row['comment'] = []
                if comments:
                    if comments[0][2]:
                        row['color'] = comments[0][2]
                    else:
                        row['color'] = "#FFFFFF"
                    for comment in comments:
                        row['comment'].append("{}:{}".format(comment[1], comment[0]))

                if not comments:
                    row['comment'] = " "
                context.append(row)
    """
    return render(request, 'archive.html', {'context': context})
