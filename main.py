# Standard library modules
import os
import sys
from threading import Thread

# Third-party modules
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt
from pytube import YouTube
from pydub import AudioSegment
import requests
import ffmpeg

class MainWindow(QMainWindow):

    ''' Main class of the script. It builds a GUI during program startup 
    and it holds all methods that can be called by user 
    while interacting with interface. '''

    def __init__(self, link="", selected_settings=None, available_settings={}):
        super().__init__()

        # Empty variables declarations, they will be overwritten later
        self.link = link
        self.selected_settings = selected_settings
        self.available_settings = available_settings

        # User input widget
        self.input_line = QLineEdit(self)
        self.input_line.setPlaceholderText("Enter link")

        # Button to request for information on certain video
        self.load_info_button = QPushButton("Load video info", self)
        self.load_info_button.clicked.connect(lambda: Thread(
            self.load_info(self.input_line.text())).start())

        # Empty drop-down list of media options
        self.choose_settings = QComboBox()
        self.choose_settings.currentTextChanged.connect(
            self.set_selected_option)

        # Button to execute downloading process, disabled when no information loaded
        self.download_button = QPushButton("Download", self)
        self.download_button.clicked.connect(lambda: Thread(
            self.download_stream(self.link, self.selected_settings)).start())
        self.download_button.setEnabled(False)

        # Progress bar to monitor downloading process
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)

        # Text label to notify user about the status of current activity
        self.status = QLabel()
        self.status.setStyleSheet("color: gray")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Label displaying current video title
        self.video_title = QLabel()
        self.video_title.setText("Title: ")
        self.video_title.setWordWrap(True)

        # Label displaying current video author's channel name
        self.video_author = QLabel()
        self.video_author.setText("Author: ")

        # Widgets to display current video thumbnail
        self.thumbnail_pixmap = QPixmap()
        self.video_thumbnail = QLabel()

        # Layout declaration and general settings
        layout = QGridLayout()
        layout.setSpacing(10)
        layout.setColumnMinimumWidth(0, 350)
        layout.setColumnMinimumWidth(1, 200)
        layout.setRowMinimumHeight(0, 60)

        # First column widgets bindings
        layout.addWidget(self.input_line, 0, 0)
        layout.addWidget(self.load_info_button, 1, 0)
        layout.addWidget(self.choose_settings, 2, 0)
        layout.addWidget(self.download_button, 3, 0)
        layout.addWidget(self.progress_bar, 4, 0)
        layout.addWidget(self.status, 5, 0)

        # Second column widgets bindings
        layout.addWidget(self.video_title, 0, 1)
        layout.addWidget(self.video_author, 1, 1)
        layout.addWidget(self.video_thumbnail, 2, 1, 5, 1)

        # Container holding main layout
        container = QWidget()
        container.setLayout(layout)

        # General window settings
        self.setCentralWidget(container)
        self.setWindowTitle('YouThon')
        self.setWindowIcon(QIcon('icon.png'))

    def monitor_progress(self, stream, chunk, bytes_remaining):

        ''' Calcutates percentage progress on downloading
        currently selected media and displays that value on progressbar.
        '''

        size = stream.filesize
        progress = int(((size - bytes_remaining) / size) * 100)
        self.progress_bar.setValue(progress)

    def download_stream(self, link, settings):

        ''' Determines the type of media requested to parse 
        and attempts to download it. Once a raw audio-only or 
        video-only stream is downloaded, converts it to user-friendly 
        format, embedding an audio into video stream and saving the 
        output in MP4 format, or exporting MP3 media 
        from MP4 audio-only raw file. If an error occurs, 
        user is notified and prompted as to try again.
        '''
        # Resetting the following values
        self.progress_bar.setValue(0)
        self.input_line.clear()

        try:

            # Notifying user that downloading has started succesfully
            self.status.setText("Downloading selected media...")

            # Creating pytube.YouTube object and determining an 
            # itag for the media options selected by user
            yt = YouTube(link, on_progress_callback=self.monitor_progress)
            itag = list(self.available_settings.keys())[list(self.available_settings.values()).index(settings)]
            stream = yt.streams.get_by_itag(itag)

            # If video stream was selected
            if stream.type == 'video':

                stream_audio = yt.streams.get_audio_only()

                # Declaring filenames. Characters forbidden for filenames 
                # in Windows are being removed from final output name.
                filename_audio_temporary = 'temp.' + str(stream_audio.subtype)
                filename_video_temporary = 'temp2.mp4'
                filename_output = yt.title + '.mp4'
                filename_output = "".join(i for i in filename_output if i not in "\/:*?<>|")

                # Audio and video downloaded separately to temporary files
                stream.download(filename=filename_video_temporary)
                stream_audio.download(filename=filename_audio_temporary)

                # Concatenating audio and video tracks into MP4 
                # file named after video title on YouTube
                input_video = ffmpeg.input(filename_video_temporary)
                input_audio = ffmpeg.input(filename_audio_temporary)
                ffmpeg.concat(input_video, input_audio, v=1, a=1).output(filename_output).run(overwrite_output=True)

                # Removing temporary files
                os.remove(filename_video_temporary)
                os.remove(filename_audio_temporary)

            # If audio stream was selected
            else:

                # Declaring filenames. Characters forbidden for filenames 
                # in Windows are being removed from final output name.
                filename_temporary = 'temp.' + str(stream.subtype)
                filename_output = yt.title + '.mp3'
                filename_output = "".join(i for i in filename_output if i not in "\/:*?<>|")

                # Extracting bitrate value without unit
                bitrate = str(stream.bitrate)[:-3]

                # Downloading raw stream and converting to 
                # MP3 file while preserving its original bitrate
                stream.download(filename=filename_temporary)
                AudioSegment.from_file(filename_temporary).export(filename_output, format="mp3", bitrate=bitrate)

                # Removing temporary file
                os.remove(filename_temporary)

            # Notyfying user about success
            self.status.setText("Media downloaded succesfully.")

        except:
            # Notifying user and disabling download button whenever an error occurs.
            self.status.setText("Unfortunately, something went wrong. Try another option.")
            self.download_button.setEnabled(False)

    def load_info(self, link):

        ''' Loads information on current YouTube video such as its 
        title, author's channel name, thumbnail and available media 
        options from user provided link.
        '''
        # Resetting the following values
        self.progress_bar.setValue(0)
        self.choose_settings.clear()
        self.available_settings.clear()

        try:
            # Creating pytube.YouTube object to extract 
            # information regarding current video.
            yt = YouTube(link)

            # Building a list of available media 
            # settings and adding it to drop-down menu
            for stream in yt.streams.filter(subtype='mp4').order_by('resolution'):
                if stream.is_progressive == 0:
                    description = 'mp4 ' + str(stream.resolution) + ' ' + str(stream.fps) + 'fps '
                    self.available_settings[stream.itag] = description
            for stream in yt.streams.filter(type='audio').order_by('abr'):
                description = 'mp3 ' + str(stream.abr)
                self.available_settings[stream.itag] = description
            self.choose_settings.addItems(self.available_settings.values())

            # Displaying collected information to user
            self.link = link
            self.set_thumbnail(yt.thumbnail_url)
            self.download_button.setEnabled(True)
            self.video_title.setText(f"Title: {yt.title}")
            self.video_author.setText(f"Author: {yt.author}")

            # Notifying user about success
            self.status.setText("Information loaded succesfully.")

        except:
            # Notifying user and disabling download button whenever an error occurs.
            self.status.setText("Unfortunately, something went wrong. Try another link.")
            self.download_button.setEnabled(False)

    def set_selected_option(self):

        '''Assigning currently selected media option to a variable 
        later used as an argument when attempting download process'''

        self.selected_settings = self.choose_settings.currentText()

    def set_thumbnail(self, imageURL):

        '''Displaying thumbnail of current video'''

        self.thumbnail_pixmap.loadFromData(requests.get(imageURL).content)
        self.thumbnail_pixmap = self.thumbnail_pixmap.scaled(160, 120)
        self.video_thumbnail.setPixmap(self.thumbnail_pixmap)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
