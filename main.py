from pytube import YouTube
import pytube
from PyQt6.QtWidgets import QApplication, QWidget, QComboBox, QMainWindow, QVBoxLayout, QPushButton, QLineEdit, QProgressBar
import sys
from threading import Thread

# https://www.youtube.com/watch?v=D-eDNDfU3oY

pytube.request.default_range_size = 1048576

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.available_settings = []
        self.choose_settings = QComboBox()
        self.choose_settings.addItems(self.available_settings)

        self.download_button = QPushButton("Download", self)
        self.download_button.clicked.connect(self.download)

        self.input_line = QLineEdit(self)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)

        self.load_info_button = QPushButton("Load video info", self)
        self.load_info_button.clicked.connect(self.load_info_thread)

        layout = QVBoxLayout()
        layout.addWidget(self.input_line)
        layout.addWidget(self.load_info_button)
        layout.addWidget(self.choose_settings)
        layout.addWidget(self.download_button)
        layout.addWidget(self.progress_bar)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
    def download(self):
        downloading_process = Thread(target=self.execute_process(self.input_line.text()))
        downloading_process.start()

    def load_info_thread(self):
        load_info_process = Thread(target=self.load_info(self.input_line.text()))
        load_info_process.start()

    def on_progress(self, stream, chunk, bytes_remaining):
        size = stream.filesize
        progress = int(((size - bytes_remaining) / size) * 100)
        self.progress_bar.setValue(progress)
    
    def execute_process(self, link):
        self.progress_bar.setValue(0)
        self.input_line.clear()
        yt = YouTube(link, on_progress_callback=self.on_progress)
        stream = yt.streams.filter(res='720p').first()
        stream.download()

    def load_info(self, link):
        yt = YouTube(link, on_progress_callback=self.on_progress)
        for stream in yt.streams:
            description = str(stream.type) + str(stream.resolution) + str(stream.fps)
            self.available_settings.append(description)
        self.choose_settings.addItems(self.available_settings)

if __name__ == '__main__':
    main()