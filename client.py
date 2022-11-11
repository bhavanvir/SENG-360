import threading
import socket

# choose a nickname
nickname = input("Choose a nickname: ")

# localhost 
host = '127.0.0.1'
port = 7000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

def receive():
    while True:
        try:
            # receive message from server
            # if 'NICK' send nickname
            message = client.recv(1024).decode('ascii')
            if message == 'NICK':
                client.send(nickname.encode('ascii'))
            else:
                print(message)
        except:
            # close connection when error
            print("An has error occured")
            client.close()
            break

def write():
    while True:
        # send messages to server
        message = f'{nickname}: {input("")}'
        client.send(message.encode('ascii'))

def main():
    # start receiving thread
    receive_thread = threading.Thread(target=receive)
    receive_thread.start()

    # start writing thread
    write_thread = threading.Thread(target=write)
    write_thread.start()

if __name__ == '__main__':
    main()