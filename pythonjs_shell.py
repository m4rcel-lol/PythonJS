import os
import subprocess
import sys
import re
import webbrowser
import asyncio
import threading
import getpass
import tempfile
import msvcrt

PYTHONJS_SHELL_VERSION = '0.2'
PYTHONJS_LANG_VERSION = '0.2'

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
        # Fallback: define dummy color/style codes
        class Dummy:
            def __getattr__(self, name):
                return ''
        Fore = Style = Dummy()

def parse_line(line, env):
    # Remove comments
    line = line.split('//')[0].strip()
    if not line:
        return
    # Print statement (Python or JS style)
    if line.startswith('print(') and line.endswith(')'):
        to_print = line[6:-1]
        print(eval_expr(to_print, env))
    elif line.startswith('console.log(') and line.endswith(')'):
        to_print = line[12:-1]
        print(eval_expr(to_print, env))
    # Variable assignment (let, var, or none)
    elif re.match(r'^(let|var)\s+\w+\s*=.*', line) or re.match(r'^\w+\s*=.*', line):
        # Remove let/var if present
        line = re.sub(r'^(let|var)\s+', '', line)
        var, expr = line.split('=', 1)
        var = var.strip()
        value = eval_expr(expr.strip(), env)
        env[var] = value
    else:
        print(f"{Fore.YELLOW}[PythonJS] Unknown or unsupported syntax: {line}{Style.RESET_ALL}")

def eval_expr(expr, env):
    try:
        expr = expr.replace('true', 'True').replace('false', 'False')
        expr = expr.replace('null', 'None')
        expr = expr.replace('&&', 'and').replace('||', 'or')
        expr = expr.replace('===', '==').replace('!==', '!=')
        return eval(expr, {}, env)
    except Exception:
        return expr

def run_pyjs_file(filename):
    # Read and preprocess the code
    with open(filename, 'r', encoding='utf-8') as f:
        code = f.read()
    code = code.replace('console.log(', 'print(')

    # Write code to a temporary file
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.py') as tmp:
        tmp.write(code)
        tmp_filename = tmp.name

    # Start the subprocess
    proc = subprocess.Popen([sys.executable, tmp_filename], cwd=os.path.dirname(filename))

    # Function to listen for Ctrl+M
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

def run_snake_game():
    import turtle
    import time
    import random

    delay = 0.1
    score = 0
    high_score = 0

    win = turtle.Screen()
    win.title("PythonJS Snake Game")
    win.bgcolor("#222831")
    win.setup(width=600, height=600)
    win.tracer(0)

    head = turtle.Turtle()
    head.speed(0)
    head.shape("square")
    head.color("#00ff00")
    head.penup()
    head.goto(0, 0)
    head.direction = "stop"

    food = turtle.Turtle()
    food.speed(0)
    food.shape("circle")
    food.color("#ff2058")
    food.penup()
    food.goto(0, 100)

    segments = []

    score_display = turtle.Turtle()
    score_display.speed(0)
    score_display.color("#f6f6f6")
    score_display.penup()
    score_display.hideturtle()
    score_display.goto(0, 260)
    score_display.write("Score: 0  High Score: 0", align="center", font=("Courier", 24, "normal"))

    def go_up():
        if head.direction != "down":
            head.direction = "up"
    def go_down():
        if head.direction != "up":
            head.direction = "down"
    def go_left():
        if head.direction != "right":
            head.direction = "left"
    def go_right():
        if head.direction != "left":
            head.direction = "right"
    def move():
        x = head.xcor()
        y = head.ycor()
        if head.direction == "up":
            head.sety(y + 20)
        if head.direction == "down":
            head.sety(y - 20)
        if head.direction == "left":
            head.setx(x - 20)
        if head.direction == "right":
            head.setx(x + 20)

    win.listen()
    win.onkey(go_up, "Up")
    win.onkey(go_down, "Down")
    win.onkey(go_left, "Left")
    win.onkey(go_right, "Right")

    try:
        while True:
            win.update()
            # Border collision
            if head.xcor() > 290 or head.xcor() < -290 or head.ycor() > 290 or head.ycor() < -290:
                time.sleep(1)
                head.goto(0, 0)
                head.direction = "stop"
                for segment in segments:
                    segment.goto(1000, 1000)
                segments.clear()
                score = 0
                score_display.clear()
                score_display.write(f"Score: {score}  High Score: {high_score}", align="center", font=("Courier", 24, "normal"))
            # Food collision
            if head.distance(food) < 20:
                x = random.randint(-14, 14) * 20
                y = random.randint(-14, 14) * 20
                food.goto(x, y)
                new_segment = turtle.Turtle()
                new_segment.speed(0)
                new_segment.shape("square")
                new_segment.color("#00ff99")
                new_segment.penup()
                segments.append(new_segment)
                score += 10
                if score > high_score:
                    high_score = score
                score_display.clear()
                score_display.write(f"Score: {score}  High Score: {high_score}", align="center", font=("Courier", 24, "normal"))
            # Move segments
            for i in range(len(segments) - 1, 0, -1):
                x = segments[i - 1].xcor()
                y = segments[i - 1].ycor()
                segments[i].goto(x, y)
            if segments:
                segments[0].goto(head.xcor(), head.ycor())
            move()
            # Body collision
            for segment in segments:
                if segment.distance(head) < 20:
                    time.sleep(1)
                    head.goto(0, 0)
                    head.direction = "stop"
                    for segment in segments:
                        segment.goto(1000, 1000)
                    segments.clear()
                    score = 0
                    score_display.clear()
                    score_display.write(f"Score: {score}  High Score: {high_score}", align="center", font=("Courier", 24, "normal"))
            time.sleep(delay)
    except turtle.Terminator:
        print("Snake game exited.")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILES_DIR = os.path.join(BASE_DIR, 'files')
if not os.path.exists(FILES_DIR):
    os.makedirs(FILES_DIR)

CURRENT_DIR = FILES_DIR

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def shell():
    global CURRENT_DIR
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
  cd [path]             - Change directory (within files folder)
  run [filename.pyjs]   - Run a PythonJS file
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
                            run_pyjs(filename)
            elif command == 'run':
                if not args or not args[0].endswith('.pyjs'):
                    print(Fore.RED + 'Usage: run [filename.pyjs]' + getattr(Style, 'RESET_ALL', ''))
                else:
                    filename = os.path.join(CURRENT_DIR, args[0])
                    if os.path.exists(filename):
                        run_pyjs(filename)
                    else:
                        print(Fore.RED + 'File does not exist.' + getattr(Style, 'RESET_ALL', ''))
            elif command == 'execute':
                if not args:
                    print(Fore.RED + 'Usage: execute [executable] [optional arguments]' + getattr(Style, 'RESET_ALL', ''))
                else:
                    try:
                        subprocess.Popen(' '.join(args), shell=True)
                        print(Fore.GREEN + f"Executed: {' '.join(args)}" + getattr(Style, 'RESET_ALL', ''))
                    except Exception as e:
                        print(Fore.RED + f"Failed to execute: {e}" + getattr(Style, 'RESET_ALL', ''))
            elif command == 'restart':
                print(Fore.CYAN + 'Restarting PythonJS Shell...' + getattr(Style, 'RESET_ALL', ''))
                python = sys.executable
                os.execl(python, python, *sys.argv)
            elif command == 'support':
                try:
                    import discord
                except ImportError:
                    print(Fore.CYAN + 'discord.py not found. Installing...' + getattr(Style, 'RESET_ALL', ''))
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'discord.py'])
                    import discord
                from support import DISCORD_BOT_TOKEN, SUPPORT_USER_ID
                import asyncio
                import threading

                class SupportClient(discord.Client):
                    def __init__(self, *args, **kwargs):
                        super().__init__(*args, **kwargs)
                        self.loop_running = True
                        self.last_message_id = None
                        self.received_msgs = []
                        self.ready_event = asyncio.Event()
                        self.loop_ref = None
                        self.thread_done = threading.Event()

                    async def on_ready(self):
                        print(Fore.CYAN + f'Connected to Discord as {self.user}. Starting support chat with m5rcel. Type /exit to quit.' + getattr(Style, 'RESET_ALL', ''))
                        self.user_obj = await self.fetch_user(SUPPORT_USER_ID)
                        self.ready_event.set()
                        asyncio.create_task(self.listen_for_replies())

                    async def on_message(self, message):
                        if message.author.id == SUPPORT_USER_ID and isinstance(message.channel, discord.DMChannel):
                            self.received_msgs.append(f"m5rcel: {message.content}")
                            print(Fore.MAGENTA + f"m5rcel: {message.content}" + getattr(Style, 'RESET_ALL', ''))

                    async def listen_for_replies(self):
                        await self.wait_until_ready()
                        while self.loop_running:
                            await asyncio.sleep(1)

                    async def send_support_message(self, text):
                        await self.ready_event.wait()
                        await self.user_obj.send(text)
                        print(Fore.GREEN + f"You: {text}" + getattr(Style, 'RESET_ALL', ''))

                    async def close_support(self):
                        self.loop_running = False
                        try:
                            await self.change_presence(status=discord.Status.offline)
                        except Exception:
                            pass
                        await self.close()
                        try:
                            loop = asyncio.get_event_loop()
                            loop.stop()
                        except Exception:
                            pass

                def start_support_chat():
                    intents = discord.Intents.default()
                    intents.messages = True
                    intents.dm_messages = True
                    client = SupportClient(intents=intents)
                    client.loop_ref = None

                    def run_client():
                        loop = asyncio.new_event_loop()
                        client.loop_ref = loop
                        asyncio.set_event_loop(loop)
                        try:
                            loop.run_until_complete(client.start(DISCORD_BOT_TOKEN))
                        finally:
                            loop.stop()
                            loop.close()
                            client.thread_done.set()

                    thread = threading.Thread(target=run_client, daemon=True)
                    thread.start()

                    # Wait for the event loop to be set
                    import time
                    while client.loop_ref is None:
                        time.sleep(0.05)
                    # Wait for the bot to be ready before allowing input
                    while not client.ready_event.is_set():
                        time.sleep(0.05)

                    try:
                        while True:
                            msg = input(Fore.BLUE + '[Support Chat] > ' + getattr(Style, 'RESET_ALL', ''))
                            if msg.strip() == '/exit':
                                print(Fore.CYAN + 'Support Chat has ended! To Exit, Exit this window and reopen PythonJS.' + getattr(Style, 'RESET_ALL', ''))
                                fut = asyncio.run_coroutine_threadsafe(client.close_support(), client.loop_ref)
                                fut.result()
                                client.thread_done.wait()
                                sys.exit(0)
                            elif msg.strip():
                                fut = asyncio.run_coroutine_threadsafe(client.send_support_message(msg.strip()), client.loop_ref)
                                fut.result()
                    except KeyboardInterrupt:
                        print(Fore.CYAN + '\nSupport Chat has ended! To Exit, Exit this window and reopen PythonJS.' + getattr(Style, 'RESET_ALL', ''))
                        fut = asyncio.run_coroutine_threadsafe(client.close_support(), client.loop_ref)
                        fut.result()
                        client.thread_done.wait()
                        sys.exit(0)

                start_support_chat()
                continue
            elif command == 'snake':
                run_snake_game()
            elif command == 'site':
                print(Fore.CYAN + 'Opening PythonJS main page in your browser...' + getattr(Style, 'RESET_ALL', ''))
                webbrowser.open('https://m4rcel.lol/pythonjs')
            elif command == 'print':
                if not args:
                    print(Fore.RED + 'Usage: print [text]' + getattr(Style, 'RESET_ALL', ''))
                else:
                    print(' '.join(args))
            elif command == 'version':
                print(Fore.CYAN + '╔' + '═'*36 + '╗' + getattr(Style, 'RESET_ALL', ''))
                print(Fore.CYAN + '║{:^36s}║'.format('PythonJS Version Info') + getattr(Style, 'RESET_ALL', ''))
                print(Fore.CYAN + '╠' + '═'*36 + '╣' + getattr(Style, 'RESET_ALL', ''))
                print(Fore.CYAN + '║ Shell:    v{:<24}║'.format(PYTHONJS_SHELL_VERSION) + getattr(Style, 'RESET_ALL', ''))
                print(Fore.CYAN + '║ Language: v{:<24}║'.format(PYTHONJS_LANG_VERSION) + getattr(Style, 'RESET_ALL', ''))
                print(Fore.CYAN + '╚' + '═'*36 + '╝' + getattr(Style, 'RESET_ALL', ''))
                continue
            elif command == 'credits':
                print(Fore.MAGENTA + '╔' + '═'*36 + '╗' + getattr(Style, 'RESET_ALL', ''))
                print(Fore.MAGENTA + '║{:^36s}║'.format('PythonJS by m5rcel') + getattr(Style, 'RESET_ALL', ''))
                print(Fore.MAGENTA + '╠' + '═'*36 + '╣' + getattr(Style, 'RESET_ALL', ''))
                print(Fore.MAGENTA + '║{:^36s}║'.format('Discord: m5rcel') + getattr(Style, 'RESET_ALL', ''))
                print(Fore.MAGENTA + '╚' + '═'*36 + '╝' + getattr(Style, 'RESET_ALL', ''))
                continue
            elif command == 'cmd':
                print(Fore.CYAN + 'Exiting PythonJS Shell and opening Windows Command Prompt...' + getattr(Style, 'RESET_ALL', ''))
                os.system('start cmd')
                break
            elif command == 'clear':
                clear()
                continue
            elif command == 'whoami':
                user = getpass.getuser()
                print(Fore.CYAN + f'Current user: {user}' + getattr(Style, 'RESET_ALL', ''))
                continue
            elif command == 'mp3':
                if not args:
                    print(Fore.RED + 'Usage: mp3 [name of mp3 without extension]' + getattr(Style, 'RESET_ALL', ''))
                else:
                    mp3_name = args[0] + '.mp3'
                    mp3_path = os.path.join(CURRENT_DIR, mp3_name)
                    if os.path.exists(mp3_path):
                        try:
                            if sys.platform == 'win32':
                                os.startfile(mp3_path)
                            elif sys.platform == 'darwin':
                                subprocess.Popen(['open', mp3_path])
                            else:
                                subprocess.Popen(['xdg-open', mp3_path])
                            print(Fore.GREEN + f'Playing {mp3_name}' + getattr(Style, 'RESET_ALL', ''))
                        except Exception as e:
                            print(Fore.RED + f'Failed to play mp3: {e}' + getattr(Style, 'RESET_ALL', ''))
                    else:
                        print(Fore.RED + f'MP3 file not found: {mp3_name}' + getattr(Style, 'RESET_ALL', ''))
            elif command == 'troll':
                svg_path = os.path.join(CURRENT_DIR, 'troll.svg')
                if os.path.exists(svg_path):
                    try:
                        if sys.platform == 'win32':
                            os.startfile(svg_path)
                        elif sys.platform == 'darwin':
                            subprocess.Popen(['open', svg_path])
                        else:
                            subprocess.Popen(['xdg-open', svg_path])
                        print(Fore.GREEN + 'Troll face displayed!' + getattr(Style, 'RESET_ALL', ''))
                    except Exception as e:
                        print(Fore.RED + f'Failed to open troll.svg: {e}' + getattr(Style, 'RESET_ALL', ''))
                else:
                    print(Fore.RED + 'troll.svg not found in files folder.' + getattr(Style, 'RESET_ALL', ''))
            else:
                print(Fore.RED + f'Unknown command: {command}' + getattr(Style, 'RESET_ALL', ''))
        except KeyboardInterrupt:
            print(Fore.CYAN + '\nExiting PythonJS Shell.' + getattr(Style, 'RESET_ALL', ''))
            break

def run_pyjs(filename):
    run_pyjs_file(filename)

if __name__ == '__main__':
    shell()
