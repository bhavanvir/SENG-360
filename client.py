import threading
import socket
import os
import maskpass

# choose a username and password
username = ""
password = ""

# localhost 
host = '127.0.0.1'
port = 7000

# connect to server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

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
        elif message == 'FAIL':
            client.shutdown(socket.SHUT_RDWR)
            client.close()
            # dirty solution to force program to exit without waiting for threads to finish
            os._exit(1)
        else:
            print(message)

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
    write_thread = threading.Thread(target=write)
    write_thread.start()

    receive_thread.join()
    write_thread.join()

if __name__ == '__main__':
    main()