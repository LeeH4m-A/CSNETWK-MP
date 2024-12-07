import socket
import os
import threading
from datetime import datetime

HOSTADD = "127.0.0.1"
HOSTPORT = 12345
DIRECTORY = "./server_files" 

os.makedirs(DIRECTORY, exist_ok=True)

serverClients = {}

def clientManager(clientSocket, clientAddress):
    try:
        while True:
            data = clientSocket.recv(1024).decode()
            if not data:
                break
            print(f"Command from {clientAddress}: {data}")

            arguments = data.split(' ', 1)
            command = arguments[0]
            params = arguments[1] if len(arguments) > 1 else ""

            if command == "/join":
                if params == "127.0.0.1 12345":
                    clientSocket.send("Connection to the File Exchange Server is successful!".encode())
            elif command == "/leave":
                clientSocket.send("Connection closed. Thank you!".encode())
                break
            elif command == "/register":
                registerCommand(clientSocket, params)
            elif command == "/store":
                storeCommand(clientSocket, params)
            elif command == "/dir":
                dirCommand(clientSocket)
            elif command == "/get":
                getCommand(clientSocket, params)
            else:
                clientSocket.send("Error: Command not found.".encode())
    except Exception as errorReceipt:
        print(f"Error handling client {clientAddress}: {errorReceipt}")
    finally:
        if clientSocket in serverClients:
            del serverClients[clientSocket]
        clientSocket.close()

def registerCommand(clientSocket, alias):
    if alias in serverClients.values():
        clientSocket.send("Error: Registration failed. Handle or alias already exists.".encode())
    elif len(alias) == 0:
        clientSocket.send("Error: Registration failed. Invalid alias/syntax.".encode())
    else:
        serverClients[clientSocket] = alias
        clientSocket.send(f"Welcome {alias}!".encode())
        
def storeCommand(clientSocket, filename):
    try:
        clientSocket.send("READY".encode())
        filepath = os.path.join(DIRECTORY, filename)
        with open(filepath, "wb") as file:
            while True:
                data = clientSocket.recv(4096)
                if data == b"EOF":
                    break
                file.write(data)
        clientSocket.send(f"{filename} uploaded successfully.".encode())
    except Exception as errorReceipt:
        print(f"Error storing file {filename}: {errorReceipt}")
        clientSocket.send("Error: File upload failed.".encode())

def dirCommand(clientSocket):
    files = os.listdir(DIRECTORY)
    response = "Server Directory:\n" + "\n".join(files)
    clientSocket.send(response.encode())

def getCommand(clientSocket, filename):
    filepath = os.path.join(DIRECTORY, filename)
    if os.path.exists(filepath):
        clientSocket.send("READY".encode())
        with open(filepath, "rb") as file:
            while chunk := file.read(4096):
                clientSocket.send(chunk)
        clientSocket.send(b"EOF")
    else:
        clientSocket.send("Error: File not found in the server.".encode())

    

        
        
def runServer():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serverSocket:
        serverSocket.bind((HOSTADD, HOSTPORT))
        serverSocket.listen(3)
        print(f"Server running on {HOSTADD} : {HOSTPORT}")
        while True:
            clientSocket, clientAddress = serverSocket.accept()
            print(f"New connection from {clientAddress}")
            threading.Thread(target = clientManager, args=(clientSocket, clientAddress)).start()

if __name__ == "__main__":
    runServer()
