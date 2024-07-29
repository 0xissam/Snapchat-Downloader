# Snapchat Downloader

A simple PyQt5 application to download Snapchat stories for a list of specified users. The application allows you to add and remove usernames, download their stories, and view the progress and log of the download process.

## Features

- Add and remove Snapchat usernames
- Download stories from specified usernames
- Display download progress and log
- Show warnings if no users are added when attempting to download

## Installation

### Using the Executable Installer

1. Download the latest version of the installer from the [Releases](https://github.com/your-username/snapchat-downloader/releases) page.

2. Run the installer and follow the on-screen instructions to install the application.

### Building from Source

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/snapchat-downloader.git
    cd snapchat-downloader
    ```

2. Create a virtual environment and activate it (optional but recommended):

    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

4. If you want to create an executable, you can use PyInstaller:

    ```bash
    pip install pyinstaller
    pyinstaller --onefile snapchat_downloader.py
    ```

    The executable will be created in the `dist` folder.

## Usage

1. Run the application:

    - If you installed using the executable installer, locate and launch the `Snapchat Downloader` application from your start menu or desktop shortcut.
    - If you are running from source, use the following command:

    ```bash
    python snapchat_downloader.py
    ```

2. Use the UI to add Snapchat usernames, remove selected usernames, and start the download process.

## Requirements

- Python 3.x
- PyQt5
- requests
- beautifulsoup4

You can install the required packages using:

```bash
pip install PyQt5 requests beautifulsoup4
```

### How It Works

1. Adding Users: You can add Snapchat usernames to the list using the input field and "Add User" button.

2. Removing Users: Select usernames from the list and click "Remove Selected User" to remove them.

3. Downloading Stories: Click the "Download" button to start downloading stories for the users in the list. The progress bar will show the progress, and the log area will display the status of the downloads.

4. Error Handling: If no users are added when you click "Download", a warning message will appear.