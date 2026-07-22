import sys
import os
import subprocess
import shutil

# ░█████╗░░█████╗░░██████╗░█████╗░░█████╗░██████╗░███████╗
# ██╔══██╗██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔════╝
# ██║░░╚═╝███████║╚█████╗░██║░░╚═╝███████║██║░░██║█████╗░░
# ██║░░██╗██╔══██║░╚═══██╗██║░░██╗██╔══██║██║░░██║██╔══╝░░
# ╚█████╔╝██║░░██║██████╔╝╚█████╔╝██║░░██║██████╔╝███████╗
# ░╚════╝░╚═╝░░╚═╝╚═════╝░░╚════╝░╚═╝░░╚═╝╚═════╝░╚══════╝
#
# Compilable-Transpiled Programming Language 
#
# Version: 1.2.2

import sub.translator
import sub.b2e
import sub.errorlib as erl
from sub.type_checker import TypeChecker

version = "1.2.2; Compiler 1.2.0; TypeChecker 1.0.0"

def get_sub_dir():
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(os.path.abspath(sys.executable)), "sub")
    return os.path.abspath("sub")

SUB_DIR = get_sub_dir()

if len(sys.argv) < 2:
    print("Type file for compilation.")
    sys.exit(1)

command = sys.argv[1]

if command == "version":
    print(f"Cascade {version}")
    sys.exit(0)

def filerun(content, type="new"):
    sub.b2e.buildExe(content)
    
    exe_path = os.path.join(SUB_DIR, "output.exe")
    if os.path.exists(exe_path):
        if type == "new":
            try:
                subprocess.Popen(f'cmd.exe /c "{exe_path}"', creationflags=subprocess.CREATE_NEW_CONSOLE)
            except Exception as e:
                erl.showFastError("Compilation", e, "...")
        elif type == "old":
            try:
                subprocess.Popen(f'conhost cmd.exe /c "{exe_path}"', creationflags=subprocess.CREATE_NEW_CONSOLE)
            except Exception as e:
                erl.showFastError("Compilation", e, "...")
    else:
        erl.showFastError("Compilation", "An error occurred while compiling the program", "...")

if len(sys.argv) == 3 and sys.argv[2] == "build":
    with open(command, 'r', encoding='utf-8') as f:
        code = f.read()
    if code.strip() != "":
        translated = sub.translator.translatecode(code)
        if translated:
            sub.b2e.buildExe(translated)

            output_exe = os.path.join(SUB_DIR, 'output.exe')
            if os.path.exists(output_exe):
                destination = os.path.join(os.getcwd(), 'build.exe')
                shutil.move(output_exe, destination)
                print(f"Succes: Builded at {destination}")

    sys.exit(0)
elif len(sys.argv) == 3 and sys.argv[2] == "oldmode":
    if not os.path.exists(command):
        print(f"File {command} not found")
        sys.exit(1)

    with open(command, 'r', encoding='utf-8') as f:
        code = f.read()

    if code.strip() != "":
        translated = sub.translator.translatecode(code)
        if translated:
            print(translated)
            filerun(translated, "old")

    sys.exit(0)

if not os.path.exists(command):
    print(f"File {command} not found")
    sys.exit(1)

with open(command, 'r', encoding='utf-8') as f:
    code = f.read()

if code.strip() != "":
    translated = sub.translator.translatecode(code)
    if translated:

        print(translated)

        filerun(translated)