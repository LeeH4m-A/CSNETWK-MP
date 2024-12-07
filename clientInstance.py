import socket
import os

SERVER_HOST = "127.0.0.1"  # Update with server's IP
SERVER_PORT = 12345

def send_file(filepath, clientSocket):
    if not os.path.exists(filepath):
        print("Error: File not found.")
        return
    file_name = os.path.basename(filepath)
    clientSocket.send(f"/store {file_name}".encode())
    response = clientSocket.recv(1024).decode()
    if response == "READY":
        with open(filepath, "rb") as file:
            while chunk := file.read(4096):
                clientSocket.send(chunk)
        print("File Sent")
        clientSocket.send(b"EOF")
        print(clientSocket.recv(1024).decode())

def receive_file(file_name, client_socket):
    client_socket.send(f"/get {file_name}".encode())
    response = client_socket.recv(1024).decode()
    if response == "READY":
        with open(file_name, "wb") as file:
            while True:
                data = client_socket.recv(4096)
                if data == b"EOF":
                    break
                file.write(data)
        print(f"File {file_name} downloaded successfully.")
    else:
        print(response)

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            serverJoined = False
            registered = False
            while True:
                print("What would you like to do?")
                print("\n\n")
                command = input(">")
                if command == "/?":
                    print("Printing commands list...")
                    print("""
                        __________________________________________________________________________________________________
                        COMMANDS LIST:
                                Connect to the Server Application:                      /join <server_ip_add> <port>
                                Disconnect from the Server Application:                 /leave                 
                                Register a handle/alias:                                /register <handle>
                                Send a file to the Server:                              /store <filename>              
                                Request the directory file list from the Server:        /dir
                                Fetch a file from the Server:                           /get <filename>
                                Request the list of commands:                           /?
                        __________________________________________________________________________________________________      
                        """)
                elif command.startswith("/join"):
                    if command.removeprefix("/join ") == "127.0.0.1 12345":
                        client_socket.connect((SERVER_HOST, SERVER_PORT))
                        print("Connection to the File Exchange Server is successful!")
                        serverJoined = True
                    else:
                        print("Error: Connection to the Server has failed! Please check IP Address and Port Number.")   
                elif command.startswith("/store"):
                    if (not serverJoined) or (not registered):
                        print("Error: You must connect to the server and register first before sending/storing files.")
                    else:
                        file_path = command.split(" ", 1)[1]
                        send_file(file_path, client_socket)
                elif command.startswith("/get"):
                    if (not serverJoined) or (not registered):
                        print("Error: You must connect to the server and register first before requesting any files.")
                    else:
                        file_name = command.split(" ", 1)[1]
                        receive_file(file_name, client_socket)
                elif command == "/leave":
                    if not serverJoined:
                        print("Error: There is no connected server to leave")
                    else:
                        break
                elif command == "/dir":
                    if (not serverJoined) or (not registered):
                        print("Error: You must connect to the server and register first before requesting the directory list.")
                    else:
                        client_socket.send(command.encode())
                        response = client_socket.recv(1024).decode()
                        print(response)
                elif command.startswith("/register"):
                    if (not serverJoined):
                        print("Error: You must connect to the server first before registering an alias.")
                    else:
                        client_socket.send(command.encode())
                        response = client_socket.recv(1024).decode()
                        print(response)
                        if response.startswith("Welcome"):
                            registered = True
                else:
                    if (not serverJoined) or (not registered):
                        print("Command Not Found.")
                    else:
                        client_socket.send(command.encode())
                        response = client_socket.recv(1024).decode()
                        print(response)
                input("Press ENTER to continue...")
                os.system('cls')
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
