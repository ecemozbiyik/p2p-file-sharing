from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QPushButton, QFileDialog
import logging
import sys


class LogHandler(logging.Handler):
    def __init__(self, text_edit):
        super().__init__()
        self.text_edit = text_edit

    def emit(self, record):
        log_entry = self.format(record)
        self.text_edit.append(log_entry)


class P2PLogViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("P2P File Sharing Logs")
        self.resize(800, 600)

        # Log Display
        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)

        # Buttons
        self.clear_logs_button = QPushButton("Clear Logs", self)
        self.clear_logs_button.clicked.connect(self.clear_logs)

        self.export_logs_button = QPushButton("Export Logs", self)
        self.export_logs_button.clicked.connect(self.export_logs)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        layout.addWidget(self.clear_logs_button)
        layout.addWidget(self.export_logs_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Setup Logger
        self.setup_logger()

    def setup_logger(self):
        handler = LogHandler(self.text_edit)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(logging.INFO)

        # Log an initial message
        logging.info("P2P File Sharing Log Viewer Started")

    def clear_logs(self):
        """Clear the logs displayed in the text edit."""
        self.text_edit.clear()
        logging.info("Logs cleared")

    def export_logs(self):
        """Export logs to a file."""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Logs As", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_path:
            with open(file_path, "w") as file:
                file.write(self.text_edit.toPlainText())
            logging.info(f"Logs exported to {file_path}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = P2PLogViewer()
    viewer.show()
    sys.exit(app.exec_())
