import sqlite3
import uuid
import datetime

def initialize():
    con = sqlite3.connect('client_database.db')
    con.execute("PRAGMA foreign_keys = 1")
    cur = con.cursor()

    # create users table
    cur.execute('''CREATE TABLE IF NOT EXISTS users
    (uuid TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT NOT NULL)''')

    # create messages table
    cur.execute('''CREATE TABLE IF NOT EXISTS messages
    (messageID TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    message TEXT NOT NULL,
    recipientUUID TEXT,
    senderUUID TEXT,
    FOREIGN KEY (senderUUID) REFERENCES users (uuid))''')
    con.commit()

def insert_user(username, password):
    username_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(username)))

    con = sqlite3.connect('client_database.db')
    cur = con.cursor()
    cur.execute("INSERT INTO users (uuid, username, password) VALUES (?, ?, ?)", (username_uuid, username, password))
    con.commit()

def insert_message(message, recipients, sender):
    recipient_uuid = ""
    if recipients:
        for i in range(len(recipients)):
            recipient_uuid += str(uuid.uuid5(uuid.NAMESPACE_DNS, str(recipients[i])))
            if i != len(recipients) - 1:
                recipient_uuid += ", "
    elif not recipients:
        recipient_uuid = None

    message_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(message)))
    sender_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(sender)))

    current_time = datetime.datetime.now()
    converted_timestamp = str(current_time.timestamp())

    con = sqlite3.connect('client_database.db')
    cur = con.cursor()
    cur.execute("INSERT INTO messages (messageID, timestamp, message, recipientUUID, senderUUID) VALUES (?, ?, ?, ?, ?)", (message_uuid, converted_timestamp, message, recipient_uuid, sender_uuid))
    con.commit()