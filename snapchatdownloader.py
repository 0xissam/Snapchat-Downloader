import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLineEdit, QPushButton,
                             QVBoxLayout, QHBoxLayout, QProgressBar, QTextEdit,
                             QListWidget, QMessageBox)
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QIcon
import os
import requests
from bs4 import BeautifulSoup
import json
from time import sleep


class DownloadThread(QThread):
    update_progress = pyqtSignal(int)
    update_log = pyqtSignal(str)
    download_complete = pyqtSignal()

    def __init__(self, userslist):
        super().__init__()
        self.userslist = userslist

    def run(self):
        base_path = os.path.join(os.path.expanduser("~"), "Desktop/snap")
        os.makedirs(base_path, exist_ok=True)
        os.chdir(base_path)

        for idx, username in enumerate(self.userslist):
            json_dict = self.get_json(username)
            if json_dict:
                self.download_media(json_dict)
            self.update_progress.emit((idx + 1) * 100 // len(self.userslist))

        self.download_complete.emit()

    def get_json(self, username):
        base_url = "https://story.snapchat.com/@"
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/103.0.2'}
        mix = base_url + username
        r = requests.get(mix, headers=headers)

        if not r.ok:
            self.update_log.emit("Oh Snap! No connection with Snap!")
            return None

        soup = BeautifulSoup(r.content, "html.parser")
        snaps = soup.find(id="__NEXT_DATA__").string.strip()
        data = json.loads(snaps)

        return data

    def download_media(self, json_dict):
        try:
            for i in json_dict["props"]["pageProps"]["story"]["snapList"]:
                file_url = i["snapUrls"]["mediaUrl"]

                if not file_url:
                    self.update_log.emit("There is a Story but no URL is provided by Snapchat.")
                    continue

                r = requests.get(file_url, stream=True, headers={'User-Agent': 'Mozilla/5.0'})

                if "image" in r.headers['Content-Type']:
                    file_name = r.headers['ETag'].replace('"', '') + ".jpeg"
                elif "video" in r.headers['Content-Type']:
                    file_name = r.headers['ETag'].replace('"', '') + ".mp4"
                else:
                    continue

                if os.path.isfile(file_name):
                    continue

                sleep(0.3)

                if r.status_code == 200:
                    with open(file_name, 'wb') as f:
                        for chunk in r:
                            f.write(chunk)
                    self.update_log.emit(f"Downloaded {file_name}")
                else:
                    self.update_log.emit("[-] Cannot make connection to download media!")
        except KeyError:
            self.update_log.emit("[-] No stories found for the last 24h.\n")


class SnapchatDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.userslist = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Snapchat Downloader')
        self.setWindowIcon(QIcon('snap.png'))

        main_layout = QVBoxLayout()
        form_layout = QVBoxLayout()
        user_list_layout = QVBoxLayout()

        self.setStyleSheet("""
            QWidget {
                font-size: 14px;
            }
            QLineEdit, QTextEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #5cb85c;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #4cae4c;
            }
            QProgressBar {
                height: 20px;
                text-align: center;
            }
            QListWidget {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QTextEdit {
                background-color: black;
                color: white;
                font-family: Consolas, monospace;
            }
        """)

        self.user_list_widget = QListWidget()
        self.user_list_widget.addItems(self.userslist)
        user_list_layout.addWidget(self.user_list_widget)

        self.new_user_input = QLineEdit()
        self.new_user_input.setPlaceholderText('Enter new username')
        self.add_user_button = QPushButton('Add User')
        self.add_user_button.clicked.connect(self.add_user)
        self.remove_user_button = QPushButton('Remove Selected User')
        self.remove_user_button.clicked.connect(self.remove_user)

        user_buttons_layout = QHBoxLayout()
        user_buttons_layout.addWidget(self.new_user_input)
        user_buttons_layout.addWidget(self.add_user_button)
        user_buttons_layout.addWidget(self.remove_user_button)
        user_list_layout.addLayout(user_buttons_layout)

        self.progress_bar = QProgressBar()

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)

        self.download_button = QPushButton('Download')
        self.download_button.clicked.connect(self.start_download)

        form_layout.addLayout(user_list_layout)
        form_layout.addWidget(self.progress_bar)
        form_layout.addWidget(self.log_area)

        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.download_button)

        self.setLayout(main_layout)

    def add_user(self):
        new_user = self.new_user_input.text().strip()
        if new_user and new_user not in self.userslist:
            self.userslist.append(new_user)
            self.user_list_widget.addItem(new_user)
            self.new_user_input.clear()
        else:
            QMessageBox.warning(self, "Error", "Invalid or duplicate username.")

    def remove_user(self):
        selected_items = self.user_list_widget.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            self.userslist.remove(item.text())
            self.user_list_widget.takeItem(self.user_list_widget.row(item))

    def start_download(self):
        if not self.userslist:
            QMessageBox.warning(self, "Error", "Please add at least one user before downloading.")
            return

        self.download_button.setDisabled(True)
        self.log_area.clear()
        self.progress_bar.setValue(0)
        self.thread = DownloadThread(self.userslist)
        self.thread.update_progress.connect(self.update_progress)
        self.thread.update_log.connect(self.update_log)
        self.thread.download_complete.connect(self.download_complete)
        self.thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_log(self, message):
        self.log_area.append(message)

    def download_complete(self):
        self.download_button.setDisabled(False)
        self.progress_bar.setValue(0)
        QMessageBox.information(self, "Download Complete", "Downloaded successfully.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SnapchatDownloader()
    ex.show()
    sys.exit(app.exec_())
