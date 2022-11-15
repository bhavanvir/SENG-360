import threading 
import socket
import database

# localhost 
host = '127.0.0.1'
port = 7000

# create socket and bind to port
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((host, port))
server.listen()

clients = []
usernames = []

# get all clients and send message to all clients
def broadcast(message):
    for client in clients:
        client.send(message)

# handle messages from clients
def handle(client):
    while True:
        try:
            # broadcast message
            message = client.recv(1024).decode('ascii')
            username = client.recv(1024).decode('ascii')
            recipients = [user for user in usernames if user != username]
            database.insert_message(message, recipients, username)
            broadcast_message = f"{username}: {message}".encode('ascii')
            broadcast(broadcast_message)
        except:
            # remove and close client connection
            index = clients.index(client)
            clients.remove(client)
            client.close()
            username = usernames[index]
            broadcast(f'{username} has left the chat'.encode('ascii'))
            usernames.remove(username)
            break

# receive and broadcast messages
def receive():
    while True:
        # accept connection
        client, address = server.accept()
        print(f"Connected with {str(address)}")

        action = client.recv(1024).decode('ascii')

        # request and store username and password
        client.send('USER'.encode('ascii'))
        username = client.recv(1024).decode('ascii')
        usernames.append(username)

        client.send('PASS'.encode('ascii'))
        password = client.recv(1024).decode('ascii')

        if action == "LOGIN":
            if database.check_password(username, password):
                print(f"Succeeded in logging in client with username {username}")
                client.send(f"Successfully logged in as {username}".encode('ascii'))
            else:
                print(f"Failed in logging in client with username {username}")
                client.send(f"Failed to log in as {username}".encode('ascii'))
                client.send('FAIL'.encode('ascii'))
                exit(1)
        elif action == "REGISTER":
            if database.insert_user(username, password):
                print(f"Registered client with username {username}")
                client.send(f"Successfully registered as {username}".encode('ascii'))
            else:
                client.send(f"{username} already exists".encode('ascii'))
                client.send('FAIL'.encode('ascii'))
                print(f"Attemped to register client with username {username}, but it already exists")

                try:
                    server.shutdown(socket.SHUT_RDWR)
                    server.close()
                except OSError:
                    break
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

        if action != "DELETE":
            # Display successful authentication message
            clients.append(client)

            # print and broadcast username
            broadcast(f"{username} joined the chat\n".encode('ascii'))
            client.send('Connected to the server'.encode('ascii'))

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