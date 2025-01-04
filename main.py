from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLineEdit, QLabel, QTextEdit, QFileDialog
)
from PyQt5.QtCore import pyqtSignal
import logging
import sys
import threading
import socket
from app.file_transfer import send_file, receive_file

class P2PFileSharingApp(QMainWindow):
    log_signal = pyqtSignal(str)  # Signal to safely update logs from threads

    def __init__(self):
        super().__init__()
        self.setWindowTitle("P2P File Sharing Application")
        self.resize(800, 600)

        # Internal variables for managing connections
        self.sender_socket = None
        self.receiver_socket = None
        self.sender_conn = None  # For persistent sender connection

        # Connect the signal to a slot for updating logs
        self.log_signal.connect(self.append_log)

        # Main Layout
        self.layout = QVBoxLayout()

        # Host and Port Fields
        self.layout.addWidget(QLabel("Enter Host (IP):"))
        self.host_input = QLineEdit()
        self.layout.addWidget(self.host_input)

        self.layout.addWidget(QLabel("Enter Port:"))
        self.port_input = QLineEdit()
        self.layout.addWidget(self.port_input)

        # File Selection
        self.layout.addWidget(QLabel("File to Send:"))
        self.file_path_input = QLineEdit()
        self.layout.addWidget(self.file_path_input)

        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_file)
        self.layout.addWidget(self.browse_button)

        # Start Sender Button
        self.start_sender_button = QPushButton("Start Sender")
        self.start_sender_button.clicked.connect(self.start_sender)
        self.layout.addWidget(self.start_sender_button)

        # Start Receiver Button
        self.start_receiver_button = QPushButton("Start Receiver")
        self.start_receiver_button.clicked.connect(self.start_receiver)
        self.layout.addWidget(self.start_receiver_button)

        # Send File Button
        self.send_file_button = QPushButton("Send File")
        self.send_file_button.clicked.connect(self.send_file_action)
        self.layout.addWidget(self.send_file_button)

        # Log Display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.layout.addWidget(QLabel("Logs:"))
        self.layout.addWidget(self.log_display)

        # Set Main Layout
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    def append_log(self, message):
        """Append a log message to the log display."""
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
            self.sender_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sender_socket.connect((host, port))
            self.sender_conn = self.sender_socket  # Keep connection alive
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
            conn, addr = self.receiver_socket.accept()
            self.log_signal.emit(f"Connected to sender: {addr}. Ready to receive files.")
            while True:  # Keep listening for files
                threading.Thread(target=self.receive_file_wrapper, args=(save_directory, conn), daemon=True).start()
        except Exception as e:
            self.log_signal.emit(f"Error establishing receiver connection: {e}")

    def receive_file_wrapper(self, save_directory, conn):
        try:
            receive_file(save_directory, conn)
            self.log_signal.emit("File received successfully.")
        except Exception as e:
            self.log_signal.emit(f"Error receiving file: {e}")

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = P2PFileSharingApp()
    main_window.show()
    sys.exit(app.exec_())
