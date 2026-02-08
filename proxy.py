import sys
import socket
import threading

HEX_FILTER = ''.join(
    [(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range(256)]
)

def hexdump(src, length=16, show=True):
    if isinstance(src, bytes):
        src = src.decode()
    results = list()
    for i in range(0, len(src), length):
        word = str(src[i:i+length]) # rozdziela string na slowa o dlugosci length
        printable = word.translate(HEX_FILTER)
        # printuje liczbowe reprezentacje liter, ktre potem sa konwertowane na hexy po w znaki po 2 hexy
        hexa = ' '.join([f'{ord(c):02X}' for c in word])

        hexwidth = length*3
        # w pierwszej lini printuje 4 hexy, potem po 2 hexy zdefiniowane w hexa
        results.append(f'{i:04x} {hexa:<{hexwidth}} {printable}')
    if show:
        for line in results:
            print(line)
    else:
        return results

def receive_from(connection):
    buffer = b''
    connection.settimeout(5)
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except Exception as e:
        print('Blad ', e)
        pass
    return buffer

def request_handler(buffer):
    # Tu mozemy zrobic fajne rzeczy z requestami
    return buffer

def response_handler(buffer):
    return buffer

def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))
    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)
    remote_buffer = response_handler(remote_buffer)
    if len(remote_buffer):
        print("[<==] Wyslano %d bajtow do lokalnego hosta." % len(remote_buffer))
        client_socket.send(remote_buffer)

    while True:
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            line = "[<==] Odebrano %d bajtow od lokalnego hosta." % len(local_buffer)
            print(line)
            hexdump(local_buffer)

            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print("[==>] Wyslano do zdalnego hosta")

        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            line = "[<==] Odebrano %d bajtow od zewnetrznego hosta." % len(local_buffer)
            print(line)
            hexdump(remote_buffer)

            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print("[==>] Wyslano do lokalnego hosta.")

        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] Nie ma wiecej danych, zamkniecie polaczenia.")
            break

def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
    except Exception as e:
        print("Problem z utworzeniem gniazda: %r" % e)
        print("[!!] Brak mozliwosci nasluchu na %s:%d"% (local_host, local_port))
        print("[!!] Sprawdz inne gniazda nasluchu lub zmien uprawnienia")
        sys.exit(0)
    print("[*] Nasluch na %s:%d" % (local_host, local_port))
    server.listen(5)
    while True:
        client_socket, addr = server.accept()
        line = "> Odebrano polaczenie przychodzac od %S:%d" % (remote_host, remote_port)
        print(line)
        proxy_thread = threading.Thread(
            target=proxy_handler,
            args=(client_socket, remote_host, remote_port, receive_first)
        )
        proxy_thread.start()

def main():
    if len(sys.argv[1:]) != 5:
        print("Uzycie: ./proxy.py [lokalny gost] [Lokalny port]", end='')
        print("[Zdalny host] [zdalny port] [najpierw_odbieranie]")
        print("Przyklad: python proxy.py 127.0.01 9000 10.12.132.1 9000 True")
        sys.exit(0)

    local_host = sys.argv[1]
    local_port = int(sys.argv[2])

    remote_host = sys.arv[3]
    remote_port = int(sys.arv[4])
    receive_first = sys.argv[5]

    receive_first = True if "True" in receive_first else False

    server_loop(local_host, local_port, remote_host, remote_port, receive_first)

if __name__ == '__main__':
    main()


