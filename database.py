import sqlite3
import uuid
import datetime
import bcrypt

# Initialize the database if it does not already exist
# None -> None
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

# Insert a user into the user's table. 
# username (string), password (string) -> Bool
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

# Check if the given username exists in the database
# username (String) -> Bool
def user_exists(username):
    con = sqlite3.connect('client_database.db')
    cur = con.cursor()
    rows = cur.execute("SELECT * FROM users WHERE username=?", (username, )).fetchone()
    if rows:
        return True
    return False

# Delete a user from the database
# username (String) -> Bool
def delete_user(username):
    con = sqlite3.connect('client_database.db')
    cur = con.cursor()
    try:
        cur.execute("DELETE FROM users WHERE username = (?)", (username,))
        con.commit()
        return True
    except:
        return False

# Check if the given credentials are valid
# username (String), password (String) -> Bool
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

# Insert a message to the database
#  message (String), recipient (String), sender (String) -> None
def insert_message(message, recipient, sender):
    recipient_uuid = ""
    if recipient:
        recipient_uuid += str(uuid.uuid5(uuid.NAMESPACE_DNS, str(recipient)))
    elif not recipient:
        recipient_uuid = None

    message_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(message)))
    sender_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(sender)))

    current_time = datetime.datetime.now()
    converted_timestamp = str(current_time.timestamp())

    con = sqlite3.connect('client_database.db')
    cur = con.cursor()
    cur.execute("INSERT INTO messages (messageID, timestamp, message, recipientUUID, senderUUID) VALUES (?, ?, ?, ?, ?)", (message_uuid, converted_timestamp, message, recipient_uuid, sender_uuid))
    con.commit()

# Get the ID of a user
# username (String) -> uuid (String)
def get_uuid(username):
    con = sqlite3.connect('client_database.db')
    cur = con.cursor()
    records = cur.execute("SELECT * FROM users WHERE username=?", (username, ))
    records = cur.fetchall()[0]
    return records[0]

# Get the message history between two users
# Requester (String), Reciever (String) -> messages (List)
def get_message_history_between_users(requester, reciever):
   
    # Organize the message packets in the format (sender, message)
    messages = []
    
    try:
        # Get the UUID of the username's 
        requester_uuid = get_uuid(requester)
        reciever_uuid = get_uuid(reciever)
        
        con = sqlite3.connect('client_database.db')
        cur = con.cursor()
        cur.execute("SELECT * FROM messages WHERE (senderUUID = (?) AND recipientUUID = (?)) OR (senderUUID = (?) AND recipientUUID = (?))", (requester_uuid, reciever_uuid, reciever_uuid, requester_uuid))
        records = cur.fetchall()
        
        for row in records:
            sender_uuid = row[4]
            message = row[2]
            timestamp = datetime.datetime.fromtimestamp(int(float(row[1])))
            if sender_uuid == requester_uuid:
                messages.append((requester, message, timestamp)) 
            else:
                messages.append((reciever, message, timestamp)) 
        return messages
    
    except:
        return messages

# Delete the message history of a user
# username (String) -> output message (String)
def message_history(username):
    con = sqlite3.connect('client_database.db')
    cur = con.cursor()
    cur.execute("SELECT timestamp, message FROM users u JOIN messages m ON u.uuid = m.senderUUID WHERE u.username = (?)", (username,))
    records = cur.fetchall()

    i = 0
    output = f"""\nSuccessfully deleted the following messages for {username}:"""
    for timestamp, message in records:
        if i == 0 or i == len(records):
            output += "\n"

        dt_object = datetime.datetime.fromtimestamp(float(timestamp)).strftime("%Y/%m/%d %H:%M:%S")
        output += f"{dt_object}: {message}\n"
    
        i += 1

    return output

# Delete the message history of a user (This time there is no output message)
# username (String) -> None
def delete_messages(username):
    con = sqlite3.connect('client_database.db')
    cur = con.cursor()
    username_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(username)))
    cur.execute("DELETE FROM messages WHERE senderUUID = (?)", (username_uuid,))
    con.commit()