import threading 
import socket
import database
import pickle
import base64
import hashlib
import pyDHE
from Crypto import Random
from Crypto.Cipher import AES
from Crypto import Util

# localhost 
host = '127.0.0.1'
port = 7000

# create socket and bind to porty
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((host, port))
server.listen()

clients = []
usernames = []
key_mappings = {}

class AESCipherGCM(object):
    def __init__(self, key): 
        self.blockSize = AES.block_size
        self.key = hashlib.sha256(key).digest()

    def _pad(self, payload):
        padSize = self.blockSize - len(payload) % self.blockSize
        return payload + chr(padSize) * padSize

    @staticmethod
    def _unpad(payload):
        #length = self.blockSize - len(payload) % self.blockSize
        #return payload[:length]
        return payload[:-ord(payload[len(payload)-1:])]

    def encrypt(self, plaintext):
        plaintext = self._pad(plaintext)
        initializationVector = Random.new().read(AES.block_size)
        # Use AES-GCM for encryption
        aes_gcm = AES.new(self.key, AES.MODE_GCM, initializationVector)
        return base64.b64encode(initializationVector + aes_gcm.encrypt(plaintext.encode()))

    def decrypt(self, ciphertext):
        ciphertext = base64.b64decode(ciphertext)
        initializationVector = ciphertext[:AES.block_size]
        aes_gcm = AES.new(self.key, AES.MODE_GCM, initializationVector)
        return self._unpad(aes_gcm.decrypt(ciphertext[AES.block_size:])).decode('ISO-8859-1')

# get all clients and send message to all clients
def broadcast(message):
    for client in clients:
        client.send(message)

# handle messages from clients
def handle(client):
    # Variable to check if successful user authentication has occured
    SUCCESS_LOGIN = False
    
    action = client.recv(1024).decode('ascii')
    # request and store username and password
    client.send('USER'.encode('ascii'))
    username = client.recv(1024).decode('ascii')
    usernames.append(username)
    client.send('PASS'.encode('ascii'))
    password = client.recv(1024).decode('ascii')
    client.send('KEY'.encode('ascii'))
    data = client.recv(4096)
    key = bytearray(data)
    
    if action == "LOGIN":
        if database.check_password(username, password):
            key_mappings[username] = key
            print(f"Succeeded in logging in client with username {username}")
            client.send(f"Successfully logged in as {username}".encode('ascii'))
            SUCCESS_LOGIN = True
        else:
            print(f"Failed in logging in client with username {username}")
            client.send(f"Failed to log in as {username}".encode('ascii'))
            client.send('FAIL'.encode('ascii'))
    
    elif action == "REGISTER":
        if database.insert_user(username, password):
            print(f"Registered client with username {username}")
            client.send(f"Successfully registered as {username}".encode('ascii'))
            SUCCESS_LOGIN = True
        else:
            client.send(f"{username} already exists".encode('ascii'))
            client.send('FAIL'.encode('ascii'))
            print(f"Attemped to register client with username {username}, but it already exists")
    
    elif action == "DELETE":
        if database.check_password(username, password):
            print(f"Deleting user {username}")
            deleted = database.delete_user(username)
            if deleted:
                print(f"Sucessfully deleted user {username}")
                client.send(f"Sucessfully deleted user {username}".encode('ascii'))
                client.send('FAIL'.encode('ascii'))
            else:
                print(f"Error deleting user {username}")
                client.send(f"Error deleting user {username}".encode('ascii'))
                client.send('FAIL'.encode('ascii'))
        else:
            print(f"Failed to find user {username}")
            client.send(f"Invalid user credentials for {username}".encode('ascii'))
            client.send('FAIL'.encode('ascii'))
    
    elif action == "HISTORY":
        if database.message_history(username):
            print(f"Succesfully deleted message history for {username}")
            history = database.message_history(username)
            database.delete_messages(username)
            client.send(history.encode('ascii'))
        else:
            print(f"Failed to delete message history for {username}")
            client.send(f"Failed to find message history for {username}".encode('ascii'))
            client.send('FAIL'.encode('ascii'))
    
    if SUCCESS_LOGIN == True:
        # Display successful authentication message
        clients.append(client)
        
        # Show the messaging options to the user
        client.send('SHOW_MESSAGING_OPTIONS'.encode('ascii'))
        
        # Now that the user has logged in, we will process the subsequent messaging requests
        while True:
            data = client.recv(1024)
            data_obj = pickle.loads(data)
            action = data_obj[0]
            
            if action == "SEND_MSG":
                recipient, message = data_obj[1], data_obj[2]
                if database.user_exists(recipient):
                    database.insert_message(message, recipient, username)
                    print(f"Sent message to: {recipient}")
                    client.send(f"Sent messsage to {recipient}".encode('ascii'))
                else:
                    print(f"Username: {username} does not exist, therefore the message could not be sent")
                    client.send(f"Username: {username} does not exist, therefore the message could not be sent".encode('ascii'))
            
            elif action == "GET_HISTORY":
                # Send message packets to the client
                recipient = data_obj[1]
                messages = database.get_message_history_between_users(username, recipient)
                package = pickle.dumps(messages)
                client.send(package)

# receive and broadcast messages
def receive():
    while True:
        # accept connection
        client, address = server.accept()
        print(f"Connected with {str(address)}")

        #Key exchange
        password = pyDHE.new(16)
        shared_key = password.negotiate(client)
        finalKey = Util.number.long_to_bytes(shared_key)
        print('Keys shared')
        #print(shared_key)
           
         # start handling thread for client
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

def main():
    print("Server is listening...")

    # initialize database
    database.initialize()
    
    # start receiving thread
    receive()

if __name__ == "__main__":
    main()