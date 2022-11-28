import threading
import socket
import os
import maskpass
import pickle
import base64
import hashlib
import pyDHE
from Crypto import Random
from Crypto.Cipher import AES
from Crypto import Util

# choose a username and password
username = ""
password = ""

# localhost 
host = '127.0.0.1'
port = 7000

# connect to server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

#Key exchange
password = pyDHE.new(16)
shared_key = password.negotiate(client)
finalKey = Util.number.long_to_bytes(shared_key)
#print(shared_key)
print('Keys shared')


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
        return self._unpad(aes_gcm.decrypt(ciphertext[AES.block_size:])).decode('utf-8')


def receive():
    while True:
        # receive message from server
        # if 'USER' send username, if 'PASS' send password, else print message
        message = client.recv(1024).decode('ascii')
        if message == 'ACTION':
            client.send('LOGIN'.encode('ascii'))
        elif message == 'USER':
            client.send(username.encode('ascii'))
        elif message == 'PASS':
            client.send(password.encode('ascii'))
        elif message == 'SHOW_MESSAGING_OPTIONS':
            show_message_options()
        elif message == 'FAIL':
            client.shutdown(socket.SHUT_RDWR)
            client.close()
            # dirty solution to force program to exit without waiting for threads to finish
            os._exit(1)
        else:
            print(message)

def show_message_options():
    while True:
        query = input("Do you want to send a message to a user (1) or see your message history with a user (2): ")
        # Send messagec case
        if query == "1":
            recipient = input("Enter the recipient's username: ")
            # This message will be sent encrypted once end-to-end messaging is added
            message = input(f"Enter the message you would like to send to {recipient}: ")
            enc_string = AESCipherGCM(finalKey).encrypt(message)
            #print(enc_string)
            package = pickle.dumps(("SEND_MSG", recipient, enc_string))
            client.send(package)
            return_message = client.recv(1024).decode('ascii')
            print(return_message)
        # Retrieve message history case
        elif query == "2":
            recipient = input("Enter the username to see your message history with them: ")
            package = pickle.dumps(("GET_HISTORY", recipient))
            client.send(package)
            return_package = client.recv(2048)
            messages = pickle.loads(return_package)
            if len(messages) == 0:
                print(f"No messaging history found with user {recipient}")
            else:
                for message_tuple in messages:
                    # Once end-to-end encyption is implemented, we need to decrypt the content of message_tuple[1]
                    print(f"<{message_tuple[0]} @ {message_tuple[2]}> {AESCipherGCM(finalKey).decrypt(message_tuple[1])}")
        else:
            print("Invalid input")


def write():
    while True:
        # send message to server
        message = f'{input("")}'
        client.send(message.encode('ascii'))

        # send username to server
        client.send(username.encode('ascii'))

def main():
    global username
    global password 

    query = input("Do you want to login (1), register (2), delete an account (3) or delete your message history (4)?: ")
    
    if query == "1" or query.lower() == "login":
        client.send('LOGIN'.encode('ascii'))
    elif query == "2" or query.lower() == "register":
        client.send('REGISTER'.encode('ascii'))
    elif query == "3" or query.lower() == "delete":
        client.send('DELETE'.encode('ascii'))
    elif query == "4" or query.lower() == "history":
        client.send('HISTORY'.encode('ascii'))
    else:
        print("Invalid input")
        main()
    
    username = input("Enter username: ")
    password = maskpass.askpass(prompt="Enter password: ")

    # start receiving thread
    receive_thread = threading.Thread(target=receive)
    receive_thread.start()

    # start writing thread
    #write_thread = threading.Thread(target=write)
    #write_thread.start()

    receive_thread.join()
    #write_thread.join()

if __name__ == '__main__':
    main()