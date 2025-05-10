import os
import subprocess
import sys
import re
import tempfile
import threading
import msvcrt
import getpass

# Set Windows console code page to UTF-8 for proper encoding support
if os.name == 'nt':
    import ctypes
    ctypes.windll.kernel32.SetConsoleCP(65001)
    ctypes.windll.kernel32.SetConsoleOutputCP(65001)

# Reconfigure stdout encoding to UTF-8 (Python 3.7+)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Try to import colorama, install if missing
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    try:
        print("Colorama not found. Installing colorama...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'colorama'])
        from colorama import init, Fore, Style
        init(autoreset=True)
    except Exception:
        class Dummy:
            def __getattr__(self, name):
                return ''
        Fore = Style = Dummy()

PYTHONJS_SHELL_VERSION = '0.5'
PYTHONJS_LANG_VERSION = '0.5'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILES_DIR = os.path.join(BASE_DIR, 'files')
if not os.path.exists(FILES_DIR):
    os.makedirs(FILES_DIR)

CURRENT_DIR = FILES_DIR
nano_installed = False  # Track if nano install was attempted

def interpret_pyjs_file(filename):
    """
    Reads a .pyjs file, converts JS-like syntax to Python, and executes it.
    """
    with open(filename, 'r', encoding='utf-8') as f:
        code = f.read()

    # Basic JS to Python replacements
    code = code.replace('console.log(', 'print(')
    code = re.sub(r'\b(var|let|const)\b', '', code)  # remove var/let/const keywords
    code = code.replace('true', 'True').replace('false', 'False').replace('null', 'None')
    code = code.replace('&&', 'and').replace('||', 'or')
    code = code.replace('===', '==').replace('!==', '!=')

    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.py', encoding='utf-8') as tmp:
        tmp.write(code)
        tmp_filename = tmp.name

    proc = subprocess.Popen([sys.executable, tmp_filename], cwd=os.path.dirname(filename))
    proc.wait()

def run_pyjs_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        code = f.read()
    code = code.replace('console.log(', 'print(')

    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.py', encoding='utf-8') as tmp:
        tmp.write(code)
        tmp_filename = tmp.name

    proc = subprocess.Popen([sys.executable, tmp_filename], cwd=os.path.dirname(filename))

    def listen_for_ctrl_m():
        while proc.poll() is None:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key == b'\r':  # Ctrl+M is carriage return
                    print("\n[PythonJS] Ctrl+M detected, stopping user code...")
                    proc.terminate()
                    break

    listener = threading.Thread(target=listen_for_ctrl_m, daemon=True)
    listener.start()

    proc.wait()
    listener.join()

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def shell():
    global CURRENT_DIR, nano_installed
    print(Fore.CYAN + getattr(Style, 'BRIGHT', '') + """
╔════════════════════════════════════╗
║       Welcome to PythonJS Shell!   ║
╚════════════════════════════════════╝
""" + getattr(Style, 'RESET_ALL', ''))
    print(Fore.MAGENTA + "Type 'help' for commands.\n" + getattr(Style, 'RESET_ALL', ''))
    while True:
        try:
            prompt = (Fore.GREEN + getattr(Style, 'BRIGHT', '') + f"PythonJS" + getattr(Style, 'RESET_ALL', '') +
                      Fore.YELLOW + f"({CURRENT_DIR})" + getattr(Style, 'RESET_ALL', '') +
                      Fore.BLUE + " > " + getattr(Style, 'RESET_ALL', ''))
            cmd = input(prompt).strip()
            if not cmd:
                continue
            parts = cmd.split()
            command = parts[0]
            args = parts[1:]

            if command == 'exit':
                print(Fore.CYAN + 'Exiting PythonJS Shell.' + getattr(Style, 'RESET_ALL', ''))
                break
            elif command == 'help':
                print(Fore.CYAN + getattr(Style, 'BRIGHT', '') + """
Commands:
  new [filename.pyjs]   - Create and edit a new PythonJS file
  nano [filename.pyjs]  - Edit a PythonJS file with nano editor
  cd [path]             - Change directory (within files folder)
  run [filename.pyjs]   - Run a PythonJS file with custom interpreter
  execute [exe] [args]  - Run an executable (e.g., execute notepad)
  mp3 [name]            - Play an mp3 file from the files folder (e.g., mp3 songname)
  troll                 - Show troll.svg from the files folder
  restart               - Restart the PythonJS shell
  print [text]          - Print text to the shell
  clear                 - Clear the terminal
  whoami                - Show the current user
  support [message]     - Send a support message via Discord
  snake                 - Play the Snake game
  site                  - Open the PythonJS website
  version               - Show the PythonJS shell and language version
  credits               - Show credits for PythonJS
  cmd                   - Exit PythonJS and open Windows Command Prompt
  exit                  - Exit the shell
  powershell            - Open PythonJS Shell in a new PowerShell window
  ps                    - Exit PythonJS and open PowerShell
""" + getattr(Style, 'RESET_ALL', ''))
            elif command == 'cd':
                if not args:
                    print(Fore.RED + 'Usage: cd [path]' + getattr(Style, 'RESET_ALL', ''))
                else:
                    new_dir = os.path.abspath(os.path.join(CURRENT_DIR, args[0]))
                    if os.path.commonpath([new_dir, FILES_DIR]) != FILES_DIR or not os.path.isdir(new_dir):
                        print(Fore.RED + 'Error: Can only cd within the files folder.' + getattr(Style, 'RESET_ALL', ''))
                    else:
                        CURRENT_DIR = new_dir
                        print(Fore.GREEN + f'Changed directory to {CURRENT_DIR}' + getattr(Style, 'RESET_ALL', ''))
            elif command == 'new':
                if not args or not args[0].endswith('.pyjs'):
                    print(Fore.RED + 'Usage: new [filename.pyjs]' + getattr(Style, 'RESET_ALL', ''))
                else:
                    filename = os.path.join(CURRENT_DIR, args[0])
                    subprocess.call(['notepad', filename])
                    if os.path.exists(filename):
                        run_now = input(Fore.CYAN + 'File saved. Run now? (y/n): ' + getattr(Style, 'RESET_ALL', '')).strip().lower()
                        if run_now == 'y':
                            interpret_pyjs_file(filename)
            elif command == 'nano':
                if not args or not args[0].endswith('.pyjs'):
                    print(Fore.RED + 'Usage: nano [filename.pyjs]' + Style.RESET_ALL)
                else:
                    filename = os.path.join(CURRENT_DIR, args[0])
                    if not os.path.exists(filename):
                        print(Fore.RED + 'File does not exist.' + Style.RESET_ALL)
                        continue
                    try:
                        subprocess.call(['nano', filename])
                    except FileNotFoundError:
                        if not nano_installed:
                            print(Fore.YELLOW + "Nano not found. Attempting to install nano..." + Style.RESET_ALL)
                            nano_installed = True
                            installed = False
                            # Try Chocolatey
                            try:
                                subprocess.check_call(['choco', 'install', 'nano', '-y'])
                                installed = True
                            except Exception:
                                pass
                            # If Chocolatey failed, try winget
                            if not installed:
                                try:
                                    subprocess.check_call(['winget', 'install', '--id', 'GNU.nano', '-e', '--accept-source-agreements', '--accept-package-agreements'])
                                    installed = True
                                except Exception:
                                    pass
                            if installed:
                                print(Fore.GREEN + "Nano installed successfully. Launching nano..." + Style.RESET_ALL)
                                try:
                                    subprocess.call(['nano', filename])
                                except FileNotFoundError:
                                    print(Fore.RED + "Nano still not found after installation. Opening with Notepad instead." + Style.RESET_ALL)
                                    subprocess.call(['notepad', filename])
                            else:
                                print(Fore.RED + "Failed to install nano automatically. Opening with Notepad instead." + Style.RESET_ALL)
                                subprocess.call(['notepad', filename])
                        else:
                            print(Fore.RED + "Nano not found and installation already attempted. Opening with Notepad instead."                                subprocess.call(['notepad', filename])
            elif command == 'run':
                if not args or not args[0].endswith('.pyjs'):
                    print(Fore.RED + 'Usage: run [filename.pyjs]' + getattr(Style, 'RESET_ALL', ''))
                else:
                    filename = os.path.join(CURRENT_DIR, args[0])
                    if os.path.exists(filename):
                        interpret_pyjs_file(filename)
                    else:
                        print(Fore.RED + 'File does not exist.' + getattr(Style, 'RESET_ALL', ''))
            elif command == 'clear':
                clear()
            elif command == 'whoami':
                print(Fore.GREEN + f'Current user: {getpass.getuser()}' + getattr(Style, 'RESET_ALL', ''))
            else:
                print(Fore.RED + f'Unknown command: {command}' + getattr(Style, 'RESET_ALL', ''))
        except KeyboardInterrupt:
            print(Fore.CYAN + '\nExiting PythonJS Shell.' + getattr(Style,'RESET_ALL', ''))
            break

if __name__ == '__main__':
    shell()
