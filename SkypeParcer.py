'''
У скайпа есть веб-версия скайпа, открывающаяся в браузере. Требуется парсить веб-версию скайпа, диалоги с контактами от туда и те диалоги, где сообщение человека, а не наше, не собственное сообщение, последнее - выводить в списочек на отдельную веб-страничку парсера. Страничка без дизайна.

В табличке, куда выводим строчки с диалогами клиентами, есть поля для ввода текста два. У каждой строчки - два поля куда можно написать комментарий. Каждому диалогу, где сообщение последние не от нас - можно оставить в двух колонках два текстовых комментария.

Парсим скайп, где сообщение последние - выводим в табличку.
В табличке можно убрать строчку принудительно из отображения ее там кнопочкой "в архив"
Два текстовых поля для ввода комментария у каждой строчки в таблице.

https://docs.google.com/spreadsheets/d/1COO6t40avsXZLTW8LWMaYfaFrLWVavjIDL_QbHrwFts/edit#gid=0
'''



from skpy import *
sk=Skype("ostrowsky_", "geu9Kali5")
contacts = []
chats = {}
source_contacts = sk.contacts
for contact in source_contacts:
    contacts.append("8:"+ str(contact.id))
print(contacts)
chats = sk.chats.recent()
for chat in chats:
    print(chat, '\n')
'''
for contact in contacts:
    chat = sk.chats.chat(contact).getMsgs()
    if chat:
        print(chat[0], '\n')

recent_messages = sk.chats.chat(contact).getMsgs()
    if recent_messages:
        print(contact, '--->', recent_messages[0])
#print(sk.chats["8:alena.ry12"].getMsgs())


for contact in contacts:
    chat[contact] = sk.contacts[contact].chat.getMsgs()
    print(chat[contact])


chats = sk.chats.recent()
res = sk.chats.chat("8:cris.senno").getMsgs()
for i in res:
    print(i, '\n')
'''