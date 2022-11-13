import threading
import socket
import os

# choose a username and password
username = ""
password = ""

# localhost 
host = '127.0.0.1'
port = 7000

# connect to server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect((host, port))

def receive():
    while True:
        # receive message from server
        # if 'USER' send username, if 'PASS' send password, else print message
        message = server.recv(1024).decode('ascii')
        if message == 'ACTION':
            server.send('LOGIN'.encode('ascii'))
        elif message == 'USER':
            server.send(username.encode('ascii'))
        elif message == 'PASS':
            server.send(password.encode('ascii'))
        elif message == 'FAIL':
            server.shutdown(socket.SHUT_RDWR)
            server.close()
            # dirty solution to force program to exit without waiting for threads to finish
            os._exit(1)
        else:
            print(message)

def write():
    while True:
        # send message to server
        message = f'{input("")}'
        server.send(message.encode('ascii'))

        # send username to server
        server.send(username.encode('ascii'))

def main():
    global username
    global password 

    query = input("Do you want to login (1), register (2) or delete an account (3) ?: ")
    
    if query == "1" or query == "login":
        server.send('LOGIN'.encode('ascii'))
    elif query == "2" or query == "register":
        server.send('REGISTER'.encode('ascii'))
    elif query == "3" or query == "delete":
        server.send('DELETE'.encode('ascii'))
    else:
        print("Invalid input")
        main()
    
    username = input("Enter username: ")
    password = input("Enter password: ")

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