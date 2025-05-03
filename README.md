# 💻 PythonJS

🖼️ A hybrid programming language and shell combining Python and JavaScript features.

## ⚙️ Features
- Custom shell with commands: `new`, `cd`, `run`, `support`
- `.pyjs` files: Write code in a Python+JS style
- Notepad integration for editing
- Discord support chat (coming soon)

## 🪴 Usage
1. Install PythonJS by going to Releases > PythonJS Release Version 2.0 > `bootstrap_pythonjs.py`
2. Run the shell by:
   ```
   python pythonjs_shell.py
   ```
or by running `pythonjs_shell.py` file manually

2. ⌨️ Use commands like:
   - `new myscript.pyjs` (edit in Notepad)
   - `run myscript.pyjs`
   - `cd path/to/dir`
   - `support your message here`

## 😎 File Association (Windows)
To associate `.pyjs` files to run with PythonJS Shell:

1. Right-click a `.pyjs` file > Open with > Choose another app
2. Browse to your Python executable (e.g., `python.exe`)
3. Add arguments:
   - Target: `pythonw.exe C:\Users\mrcel\pythonjs\pythonjs_shell.py "%1"`
4. (Optional) Use a .reg file for advanced association.

---

## 🔨 CWO [ CURRENTLY WORKING ON ] FEATURE(S)
- Discord support chat
