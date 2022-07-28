from pytube import YouTube
import pytube
from PyQt6.QtWidgets import QApplication, QWidget, QComboBox, QMainWindow, QVBoxLayout, QPushButton, QLineEdit, QProgressBar
import sys
from threading import Thread

pytube.request.default_range_size = 1048576
videos_resolutions = ['144p','240p','360p','480p','720p','1080p']
videos_fps = ['15fps','30fps','60fps']

def on_progress(stream, chunk, bytes_remaining):
    size = stream.filesize
    progress = int(((size - bytes_remaining) / size) * 100)
    print(progress)
    self.progress_bar.setValue(progress)
    
def execute_process(link):

    link1 = 'https://www.youtube.com/watch?v=D-eDNDfU3oY'
    yt = YouTube(link1, on_progress_callback=on_progress)

    stream = yt.streams.filter(res='720p').first()
    stream.download()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.choose_resolution = QComboBox()
        self.choose_resolution.addItems(videos_resolutions)

        self.choose_fps = QComboBox()
        self.choose_fps.addItems(videos_fps)

        self.download_button = QPushButton("Download", self)
        self.download_button.clicked.connect(self.download)

        self.input_line = QLineEdit(self)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)

        layout = QVBoxLayout()
        layout.addWidget(self.input_line)
        layout.addWidget(self.choose_resolution)
        layout.addWidget(self.choose_fps)
        layout.addWidget(self.download_button)
        layout.addWidget(self.progress_bar)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
    def download(self):
        downloading_process = Thread(target=execute_process(self.input_line.text()))
        downloading_process.start()

if __name__ == '__main__':
    main()