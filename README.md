# Learning Tracker 1-4-7

A small Windows desktop app for tracking what you studied and reminding you to revise it using the 1-4-7 revision rule.

The idea is simple:

- Log a topic you learned today.
- The app stores it locally.
- It reminds you to revise the topic after 1 day, 4 days, and 7 days.
- You can mark each revision as done.

This project was built as a simple learning/productivity tool and also as a way to understand how Python desktop tray apps work.

---

## Why I Built This

When studying, it is easy to learn something once and forget to revise it later. The 1-4-7 rule helps by reminding you at fixed intervals:

| Revision | When |
| --- | --- |
| R1 | 1 day after learning |
| R2 | 4 days after learning |
| R3 | 7 days after learning |

This app keeps track of those dates automatically.

---

## Main Features

- Log today's studied topic from the system tray.
- Store all topics locally in SQLite.
- Show reminders for topics due for revision.
- Show overdue revisions if the app was closed on the exact reminder day.
- Mark individual revision items as done.
- Change the daily prompt time from settings.
- Optional startup with Windows.
- Runs quietly in the background from the system tray.
- Keeps logs for debugging.

---

## How The App Works

The app has three main parts:

1. A tray icon that stays in the Windows system tray.
2. Small popup windows for input, revision, and settings.
3. A local database that stores topics and revision dates.

Basic flow:

```text
User logs topic
      |
      v
Topic saved in SQLite
      |
      v
Revision dates are calculated: +1, +4, +7 days
      |
      v
App checks due/overdue topics
      |
      v
User gets reminder and marks revision done
```

---

## Tech Stack

### Python

Python is used for the main application logic.

It handles:

- Starting the app
- Creating tray menu actions
- Opening popup windows
- Scheduling reminders
- Reading and writing the database
- Saving settings
- Logging errors

Main files:

- `main.py`
- `api.py`
- `db.py`
- `settings.py`

---

### pystray

`pystray` is used for the Windows system tray icon.

This is the library that allows the app to run in the background and show a tray icon near the clock.

It is used for:

- Creating the tray icon
- Adding right-click menu options
- Opening input, revision, and settings windows from the tray
- Showing system notifications
- Exiting the app from the tray menu

Example tray actions:

- Log Today's Topic
- Check Revisions
- Settings
- Exit

---

### pywebview

`pywebview` is used to show small desktop windows using HTML, CSS, and JavaScript.

Instead of building the UI with Tkinter or PyQt, this app uses HTML pages inside desktop windows.

It is used for:

- Topic input window
- Revision reminder window
- Settings window

The UI files are inside the `ui/` folder:

- `ui/tray_input.html`
- `ui/revision.html`
- `ui/settings.html`

Important note:

The app uses a hidden pywebview root window to keep the webview event loop running in the background. Actual windows are opened only when needed from the tray menu or reminder logic.

---

### SQLite

SQLite is used as the local database.

It stores:

- Topic name
- Date when the topic was logged
- Revision 1 date
- Revision 2 date
- Revision 3 date
- Whether each revision is done or not

Database file location:

```text
%LocalAppData%\LearningTracker147\learning.db
```

SQLite was chosen because it is simple, local, and does not need a separate server.

---

### schedule

The `schedule` library is used for daily reminder timing.

It checks the configured prompt time and triggers the app to remind the user.

Default prompt time:

```text
21:00
```

The time can be changed from the settings window.

---

### platformdirs

`platformdirs` is used to find the correct local app data folder on Windows.

This avoids hardcoding paths and keeps app data in a proper user-specific location.

Used for:

- Database path
- Config path
- Log path

---

### Pillow

`Pillow` is used to generate the tray icon image.

The icon is created in Python code instead of depending on an external image file.

---

### HTML, CSS, and JavaScript

The UI is written using normal web technologies:

- HTML for structure
- CSS for design
- JavaScript for button actions and UI updates

JavaScript talks to Python through `window.pywebview.api`.

Example:

```javascript
window.pywebview.api.save_topic(topic)
```

This calls a Python method from the HTML UI.

---

## Project Structure

```text
learning_tracker/
|
|-- main.py              # Starts the app, tray icon, scheduler, and windows
|-- api.py               # Python functions called from JavaScript UI
|-- db.py                # SQLite database functions
|-- settings.py          # Reads and writes config.json
|-- paths.py             # Central app data paths
|-- logging_setup.py     # App logging setup
|-- requirements.txt     # Python dependencies
|-- README.md            # Project documentation
|
|-- ui/
|   |-- tray_input.html  # Window to log today's topic
|   |-- revision.html    # Window to show revision items
|   |-- settings.html    # Window to change settings
|
|-- assets/              # App assets
|-- windows/             # Older/placeholder window files
|-- data/                # Local development data folder
```

---

## Important Files Explained

### `main.py`

This is the entry point of the app.

It does these things:

- Initializes the database
- Starts pywebview
- Starts the tray icon
- Starts the scheduler
- Sends tray notifications
- Opens popup windows when requested

It also uses a queue for UI actions. This helps avoid opening windows directly from many different threads.

---

### `api.py`

This file connects the HTML UI with Python.

For example, when the user clicks "Save" in the input window, JavaScript calls Python code from this file.

Main classes:

- `InputApi`
- `RevisionApi`
- `SettingsApi`

---

### `db.py`

This file handles the SQLite database.

It can:

- Create the topics table
- Add a new topic
- Find due or overdue revisions
- Mark a revision as done
- Count topics logged today

---

### `settings.py`

This file handles app settings.

It stores settings in:

```text
%LocalAppData%\LearningTracker147\config.json
```

Current settings:

- Daily prompt time
- Start with Windows

---

### `paths.py`

This file keeps all app paths in one place.

It defines:

- Data folder
- Database path
- Config path
- Log folder

This makes path handling cleaner and safer.

---

### `logging_setup.py`

This file sets up logging.

Logs are saved here:

```text
%LocalAppData%\LearningTracker147\logs\app.log
```

Logs are useful for checking errors if the app does not behave correctly.

---

## Setup

### Requirements

- Python 3.9 or newer
- Windows 10/11
- Microsoft Edge WebView2 Runtime

Most modern Windows systems already include WebView2.

---

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

### Run The App

```bash
python main.py
```

The app runs in the background. Use the system tray icon to open actions.

---

## Usage

Right-click the tray icon and choose:

| Action | What it does |
| --- | --- |
| Log Today's Topic | Opens a small window to save a topic |
| Check Revisions | Shows revision topics due today or overdue |
| Settings | Change prompt time and startup option |
| Exit | Closes the app |

---

## Data And Privacy

- The app works locally.
- Topics are stored on your own computer.
- No account is needed.
- No server is used.
- Data is stored in SQLite inside LocalAppData.

---

## Build EXE

Optional command:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name LearningTracker147 main.py
```

The generated app will be inside the `dist/` folder.

---

## What I Learned

While building this project, I learned:

- How to create a Windows system tray app using `pystray`
- How tray menus work in Python
- How to show small desktop windows using `pywebview`
- How JavaScript can call Python functions through pywebview
- How to store simple app data using SQLite
- How to use `platformdirs` for proper app data paths
- Why background apps need careful thread handling
- Why logging is important for debugging desktop apps

---

## Future Improvements

Some possible improvements:

- Add edit/delete topic option
- Add export to CSV
- Add better notification actions
- Add a dashboard for all saved topics
- Build and test a standalone `.exe`

---

## License

MIT
