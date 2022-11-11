import threading
import socket

# choose a username and password
username = input("Choose a username: ")
password = input("Choose a password: ")

# localhost 
host = '127.0.0.1'
port = 7000

# connect to server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

def receive():
    while True:
        try:
            # receive message from server
            # if 'USER' send username, if 'PASS' send password, else print message
            message = client.recv(1024).decode('ascii')
            if message == 'USER':
                client.send(username.encode('ascii'))
            elif message == 'PASS':
                client.send(password.encode('ascii'))
            else:
                print(message)
        except:
            # close connection when error
            print("An has error occured")
            client.close()
            break

def write():
    while True:
        # send message to server
        message = f'{input("")}'
        client.send(message.encode('ascii'))

        # send username to server
        client.send(username.encode('ascii'))

def main():
    # start receiving thread
    receive_thread = threading.Thread(target=receive)
    receive_thread.start()

    # start writing thread
    write_thread = threading.Thread(target=write)
    write_thread.start()

if __name__ == '__main__':
    main()