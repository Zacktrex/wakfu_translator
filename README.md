# Create an English Quick Start TXT with note that Steam isn't required and how to find wakfu_chat.log anywhere
content = r"""Wakfu Chat Translator — Quick Start (Windows, Any Launcher)
==============================================================

This short guide complements the full README. It shows how to download the project, open a terminal, install dependencies, run the app, and point it to your Wakfu chat log.

--------------------------------------------------------------
A) Prerequisites
--------------------------------------------------------------
- Windows, Wakfu installed (Steam OR Ankama Launcher OR other). *
- Python 3.11 (recommended for compatibility).
  Check installed versions:    py -0p
  If 3.11 is missing:          winget install -e --id Python.Python.3.11

(*) Not limited to Steam. The key is finding the file named **wakfu_chat.log** on your machine.

--------------------------------------------------------------
B) Download the project from GitHub
--------------------------------------------------------------
1) Open the repository page on GitHub.
2) Click **Code** → **Download ZIP**.
3) Extract the ZIP (right–click → **Extract All…**).
4) Enter the extracted folder (e.g., `wakfu_translator-main`).

--------------------------------------------------------------
C) Open a terminal in the project folder
--------------------------------------------------------------
Option 1 — Context menu:
  Right–click inside the folder → **Open in Terminal** (or **Open in PowerShell**).

Option 2 — Explorer address bar:
  Type `powershell` and press Enter.

Make sure the prompt shows the project path.

--------------------------------------------------------------
D) Create and activate the virtual environment (3.11)
--------------------------------------------------------------
py -3.11 -m venv .venv311

# If you're in PowerShell, allow scripts ONLY for this session:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv311\Scripts\Activate.ps1
python --version   # should display 3.11.x

(If using CMD: ".venv311\Scripts\activate.bat")

--------------------------------------------------------------
E) Install dependencies
--------------------------------------------------------------
python -m pip install --upgrade pip
python -m pip install argostranslate
python -m pip install PyQt5

# Install a language model (example EN→ES)
python -c "import argostranslate.package as p; p.update_package_index(); m=[x for x in p.get_available_packages() if x.from_code=='en' and x.to_code=='es'][0]; p.install_from_path(m.download()); print('EN→ES model installed')"

--------------------------------------------------------------
F) Run the application (ALWAYS with the venv’s python)
--------------------------------------------------------------
PowerShell:
  & ".\.venv311\Scripts\python.exe" .\main.py

CMD:
  ".venv311\Scripts\python.exe" main.py

--------------------------------------------------------------
G) Configure the Chat Log Path (then restart the app)
--------------------------------------------------------------
In **Settings** → **Chat Log Path**, select your real **wakfu_chat.log** file.

Typical locations:
• Steam:
  C:\Program Files (x86)\Steam\steamapps\common\Wakfu\preferences\logs\wakfu_chat.log

• Ankama Launcher / other installs:
  The path may differ. Use a search to locate the file:

  PowerShell (search drive C:):
    Get-ChildItem C:\ -Recurse -File -Filter wakfu_chat.log -ErrorAction SilentlyContinue |
      Select-Object FullName, LastWriteTime, Length

  Or search under your user profile first (faster):
    Get-ChildItem "$env:USERPROFILE" -Recurse -File -Filter wakfu_chat.log -ErrorAction SilentlyContinue |
      Select-Object FullName, LastWriteTime, Length

Once found, paste the full path into **Chat Log Path** (or use **Browse…**).
If the file picker complains “The file name is not valid”, change the filter to **All files (*.*)** and select `wakfu_chat.log`.
Click **Save**, then **close and re-open** the app.

--------------------------------------------------------------
H) Test
--------------------------------------------------------------
In the game, type a line in the **General** channel (or force it with /s):
/s hello translator test

You should see the translation appear in the app window.

Note: Some builds only process the **[General]** channel. Messages in **[Group]/[Local]/[Recruitment]** may not be translated unless the filter is expanded in code.

--------------------------------------------------------------
I) Common errors (very brief)
--------------------------------------------------------------
• ModuleNotFoundError (argostranslate/PyQt5):
  Install inside the venv and run with:
    & ".\.venv311\Scripts\python.exe" .\main.py

• PSSecurityException when activating venv:
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

• “The file name is not valid” when choosing the log:
  Switch the file filter to **All files (*.*)** and select `wakfu_chat.log`.

• No translation in Group/Local:
  Some builds only parse **[General]**. Try `/s` or widen the channel regex in code.

End.
"""
path = "/mnt/data/QUICKSTART_Wakfu_Translator_EN.txt"
with open(path, "w", encoding="utf-8") as f:
    f.write(content)

path
