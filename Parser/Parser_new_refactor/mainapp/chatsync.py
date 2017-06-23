from skpy import Skype
sk = Skype('anna.freelanser', 'HfrbYfYt,t919') # connect to Skype

sk.user # you
sk.contacts # your contacts
sk.chats # your conversations
print(sk.contacts)
'''
ch = sk.chats.create(["joe.4", "daisy.5"]) # new group conversation
ch = sk.contacts["joe.4"].chat # 1-to-1 conversation

ch.sendMsg(content) # plain-text message
ch.sendFile(open("song.mp3", "rb"), "song.mp3") # file upload
ch.sendContact(sk.contacts["daisy.5"]) # contact sharing
ch.getMsgs() # retrieve recent messages
'''