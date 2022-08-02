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

        self.available_settings = {}
        self.selected_settings = None
        self.choose_settings = QComboBox()
        self.choose_settings.currentTextChanged.connect(self.item_selected)

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
        downloading_process = Thread(target=self.execute_process(self.input_line.text(), self.selected_settings))
        downloading_process.start()

    def load_info_thread(self):
        load_info_process = Thread(target=self.load_info(self.input_line.text()))
        load_info_process.start()

    def on_progress(self, stream, chunk, bytes_remaining):
        size = stream.filesize
        progress = int(((size - bytes_remaining) / size) * 100)
        self.progress_bar.setValue(progress)
    
    def execute_process(self, link, settings):
        link1 = 'https://www.youtube.com/watch?v=D-eDNDfU3oY'
        self.progress_bar.setValue(0)
        self.input_line.clear()
        yt = YouTube(link1, on_progress_callback=self.on_progress)
        itag = list(self.available_settings.keys())[list(self.available_settings.values()).index(settings)]
        stream = yt.streams.get_by_itag(itag)
        print(stream)
        stream.download()

    def load_info(self, link):
        link1 = 'https://www.youtube.com/watch?v=D-eDNDfU3oY'
        self.choose_settings.clear()
        yt = YouTube(link1, on_progress_callback=self.on_progress)
        for index, stream in enumerate(yt.streams.filter(type='video').order_by('resolution'), 1):
                description = '[' + str(index) + '] ' + str(stream.type) + ' ' + str(stream.resolution) + ' ' +  str(stream.fps) + 'fps'
                self.available_settings[stream.itag] = description
        for index, stream in enumerate(yt.streams.filter(type='audio').order_by('abr'), 1):
                description = '[' + str(index) + '] ' + str(stream.type) + ' ' + str(stream.abr)
                self.available_settings[stream.itag] = description
        self.choose_settings.addItems(self.available_settings.values())

    def item_selected(self):
        self.selected_settings = self.choose_settings.currentText()

if __name__ == '__main__':
    main()