import os
import logging
import socket
import threading
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLineEdit, QLabel, QTextEdit, QFileDialog
)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt  # Qt sınıfını ekledik
# Logger Setup
def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("logs/p2p_log.txt"),
            logging.StreamHandler()
        ]
    )

setup_logger()

# File Transfer Functions
def send_file(file_path, conn):
    try:
        file_size = os.path.getsize(file_path)
        metadata = f"{os.path.basename(file_path)}|{file_size}"
        logging.info(f"[Sender] Sending metadata: {metadata}")
        conn.sendall(metadata.encode())  # Metadata gönder

        # Acknowledgment bekle
        ack = conn.recv(1024).decode()
        if ack != "READY":
            logging.error("[Sender] Receiver not ready.")
            return

        # Dosya gönder
        with open(file_path, "rb") as f:
            while chunk := f.read(1024):
                conn.sendall(chunk)
        logging.info(f"[Sender] File {file_path} sent successfully.")
        
        # Gönderim sonrası bir ACK daha bekle
        final_ack = conn.recv(1024).decode()
        if final_ack == "DONE":
            logging.info("[Sender] Receiver confirmed file received.")
    except Exception as e:
        logging.error(f"[Sender] Error during file sending: {e}")

def receive_file(conn, save_directory):
    try:
        while True:  # Bağlantı açık olduğu sürece dinle
            metadata = conn.recv(1024).decode()
            if not metadata:
                break  # Bağlantı kesildi
            logging.info(f"[Receiver] Metadata received: {metadata}")
            
            if "|" not in metadata:
                conn.sendall("ERROR".encode())
                continue

            filename, file_size = metadata.split("|")
            file_size = int(file_size)

            # Hazır olduğunu bildir
            conn.sendall("READY".encode())
            
            # Seçilen dizine dosyayı kaydet
            save_path = os.path.join(save_directory, filename)
            os.makedirs(save_directory, exist_ok=True)

            with open(save_path, "wb") as f:
                received = 0
                while received < file_size:
                    chunk = conn.recv(1024)
                    if not chunk:
                        break
                    f.write(chunk)
                    received += len(chunk)

            logging.info(f"[Receiver] File received and saved to {save_path}.")
            
            # Göndericiye tamamlandığını bildir
            conn.sendall("DONE".encode())
    except Exception as e:
        logging.error(f"[Receiver] Error during file reception: {e}")

class P2PFileSharingApp(QMainWindow):
    log_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("P2P File Sharing Application")
        self.resize(900, 650)
        self.closing = False
        self.sender_socket = None
        self.receiver_socket = None
        self.sender_conn = None

        self.log_signal.connect(self.append_log)

        # Main Layout
        self.main_layout = QVBoxLayout()

        # Header Section
        self.header_label = QLabel("P2P File Sharing Application")
        self.header_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.header_label.setStyleSheet("color: #003399; margin: 10px 0;")
        self.header_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.header_label)

        # Host and Port Input
        self.input_layout = QHBoxLayout()
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("Enter Host (IP)")
        self.input_layout.addWidget(QLabel("Host: "))
        self.input_layout.addWidget(self.host_input)

        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("Enter Port")
        self.input_layout.addWidget(QLabel("Port: "))
        self.input_layout.addWidget(self.port_input)
        self.main_layout.addLayout(self.input_layout)

        # File Selection Section
        self.file_layout = QHBoxLayout()
        self.file_path_input = QLineEdit()
        self.file_path_input.setPlaceholderText("Select a file to send")
        self.file_layout.addWidget(self.file_path_input)

        self.browse_button = QPushButton("Browse")
        self.browse_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px 15px;")
        self.browse_button.clicked.connect(self.browse_file)
        self.file_layout.addWidget(self.browse_button)
        self.main_layout.addLayout(self.file_layout)

        # Action Buttons
        self.button_layout = QHBoxLayout()
        self.start_sender_button = QPushButton("Start Sender")
        self.start_sender_button.setStyleSheet("background-color: #2196F3; color: white;")
        self.start_sender_button.clicked.connect(self.start_sender)
        self.button_layout.addWidget(self.start_sender_button)

        self.start_receiver_button = QPushButton("Start Receiver")
        self.start_receiver_button.setStyleSheet("background-color: #2196F3; color: white;")
        self.start_receiver_button.clicked.connect(self.start_receiver)
        self.button_layout.addWidget(self.start_receiver_button)

        self.send_file_button = QPushButton("Send File")
        self.send_file_button.setStyleSheet("background-color: #FF5722; color: white;")
        self.send_file_button.clicked.connect(self.send_file_action)
        self.button_layout.addWidget(self.send_file_button)

        self.main_layout.addLayout(self.button_layout)

        # Logs Section
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("border: 1px solid #ccc; background-color: #f9f9f9;")
        self.main_layout.addWidget(QLabel("Logs:"))
        self.main_layout.addWidget(self.log_display)

        # Set Main Layout
        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

    def append_log(self, message):
        self.log_display.append(message)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if file_path:
            self.file_path_input.setText(file_path)

    def start_sender(self):
        host = self.host_input.text()
        port = int(self.port_input.text())

        if host and port:
            threading.Thread(target=self.run_sender_connection, args=(host, port), daemon=True).start()
        else:
            self.log_signal.emit("Please enter valid host and port to start sender.")

    def run_sender_connection(self, host, port):
        try:
            if self.sender_socket:
                self.sender_socket.close()
            self.sender_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sender_socket.connect((host, port))
            self.sender_conn = self.sender_socket
            self.log_signal.emit(f"Sender connected to {host}:{port}. Ready to send files.")
        except Exception as e:
            self.log_signal.emit(f"Error establishing sender connection: {e}")

    def start_receiver(self):
        save_directory = QFileDialog.getExistingDirectory(self, "Select Save Directory")
        port = int(self.port_input.text())

        if save_directory and port:
            threading.Thread(target=self.run_receiver_connection, args=(save_directory, port), daemon=True).start()
        else:
            self.log_signal.emit("Please select a directory and enter a valid port.")

    def run_receiver_connection(self, save_directory, port):
        try:
            self.receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.receiver_socket.bind(("", port))
            self.receiver_socket.listen(1)
            self.log_signal.emit(f"Receiver listening on port {port}...")
            while True:  # Bağlantıyı açık tut
                conn, addr = self.receiver_socket.accept()
                self.log_signal.emit(f"Connected to sender: {addr}. Ready to receive files.")
                self.receive_file_wrapper(conn, save_directory)
        except Exception as e:
            self.log_signal.emit(f"Error establishing receiver connection: {e}")
        finally:
            if self.receiver_socket:
                self.receiver_socket.close()

    def receive_file_wrapper(self, conn, save_directory):
        try:
            receive_file(conn, save_directory)
            self.log_signal.emit("File received successfully.")
        except Exception as e:
            self.log_signal.emit(f"Error receiving file: {e}")
        finally:
            if conn:
                conn.close()

    def send_file_action(self):
        file_path = self.file_path_input.text()

        if file_path and self.sender_conn:
            self.log_signal.emit(f"Preparing to send file: {file_path}...")
            threading.Thread(target=self.run_send_file, args=(file_path,), daemon=True).start()
        else:
            self.log_signal.emit("Please select a file and ensure the sender is connected.")

    def run_send_file(self, file_path):
        try:
            send_file(file_path, self.sender_conn)
            self.log_signal.emit(f"File {file_path} sent successfully.")
        except Exception as e:
            self.log_signal.emit(f"Error sending file: {e}")

    def close_application(self):
        self.closing = True
        if self.receiver_socket:
            self.receiver_socket.close()
        if self.sender_socket:
            self.sender_socket.close()
        self.close()

if __name__ == "__main__":
    app = QApplication([])
    main_window = P2PFileSharingApp()
    main_window.show()
    app.exec_()
