# Wakfu Chat Translator — Quick Start

This guide shows how to set up and run the app, and how to locate your `wakfu_chat.log`.

> ⚠️ Steam is **NOT required**. This works with any Wakfu installation (Ankama Launcher or others).
> The only requirement is locating `wakfu_chat.log`.

---

## 1. Prerequisites

* Windows
* Wakfu installed (any launcher)
* Python 3.11

Check Python:

```
py -0p
```

Install if missing:

```
winget install -e --id Python.Python.3.11
```

---

## 2. Download Project

* Go to GitHub repo
* Click **Code → Download ZIP**
* Extract and open the folder

---

## 3. Open Terminal

Right-click inside the folder → **Open in Terminal**

---

## 4. Setup Virtual Environment

```
py -3.11 -m venv .venv311
```

PowerShell:

```
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv311\Scripts\Activate.ps1
```

---

## 5. Install Dependencies

```
python -m pip install --upgrade pip
pip install argostranslate PyQt5
```

Install language model (example EN→ES):

```
python -c "import argostranslate.package as p; p.update_package_index(); m=[x for x in p.get_available_packages() if x.from_code=='en' and x.to_code=='es'][0]; p.install_from_path(m.download())"
```

---

## 6. Run the App

```
.\.venv311\Scripts\python.exe main.py
```

---

## 7. Find `wakfu_chat.log`

### Common locations:

**Steam**

```
C:\Program Files (x86)\Steam\steamapps\common\Wakfu\preferences\logs\wakfu_chat.log
```

**Other installs**
Search using PowerShell:

```
Get-ChildItem "$env:USERPROFILE" -Recurse -Filter wakfu_chat.log -ErrorAction SilentlyContinue
```

---

## 8. Configure

* Open app → Settings
* Set **Chat Log Path**
* Restart app

---

## 9. Test

In-game:

```
/s hello translator test
```

---

## ⚠️ Notes

* Some builds only translate **[General] channel**
* Use `/s` if needed

---

## 🛠 Common Issues

* **Module not found** → install inside venv
* **Execution policy error** → use `Set-ExecutionPolicy`
* **Invalid file name** → switch to *All files (.)*

---

Done 🚀
