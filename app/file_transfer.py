import os
import socket
import hashlib
import logging

def send_file(filename, host, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            file_size = os.path.getsize(filename)
            checksum = hashlib.md5(open(filename, 'rb').read()).hexdigest()
            metadata = f"{os.path.basename(filename)}|{file_size}|{checksum}"
            s.sendall(metadata.encode())

            ack = s.recv(1024).decode()
            if ack == "READY":
                with open(filename, 'rb') as f:
                    while chunk := f.read(1024):
                        s.sendall(chunk)
                logging.info(f"File {filename} sent successfully to {host}:{port}")
            else:
                logging.error("Receiver is not ready")
    except Exception as e:
        logging.error(f"Error while sending file: {e}")

def receive_file(save_path, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', port))
            s.listen(1)
            conn, addr = s.accept()
            with conn:
                metadata = conn.recv(1024).decode()
                if '|' not in metadata or metadata.count('|') != 2:
                    raise ValueError("Invalid metadata format received")

                filename, file_size, checksum = metadata.split('|')
                conn.sendall("READY".encode())

                 # Eğer save_path bir dizinse, içine dosya adı ekle
                if os.path.isdir(save_path):
                    save_path = os.path.join(save_path, filename)


                # Dizin oluşturma
                directory = os.path.dirname(save_path)
                if directory and not os.path.exists(directory):
                    os.makedirs(directory)

                with open(save_path, 'wb') as f:
                    received = 0
                    while received < int(file_size):
                        chunk = conn.recv(1024)
                        if not chunk:
                            break
                        f.write(chunk)
                        received += len(chunk)

                logging.info(f"File received and saved to {save_path}")
    except Exception as e:
        logging.error(f"Error while receiving file: {e}")
