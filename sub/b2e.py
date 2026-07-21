### CascadeLang ###
# Batch to exe comiler
#
# Packs the created Batch file into an EXE for subsequent assembly or execution
###################
import os
import sys
import subprocess

import sub.errorlib as erl

def get_sub_dir():
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        return os.path.join(exe_dir, "sub")
    return os.path.abspath("sub")

SUB_DIR = get_sub_dir()

def kill_old_processes():
    try:
        subprocess.run(["taskkill", "/F", "/IM", "output.exe"], 
                       stdout=subprocess.DEVNULL, 
                       stderr=subprocess.DEVNULL)
    except Exception:
        pass

def buildExe(code):
    kill_old_processes()
    
    exe_path = os.path.join(SUB_DIR, "output.exe")
    temp_bat = os.path.join(SUB_DIR, "temp.bat")
    bat2exe_path = os.path.join(SUB_DIR, "bat2exe.exe")

    if os.path.exists(exe_path):
        try:
            os.remove(exe_path)
        except PermissionError:
            erl.showFastError("Compilation", "The recompile file is already running, and its process could not be completed", "Complete the process through the Task Manager")
            return

    with open(temp_bat, 'w', encoding='utf-8') as f:
        f.write(code)

    subprocess.run(f'"{bat2exe_path}" temp.bat', shell=True, cwd=SUB_DIR)

    if os.path.exists(temp_bat):
        try:
            os.remove(temp_bat)
        except OSError:
            pass