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

def receive_file(save_directory, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', port))
            s.listen(1)
            logging.info(f"Listening for connections on port {port}...")
            conn, addr = s.accept()
            with conn:
                logging.info(f"Connection established with {addr}")

                # Step 1: Receive metadata
                metadata = conn.recv(1024).decode()
                if '|' not in metadata or metadata.count('|') != 2:
                    raise ValueError("Invalid metadata format received")

                filename, file_size, checksum = metadata.split('|')
                file_size = int(file_size)

                # Step 2: Construct the save path
                save_path = os.path.join(save_directory, filename)

                # Create the save directory if it doesn't exist
                os.makedirs(save_directory, exist_ok=True)

                # Step 3: Send READY signal to the sender
                conn.sendall("READY".encode())

                # Step 4: Receive the file in chunks
                received = 0
                with open(save_path, 'wb') as f:
                    while received < file_size:
                        chunk = conn.recv(1024)
                        if not chunk:
                            break
                        f.write(chunk)
                        received += len(chunk)

                # Step 5: Validate the checksum
                received_checksum = hashlib.md5(open(save_path, 'rb').read()).hexdigest()
                if received_checksum == checksum:
                    logging.info(f"File received successfully and saved to {save_path}")
                else:
                    logging.error("Checksum mismatch! File may be corrupted.")

    except Exception as e:
        logging.error(f"Error while receiving file: {e}")

