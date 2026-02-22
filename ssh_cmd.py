from os import name

import paramiko

def ssh_command(ip, port, user, passwd, cmd):
    # tworzymy obiekt paramiko > dodajemy missing policy > łączymy sie
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port=port, username=user, password=passwd)

    # wykonaj komende
    _, stdout, stderr = client.exec_command(cmd)
    # zbierz output i wyprintuj po linijce
    output = stdout.readlines() + stderr.readlines()
    if output:
        print("=== Wyniki ===")
        for line in output:
            print(line.strip())


if __name__ == '__main__':
    import getpass

    user = input('Nazwa uzytkownika')
    password = getpass.getpass("Podaj haslo")
    ip = input("Adres serwera: ")
    port = input("Port serwera: ") or 2222
    cmd = input("Exec: ") or 'id'

    ssh_command(ip, port, user, password, cmd)

