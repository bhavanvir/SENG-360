import sqlite3
import uuid
import datetime
import bcrypt

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
    password_salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), password_salt)
    con = sqlite3.connect('client_database.db')
    cur = con.cursor()
    try:
        cur.execute("INSERT INTO users (uuid, username, password) VALUES (?, ?, ?)", (username_uuid, username, hashed_password ))
        con.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def check_password(username, password):
    con = sqlite3.connect('client_database.db')
    cur = con.cursor()
    cur.execute("SELECT password FROM users WHERE username = (?)", (username,))
    try:
        records = cur.fetchall()[0]
        password_valid = bcrypt.checkpw(password.encode('utf-8'), records[0])
        return password_valid
    except IndexError:
        pass

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

def message_history(username):
    mapping = {}

    con = sqlite3.connect('client_database.db')
    cur = con.cursor()
    cur.execute("SELECT timestamp, message FROM users u JOIN messages m ON u.uuid = m.senderUUID WHERE u.username = (?)", (username,))
    records = cur.fetchall()

    for timestamp, message in records:
        dt_object = datetime.datetime.fromtimestamp(float(timestamp)).strftime("%d/%m/%Y %H:%M:%S")
        mapping[dt_object] = message

    return mapping