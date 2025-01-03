import socket

def send_file(filename, host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        with open(filename, 'rb') as f:
            while chunk := f.read(1024):
                s.sendall(chunk)

def receive_file(save_path, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', port))
        s.listen(1)
        conn, addr = s.accept()
        with conn:
            with open(save_path, 'wb') as f:
                while chunk := conn.recv(1024):
                    f.write(chunk)
