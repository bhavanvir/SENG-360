import threading 
import socket

# localhost 
host = '127.0.0.1'
port = 7000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((host, port))
server.listen()

clients = []
nicknames = []

# get all clients and send message to all clients
def broadcast(message):
    for client in clients:
        client.send(message)

# handle messages from clients
def handle(client):
    while True:
        try:
            # broadcast message
            message = client.recv(1024)
            broadcast(message)
        except:
            # remove and close client connection
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nickname[index]
            broadcast(f'{nickname} has left the chat'.encode('ascii'))
            nicknames.remove(nickname)
            break

# receive and broadcast messages
def receive():
    while True:
        # accept connection
        client, address = server.accept()
        print(f"Connected with {str(address)}")

        # request and store nickname
        client.send('NICK'.encode('ascii'))
        nickname = client.recv(1024).decode('ascii')
        nicknames.append(nickname)
        clients.append(client)

        # print and broadcast nickname
        print(f"Nickname of the client is {nickname}")
        broadcast(f"{nickname} joined the chat".encode('ascii'))
        client.send('Connected to the server'.encode('ascii'))

        # start handling thread for client
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

def main():
    print("Server is listening...")
    receive()

if __name__ == "__main__":
    main()