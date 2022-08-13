from pytube import YouTube
import pytube
from PyQt6.QtWidgets import QApplication, QWidget, QComboBox, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QProgressBar, QLabel, QGridLayout
import sys
from threading import Thread
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt
import requests

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

        self.video_thumbnail  = QLabel()
        self.pixmap = QPixmap('thumbnail_placeholder.png')
        self.video_thumbnail.setPixmap(self.pixmap)

        self.download_button = QPushButton("Download", self)
        self.download_button.clicked.connect(self.download)
        self.download_button.setEnabled(False)

        self.input_line = QLineEdit(self)
        self.input_line.setPlaceholderText("Enter link") 

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)

        self.load_info_button = QPushButton("Load video info", self)
        self.load_info_button.clicked.connect(self.load_info_thread)

        self.video_title = QLabel()
        self.video_author = QLabel()
        self.user_info = QLabel()

        self.video_title.setText("Title: ")
        self.video_author.setText("Author: ")
        self.user_info.setStyleSheet("color: gray")
        self.user_info.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QGridLayout()
        layout.setSpacing(10)
        layout.setColumnMinimumWidth(0,300)

        layout.addWidget(self.input_line,0,0)
        layout.addWidget(self.load_info_button,1,0)
        layout.addWidget(self.choose_settings,2,0)
        layout.addWidget(self.download_button,3,0)
        layout.addWidget(self.progress_bar,4,0)
        layout.addWidget(self.user_info,5,0)

        layout.addWidget(self.video_title,0,1)
        layout.addWidget(self.video_author,1,1)
        layout.addWidget(self.video_thumbnail,2,1,5,1)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.setWindowTitle('YouThon')
        self.setWindowIcon(QIcon('icon.png'))
        
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
        self.progress_bar.setValue(0)
        self.input_line.clear()
        yt = YouTube(link, on_progress_callback=self.on_progress)
        itag = list(self.available_settings.keys())[list(self.available_settings.values()).index(settings)]
        stream = yt.streams.get_by_itag(itag)
        stream.download()
        self.user_info.setText("Media downloaded succesfully.")

    def load_info(self, link):
        self.choose_settings.clear()
        yt = YouTube(link, on_progress_callback=self.on_progress)
        for index, stream in enumerate(yt.streams.filter(type='video').order_by('resolution'), 1):
                description = '[' + str(index) + '] ' + str(stream.type) + ' ' + str(stream.resolution) + ' ' +  str(stream.fps) + 'fps'
                self.available_settings[stream.itag] = description
        for index, stream in enumerate(yt.streams.filter(type='audio').order_by('abr'), 1):
                description = '[' + str(index) + '] ' + str(stream.type) + ' ' + str(stream.abr)
                self.available_settings[stream.itag] = description
        self.choose_settings.addItems(self.available_settings.values())

        self.getAndSetImageFromURL(yt.thumbnail_url)
        self.download_button.setEnabled(True)
        self.video_title.setText(f"Title: {yt.title}")
        self.video_author.setText(f"Author: {yt.author}")
        self.user_info.setText("Information loaded succesfully.")

    def item_selected(self):
        self.selected_settings = self.choose_settings.currentText()
    
    def getAndSetImageFromURL(self,imageURL):
        try:
            request = requests.get(imageURL)
            self.pixmap.loadFromData(request.content)
            self.pixmap = self.pixmap.scaled(160,120)
            self.video_thumbnail.setPixmap(self.pixmap)
            QApplication.processEvents()
        except:
            pass

if __name__ == '__main__':
    main()